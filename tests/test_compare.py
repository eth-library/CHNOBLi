import os
import tempfile
import pytest
from .test_data import params
from utility.compare import (
    compare_gnd_info,
    compare_references,
    compare_linking_person,
    compare_linking_places,
    compare_linking,
    compare_tagging
)


# -------------------------------------------------
# Test compare_gnd_info
# -------------------------------------------------
@pytest.mark.parametrize(
    "entity_pre, entity_post",
    [({"gnd_ids": []}, {"gnd_ids": []}),
     ({"gnd_ids": [12, 13, 14]}, {"gnd_ids": [14, 14, 13, 12]}),
     ],
)
def test_compare_gnd_info(entity_pre, entity_post):
    assert compare_gnd_info(entity_pre, entity_post)

    with pytest.raises(Exception) as excinfo:
        compare_gnd_info({"gnd_ids": [12]}, {"gnd_ids": [15]})
    assert str(excinfo.value) == "The found gnd_ids of at least one entity changed."


# -------------------------------------------------
# Test compare_references
# -------------------------------------------------
@pytest.mark.parametrize(
    "entity_pre, entity_post",
    [({"references": {"1": {"refs": [{"sent": "", "coords": ""},
                                     {"sent": "a", "coords": "b"}]},
                      "2": {"refs": [{"sent": "", "coords": ""}]},
                      "3": {"refs": [{"sent": "", "coords": ""}]}}},
      {"references": {"1": {"refs": [{"sent": "", "coords": ""},
                                     {"sent": "a", "coords": "b"}]},
                      "2": {"refs": [{"sent": "", "coords": ""}]},
                      "3": {"refs": [{"sent": "", "coords": ""}]}}}),
     ],
)
def test_compare_references(entity_pre, entity_post):
    assert compare_references(entity_pre, entity_post)

    with pytest.raises(Exception) as excinfo:
        compare_references(
            {"references": {"1": {"refs": [{"sent": "", "coords": ""}]},
                            "2": {"refs": [{"sent": "", "coords": ""}]},
                            "3": {"refs": [{"sent": "", "coords": ""}]}}},
            {"references": {"1": {"refs": [{"sent": "", "coords": ""}]},
                            "3": {"refs": [{"sent": "", "coords": ""}]}}})
    assert str(excinfo.value) == "The page references do not match for at least one entity"

    with pytest.raises(Exception) as excinfo:
        compare_references(
            {"references": {"1": {"refs": [{"sent": "", "coords": ""}]},
                            "2": {"refs": [{"sent": "", "coords": ""}]},
                            "3": {"refs": [{"sent": "", "coords": ""}]}}},
            {"references": {"1": {"refs": [{"sent": "", "coords": ""}]},
                            "2": {"refs": [{"sent": "", "coords": ""}]},
                            "3": {"refs": [{"sent": "", "coords": ""},
                                           {"sent": "", "coords": ""}]}}})
    assert str(excinfo.value) == "The number of references for this entity changed."

    with pytest.raises(Exception) as excinfo:
        compare_references(
            {"references": {"1": {"refs": [{"sent": "", "coords": ""},
                                           {"sent": "a", "coords": ""}]}}},
            {"references": {"1": {"refs": [{"sent": "", "coords": ""},
                                           {"sent": "", "coords": ""}]}}})
    assert str(excinfo.value) == "The number of the sentence where at least one entity is mentioned changed."

    with pytest.raises(Exception) as excinfo:
        compare_references(
            {"references": {"1": {"refs": [{"sent": "", "coords": ""},
                                           {"sent": "", "coords": "a"}]}}},
            {"references": {"1": {"refs": [{"sent": "", "coords": ""},
                                           {"sent": "", "coords": ""}]}}})
    assert str(excinfo.value) == "The coordinates where at least one entity is mentioned changed."


# -------------------------------------------------
# Test compare_linking_person
# -------------------------------------------------
@pytest.mark.parametrize(
    "list_pre, list_post",
    params.PARAMS_compare_linking_person,
)
def test_compare_linking_person(list_pre, list_post):
    assert compare_linking_person(list_pre, list_post)

    with pytest.raises(Exception) as excinfo:
        compare_linking_person(
            [{"type": "PER",
              "lastname": "a",
              "firstname": "",
              "abbr_firstname": "",
              "address": "",
              "titles": "",
              "profession": "",
              "other": [],
              "id": "",
              "references": {},
              "gnd_ids": []}],
            [{"type": "PER",
              "lastname": "b",
              "firstname": "",
              "abbr_firstname": "",
              "address": "",
              "titles": "",
              "profession": "",
              "other": [],
              "id": "",
              "references": {},
              "gnd_ids": []}])
    assert str(
        excinfo.value) == "The last name of at least one entity changed."

    with pytest.raises(Exception) as excinfo:
        compare_linking_person(
            [{"type": "PER",
              "lastname": "",
              "firstname": ["Hans Ueli"],
              "abbr_firstname": "",
              "address": "",
              "titles": "",
              "profession": "",
              "other": [],
              "id": "",
              "references": {},
              "gnd_ids": []}],
            [{"type": "PER",
              "lastname": "",
              "firstname": ["Ueli Hans"],
              "abbr_firstname": "",
              "address": "",
              "titles": "",
              "profession": "",
              "other": [],
              "id": "",
              "references": {},
              "gnd_ids": []}])
    assert str(
        excinfo.value) == "The first names of at least one entity changed."

    with pytest.raises(Exception) as excinfo:
        compare_linking_person(
            [{"type": "PER",
              "lastname": "",
              "firstname": "",
              "abbr_firstname": ["a", "b"],
              "address": "",
              "titles": "",
              "profession": "",
              "other": [],
              "id": "",
              "references": {},
              "gnd_ids": []}],
            [{"type": "PER",
              "lastname": "",
              "firstname": "",
              "abbr_firstname": ["b", "a"],
              "address": "",
              "titles": "",
              "profession": "",
              "other": [],
              "id": "",
              "references": {},
              "gnd_ids": []}])
    assert str(
        excinfo.value
        ) == "The abbreviated first names of at least one entity changed."

    with pytest.raises(Exception) as excinfo:
        compare_linking_person(
            [{"type": "PER",
              "lastname": "",
              "firstname": "",
              "abbr_firstname": "",
              "address": ["b"],
              "titles": "",
              "profession": "",
              "other": [],
              "id": "",
              "references": {},
              "gnd_ids": []}],
            [{"type": "PER",
              "lastname": "",
              "firstname": "",
              "abbr_firstname": "",
              "address": ["a"],
              "titles": "",
              "profession": "",
              "other": [],
              "id": "",
              "references": {},
              "gnd_ids": []}])
    assert str(excinfo.value) == "The address of at least one entity changed."

    with pytest.raises(Exception) as excinfo:
        compare_linking_person(
            [{"type": "PER",
              "lastname": "",
              "firstname": "",
              "abbr_firstname": "",
              "address": "",
              "titles": ["a"],
              "profession": "",
              "other": [],
              "id": "",
              "references": {},
              "gnd_ids": []}],
            [{"type": "PER",
              "lastname": "",
              "firstname": "",
              "abbr_firstname": "",
              "address": "",
              "titles": ["b"],
              "profession": "",
              "other": [],
              "id": "",
              "references": {}, "gnd_ids": []}])
    assert str(excinfo.value) == "The titles of at least one entity changed."

    with pytest.raises(Exception) as excinfo:
        compare_linking_person(
            [{"type": "PER",
              "lastname": "",
              "firstname": "",
              "abbr_firstname": "",
              "address": "",
              "titles": "",
              "profession": ["a"],
              "other": [],
              "id": "",
              "references": {},
              "gnd_ids": []}],
            [{"type": "PER",
              "lastname": "",
              "firstname": "",
              "abbr_firstname": "",
              "address": "",
              "titles": "",
              "profession": ["b"],
              "other": [],
              "id": "",
              "references": {}, "gnd_ids": []}])
    assert str(excinfo.value) == "The profession of at least one entity changed."

    with pytest.raises(Exception) as excinfo:
        compare_linking_person(
            [{"type": "PER",
              "lastname": "",
              "firstname": "",
              "abbr_firstname": "",
              "address": "",
              "titles": "",
              "profession": "",
              "other": ["ab"],
              "id": "",
              "references": {},
              "gnd_ids": []}],
            [{"type": "PER",
              "lastname": "",
              "firstname": "",
              "abbr_firstname": "",
              "address": "",
              "titles": "",
              "profession": "",
              "other": ["cd"],
              "id": "",
              "references": {}, "gnd_ids": []}])
    assert str(excinfo.value) == "The 'other' field of at least one entity changed."

    with pytest.raises(Exception) as excinfo:
        compare_linking_person(
            [{"type": "PER",
              "lastname": "",
              "firstname": "",
              "abbr_firstname": "",
              "address": "",
              "titles": "",
              "profession": "",
              "other": "",
              "id": "",
              "references": {},
              "gnd_ids": []}],
            [{"type": "GPE",
              "lastname": "",
              "firstname": "",
              "abbr_firstname": "",
              "address": "",
              "titles": "",
              "profession": "",
              "other": "",
              "id": "",
              "references": {}, "gnd_ids": []}])
    assert str(excinfo.value) == "The type of at least one entity changed."

    with pytest.raises(Exception) as excinfo:
        compare_linking_person(
            [{"type": "PER",
              "lastname": "",
              "firstname": "",
              "abbr_firstname": "",
              "address": "",
              "titles": "",
              "profession": "",
              "other": "",
              "id": "1",
              "references": {},
              "gnd_ids": []}],
            [{"type": "PER",
              "lastname": "",
              "firstname": "",
              "abbr_firstname": "",
              "address": "",
              "titles": "",
              "profession": "",
              "other": "",
              "id": "2",
              "references": {}, "gnd_ids": []}])
    assert str(excinfo.value) == "The id of at least one entity changed."


# -------------------------------------------------
# Test compare_linking_places
# -------------------------------------------------
@pytest.mark.parametrize(
    "entity_pre, entity_post",
    [([{"type": "CIT", "name": "", "tokens": "", "id": "", "references": {},
        "gnd_ids": []}],
      [{"type": "CIT", "name": "", "tokens": "", "id": "", "references": {},
        "gnd_ids": []}]),
     ([{"type": "CTR", "name": "", "tokens": "", "id": "", "references": {},
        "gnd_ids": []}],
      [{"type": "CTR", "name": "", "tokens": "", "id": "", "references": {},
        "gnd_ids": []}]),
     ([{"type": "GEO", "name": "", "tokens": "", "id": "", "references": {},
        "gnd_ids": []}],
      [{"type": "GEO", "name": "", "tokens": "", "id": "", "references": {},
        "gnd_ids": []}]),
     ([{"type": "PER", "name": "", "tokens": "", "id": "", "references": {},
        "gnd_ids": []}],
      [{"type": "GEO", "name": "", "tokens": "", "id": "", "references": {},
        "gnd_ids": []}]),
        # this is a function for comparing places
        # so if it's not a place tag it will simply return true
     ([{"type": "CIT", "name": "", "tokens": ["b", "a"], "id": "",
        "references": {}, "gnd_ids": []}],
      [{"type": "CIT", "name": "", "tokens": ["a", "b"], "id": "",
        "references": {}, "gnd_ids": []}])
     ],
)
def test_compare_linking_places(entity_pre, entity_post):
    assert compare_linking_places(entity_pre, entity_post)
    with pytest.raises(Exception) as excinfo:
        compare_linking_places(
            [{"type": "CIT", "name": "", "tokens": "", "id": "",
              "references": {}, "gnd_ids": []}],
            [{"type": "CIT", "name": "", "tokens": "", "id": "",
              "gnd_ids": []}])
    assert str(excinfo.value) == "The entity keys have changed."

    with pytest.raises(Exception) as excinfo:
        compare_linking_places(
            [{"type": "CIT", "name": "a", "tokens": "", "id": "",
              "references": {}, "gnd_ids": []}],
            [{"type": "CIT", "name": "b", "tokens": "", "id": "",
              "references": {}, "gnd_ids": []}])
    assert str(excinfo.value) == "The name of at least one entity changed."

    with pytest.raises(Exception) as excinfo:
        compare_linking_places(
            [{"type": "CIT", "name": "", "tokens": ["b"], "id": "",
              "references": {}, "gnd_ids": []}],
            [{"type": "CIT", "name": "", "tokens": ["a"], "id": "",
              "references": {}, "gnd_ids": []}])
    assert str(excinfo.value) == "The tokens of at least one entity changed."

    with pytest.raises(Exception) as excinfo:
        compare_linking_places(
            [{"type": "CIT", "name": "", "tokens": "", "id": "",
              "references": {}, "gnd_ids": []}],
            [{"type": "GEO", "name": "", "tokens": "", "id": "",
              "references": {}, "gnd_ids": []}])
    assert str(excinfo.value) == "The type of at least one entity changed."

    with pytest.raises(Exception) as excinfo:
        compare_linking_places(
            [{"type": "GEO", "name": "", "tokens": "", "id": "1",
              "references": {}, "gnd_ids": []}],
            [{"type": "GEO", "name": "", "tokens": "", "id": "2",
              "references": {}, "gnd_ids": []}])
    assert str(excinfo.value) == "The id of at least one entity changed."


# -------------------------------------------------
# Test compare_linking
# -------------------------------------------------
def test_compare_linking():
    # # Prepare a temporary file
    fake_data_pre = """[{
        "lastname": "",
        "firstname": ["A B"],
        "abbr_firstname": [],
        "address": [],
        "titles": [],
        "profession": [],
        "other": [],
        "references": {
            "abc.txt": {
                "pid": "abc",
                "refs": [{"sent": 1, "coords": ["abc", "def"]}],
                "elements": ["e111"]
            }
        },
        "type": "PER",
        "id": 0,
        "gnd_ids": []
    }]"""
    fake_data_post = """[{
        "lastname": "",
        "firstname": ["A B"],
        "abbr_firstname": [],
        "address": [],
        "titles": [],
        "profession": [],
        "other": [],
        "references": {
            "abc.txt": {
                "pid": "abc",
                "refs": [{"sent": 1, "coords": ["abc", "def"]}],
                "elements": ["e111"]
            }
        },
        "type": "PER",
        "id": 0,
        "gnd_ids": []
    }]"""
    with tempfile.NamedTemporaryFile(mode="w",
                                     delete=False,
                                     suffix=".json") as tmp:
        tmp.write(fake_data_pre)
        temp_path_pre = tmp.name

    with tempfile.NamedTemporaryFile(mode="w",
                                     delete=False,
                                     suffix=".json") as tmp:
        tmp.write(fake_data_post)
        temp_path_post = tmp.name

    try:
        assert compare_linking(temp_path_pre, temp_path_post)
    finally:
        # Clean up temp file
        os.remove(temp_path_pre)
        os.remove(temp_path_post)

    # Prepare a temporary file
    fake_data_pre = """[{
        "lastname": "",
        "firstname": ["A B"],
        "abbr_firstname": [],
        "address": [],
        "titles": [],
        "profession": [],
        "other": [],
        "references": {
            "abc.txt": {
                "pid": "abc",
                "refs": [{"sent": 1, "coords": ["abc", "def"]}],
                "elements": ["e111"]
            }
        },
        "type": "PER",
        "id": 0,
        "gnd_ids": []
    }]"""
    fake_data_post = """[{
        "lastname": "",
        "firstname": ["A B"],
        "abbr_firstname": [],
        "address": [],
        "titles": [],
        "profession": [],
        "other": [],
        "references": {
        "abc.txt": {
            "pid": "abc",
                "refs": [{"sent": 1, "coords": ["abc", "def"]}],
                "elements": ["e111"]
            }
        },
        "type": "PER",
        "id": 0,
        "gnd_ids": []
    },{
        "lastname": "",
        "firstname": ["A C"],
        "abbr_firstname": [],
        "address": [],
        "titles": [],
        "profession": [],
        "other": [],
        "references": {
            "abc.txt": {
                "pid": "abc",
                "refs": [{"sent": 1, "coords": ["abc", "def"]}],
                "elements": ["e111"]
            }
        },
        "type": "PER",
        "id": 0,
        "gnd_ids": []
    }]"""
    with tempfile.NamedTemporaryFile(mode="w",
                                     delete=False,
                                     suffix=".json") as tmp:
        tmp.write(fake_data_pre)
        temp_path_pre = tmp.name

    with tempfile.NamedTemporaryFile(mode="w",
                                     delete=False,
                                     suffix=".json") as tmp:
        tmp.write(fake_data_post)
        temp_path_post = tmp.name

    try:
        with pytest.raises(Exception) as excinfo:
            compare_linking(temp_path_pre, temp_path_post)
        assert str(excinfo.value) == "The number of entities found changed"
    finally:
        # Clean up temp file
        os.remove(temp_path_pre)
        os.remove(temp_path_post)


# -------------------------------------------------
# Test compare_tagging
# -------------------------------------------------
def test_compare_tagging():
    fake_data_pre = """{"a": [[{"token": "", "coord": "", "normalized": "", "tag": ""}]]}"""
    fake_data_post = """{"a": [[{"token": "", "coord": "", "normalized": "", "tag": ""}]]}"""
    with tempfile.NamedTemporaryFile(mode="w",
                                     delete=False,
                                     suffix=".jsonl") as tmp:
        tmp.write(fake_data_pre)
        temp_path_pre = tmp.name

    with tempfile.NamedTemporaryFile(mode="w",
                                     delete=False,
                                     suffix=".jsonl") as tmp:
        tmp.write(fake_data_post)
        temp_path_post = tmp.name

    try:
        assert compare_tagging(temp_path_pre, temp_path_post)
    finally:
        # Clean up temp file
        os.remove(temp_path_pre)
        os.remove(temp_path_post)

    fake_data_pre = """{"a": [[{"token": "", "coord": "", "normalized": "", "tag": ""}]]}"""
    fake_data_post = """{"a": [[{"token": "", "coord": "", "normalized": "", "tag": ""},
                                {"token": "", "coord": "", "normalized": "", "tag": ""}]]}"""
    with tempfile.NamedTemporaryFile(mode="w",
                                     delete=False,
                                     suffix=".jsonl") as tmp:
        tmp.write(fake_data_pre)
        temp_path_pre = tmp.name

    with tempfile.NamedTemporaryFile(mode="w",
                                     delete=False,
                                     suffix=".jsonl") as tmp:
        tmp.write(fake_data_post)
        temp_path_post = tmp.name

    try:
        with pytest.raises(Exception) as excinfo:
            compare_tagging(temp_path_pre, temp_path_post)
        assert str(
            excinfo.value) == "The tagging output is not the same length."
    finally:
        # Clean up temp file
        os.remove(temp_path_pre)
        os.remove(temp_path_post)

    fake_data_pre = """{"a": [[{"token": "", "coord": "", "normalized": "", "tag": ""}]]}"""
    fake_data_post = """{"b": [[{"token": "", "coord": "", "normalized": "", "tag": ""}]]}"""
    with tempfile.NamedTemporaryFile(mode="w",
                                     delete=False,
                                     suffix=".jsonl") as tmp:
        tmp.write(fake_data_pre)
        temp_path_pre = tmp.name

    with tempfile.NamedTemporaryFile(mode="w",
                                     delete=False,
                                     suffix=".jsonl") as tmp:
        tmp.write(fake_data_post)
        temp_path_post = tmp.name

    try:
        with pytest.raises(Exception) as excinfo:
            compare_tagging(temp_path_pre, temp_path_post)
        assert str(excinfo.value) == "The pages processed are not the same."
    finally:
        # Clean up temp file
        os.remove(temp_path_pre)
        os.remove(temp_path_post)

    fake_data_pre = """{"a": [[{"token": "", "coord": "", "normalized": "", "tag": ""}]]}"""
    fake_data_post = """{"a": []}"""
    with tempfile.NamedTemporaryFile(mode="w",
                                     delete=False,
                                     suffix=".jsonl") as tmp:
        tmp.write(fake_data_pre)
        temp_path_pre = tmp.name

    with tempfile.NamedTemporaryFile(mode="w",
                                     delete=False,
                                     suffix=".jsonl") as tmp:
        tmp.write(fake_data_post)
        temp_path_post = tmp.name

    try:
        with pytest.raises(Exception) as excinfo:
            compare_tagging(temp_path_pre, temp_path_post)
        assert str(
            excinfo.value) == "The lists of processed tokens are not the same."
    finally:
        # Clean up temp file
        os.remove(temp_path_pre)
        os.remove(temp_path_post)

    fake_data_pre = """{"a": [[{"token": ["a","b"], "coord": "", "normalized": "", "tag": ""}]]}"""
    fake_data_post = """{"a": [[{"token": ["a"], "coord": "", "normalized": "", "tag": ""}]]}"""
    with tempfile.NamedTemporaryFile(mode="w",
                                     delete=False,
                                     suffix=".jsonl") as tmp:
        tmp.write(fake_data_pre)
        temp_path_pre = tmp.name

    with tempfile.NamedTemporaryFile(mode="w",
                                     delete=False,
                                     suffix=".jsonl") as tmp:
        tmp.write(fake_data_post)
        temp_path_post = tmp.name

    try:
        with pytest.raises(Exception) as excinfo:
            compare_tagging(temp_path_pre, temp_path_post)
        assert str(excinfo.value) == "At least one token changed."
    finally:
        # Clean up temp file
        os.remove(temp_path_pre)
        os.remove(temp_path_post)

    fake_data_pre = """{"a": [[{"token": "", "coord": ["a"], "normalized": "", "tag": ""}]]}"""
    fake_data_post = """{"a": [[{"token": "", "coord": ["b"], "normalized": "", "tag": ""}]]}"""
    with tempfile.NamedTemporaryFile(mode="w",
                                     delete=False,
                                     suffix=".jsonl") as tmp:
        tmp.write(fake_data_pre)
        temp_path_pre = tmp.name

    with tempfile.NamedTemporaryFile(mode="w",
                                     delete=False,
                                     suffix=".jsonl") as tmp:
        tmp.write(fake_data_post)
        temp_path_post = tmp.name

    try:
        with pytest.raises(Exception) as excinfo:
            compare_tagging(temp_path_pre, temp_path_post)
        assert str(
            excinfo.value) == "The coordinate of at least one token changed."
    finally:
        # Clean up temp file
        os.remove(temp_path_pre)
        os.remove(temp_path_post)

    fake_data_pre = """{"a": [[{"token": "", "coord": "", "normalized": ["a"], "tag": ""}]]}"""
    fake_data_post = """{"a": [[{"token": "", "coord": "", "normalized": ["b"], "tag": ""}]]}"""
    with tempfile.NamedTemporaryFile(mode="w",
                                     delete=False,
                                     suffix=".jsonl") as tmp:
        tmp.write(fake_data_pre)
        temp_path_pre = tmp.name

    with tempfile.NamedTemporaryFile(mode="w",
                                     delete=False,
                                     suffix=".jsonl") as tmp:
        tmp.write(fake_data_post)
        temp_path_post = tmp.name

    try:
        with pytest.raises(Exception) as excinfo:
            compare_tagging(temp_path_pre, temp_path_post)
        assert str(excinfo.value) == "At least one token changed."
    finally:
        # Clean up temp file
        os.remove(temp_path_pre)
        os.remove(temp_path_post)

    fake_data_pre = """{"a": [[{"token": "", "coord": "", "normalized": "", "tag": "a"}]]}"""
    fake_data_post = """{"a": [[{"token": "", "coord": "", "normalized": "", "tag": "b"}]]}"""
    with tempfile.NamedTemporaryFile(mode="w",
                                     delete=False,
                                     suffix=".jsonl") as tmp:
        tmp.write(fake_data_pre)
        temp_path_pre = tmp.name

    with tempfile.NamedTemporaryFile(mode="w",
                                     delete=False,
                                     suffix=".jsonl") as tmp:
        tmp.write(fake_data_post)
        temp_path_post = tmp.name

    try:
        with pytest.raises(Exception) as excinfo:
            compare_tagging(temp_path_pre, temp_path_post)
        assert str(excinfo.value) == "At least one token changed."
    finally:
        # Clean up temp file
        os.remove(temp_path_pre)
        os.remove(temp_path_post)
