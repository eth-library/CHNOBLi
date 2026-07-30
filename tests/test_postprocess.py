import re
from unittest.mock import patch, MagicMock, mock_open
from lxml import etree
import pytest

from src.postprocess import (
    initialize_found_entry,
    initialize_found_place_entry,
    add_info_to_entity,
    add_info_to_place_entity,
    decide_articles,
    adjust_information,
    get_structure_info,
    process_page,
    get_found_names,
    populate_year_dict,
    get_data_paths_iterative,
    execute_postprocessing
)
from utility.settings import settings

# -------------------------------------------------
# Test initialize_found_entry
# -------------------------------------------------
def test_initialize_found_entry():
    empty_entry = {
        "info": {
            "lastnames": [],
            "firstnames": [],
            "abbr_firstnames": [],
            "occupations": [],
            "titles": [],
            "address": [],
            "others": []
            },
        "pid": [],
        "pageNames": [],
        "pageNo": [],
        "sentenceNo": [],
        "positions": []
        }
    assert empty_entry == initialize_found_entry()


# -------------------------------------------------
# Test initialize_found_place_entry
# -------------------------------------------------
def test_initialize_found_place_entry():
    empty_place_entry = {
        "tokens": [],
        "type": "",
        "pid": [],
        "pageNames": [],
        "pageNo": [],
        "sentenceNo": [],
        "positions": []
        }
    assert empty_place_entry == initialize_found_place_entry()


# -------------------------------------------------
# Test add_info_to_entity
# -------------------------------------------------
def test_add_info_to_entity_with_articles():
    entity = initialize_found_entry()
    entity["articles"] = ["article1", "article2"]
    tag = "LN"
    token = {"token": "Doe", "coord": (0, 3)}
    pageNo = 1
    sentNo = 2
    pageName = "page1.txt"
    pid = "12345"

    # this will be ignored because structure info is only added once
    articles = ["article3"]

    add_info_to_entity(entity,
                       tag,
                       token,
                       pageNo,
                       sentNo,
                       pageName,
                       articles,
                       pid)

    assert entity["info"]["lastnames"] == ["Doe"]
    assert entity["pageNames"] == ["page1.txt"]
    assert entity["pid"] == ["12345"]
    assert entity["positions"] == [(0, 3)]
    assert entity["pageNo"] == [1]
    assert entity["sentenceNo"] == [2]
    assert entity["type"] == "PER"
    assert entity["articles"] == ["article1", "article2"]


def test_add_info_to_entity_without_articles_copilot():
    entity = initialize_found_entry()
    tag = "LN"
    token = {"token": "Doe", "coord": (0, 3)}
    pageNo = 1
    sentNo = 2
    pageName = "page1.txt"
    pid = "12345"

    add_info_to_entity(entity,
                       tag,
                       token,
                       pageNo,
                       sentNo,
                       pageName,
                       [],
                       pid)

    assert entity["info"]["lastnames"] == ["Doe"]
    assert entity["pageNames"] == ["page1.txt"]
    assert entity["pid"] == ["12345"]
    assert entity["positions"] == [(0, 3)]
    assert entity["pageNo"] == [1]
    assert entity["sentenceNo"] == [2]
    assert entity["type"] == "PER"
    assert entity["articles"] == []


def test_add_info_to_entity_unknown_tag_copilot():
    entity = initialize_found_entry()
    tag = "UNKNOWN"
    token = {"token": "UnknownToken", "coord": (4, 10)}
    pageNo = 1
    sentNo = 2
    pageName = "page2.txt"
    articles = ["article3"]
    pid = "67890"

    add_info_to_entity(entity,
                       tag,
                       token,
                       pageNo,
                       sentNo,
                       pageName,
                       articles,
                       pid)

    assert entity["info"]["others"] == ["UnknownToken"]
    assert entity["pageNames"] == ["page2.txt"]
    assert entity["pid"] == ["67890"]
    assert entity["positions"] == [(4, 10)]
    assert entity["pageNo"] == [1]
    assert entity["sentenceNo"] == [2]
    assert entity["type"] == "PER"
    assert entity["articles"] == ["article3"]


# -------------------------------------------------
# Test add_info_to_place_entity
# -------------------------------------------------
def test_add_info_to_place_entity_with_articles():
    entity = initialize_found_place_entry()
    entity["articles"] = ["article1", "article2"]
    tag = "LOC"
    token = {"token": "Berlin", "coord": (0, 6)}
    pageNo = 1
    sentNo = 2
    pageName = "page1.txt"
    pid = "12345"

    # this will be ignored because structure info is only added once
    articles = ["article3"]

    add_info_to_place_entity(entity,
                             tag,
                             token,
                             pageNo,
                             sentNo,
                             pageName,
                             articles,
                             pid)

    assert entity["tokens"] == ["Berlin"]
    assert entity["type"] == "LOC"
    assert entity["pid"] == ["12345"]
    assert entity["pageNames"] == ["page1.txt"]
    assert entity["positions"] == [(0, 6)]
    assert entity["pageNo"] == [1]
    assert entity["sentenceNo"] == [2]
    assert entity["articles"] == ["article1", "article2"]


def test_add_info_to_place_entity_without_articles_copilot():
    entity = initialize_found_place_entry()
    tag = "LOC"
    token = {"token": "Berlin", "coord": (0, 6)}
    pageNo = 1
    sentNo = 2
    pageName = "page1.txt"
    pid = "12345"

    add_info_to_place_entity(entity,
                             tag,
                             token,
                             pageNo,
                             sentNo,
                             pageName,
                             [],
                             pid)

    assert entity["tokens"] == ["Berlin"]
    assert entity["type"] == "LOC"
    assert entity["pid"] == ["12345"]
    assert entity["pageNames"] == ["page1.txt"]
    assert entity["positions"] == [(0, 6)]
    assert entity["pageNo"] == [1]
    assert entity["sentenceNo"] == [2]
    assert entity["articles"] == []


# -------------------------------------------------
# Test decide_articles
# -------------------------------------------------
def test_decide_articles_single_article_copilot():
    articles = ["article1"]

    result = decide_articles(articles)

    assert result == ["article1"]  # Single article should be returned as is


def test_decide_articles_multiple_articles_with_two_elements():
    articles = [["article1", "article2"], "page1"]

    result = decide_articles(articles)

    assert result == [["article1", "article2"]]


def test_decide_articles_empty_list_copilot():
    articles = []

    result = decide_articles(articles)

    assert result == []


# -------------------------------------------------
# Test adjust_information
# -------------------------------------------------
def test_adjust_information_single_value_copilot():
    entitylist = [
        {
            "pageNames": ["page1.txt"],
            "pageNo": [1],
            "sentenceNo": [2],
            "pid": ["12345"]
        }
    ]

    adjust_information(entitylist)

    assert entitylist[0]["pageNames"] == "page1.txt"
    assert entitylist[0]["pageNo"] == 1
    assert entitylist[0]["sentenceNo"] == 2
    assert entitylist[0]["pid"] == "12345"


def test_adjust_information_multiple_values_copilot():
    entitylist = [
        {
            "pageNames": ["page1.txt", "page1.txt"],
            "pageNo": [1, 1],
            "sentenceNo": [2, 2],
            "pid": ["12345", "12345"]
        }
    ]

    adjust_information(entitylist)

    assert entitylist[0]["pageNames"] == "page1.txt"
    assert entitylist[0]["pageNo"] == 1
    assert entitylist[0]["sentenceNo"] == 2
    assert entitylist[0]["pid"] == "12345"


def test_adjust_information_empty_pid_copilot():
    entitylist = [
        {
            "pageNames": ["page1.txt"],
            "pageNo": [1],
            "sentenceNo": [2],
            "pid": []
        }
    ]

    adjust_information(entitylist)

    assert entitylist[0]["pageNames"] == "page1.txt"
    assert entitylist[0]["pageNo"] == 1
    assert entitylist[0]["sentenceNo"] == 2
    assert "pid" not in entitylist[0]  # Ensure "pid" is removed


# -------------------------------------------------
# Test get_structure_info
# -------------------------------------------------
def test_get_structure_info_with_custom_path():
    mock_xml_content = """
    <root>
        <element-list>
            <element type="Agora:Document">
                <attr type="Agora:DocumentID">doc123</attr>
            </element>
            <element type="Agora:ImageSet">
                <element type="Agora:Page" ID="page1">
                    <attr type="Agora:PhysicalNo">1</attr>
                    <resource-id>res1</resource-id>
                </element>
            </element>
            <element type="Journal">
                <element ID="article1">
                </element>
            </element>
        </element-list>
        <link-list>
            <link from="article1" to="page1"/>
        </link-list>
        <resource-list>
            <resource ID="res1">
                <attr type="Agora:Path">/path/to/page1.jpg</attr>
            </resource>
        </resource-list>
    </root>
    """
    # Mock etree.parse to return the mock XML content
    with patch("lxml.etree.parse") as mock_parse:
        mock_root = etree.fromstring(mock_xml_content)
        mock_parse.return_value = MagicMock(getroot=lambda: mock_root)

        result = get_structure_info(("short", "2023"),
                                    custom_path="/path/to/custom.xml")

    assert "page1.txt" in result
    assert result["page1.txt"] == ("doc123:page1", [{"article1": {}}], "1")


def test_get_structure_info_with_missing_file():
    result = get_structure_info(("short", "2023"), custom_path=None)

    assert not result


def test_get_structure_info_with_default_path_copilot():
    year = ("short", "2023")
    mock_xml_content = """
    <root>
        <element-list>
            <element type="Agora:Document">
                <attr type="Agora:DocumentID">doc456</attr>
            </element>
            <element type="Agora:ImageSet">
                <element type="Agora:Page" ID="page2">
                    <attr type="Agora:PhysicalNo">2</attr>
                    <resource-id>res2</resource-id>
                </element>
            </element>
            <element type="Journal">
                 <element ID="article2">
                 </element>
            </element>
        </element-list>
        <link-list>
            <link from="article2" to="page2"/>
        </link-list>
        <resource-list>
            <resource ID="res2">
                <attr type="Agora:Path">/path/to/page2.jpg</attr>
            </resource>
        </resource-list>
    </root>
    """
    mock_root = etree.fromstring(mock_xml_content)

    # Mock etree.parse to return the mock XML content
    with patch("lxml.etree.parse",
               return_value=MagicMock(getroot=lambda: mock_root)):
        result = get_structure_info(year)

    assert "page2.txt" in result
    assert result["page2.txt"] == ("doc456:page2", [{"article2": {}}], "2")


# -------------------------------------------------
# Test process_page
# -------------------------------------------------
def test_process_page_person_entity_copilot():
    page = "page1.txt"
    sentences = [
        [
            {"tag": "B-PER-LN", "token": "Doe", "coord": (0, 3)},
            {"tag": "I-PER-FN", "token": "John", "coord": (4, 8)},
        ]
    ]
    entitylist = []
    structure_info = {page: ("doc123:page1", ["article1"], "1")}

    process_page(page, sentences, entitylist, [], structure_info, 1)

    assert len(entitylist) == 1
    assert entitylist[0]["info"]["lastnames"] == ["Doe"]
    assert entitylist[0]["info"]["firstnames"] == ["John"]
    assert entitylist[0]["articles"] == ["article1"]
    # many duplicates, is that what we want?
    assert entitylist[0]["pageNames"] == ["page1.txt", "page1.txt"]
    assert entitylist[0]["pageNo"] == [1, 1]
    assert entitylist[0]["sentenceNo"] == [0, 0]
    assert entitylist[0]["pid"] == ["doc123:page1", "doc123:page1"]


def test_process_page_place_entity_copilot():
    page = "page2.txt"
    sentences = [
        [
            {"tag": "B-LOC", "token": "Berlin", "coord": (0, 6)},
            {"tag": "I-LOC", "token": "Germany", "coord": (7, 14)},
        ]
    ]
    placeEntitylist = []
    structure_info = {page: ("doc456:page2", ["article2"], "2")}

    process_page(page, sentences, [], placeEntitylist, structure_info, 2)

    assert len(placeEntitylist) == 1
    assert placeEntitylist[0]["tokens"] == ["Berlin", "Germany"]
    assert placeEntitylist[0]["type"] == "LOC"
    assert placeEntitylist[0]["articles"] == ["article2"]
    # many duplicates, is that what we want?
    assert placeEntitylist[0]["pageNames"] == ["page2.txt", "page2.txt"]
    assert placeEntitylist[0]["pageNo"] == [2, 2]
    assert placeEntitylist[0]["sentenceNo"] == [0, 0]
    assert placeEntitylist[0]["pid"] == ["doc456:page2", "doc456:page2"]


def test_process_page_no_structure_info_copilot():
    page = "page3.txt"
    sentences = [
        [
            {"tag": "B-PER-LN", "token": "Smith", "coord": (0, 5)},
        ]
    ]
    entitylist = []
    placeEntitylist = []
    structure_info = {}  # No structure info for this page
    i = 3

    process_page(page,
                 sentences,
                 entitylist,
                 placeEntitylist,
                 structure_info,
                 i)

    assert len(entitylist) == 1
    assert entitylist[0]["info"]["lastnames"] == ["Smith"]
    assert entitylist[0]["pageNames"] == ["page3.txt"]
    assert entitylist[0]["pageNo"] == [3]
    assert entitylist[0]["sentenceNo"] == [0]
    assert entitylist[0]["pid"] == [None]  # No PID available
    assert entitylist[0]["articles"] == []  # No articles available


# -------------------------------------------------
# Test get_found_names
# -------------------------------------------------
def test_get_found_names_with_valid_structure_info_copilot():
    items = (("short", "2023"), "page1.jsonl", False)
    structure_info = {
        "page1.txt": ("doc123:page1", [{"article1": {}}], "1")
    }
    mock_file_content = """{"page1.txt": [[{"tag": "B-PER-LN", "token": "Doe",\
"coord": [0, 3]},{"tag": "I-PER-FN", "token": "John", "coord": [4, 8]}]]}"""
    with patch("builtins.open", mock_open(read_data=mock_file_content)):
        with patch("src.postprocess.get_structure_info",
                   return_value=structure_info):
            entitylist, year, pages = get_found_names(items)

    assert year == ("short", "2023")
    assert pages == ["page1.jsonl"]
    assert len(entitylist) == 1
    assert entitylist[0]["info"]["lastnames"] == ["Doe"]
    assert entitylist[0]["info"]["firstnames"] == ["John"]
    assert entitylist[0]["pageNames"] == "page1.txt"
    assert entitylist[0]["pageNo"] == 1
    assert entitylist[0]["pid"] == "doc123:page1"
    assert entitylist[0]["articles"] == [{"article1": {}}]


def test_get_found_names_with_empty_structure_info_copilot():
    items = (("short", "2023"), "page2.jsonl", True)
    structure_info = {}
    mock_file_content = """{"page2.txt": [[{"tag": "B-LOC", "token": "Berlin",\
"coord": [0, 6]},{"tag": "I-LOC", "token": "Germany", "coord": [7, 14]}]]}"""
    with patch("builtins.open", mock_open(read_data=mock_file_content)):
        with patch("src.postprocess.get_structure_info",
                   return_value=structure_info):
            entitylist, year, pages = get_found_names(items)

    assert year == ("short", "2023")
    assert pages == ["page2.jsonl"]
    assert len(entitylist) == 1
    assert entitylist[0]["tokens"] == ["Berlin", "Germany"]
    assert entitylist[0]["type"] == "LOC"
    assert entitylist[0]["pageNames"] == "page2.txt"
    assert entitylist[0]["pageNo"] == 0  # Default fallback page number
    assert entitylist[0]["pid"] is None
    assert entitylist[0]["articles"] == []


def test_get_found_names_with_multiple_pages_copilot():
    items = (("short", "2023"), ["page1.jsonl", "page2.jsonl"], True)
    structure_info = {
        "page1.txt": ("doc123:page1", [{"article1": {}}], "1"),
        "page2.txt": ("doc456:page2", [{"article2": {}}], "2")
    }
    mock_file_content_page1 = """{"page1.txt": [[{"tag": "B-PER-LN",\
"token": "Smith", "coord": [0, 5]}]]}"""
    mock_file_content_page2 = """{"page2.txt": [[{"tag": "B-LOC",\
"token": "Paris", "coord": [0, 5]}]]}"""
    with patch("builtins.open", mock_open()) as mock_file:
        mock_file.side_effect = [
            mock_open(read_data=mock_file_content_page1).return_value,
            mock_open(read_data=mock_file_content_page2).return_value
        ]
        with patch("src.postprocess.get_structure_info",
                   return_value=structure_info):
            entitylist, year, pages = get_found_names(items)

    assert year == ("short", "2023")
    assert len(entitylist) == 2
    assert pages == ["page1.jsonl", "page2.jsonl"]
    assert entitylist[0]["info"]["lastnames"] == ["Smith"]
    assert entitylist[0]["pageNames"] == "page1.txt"
    assert entitylist[0]["pageNo"] == 1
    assert entitylist[0]["pid"] == "doc123:page1"
    assert entitylist[0]["articles"] == [{"article1": {}}]

    assert entitylist[1]["tokens"] == ["Paris"]
    assert entitylist[1]["type"] == "LOC"
    assert entitylist[1]["pageNames"] == "page2.txt"
    assert entitylist[1]["pageNo"] == 2
    assert entitylist[1]["pid"] == "doc456:page2"
    assert entitylist[1]["articles"] == [{"article2": {}}]


# -------------------------------------------------
# Test populate_year_dict
# -------------------------------------------------
def test_populate_year_dict_with_json_files_copilot():
    year_dict = {}
    file_list = [
        "/path/to/magazine1/2023/file1.json",
        "/path/to/magazine1/2023/file2.json"
    ]

    populate_year_dict(year_dict, file_list)

    assert len(year_dict) == 2
    assert ("2023", "file1") in year_dict
    assert year_dict[("2023", "file1")] == file_list[0]
    assert ("2023", "file2") in year_dict
    assert year_dict[("2023", "file2")] == file_list[1]


def test_populate_year_dict_with_jsonl_files_copilot():
    year_dict = {}
    file_list = [
        "/path/to/magazine2/2023/file1.jsonl",
        "/path/to/magazine2/2023/file2.jsonl"
    ]

    populate_year_dict(year_dict, file_list)

    assert len(year_dict) == 2
    assert ("2023", "file1") in year_dict
    assert isinstance(year_dict[("2023", "file1")], list)
    assert ("2023", "file2") in year_dict
    assert isinstance(year_dict[("2023", "file2")], list)


def test_populate_year_dict_with_unsupported_file_type_copilot():
    year_dict = {}
    file_list = [
        "/path/to/magazine3/2023/file1.txt",
        "/path/to/magazine3/2023/file2.csv"
    ]

    populate_year_dict(year_dict, file_list)

    assert len(year_dict) == 0  # Unsupported file types should not be added


# # -------------------------------------------------
# Test get_data_paths_iterative
# -------------------------------------------------
def test_get_data_paths_iterative_with_custom_paths():
    settings.CUSTOM_PATHS= ["/path/to/custom1.json",
                         "/path/to/custom2.json",
                         "/path/to/custom3.json"]
    settings.BATCH_SIZE = 2

    with patch("os.path.isfile", return_value=True):
        result = list(get_data_paths_iterative())

    assert len(result) == 2
    assert result[0] == {
        ("to", "custom1"): "/path/to/custom1.json",
        ("to", "custom2"): "/path/to/custom2.json"
    }
    assert result[1] == {
        ("to", "custom3"): "/path/to/custom3.json",
    }


@patch("glob.glob")
def test_get_data_paths_iterative_with_magazine_directories(mock_glob):
    settings.PATH_TO_INPUT_FOLDERS = "/path/to/mag"
    settings.CUSTOM_PATHS = None
    settings.BATCH_SIZE = 1
    mock_glob.side_effect = [
        ["/path/to/mag/111", "/path/to/mag/222"],
        ["/path/to/mag/111"],
        ["/path/to/mag/222"],
        ["/path/to/mag/111/file1.json"],
        ["/path/to/mag/222/file2.json"]
    ]
    with patch("os.path.isdir", return_value=True):
        result = list(get_data_paths_iterative())

    assert {} in result  # artefact of yield
    result.remove({})
    assert len(result) == 2  # Two batches since BATCH_SIZE is 1
    assert ("111", "file1") in result[0]
    assert ("222", "file2") in result[1]


def test_get_data_paths_iterative_with_tag_folder():
    settings.CUSTOM_PATHS = ["/path/to/output/tag/111/file1.json",
        "/path/to/output/tag/222/file2.json",
        "/path/to/output/tag/333/file3.json"]
    settings.BATCH_SIZE = 2

    with patch("os.path.isfile", return_value=True):
        result = list(get_data_paths_iterative())

    assert len(result) == 2, result  # bc of the batchsize
    assert ("111", "file1") in result[0]
    assert ("222", "file2") in result[0]
    assert ("333", "file3") in result[1]


def test_get_data_paths_iterative_with_invalid_input_dir():
    settings.PATH_TO_INPUT_FOLDERS = "/invalid/path/"
    settings.BATCH_SIZE =  1

    with pytest.raises(Exception) as pyexc:
        list(get_data_paths_iterative())
        print(str(pyexc.value))
        assert "validation error" in str(pyexc.value), str(pyexc.value)


@patch("glob.glob")
def test_get_data_paths_iterative_with_invalid_input_mag(mock_glob):
    settings.PATH_TO_INPUT_FOLDERS = "/invalid/path/"
    settings.CUSTOM_PATHS = None
    settings.BATCH_SIZE = 1
    mock_glob.return_value = [
        "/invalid/path/111",
     ]
    with pytest.raises(Exception,
                       match=re.escape(f'The given input: {mock_glob.return_value}\
 is neither a valid directory, nor a valid file.')):
        list(get_data_paths_iterative())


# -------------------------------------------------
# Test execute_postprocessing
# -------------------------------------------------
def test_execute_postprocessing_basic_copilot():
    settings.PATH_TO_OUTFILE_FOLDER = "/tmp/"
    settings.BATCH_SIZE = 2
    settings.CUSTOM_PATHS = ["test_data/tag/test.json"]
    tasks = ["post"]
    magazines = [
        {"year1": "data1", "year2": "data2"},
        {"year3": "data3"}
    ]

    # Patch Pool, get_data_paths_iterative, get_found_names, save_data_intermediate
    with patch("src.postprocess.Pool") as mock_pool, \
         patch("src.postprocess.get_found_names") as mock_found_names, \
         patch("src.postprocess.save_data_intermediate") as mock_save:

        # Setup mocks
        mock_pool.return_value.__enter__.return_value.map.return_value = [(["entity"], ("mag", "2025"), ["test.json"])]
        mock_found_names.return_value = (["entity"], ("mag", "2025"), ["test.json"])

        result = execute_postprocessing(magazines, tasks, timed=False)
        assert isinstance(result, list)


@patch("src.postprocess.Pool")
@patch("src.postprocess.get_found_names")
def test_execute_postprocessing_with_agg_batchsize1(mock_get_found_names, mock_pool):
    settings.PATH_TO_OUTFILE_FOLDER = "/tmp/"
    settings.BATCH_SIZE = 1
    settings.CUSTOM_PATHS = ["test_data/tag/test.json"]
    tasks = ["post", "agg"]
    paths = ["test.json"]
    magazines = [
        {("abc", "year1"): "data1", ("abc", "year2"): "data2"},
        {("def", "year3"): "data3"}
    ]
    # Mock get_found_names to return processed data
    mock_get_found_names.side_effect = [
        ("processed_data1", "year1", paths),
        ("processed_data2", "year2", paths),
        ("processed_data3", "year3", paths)
    ]

    with patch("src.postprocess.save_data_intermediate") as mock_save:
        # Mock Pool to simulate multiprocessing
        mock_pool_instance = MagicMock()
        mock_pool.return_value.__enter__.return_value = mock_pool_instance
        mock_pool_instance.map.side_effect = lambda func, items: [
            func(item) for item in items]

        result = execute_postprocessing(magazines, tasks, timed=False)
        assert len(result) == 3
        assert result[0] == ("year1", "processed_data1", paths)
        assert result[1] == ("year2", "processed_data2", paths)
        assert result[2] == ("year3", "processed_data3", paths)

        mock_pool.assert_not_called()

        # Verify get_found_names was called for each item
        mock_get_found_names.assert_any_call((("abc", "year1"), "data1", False))
        mock_get_found_names.assert_any_call((("abc", "year2"), "data2", False))
        mock_get_found_names.assert_any_call((("def", "year3"), "data3", False))

        assert isinstance(result, list)
        # Should not call save_data_intermediate if "agg" in tasks
        mock_save.assert_not_called()


@patch("src.postprocess.Pool")
@patch("src.postprocess.get_found_names")
def test_execute_postprocessing_with_agg_batchsizek(mock_get_found_names, mock_pool):
    settings.PATH_TO_OUTFILE_FOLDER = "/tmp/"
    settings.BATCH_SIZE = 2
    settings.CUSTOM_PATHS = ["test_data/tag/test.jsonl"]
    tasks = ["post", "agg"]
    paths = ["test.jsonl"]
    magazines = [
        {("abc", "year1"): "data1", ("abc", "year2"): "data2"},
        {("def", "year3"): "data3"}
    ]
    # Mock get_found_names to return processed data
    mock_get_found_names.side_effect = [
        ("processed_data1", "year1", paths),
        ("processed_data2", "year2", paths),
        ("processed_data3", "year3", paths)
    ]

    with patch("src.postprocess.save_data_intermediate") as mock_save:
        # Mock Pool to simulate multiprocessing
        mock_pool_instance = MagicMock()
        mock_pool.return_value.__enter__.return_value = mock_pool_instance
        mock_pool_instance.map.side_effect = lambda func, items: [
            func(item) for item in items]

        result = execute_postprocessing(magazines, tasks, timed=False)
        assert len(result) == 3
        assert result[0] == ("year1", "processed_data1", paths)
        assert result[1] == ("year2", "processed_data2", paths)
        assert result[2] == ("year3", "processed_data3", paths)

        mock_pool.assert_called_with(settings.BATCH_SIZE)

        # Verify get_found_names was called for each item
        mock_get_found_names.assert_any_call((("abc", "year1"), "data1", False))
        mock_get_found_names.assert_any_call((("abc", "year2"), "data2", False))
        mock_get_found_names.assert_any_call((("def", "year3"), "data3", False))

        assert isinstance(result, list)
        # Should not call save_data_intermediate if "agg" in tasks
        mock_save.assert_not_called()
