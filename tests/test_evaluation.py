from src.evaluation import execute_evaluation
from unittest.mock import MagicMock, patch
import pytest


def test_execute_evaluation_ref_top1_copilot():
    mock_paths = MagicMock()
    mock_paths.success = True
    mock_paths.state = {}

    def get_side_effect(*args, **kwargs):
        if kwargs.get("key") == "":
            return "/tmp/gt"
        if kwargs.get("key") == "magazine":
            return "/tmp/gt/magazine_a"
        return "/tmp"

    def get_jsonl_side_effect(*args, **kwargs):
        if kwargs.get("type_") == "gt":
            return "/tmp/gt/file_a.json"
        return "/tmp/link/file_a.json"

    mock_paths.get.side_effect = get_side_effect
    mock_paths.get_jsonl.side_effect = get_jsonl_side_effect
    mock_paths.save_json = MagicMock()

    global_score = MagicMock()
    magazine_score = MagicMock()
    file_score = MagicMock()
    for score in (global_score, magazine_score, file_score):
        score.get_score.return_value = {"f1": 1.0}
        score.update_counter = MagicMock()

    settings = MagicMock(EVAL_TOPK=None, INKB_SCORE=None)
    settings.model_dump.return_value = {}

    with patch("src.evaluation.Paths", return_value=mock_paths), \
         patch("src.evaluation.Scores", side_effect=[global_score, magazine_score, file_score]), \
         patch("src.evaluation.evaluate_person", return_value={"tp": 1, "fp": 0, "fn": 0}) as mock_evaluate_person, \
         patch("src.evaluation.os.listdir", side_effect=[["magazine_a"], ["file_a.json"]]), \
         patch("src.evaluation.settings", settings):
        execute_evaluation("ref", top_k=1, timed=True)

        mock_evaluate_person.assert_called_once_with(
            gt="/tmp/gt/file_a.json",
            linked="/tmp/link/file_a.json",
            ref_level=True,
            top_k=1,
            inkb_score=False,
        )
        assert mock_paths.get.call_count == 2
        assert mock_paths.save_json.call_count == 4


def test_execute_evaluation_ref_settings_copilot():
    mock_paths = MagicMock()
    mock_paths.success = True
    mock_paths.state = {}

    def get_side_effect(*args, **kwargs):
        if kwargs.get("key") == "":
            return "/tmp/gt"
        if kwargs.get("key") == "magazine":
            return "/tmp/gt/magazine_a"
        return "/tmp"

    def get_jsonl_side_effect(*args, **kwargs):
        if kwargs.get("type_") == "gt":
            return "/tmp/gt/file_a.json"
        return "/tmp/link/file_a.json"

    mock_paths.get.side_effect = get_side_effect
    mock_paths.get_jsonl.side_effect = get_jsonl_side_effect
    mock_paths.save_json = MagicMock()

    global_score = MagicMock()
    magazine_score = MagicMock()
    file_score = MagicMock()
    for score in (global_score, magazine_score, file_score):
        score.get_score.return_value = {"f1": 1.0}
        score.update_counter = MagicMock()

    settings = MagicMock(EVAL_TOPK=10, INKB_SCORE="true")
    settings.model_dump.return_value = {}

    with patch("src.evaluation.Paths", return_value=mock_paths), \
         patch("src.evaluation.Scores", side_effect=[global_score, magazine_score, file_score]), \
         patch("src.evaluation.evaluate_person", return_value={"tp": 1, "fp": 0, "fn": 0}) as mock_evaluate_person, \
         patch("src.evaluation.os.listdir", side_effect=[["magazine_a"], ["file_a.json"]]), \
         patch("src.evaluation.settings", settings):
        execute_evaluation("ref", top_k=1, timed=True)

        mock_evaluate_person.assert_called_once_with(
            gt="/tmp/gt/file_a.json",
            linked="/tmp/link/file_a.json",
            ref_level=True,
            top_k=10,
            inkb_score=True,
        )
        assert mock_paths.get.call_count == 2
        assert mock_paths.save_json.call_count == 4


def test_execute_evaluation_ref_nopathtogt_copilot():
    mock_paths = MagicMock()
    mock_paths.success = False
    mock_paths.state = {}

    with patch("src.evaluation.Paths", return_value=mock_paths), pytest.raises(NotImplementedError):
        execute_evaluation("ref", top_k=1, timed=True)
