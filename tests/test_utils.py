import orjson
import os
import argparse
from unittest.mock import patch
import pytest

from utility.utils import (
    set_default,
    str2bool,
    positive_int,
    parse_arguments,
    check_gpu,
    save_data_intermediate,
    save_data
)
from utility.settings import settings


# -------------------------------------------------
# Tests for set_default
# -------------------------------------------------
def test_set_default_with_set_copilot():
    test_set = {1, 2, 3}

    result = set_default(test_set)

    assert isinstance(result, list)
    assert sorted(result) == [1, 2, 3]


def test_set_default_with_non_set_copilot():
    test_value = "not_a_set"

    with pytest.raises(TypeError):
        set_default(test_value)


# -------------------------------------------------
# Tests for str2bool
# -------------------------------------------------
def test_str2bool_copilot():
    # Test cases for True values
    assert str2bool("true") is True
    assert str2bool("1") is True
    assert str2bool("True") is True
    assert str2bool("TRUE") is True

    # Test cases for False values
    assert str2bool("false") is False
    assert str2bool("0") is False
    assert str2bool("False") is False
    assert str2bool("FALSE") is False

    # Test cases for invalid values
    with pytest.raises(argparse.ArgumentTypeError):
        str2bool("maybe")
    with pytest.raises(argparse.ArgumentTypeError):
        str2bool("yes")
    with pytest.raises(argparse.ArgumentTypeError):
        str2bool("no")


# -------------------------------------------------
# Tests for positive_int
# -------------------------------------------------
def test_positive_int_copilot():
    with pytest.raises(argparse.ArgumentTypeError):
        positive_int("0")
    with pytest.raises(ValueError):
        positive_int("hello")
    assert positive_int("5") == 5


# -------------------------------------------------
# Tests for check_gpu
# -------------------------------------------------
def test_check_gpu_with_gpu_available_copilot():
    args = type("Args", (object,), {"gpu": 1})  # Mock args with gpu=1

    with patch("subprocess.check_output", return_value="GPU Available"):
        assert check_gpu(args) == 1  # GPU is available, should return 1


def test_check_gpu_with_no_gpu_available_copilot():
    args = type("Args", (object,), {"gpu": 1})  # Mock args with gpu=1

    with patch("subprocess.check_output", side_effect=Exception("No GPU")):
        assert check_gpu(args) == 0  # No GPU detected, should return 0


def test_check_gpu_with_gpu_set_to_zero_copilot():
    args = type("Args", (object,), {"gpu": 0})  # Mock args with gpu=0

    result = check_gpu(args)

    assert result == 0  # GPU is set to 0, should return 0


# -------------------------------------------------
# Tests for parse_arguments
# -------------------------------------------------
def test_parse_arguments_defaults_copilot(monkeypatch):
    monkeypatch.setattr("sys.argv", ["script_name.py"])

    args = parse_arguments()

    assert args.tasks == "finish"
    assert args.gpu == 0
    assert args.magazine_year_paths is None
    assert args.config_file == "./configs/configurations.json"
    assert args.eval_level == "ref"


def test_parse_arguments_with_input_copilot(monkeypatch):
    monkeypatch.setattr(
        "sys.argv",
        [
            "script_name.py",
            "--tasks", "prep,tag",
            "--gpu", "1",
            "--magazine_year_paths", "/path/to/data",
            "--config_file", "/path/to/config.json",
            "--eval_level", "ent"
        ]
    )

    args = parse_arguments()

    assert args.tasks == "prep,tag"
    assert args.gpu == 1
    assert args.magazine_year_paths == "/path/to/data"
    assert args.config_file == "/path/to/config.json"
    assert args.eval_level == "ent"


# -------------------------------------------------
# Tests for save_data_intermediate
# -------------------------------------------------
def test_save_data_intermediate_copilot(tmp_path):
    year = ["2025", "01"]
    files = [{"key": "value"}]
    settings.PATH_TO_OUTFILE_FOLDER = str(tmp_path)
    task = "test_task"

    save_data_intermediate(year, files, task)

    yearfolder = os.path.join(tmp_path, task, year[0])
    assert os.path.exists(yearfolder)  # Check if the directory was created
    output_file = os.path.join(yearfolder, "".join(year[1:])+".jsonl")
    assert os.path.exists(output_file)  # Check if the file was created

    with open(output_file, "r", encoding="utf8") as f:
        data = []
        for i in f:
            data.append(orjson.loads(i))
        assert data == files  # Check if the content matches


# -------------------------------------------------
# Tests for save_data
# -------------------------------------------------
def test_save_data_copilot(tmp_path):
    data = [
        {
            ("2025", "01"): [{"key1": "value1"}],
            ("2025", "02"): [{"key2": "value2"}]
        }
    ]
    settings.PATH_TO_OUTFILE_FOLDER = str(tmp_path)
    taskname = "test_task"

    save_data(data, taskname)

    prepfolder = os.path.join(tmp_path, taskname)
    assert os.path.exists(prepfolder)  # Check if the task folder was created

    for batch in data:
        for year, content in batch.items():
            yearfolder = os.path.join(prepfolder, year[0])
            assert os.path.exists(yearfolder)  # Check if year dir was created
            output_file = os.path.join(yearfolder, year[1] + ".jsonl")
            assert os.path.exists(output_file)  # Check if the file was created

            with open(output_file, "r", encoding="utf8") as f:
                saved_data = []
                for i in f:
                    saved_data.append(orjson.loads(i))
                assert saved_data == content  # Check if the content matches
