import os
from .test_data import params
from collections import Counter
from unittest.mock import patch, mock_open
import pytest
from utility.evaluation_utils import (
   Paths,
   Scores,
   clean_raw,
   get_main_name,
   label_entity,
   eval_entity,
   eval_references,
   evaluate_person
)
from utility.settings import settings

# -------------------------------------------------
# 1. Test Paths Class functions
# -------------------------------------------------
def test_paths_init():
    paths = Paths()

    settings.PATH_TO_GROUND_TRUTH = None
    paths = Paths()
    assert not paths.success
    settings.PATH_TO_GROUND_TRUTH = params.conf["PATH_TO_GROUND_TRUTH"]


def test_paths_update():
    settings.PATH_TO_GROUND_TRUTH = params.conf["PATH_TO_GROUND_TRUTH"]
    settings.PATH_TO_OUTFILE_FOLDER = params.conf["PATH_TO_OUTFILE_FOLDER"]
    settings.PATH_TO_INPUT_FOLDERS = params.conf["PATH_TO_INPUT_FOLDERS"]
    paths = Paths()
    paths.update("magazine", "test_mag")
    paths.update("file", "test_file")

    # key can be gt, link, eval, input
    # state can be magazine, file or empty
    # ref level name can be ref, ent, or empty
    with pytest.raises(AssertionError) as excinfo:
        paths.get("input", "", "net", "")
        assert excinfo.value.args[0] == "'net' is not in ['ent', 'ref', '']"
    with pytest.raises(AssertionError) as excinfo:
        paths.get("input", "", "", "wirth_fuzzy")
    assert excinfo.value.args[0] == "'wirth_fuzzy' is not in ['with_fuzzy', 'without_fuzzy', '']"

    assert paths.get("input", "", "ent", "") == settings.PATH_TO_INPUT_FOLDERS
    assert paths.get(
        "input", "magazine", "", ""
    ) == settings.PATH_TO_INPUT_FOLDERS + "test_mag"
    assert paths.get(
        "input", "file", "", ""
    ) == settings.PATH_TO_INPUT_FOLDERS + "test_mag/test_file"
    assert paths.get(
        "input", "", "", "with_fuzzy"
    ) == settings.PATH_TO_INPUT_FOLDERS
    assert paths.get("input", "", "", "") == settings.PATH_TO_INPUT_FOLDERS

    for type_ in ["eval", "link"]:
        for ref_lvl in ["ent", "ref"]:
            for gt_fuzziness_name in ["with_fuzzy", "without_fuzzy"]:
                assert paths.get(
                    type_, "", ref_lvl, ""
                ) == settings.PATH_TO_OUTFILE_FOLDER+type_+"_"+ref_lvl
                assert paths.get(
                    type_, "magazine", "", ""
                ) == settings.PATH_TO_OUTFILE_FOLDER+type_+"/test_mag"
                assert paths.get(
                    type_, "file", "", ""
                ) == settings.PATH_TO_OUTFILE_FOLDER+type_+"/test_mag/test_file"
                assert paths.get(
                    type_, "", "", gt_fuzziness_name
                ) == settings.PATH_TO_OUTFILE_FOLDER+type_+"_"+gt_fuzziness_name
                assert paths.get(
                    type_, "", "", ""
                ) == settings.PATH_TO_OUTFILE_FOLDER+type_

    assert paths.get(
        "gt", "", "ent", ""
    ) == settings.PATH_TO_GROUND_TRUTH+"_ent"
    assert paths.get(
        "gt", "magazine", "", ""
    ) == settings.PATH_TO_GROUND_TRUTH+"test_mag"
    assert paths.get(
        "gt", "file", "", ""
    ) == settings.PATH_TO_GROUND_TRUTH+"test_mag/test_file"
    assert paths.get(
        "gt", "", "", "with_fuzzy"
    ) == settings.PATH_TO_GROUND_TRUTH
    assert paths.get("gt", "", "", "") == settings.PATH_TO_GROUND_TRUTH


@patch("builtins.open", new_callable=mock_open, read_data='{"key": "value"}')
@patch("utility.evaluation_utils.Paths.get")
def test_paths_get_jsonl(mock_get, mock_open_file):

    paths = Paths()
    mock_get.return_value = "./data/input/test_file.jsonl"

    result = paths.get_jsonl("input")

    assert result == [{"key": "value"}]
    mock_get.assert_called_once_with(type_="input", key="file")
    mock_open_file.assert_called_once_with(
        "./data/input/test_file.jsonl",
        "r",
        encoding="utf-8"
    )


def test_paths_check_and_create():
    paths = Paths()
    paths.update("magazine", "test_mag")
    paths.update("file", "test_file")

    already_existed = os.path.isdir(params.conf["PATH_TO_OUTFILE_FOLDER"]+"link")
    path_linked = paths.check_and_create("link", "", "", "")
    assert path_linked == params.conf["PATH_TO_OUTFILE_FOLDER"]+"link"
    assert os.path.isdir(path_linked)
    if not already_existed:
        os.rmdir(path_linked)

    for type_ in ["eval", "link"]:
        path_with_type = params.conf["PATH_TO_OUTFILE_FOLDER"] + type_

        already_existed = os.path.isdir(path_with_type)
        path = paths.check_and_create(type_, "magazine", "", "")
        assert path == path_with_type+"/test_mag"
        assert os.path.isdir(path)
        os.rmdir(path)
        if not already_existed:
            os.rmdir(path_with_type)

        already_existed = os.path.isdir(path_with_type)
        path = paths.check_and_create(type_, "file", "", "")
        assert path == path_with_type+"/test_mag/test_file"
        assert os.path.exists("/".join(path.split("/")[:-1])), path
        os.rmdir(path_with_type+"/test_mag")
        if not already_existed:
            os.rmdir(path_with_type)

        for ref_lvl in ["ent", "ref"]:
            for gt_fuzziness_name in ["with_fuzzy", "without_fuzzy"]:
                if type_ == "eval":
                    path_gt = path_with_type+"_"+ref_lvl+"_"+gt_fuzziness_name
                    already_existed = os.path.isdir(path_gt)
                    path = paths.check_and_create(
                        type_,
                        "",
                        ref_lvl,
                        gt_fuzziness_name
                    )
                    assert path == path_gt
                    assert os.path.isdir(path)
                    if not already_existed:
                        os.rmdir(path)


def test_paths_save_json():
    paths = Paths()
    paths.update("magazine", "test_mag")
    paths.update("file", "test_file")

    for type_ in ["eval", "link"]:
        path_with_type = params.conf["PATH_TO_OUTFILE_FOLDER"]+type_
        for ref_lvl in ["ent", "ref"]:
            for gt_fuzziness_name in ["with_fuzzy", "without_fuzzy"]:
                path_gt = path_with_type+"_"+ref_lvl+"_"+gt_fuzziness_name

                already_existed = os.path.isdir(path_gt)
                paths.save_json(
                    type_,
                    "magazine",
                    {"test1": "test2"},
                    ref_lvl,
                    gt_fuzziness_name
                )
                path_1 = paths.get(
                    type_,
                    "magazine",
                    ref_lvl,
                    gt_fuzziness_name
                )
                assert os.path.exists(path_1)
                os.rmdir(path_1)
                os.remove(path_gt+"/"+"test_mag.json")
                if not already_existed:
                    os.rmdir(path_gt)

                already_existed = os.path.isdir(path_gt)
                paths.save_json(
                    type_,
                    "file",
                    {"test1": "test2"},
                    ref_lvl,
                    gt_fuzziness_name
                )
                path_1 = paths.get(
                    type_,
                    "file",
                    ref_lvl,
                    gt_fuzziness_name
                )
                assert os.path.exists(path_1)
                os.remove(path_1)
                os.rmdir(path_gt+"/"+"test_mag")
                if not already_existed:
                    os.rmdir(path_gt)


# -------------------------------------------------
# 2. Test Scores Class functions
# -------------------------------------------------
def test_scores_init():
    scores = Scores({"tp": 161, "fp": 199, "fn": 74, "tn": 327})
    assert scores.precision == 0
    assert scores.recall == 0
    assert scores.f1 == 0
    assert Counter(
        {"tp": 161, "fp": 199, "fn": 74, "tn": 327}
    ) == scores.counter


def test_scores_compute_scores():
    counters = [{"tp": 161, "fp": 199, "fn": 74, "tn": 327},
                {"tp": 0, "fp": 3, "fn": 0, "tn": 93}]
    for i in counters:
        scores = Scores(i)
        scores.compute_scores()
        if scores.counter["tp"] + scores.counter["fp"] != 0:
            assert scores.precision == scores.counter["tp"] / (
                scores.counter["tp"] + scores.counter["fp"])
        else:
            assert scores.precision == 0
        if scores.counter["tp"] + scores.counter["fn"] != 0:
            assert scores.recall == scores.counter["tp"] / (
                scores.counter["tp"] + scores.counter["fn"])
        else:
            assert scores.recall == 0
        if (scores.counter["tp"] +
                scores.counter["tn"] +
                scores.counter["fp"] +
                scores.counter["fn"]) != 0:
            assert scores.accuracy == ((
                scores.counter["tn"] + scores.counter["tp"]) / (
                    scores.counter["tn"] +
                    scores.counter["tp"] +
                    scores.counter["fn"] +
                    scores.counter["fp"]))
        else:
            assert scores.accuracy == 0

        if ((scores.counter["tp"] + scores.counter["fp"] != 0) and
                (scores.counter["tp"] + scores.counter["fn"] != 0)):
            assert round(scores.f1, 10) == (
                round(2 * (
                    scores.counter["tp"] / (
                        scores.counter["tp"] + scores.counter["fp"]) *
                    scores.counter["tp"] / (
                        scores.counter["tp"] + scores.counter["fn"])) / (
                            scores.counter["tp"] / (
                                scores.counter["tp"] + scores.counter["fp"]) +
                            scores.counter["tp"] / (
                                scores.counter["tp"] + scores.counter["fn"])),
                      10)
            )
        else:
            assert scores.f1 == 0


def test_scores_update_counter():
    """
    This is a bit absurd but let's do it
    """
    counters = [{"tp": 161, "fp": 199, "fn": 74, "tn": 327},
                {"tp": 0, "fp": 3, "fn": 0, "tn": 93}]
    init_counter = {"tp": 1, "fp": 1, "fn": 1, "tn": 1}
    for i in counters:
        scores = Scores(init_counter)
        scores.update_counter(i)
        assert scores.counter["tp"] == i["tp"] + init_counter["tp"]
        assert scores.counter["fp"] == i["fp"] + init_counter["fp"]
        assert scores.counter["fn"] == i["fn"] + init_counter["fn"]
        assert scores.counter["tn"] == i["tn"] + init_counter["tn"]


def test_scores_get_score():
    """
    This is a bit absurd but let's do it
    """
    counters = [{"tp": 161, "fp": 199, "fn": 74, "tn": 327},
                {"tp": 0, "fp": 3, "fn": 0, "tn": 93}]
    roundings = [2, 3, 5]

    for i in counters:
        for r in roundings:
            scores = Scores(i)
            res = scores.get_score(round_to=r)
            assert res["tp"] == i["tp"]
            assert res["fp"] == i["fp"]
            assert res["tn"] == i["tn"]
            assert res["fn"] == i["fn"]
            if i["tp"] + i["fp"] != 0:
                assert res["Precision"] == round(
                    i["tp"] / (i["tp"] + i["fp"]),
                    r)
            else:
                assert res["Precision"] == 0
            if i["tp"] + i["fn"] != 0:
                assert res["Recall"] == round(i["tp"] / (i["tp"] + i["fn"]), r)
            else:
                assert res["Recall"] == 0
            if (i["tp"] + i["tn"] + i["fp"] + i["fn"]) != 0:
                assert res["Accuracy"] == round(((
                    i["tn"] + i["tp"]) / (
                        i["tn"] + i["tp"] + i["fn"] + i["fp"])), r)
            else:
                assert res["Accuracy"] == 0
            if i["tp"] + i["fp"] != 0 and i["tp"] + i["fn"] != 0:
                assert round(res["F1"], r) == (
                    round(2 * (
                        i["tp"] / (i["tp"] + i["fp"]) *
                        i["tp"] / (i["tp"] + i["fn"])) / (
                            i["tp"] / (i["tp"] + i["fp"]) +
                            i["tp"] / (i["tp"] + i["fn"])), r)
                )
            else:
                assert res["F1"] == 0


# -------------------------------------------------
# 3. Test clean_raw
# -------------------------------------------------
@pytest.mark.parametrize(
    "raw, top_k, is_gt, expected",
    params.PARAMS_clean_raw,
)
def test_clean_raw(raw, top_k, is_gt, expected):
    assert clean_raw(raw, top_k, is_gt) == expected


# -------------------------------------------------
# 4. Test get_main_name
# -------------------------------------------------
@pytest.mark.parametrize(
    "dictionary, expected",
    params.PARAMS_get_main_name,
)
def test_get_main_name(dictionary, expected):
    assert get_main_name(dictionary) == expected


# -------------------------------------------------
# 5. Test label_entity
# -------------------------------------------------
@pytest.mark.parametrize(
    "ent, gt, expected",
    [({'page': 'aaa-001_2004_000_0012.txt',
       'year': '2004',
       'coord': 'b'},
      [[{'page': 'aaa-001_2004_000_0012.txt',
         'year': '2004',
         'coord': 'b',
         "gt_gnd_id": "a"}]],
      "a"),
     ({'page': 'aaa-001_2004_000_0012.txt',
       'year': '2004',
       'coord': 'b'},
      [[{'page': 'aaa-001_2004_000_0012.txt',
         'year': '2004',
         'coord': 'c',
         "gt_gnd_id": "a"}]],
      "")
     ],
)
def test_label_entity(ent, gt, expected):
    assert label_entity(ent, gt) == expected


# -------------------------------------------------
# 6. Test eval_entity
# -------------------------------------------------
@pytest.mark.parametrize(
    "entity, expected",
    [({"candidates": [[]],
       "label": "a"},
      {"tp": 0, "fp": 0, "tn": 0, "fn": 1}),
     ({"candidates": ["a", "b"],
       "label": "a"},
      {"tp": 1, "fp": 0, "tn": 0, "fn": 0}),
     ({"candidates": ["a"],
       "label": ""},
      {"tp": 0, "fp": 1, "tn": 0, "fn": 0}),
     ({"candidates": [[]],
       "label": ""},
      {"tp": 0, "fp": 0, "tn": 1, "fn": 0})
     ],
)
def test_eval_entity(entity, expected):
    assert eval_entity(entity) == expected


# -------------------------------------------------
# 7. Test eval_references
# -------------------------------------------------
@pytest.mark.parametrize(
    "entity, expected",
    [({"candidates": [[], []],
       "labels": ["a", "b"]},
      {"tp": 0, "fp": 0, "tn": 0, "fn": 2}),
     ({"candidates": [["a"], ["b"]],
       "labels": ["a", "b"]},
      {"tp": 2, "fp": 0, "tn": 0, "fn": 0}),
     ({"candidates": [["a"], ["b"]],
       "labels": ["", ""]},
      {"tp": 0, "fp": 2, "tn": 0, "fn": 0}),
     ({"candidates": [[], []],
       "labels": ["", ""]},
      {"tp": 0, "fp": 0, "tn": 2, "fn": 0})
     ],
)
def test_eval_references(entity, expected):
    assert eval_references(entity) == expected


# -------------------------------------------------
# 8. Test evaluate_person
# -------------------------------------------------
@pytest.mark.parametrize(
    "gt, linked, ref_level, top_k, inkb_score, expected",
    params.PARAMS_evaluate_person,
)
def test_evaluate_person(gt, linked, ref_level, top_k, inkb_score, expected):
    assert evaluate_person(gt, linked, ref_level, top_k, inkb_score) == expected
