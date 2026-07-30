from unittest.mock import MagicMock, patch, mock_open
import main
from multiprocessing import cpu_count
from types import SimpleNamespace
import pytest
import logging
import os


def test_finish_data_executes_pipeline_for_finish_task_copilot():
    mock_settings = MagicMock()
    mock_settings.CUSTOM_PATHS = None
    mock_settings.PATH_TO_OUTFILE_FOLDER = "/tmp/out/"
    mock_settings.PATH_TO_INPUT_FOLDERS = None
    mock_settings.BATCH_SIZE = 2
    mock_settings.CUSTOM_TAG_PATH = None

    magazines = [("2020", ["file1.txt"])]
    postprocessed_data = [("2020", [{"id": 1}], [])]
    aggregated_data = [("2020", [{"id": 1}], [])]

    with patch("main.settings", mock_settings), \
         patch("main.get_data_paths_iterative", return_value=magazines) as mock_get_paths, \
         patch("main.execute_postprocessing", return_value=postprocessed_data) as mock_postprocess, \
         patch("main.execute_aggregation", return_value=aggregated_data) as mock_aggregate, \
         patch("main.execute_linking") as mock_link:
        main.finish_data(["finish"])

    assert mock_settings.PATH_TO_INPUT_FOLDERS == "/tmp/out/tag/"
    mock_get_paths.assert_called_once_with()
    mock_postprocess.assert_called_once_with(magazines, ["finish"])
    mock_aggregate.assert_called_once_with(postprocessed_data, ["finish"])
    mock_link.assert_called_once_with(aggregated_data, ["finish"])


def test_finish_data_executes_pipeline_for_finish_task_nobatchsize_copilot():
    mock_settings = MagicMock()
    mock_settings.CUSTOM_PATHS = None
    mock_settings.PATH_TO_OUTFILE_FOLDER = "/tmp/out/"
    mock_settings.PATH_TO_INPUT_FOLDERS = None
    mock_settings.BATCH_SIZE = None
    mock_settings.CUSTOM_TAG_PATH = None

    magazines = [("2020", ["file1.txt"])]
    postprocessed_data = [("2020", [{"id": 1}], [])]
    aggregated_data = [("2020", [{"id": 1}], [])]

    with patch("main.settings", mock_settings), \
         patch("main.get_data_paths_iterative", return_value=magazines) as mock_get_paths, \
         patch("main.execute_postprocessing", return_value=postprocessed_data) as mock_postprocess, \
         patch("main.execute_aggregation", return_value=aggregated_data) as mock_aggregate, \
         patch("main.execute_linking") as mock_link:
        main.finish_data(["finish"])

    assert mock_settings.PATH_TO_INPUT_FOLDERS == "/tmp/out/tag/"
    mock_get_paths.assert_called_once_with()
    mock_postprocess.assert_called_once_with(magazines, ["finish"])
    mock_aggregate.assert_called_once_with(postprocessed_data, ["finish"])
    mock_link.assert_called_once_with(aggregated_data, ["finish"])
    assert mock_settings.BATCH_SIZE == cpu_count()-1


@patch("builtins.open", new_callable=mock_open, read_data='{"id": 1}')
def test_finish_data_executes_pipeline_for_finish_task_customtagpath_copilot(mock_open_customtagpath):
    mock_settings = MagicMock()
    mock_settings.CUSTOM_PATHS = None
    mock_settings.PATH_TO_OUTFILE_FOLDER = "/tmp/out/"
    mock_settings.PATH_TO_INPUT_FOLDERS = None
    mock_settings.BATCH_SIZE = 2
    mock_settings.CUSTOM_TAG_PATH = "/tmp/in/tag/"

    magazines = [("2020", ["file1.txt"])]
    postprocessed_data = [("3000", {"id": 1}, [])]
    aggregated_data = [("2020", [{"id": 1}], [])]

    with patch("main.settings", mock_settings), \
         patch("main.get_data_paths_iterative", return_value=magazines) as mock_get_paths, \
         patch("main.execute_aggregation", return_value=aggregated_data) as mock_aggregate, \
         patch("main.execute_linking") as mock_link:
        main.finish_data(["finish"])

    assert mock_settings.PATH_TO_INPUT_FOLDERS == "/tmp/out/tag/"
    assert not mock_get_paths.called
    mock_aggregate.assert_called_once_with(postprocessed_data, ["finish"])
    mock_link.assert_called_once_with(aggregated_data, ["finish"])
    mock_open_customtagpath.assert_called_once_with("/tmp/in/tag/")


def test_main_calls_finish_data_for_finish_task_copilot():
    args = SimpleNamespace(
        tasks="finish",
        magazine_year_paths=None,
        config_file=None,
        eval_level="ref",
    )
    mock_settings = MagicMock()
    mock_settings.BATCH_SIZE = None
    mock_settings.CUSTOM_PATHS = None

    with patch("main.parse_arguments", return_value=args), \
         patch("main.check_gpu", return_value=0), \
         patch("main.settings", mock_settings), \
         patch("main.finish_data") as mock_finish_data:
        main.main()

    mock_finish_data.assert_called_once_with(["finish"])


def test_main_calls_with_configfile_invalidpaths_copilot(caplog):
    args = SimpleNamespace(
        tasks="finish",
        magazine_year_paths="first.jsonl,second.jsonl",
        config_file="/tmp/configurations.json",
        eval_level="ref",
    )
    mock_settings = MagicMock()
    mock_settings.BATCH_SIZE = None
    mock_settings.CUSTOM_PATHS = None

    with patch("main.parse_arguments", return_value=args), \
         patch("main.check_gpu", return_value=0), \
         patch("main.settings", mock_settings), \
         pytest.raises(SystemExit):
        main.main()
        log_record = caplog.records[0]
        assert log_record.levelno == logging.ERROR
        assert log_record.message == "The following input paths do not exist: first.jsonl,second.jsonl. Exiting program."
        assert log_record.lineno == 101


@patch("os.path.exists")
def test_main_calls_finish_data_for_finish_task_with_custompath_eval_copilot(mock_ospathexists, caplog):
    args = SimpleNamespace(
        tasks="eval",
        magazine_year_paths="placeholder",
        config_file=None,
        eval_level="ref",
    )
    mock_settings = MagicMock()
    mock_settings.BATCH_SIZE = None
    mock_settings.CUSTOM_PATHS = None

    mock_ospathexists.return_value = True

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

    with patch("main.parse_arguments", return_value=args), \
         patch("main.check_gpu", return_value=0), \
         patch("src.evaluation.Paths", return_value=mock_paths), \
         patch("src.evaluation.os.listdir", side_effect=[["magazine_a"], ["file_a.json"]]), \
         patch("main.settings", mock_settings):
        main.main()
        log_record = caplog.records[0]
        assert log_record.levelno == logging.WARNING
        assert log_record.message == "Careful! You have selected the task 'eval' as well as giving a custom path. Evaluation is always done on all the magazines we have ground-truth data for."


def test_main_executes_prep_and_tag_pipeline_copilot():
    args = SimpleNamespace(
        tasks="prep,tag",
        magazine_year_paths=None,
        config_file=None,
        eval_level="ref",
    )
    mock_settings = MagicMock()
    mock_settings.BATCH_SIZE = None
    mock_settings.CUSTOM_PATHS = None

    preprocessed_data = [("2020", ["file1.txt"])]

    with patch("main.parse_arguments", return_value=args), \
         patch("main.check_gpu", return_value=0), \
         patch("main.settings", mock_settings), \
         patch("main.execute_preprocessing", return_value=preprocessed_data) as mock_preprocess, \
         patch("src.tag_flair.execute_tagging") as mock_tag:
        main.main()

    mock_preprocess.assert_called_once_with()
    mock_tag.assert_called_once_with(preprocessed_data, ["prep", "tag"], 0)
