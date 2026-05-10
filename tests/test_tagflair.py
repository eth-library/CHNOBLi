from unittest.mock import MagicMock, mock_open, patch
import orjson
from flair.models import MultitaskModel
from flair.nn import Classifier
from flair.data import Label
import flair
import pytest

from src.tag_flair import (
    decide_tag_no_tag_lower_prio,
    add_sentences,
    write_sentences_to_outfile,
    tag_year_data_and_save,
    setup_flair_tagger,
    package_generator_output_paths,
    execute_tagging
)
from utility.settings import settings


# -------------------------------------------------
# Test decide_tag_no_tag_lower_prio
# -------------------------------------------------
def test_decide_tag_no_tag_lower_prio_agreeing_labels_copilot():
    labels = [
        Label(data_point="", value="I-PER", score=0.9),
        Label(data_point="", value="B-AN", score=0.8)
    ]

    result = decide_tag_no_tag_lower_prio(labels)

    assert result == "I-PER-AN"  # Both labels agree, combined tag is returned


@pytest.mark.parametrize(
    "labels, expected",
    [([Label(data_point="", value="B-PER", score=0.2),
       Label(data_point="", value="O", score=1.0)],
      "B-PER-OT"
      ),  # "O" always loses
     ([Label(data_point="", value="B-PER", score=1.0),
       Label(data_point="", value="I-GEO", score=0.2)],
      "B-PER-OT"
      ),
     ([Label(data_point="", value="B-PER", score=0.2),
       Label(data_point="", value="I-GEO", score=0.2)],
      "I-GEO"
      ),  # snmaller or equal to, det wins
     ([Label(data_point="", value="B-GEO", score=0.2),
       Label(data_point="", value="B-AN", score=0.2)],
      "B-PER-AN"
      ),  # if det wins and is a per, will be mapped to b-per
     ],
)
def test_decide_tag_no_tag_lower_prio_disagreeing_labels(labels, expected):
    result = decide_tag_no_tag_lower_prio(labels)
    assert result == expected


def test_decide_tag_no_tag_lower_prio_single_bio_label_copilot():
    labels = [
        Label(data_point="", value="I-PER", score=0.9)
    ]

    result = decide_tag_no_tag_lower_prio(labels)

    assert result == "I-PER-OT"


def test_decide_tag_no_tag_lower_prio_single_det_label_copilot():
    labels = [
        Label(data_point="", value="B-AN", score=0.8)
    ]

    result = decide_tag_no_tag_lower_prio(labels)

    assert result == "B-PER-AN"  # Single DET label is combined with "B-PER"


def test_decide_tag_no_tag_lower_prio_empty_labels_copilot():
    labels = []

    with pytest.raises(Exception, match="Empty list of labels was passed."):
        decide_tag_no_tag_lower_prio(labels)


# -------------------------------------------------
# Test add_sentence
# -------------------------------------------------
@pytest.mark.parametrize(
    "new_data",
    [({}),
     ({"file1.txt": []})
     ],
)
def test_add_sentences(new_data):
    collected_sentences = [
        MagicMock(
            filename="file1.txt",
            __iter__=lambda self: iter([
                MagicMock(
                    labels=[Label(data_point="", value="B-PER", score=0.9)],
                    orig="John",
                    coords=(0, 4),
                    text="John"
                ),
                MagicMock(
                    labels=[],
                    orig="is",
                    coords=(5, 7),
                    text="is"
                ),
                MagicMock(
                    labels=[Label(data_point="", value="O", score=0.8)],
                    orig="a",
                    coords=(8, 9),
                    text="a"
                ),
                MagicMock(
                    labels=[Label(data_point="", value="B-LOC", score=0.85)],
                    orig="teacher",
                    coords=(10, 17),
                    text="teacher"
                )
            ])
        )
    ]

    with pytest.MonkeyPatch.context() as monkeypatch:
        monkeypatch.setattr(
            "src.tag_flair.decide_tag_no_tag_lower_prio",
            lambda labels: labels[0].value if labels else "O"
        )

        if new_data == {}:
            # we don't populate the dict with files, only with sentences
            with pytest.raises(KeyError) as excinfo:
                add_sentences({}, collected_sentences)
            assert excinfo.value.args[0] == "file1.txt"
        else:
            add_sentences(new_data, collected_sentences)
            assert "file1.txt" in new_data
            assert len(new_data["file1.txt"]) == 1  # One sentence added
            sentence = new_data["file1.txt"][0]
            assert len(sentence) == 4  # Four tokens in the sentence

            assert sentence[0] == {
                "token": "John",
                "coord": (0, 4),
                "normalized": "John",
                "tag": "B-PER"
            }
            assert sentence[1] == {
                "token": "is",
                "coord": (5, 7),
                "normalized": "is",
                "tag": "O"
            }
            assert sentence[2] == {
                "token": "a",
                "coord": (8, 9),
                "normalized": "a",
                "tag": "O"
            }
            assert sentence[3] == {
                "token": "teacher",
                "coord": (10, 17),
                "normalized": "teacher",
                "tag": "B-LOC"
            }


# -------------------------------------------------
# Test write_sentences_to_outfile
# -------------------------------------------------
def test_write_sentences_to_outfile_copilot():
    mock_data = {
        "file1.txt": [
            [
                {"token": "John",
                 "coord": (0, 4),
                 "normalized": "John",
                 "tag": "B-PER"},
                {"token": "is",
                 "coord": (5, 7),
                 "normalized": "is",
                 "tag": "O"},
                {"token": "a",
                 "coord": (8, 9),
                 "normalized": "a",
                 "tag": "O"},
                {"token": "teacher",
                 "coord": (10, 17),
                 "normalized": "teacher",
                 "tag": "B-LOC"}
            ]
        ]
    }

    mock_outfile = mock_open()

    with patch("builtins.open", mock_outfile):
        with patch("builtins.open", mock_outfile):
            write_sentences_to_outfile(mock_outfile(), mock_data)

    assert mock_outfile().write.call_count == 1
    written_data = orjson.loads(mock_outfile().write.call_args[0][0].strip())
    assert "file1.txt" in written_data
    assert len(written_data["file1.txt"]) == 1
    assert written_data["file1.txt"][0][0]["token"] == "John"
    assert written_data["file1.txt"][0][0]["tag"] == "B-PER"
    assert written_data["file1.txt"][0][1]["token"] == "is"
    assert written_data["file1.txt"][0][1]["tag"] == "O"
    assert written_data["file1.txt"][0][3]["token"] == "teacher"
    assert written_data["file1.txt"][0][3]["tag"] == "B-LOC"
    assert not mock_data  # Ensure the data dictionary is cleared


# -------------------------------------------------
# Test tag_year_data_and_save
# -------------------------------------------------
def test_tag_year_data_and_save_copilot():
    collection = {
        "file1.txt": [
            [
                {"token": "John",
                 "coord": (0, 4),
                 "normalized": "John"},
                {"token": "is",
                 "coord": (5, 7),
                 "normalized": "is"},
                {"token": "a",
                 "coord": (8, 9),
                 "normalized": "a"},
                {"token": "teacher",
                 "coord": (10, 17),
                 "normalized": "teacher"}
            ]
        ]
    }
    mock_tagger = MagicMock(spec=MultitaskModel)
    outfile_path = "/path/to/output.jsonl"
    sentence_batch_size = 1

    # Mock the file writing
    mock_outfile = mock_open()
    with patch("builtins.open", mock_outfile):
        tag_year_data_and_save(collection,
                               mock_tagger,
                               outfile_path,
                               sentence_batch_size)

    # Check that the tagger's predict method was called
    assert mock_tagger.predict.called
    assert len(
        mock_tagger.predict.call_args[0][0]) == 1  # 1 batch of sentences

    # Check that the output file was written
    mock_outfile().write.assert_called()
    written_data = mock_outfile().write.call_args[0][0]
    assert b"file1.txt" in written_data
    assert b"John" in written_data
    assert b"teacher" in written_data


# -------------------------------------------------
# Test setup_flair_tagger
# -------------------------------------------------
def test_setup_flair_tagger_with_gpu():
    settings.PATH_TO_NER_MODEL_1 = "/path/to/ner_model_1.pt"
    settings.PATH_TO_NER_MODEL_2 = "/path/to/ner_model_2.pt"

    gpu_num = 1

    # Mock the Classifier.load method
    mock_classifier_1 = MagicMock(Classifier)
    mock_classifier_2 = MagicMock(Classifier)
    with patch("flair.nn.Classifier.load",
               side_effect=[mock_classifier_1, mock_classifier_2]):
        with patch("src.tag_flair.cuda_is_available", return_value=True):
            tagger = setup_flair_tagger(gpu_num)

        assert isinstance(tagger, flair.models.MultitaskModel)
        assert len(tagger.tasks) == 2
        assert tagger.tasks["Task_0"] == mock_classifier_1
        assert tagger.tasks["Task_1"] == mock_classifier_2
        assert flair.device.type == "cuda"  # Ensure GPU is being used


def test_setup_flair_tagger_with_cpu():
    settings.PATH_TO_NER_MODEL_1 = "/path/to/ner_model_1.pt"
    settings.PATH_TO_NER_MODEL_2 = "/path/to/ner_model_2.pt"

    # Mock the Classifier.load method
    mock_classifier_1 = MagicMock(Classifier)
    mock_classifier_2 = MagicMock(Classifier)

    with patch("flair.nn.Classifier.load",
               side_effect=[mock_classifier_1, mock_classifier_2]):
        with patch("src.tag_flair.cuda_is_available", return_value=False):
            tagger = setup_flair_tagger(0)

        assert isinstance(tagger, flair.models.MultitaskModel)
        assert len(tagger.tasks) == 2
        assert tagger.tasks["Task_0"] == mock_classifier_1
        assert tagger.tasks["Task_1"] == mock_classifier_2
        assert flair.device.type == "cpu"  # Ensure CPU is being used


# -------------------------------------------------
# Test package_generator_output_paths
# -------------------------------------------------
def test_package_generator_output_paths_copilot():
    generator = iter([
        (2020, ['file1', 'file2']),
        (2021, ['file3', 'file4']),
        (2022, ['file5']),
        (2023, ['file6', 'file7', 'file8'])
    ])
    batch_size = 2

    result = list(package_generator_output_paths(generator, batch_size))

    assert len(result) == 2  # Two batches expected
    assert result[0] == {
        2020: ['file1', 'file2'],
        2021: ['file3', 'file4']
    }  # First batch
    assert result[1] == {
        2022: ['file5'],
        2023: ['file6', 'file7', 'file8']
    }  # Second batch


def test_package_generator_output_paths_with_exact_batch_size_copilot():
    generator = iter([
        (2020, ['file1']),
        (2021, ['file2']),
        (2022, ['file3'])
    ])
    batch_size = 3

    result = list(package_generator_output_paths(generator, batch_size))

    assert len(result) == 1  # One batch expected
    assert result[0] == {
        2020: ['file1'],
        2021: ['file2'],
        2022: ['file3']
    }


def test_package_generator_output_paths_with_leftover():
    generator = iter([
        (2020, ['file1']),
        (2021, ['file2']),
        (2022, ['file3']),
        (2023, ['file4'])
    ])
    batch_size = 3

    result = list(package_generator_output_paths(generator, batch_size))

    assert len(result) == 2  # Two batches expected
    assert result[0] == {
        2020: ['file1'],
        2021: ['file2'],
        2022: ['file3']
    }  # First batch
    assert result[1] == {
        2023: ['file4']
    }  # Second batch


# -------------------------------------------------
# Test execute_tagging
# -------------------------------------------------
def test_execute_tagging_copilot():
    preprocessed_data = iter([
        ("2020", {
            "file1.txt": [[{
                "token": "John", "coord": (0, 4), "normalized": "John"
            }]]
        }),
        ("2021", {
            "file1.txt": [[{
                "token": "Doe", "coord": (5, 8), "normalized": "Doe"
            }]]
        })
    ])
    settings.PATH_TO_OUTFILE_FOLDER = "/path/to/output"
    settings.BATCH_SIZE = 1
    settings.SENTENCE_BATCH_SIZE = 2
    settings.PATH_TO_NER_MODEL_1 = "/path/to/ner_model_1.pt"
    settings.PATH_TO_NER_MODEL_2 = "/path/to/ner_model_2.pt"
    tasks = ["prep", "tag"]
    gpu_num = 0

    # Mock the setup_flair_tagger function
    mock_tagger = MagicMock()
    with patch("src.tag_flair.setup_flair_tagger", return_value=mock_tagger):
        # Mock os.makedirs to avoid creating directories
        with patch("os.makedirs") as mock_makedirs:
            # Mock open to avoid writing to files
            with patch("builtins.open", MagicMock()) as mock_open:
                execute_tagging(preprocessed_data, tasks, gpu_num)

                # Ensure tagging was performed
                mock_tagger.predict.assert_called()
                # Ensure output files were opened
                mock_open.assert_called()
                # Ensure directories were created
                mock_makedirs.assert_called()
