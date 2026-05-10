import orjson
import os
import tempfile
from .test_data import params
from unittest.mock import patch, mock_open
import pytest

# Import the functions from your script:
# If your script is named "preprocessing.py", do:
from src.preprocessing.preprocess import (
    PreprocessConfig,
    fuse_hyphens,
    check_for_abbrev,
    check_roman_numeral,
    tokenize,
    split_sentences,
    preprocess_file,
    get_year_chunk_paths,
    prep_year_data_for_tagging,
    start_preprocessing,
    execute_preprocessing,  # timed_execute_preprocessing
)
from utility.settings import settings


@pytest.fixture(scope="session")
def preprocess_data():
    data = PreprocessConfig(
        ABBREVIATION_FILE=settings.PATH_TO_ABBREVIATION_FILE
        )
    data.load_abbrevs()
    return data


# -------------------------------------------------
# 1. Test load_abbrevs
# -------------------------------------------------
def test_load_abbrevs(preprocess_data):
    """
    Test that load_abbrevs correctly loads abbreviations into a dictionary.
    """
    # Prepare a temporary abbrevs file
    fake_data = """vgl.
Dr.
z.B.
u.a.
a. d. D.
a. d. E.
A. d. Hrsg.
"""
    with tempfile.NamedTemporaryFile(
        mode="w", delete=False, suffix=".txt"
         ) as tmp:
        tmp.write(fake_data)
        temp_path = tmp.name

    try:
        # Load from the temporary file
        abbrev_set = preprocess_data.ABBREVIATION_LIST

        # Example checks
        assert (
            "vgl." in abbrev_set
        ), "The abbreviation 'vgl' should be in the loaded set."
        assert (
            "dr." in abbrev_set
        ), "The abbreviation 'dr' should be in the loaded set."
        assert (
            "z." in abbrev_set
        ), "Should handle abbreviations split by punctuation (z.B.)."
        assert "b." in abbrev_set, "Part of 'z.B.' as well."
        # We expect that "vgl" or "u" or "a" are keys.
        # The structure is defaultdict(list), so each key should map to a list.
        assert isinstance(
            abbrev_set["vgl."], list
        ), "Each key should map to a list of dicts."

    finally:
        # Clean up temp file
        os.remove(temp_path)


# -------------------------------------------------
# 2. Test fuse_hyphens
# -------------------------------------------------
@pytest.mark.parametrize(
    "test_content, expected",
    params.PARAMS_fuse_hyphens,
)
def test_fuse_hyphens(test_content, expected, preprocess_data):
    result = fuse_hyphens(test_content, preprocess_data)
    assert result == expected, f"Expected {expected}, got {result}"


# -------------------------------------------------
# 3. Test check_roman_numeral
# -------------------------------------------------
@pytest.mark.parametrize(
    "word,expected",
    [
        ("xvii.", True),
        ("x.", True),
        ("xiv", False),  # No trailing period
        ("XV.", True),  # Even uppercase (method lower-cases inside)
        ("abc.", False),
    ],
)
def test_check_roman_numeral(word, expected):
    """
    Verify that Roman numerals with a trailing period are identified.
    """
    assert check_roman_numeral(word) == expected


# -------------------------------------------------
# 4. Test check_for_abbrev
# -------------------------------------------------
@pytest.mark.parametrize(
    "pos, text, expected",
    params.PARAMS_check_for_abbrev,
)
def test_check_for_abbrev(pos, text, expected, preprocess_data):
    """
    Verify that abbreviations are correctly identified based on their context.
    """
    assert check_for_abbrev(pos, text, preprocess_data) == expected


# -------------------------------------------------
# 5. Test tokenize
# -------------------------------------------------
@pytest.mark.parametrize(
    "content, expected",
    params.PARAMS_tokenize,
)
def test_tokenize(content, expected, preprocess_data):
    result = tokenize(content, preprocess_data)
    assert result == expected, f"Expected {expected}, got {result}"


# -------------------------------------------------
# 6. Test split_sentences
# -------------------------------------------------
@pytest.mark.parametrize(
    "content, expected",
    params.PARAMS_split_sentences,
)
def test_split_sentences(content, expected, preprocess_data):
    result = split_sentences(content, preprocess_data)
    assert result == expected, f"Expected {expected}, got {result}"


# -------------------------------------------------
# 7. Test preprocess_file
# -------------------------------------------------
def test_preprocess_file_copilot():
    mock_content = "This 12345\nis 67891\na 12345\ntest 67891\n\
sentence. 67891\nAnother 12345\nline 67891\nwith¬ 67891\nhyphen. 67891\n"
    settings.PATH_TO_ABBREVIATION_FILE = "/path/to/abbreviation/file"
    mock_abbreviation_file_content = "Dr.\nProf."

    # Mock the abbreviation file and input file
    with patch("builtins.open",
               mock_open(read_data=mock_abbreviation_file_content))\
            as mock_file:
        preprocess_data = PreprocessConfig(
            ABBREVIATION_FILE=settings.PATH_TO_ABBREVIATION_FILE
            )
        preprocess_data.load_abbrevs()
        mock_file.assert_called_once_with(
            settings.PATH_TO_ABBREVIATION_FILE,
            encoding="utf8"
            )

    with patch("builtins.open",
               mock_open(read_data=mock_content)) as mock_file:
        sentences = preprocess_file("/path/to/input/file")

        mock_file.assert_called_with("/path/to/input/file", encoding="utf8")
        assert isinstance(sentences, list)
        assert len(sentences) > 0
        assert all(isinstance(sentence, list) for sentence in sentences)
        assert all(
            isinstance(token, dict)
            for sentence in sentences for token in sentence
            )
        assert sentences[0][0]["token"] == "This"  # Check the first token
        assert sentences[0][-1]["token"] == "."  # Check the last token
        assert sentences[-1][-2]["token"] == "withhyphen"  # Check fuse hyphens


# -------------------------------------------------
# 8. Test get_year_chunk_paths
# -------------------------------------------------
def test_get_year_chunk_paths_with_small_number_of_files_copilot():
    year = "/path/to/year"
    mock_files = [f"{year}/file{i}.txt" for i in range(5)]  # 5 files

    with patch("glob.glob", return_value=mock_files):
        result = get_year_chunk_paths(year)

        assert len(result) == 1  # Only 1 chunk since files are below the limit
        assert result[0][0] == ("to", "year")  # Chunk name
        assert result[0][1] == mock_files  # List of files


def test_get_year_chunk_paths_with_large_number_of_files_copilot():
    year = "/path/to/year"
    mock_files = [f"{year}/file{i}.txt" for i in range(1500)]  # 1500 files
    mock_chunks = [
        (i, mock_files[i * 500:(i + 1) * 500]) for i in range(3)
    ]  # Simulate splitting into 3 chunks

    with patch("glob.glob", return_value=mock_files), \
         patch("utility.split_year.split_directory", return_value=mock_chunks):
        result = get_year_chunk_paths(year)

        assert len(result) == 3  # Three chunks
        for i, (chunk_name, files) in enumerate(result):
            assert chunk_name == ("to", "year", "-", str(i).zfill(2))
            assert files == mock_chunks[i][1]  # Files in the chunk


# -------------------------------------------------
# 9. Test prep_year_data_for_tagging
# -------------------------------------------------
@pytest.mark.parametrize(
    "content, expected",
    params.PARAMS_prep_year_data_for_tagging
)
def test_prep_year_data_for_tagging(content, expected):
    # Mock the output of preprocess file
    mock_preprocess_file_output = [
        [
            {'coord': '12345:main', 'token': 'This'},
            {'coord': '67891:main', 'token': 'is'},
            {'coord': '12345:main', 'token': 'a'},
            {'coord': '67891:main', 'token': 'test'},
            {'coord': '67891:main', 'token': 'sentence'},
            {'coord': '67891:rpunc', 'token': '.'}
        ],
        [
            {'coord': '12345:main', 'token': 'Another'},
            {'coord': '67891:main', 'token': 'line'},
            {'coord': '67891;67891:main', 'token': 'withhyphen'},
            {'coord': '67891;67891:rpunc', 'token': '.'}
        ]
        ]
    with patch("src.preprocessing.preprocess.preprocess_file",
               return_value=mock_preprocess_file_output):
        assert expected == prep_year_data_for_tagging(content)


# -------------------------------------------------
# 10. Test start_preprocessing
# NOTE unfortunately can't mock the output for prep_year_data_for_tagging
# because unittest mock doesn't work with multiprocessing...
# https://github.com/python/cpython/issues/100090
# -------------------------------------------------
@pytest.mark.parametrize(
    "year_dirs, expected",
    [
        (
            ["1", "2", "3", "4", "5", "6"],
            [(('1',), {}), (('2',), {}), (('3',), {}),
             (('4',), {}), (('5',), {}), (('6',), {})]
        )
    ]
)
def test_start_preprocessing(year_dirs, expected):
    settings.BATCH_SIZE = 3
    settings.PATH_TO_ABBREVIATION_FILE = "/path/to/abbreviation/file"
    assert expected == [x for x in start_preprocessing(year_dirs)]


# -------------------------------------------------
# 11. Test execute_preprocessing
# -------------------------------------------------
def test_execute_preprocessing():
    settings.BATCH_SIZE = 3
    settings.PATH_TO_ABBREVIATION_FILE = "/path/to/abbreviation/file"
    settings.CUSTOM_PATHS = ["abc/1234"]
    assert [(('abc', '1234'), {})] == [x for x in execute_preprocessing()]

    settings.CUSTOM_PATHS = None
    settings.PATH_TO_INPUT_FOLDERS = "abc"
    assert [] == [x for x in execute_preprocessing()]

