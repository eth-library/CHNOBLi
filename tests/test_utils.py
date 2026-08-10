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
    save_data,
    transkribus_xml_to_approx_word_coord,
    erara_xml_to_word_coord,
    txt_file_to_word_coord,
    offset_len_to_linking_input
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


def test_transkribus_xml_to_approx_word_coord(tmp_path):
    xml_path = tmp_path / "page.xml"
    xml_path.write_text(
        """<?xml version="1.0" encoding="UTF-8"?>
        <PcGts xmlns="http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15">
          <Page imageWidth="100" imageHeight="200">
            <TextRegion>
              <TextLine>
                <Coords points="0,20 10,20 10,0 0,0" />
                <TextEquiv>
                  <Unicode>hello world</Unicode>
                </TextEquiv>
              </TextLine>
            </TextRegion>
          </Page>
        </PcGts>""",
        encoding="utf-8",
    )

    result = transkribus_xml_to_approx_word_coord(str(xml_path))

    assert result == "100, 200\nhello 0,0,5,20\nworld 5,0,10,20\n<EOS>\n"


def test_erara_xml_to_word_coord(tmp_path):
    xml_path = tmp_path / "page.xml"
    xml_path.write_text(
        """<?xml version="1.0" encoding="UTF-8"?>
        <alto xmlns="http://www.loc.gov/standards/alto/ns-v3#">
          <Layout>
            <Page WIDTH="100" HEIGHT="200">
              <PrintSpace>
                <TextBlock>
                  <TextLine>
                    <String CONTENT="Hello" HPOS="10" VPOS="20" WIDTH="30" HEIGHT="40" />
                    <String CONTENT="world" HPOS="50" VPOS="20" WIDTH="20" HEIGHT="40" />
                  </TextLine>
                </TextBlock>
              </PrintSpace>
            </Page>
          </Layout>
        </alto>""",
        encoding="utf-8",
    )

    result = erara_xml_to_word_coord(str(xml_path))

    assert result == "100, 200\nHello 10,20,30,40\nworld 50,20,20,40\n<EOS>\n"


def test_txt_file_to_word_coord(tmp_path):
    txt_path = tmp_path / "ocr.txt"
    txt_path.write_text("hello world", encoding="utf-8")

    result = txt_file_to_word_coord(str(txt_path))

    assert result == "hello 0,5,0,0\nworld 6,11,0,1\n<EOP>\n"


def test_offset_len_to_linking_input(tmp_path, monkeypatch):
    doc_path = tmp_path / "sample.txt"
    doc_path.write_text("Alice Smith is here", encoding="utf-8")

    monkeypatch.setattr(settings, "VD_CONTEXT_WINDOW_LEN", 1)

    result = offset_len_to_linking_input(
        [
            {
                "mention": "Alice Smith",
                "docName": str(doc_path),
                "offset": 0,
                "length": 11,
            }
        ]
    )

    assert len(result) == 1
    assert result[0]["info"]["lastnames"] == ["Smith"]
    assert result[0]["info"]["firstnames"] == ["Alice"]
    assert result[0]["info"]["type"] == "PER"
    assert result[0]["positions"] == "0:11"
    assert result[0]["context"] == "Alice Smith is"
