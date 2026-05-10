import logging
from unittest.mock import patch, MagicMock
from lxml import etree
from utility.split_year import (
    get_pagenumbers,
    check_for_missing_pages,
    cut_pagenumbers,
    compare_pagenames,
    split_directory
)
LOGGER = logging.getLogger(__name__)


# -------------------------------------------------
# Test get_pagenumbers
# -------------------------------------------------
def test_get_pagenumbers_with_issues_copilot():
    xml_content = """
    <root>
        <element type="Issue" ID="1">
            <attr type="IssueNumber">Issue1</attr>
            <element ID="2">
                <link from="2" to="3"/>
            </element>
        </element>
        <element type="Agora:Page" ID="3">
            <resource-id>page1</resource-id>
        </element>
        <resource-list>
            <resource ID="page1">
                <attr type="Agora:Path">/path/to/page1.jpg</attr>
            </resource>
        </resource-list>
    </root>
    """
    xml = etree.fromstring(xml_content)

    returncode, issue_dict = get_pagenumbers(xml)

    assert returncode == 0
    assert "Issue1" in issue_dict
    assert issue_dict["Issue1"] == ["page1.txt"]


def test_get_pagenumbers_without_issues_copilot():
    xml_content = """
    <root>
        <resource-list>
            <resource>
                <attr type="Agora:Path">/path/to/page1.jpg</attr>
            </resource>
            <resource>
                <attr type="Agora:Path">/path/to/page2.gif</attr>
            </resource>
        </resource-list>
    </root>
    """
    xml = etree.fromstring(xml_content)

    returncode, issue_dict = get_pagenumbers(xml)

    assert returncode == 0
    assert "1" in issue_dict
    assert issue_dict["1"] == ["page1.txt", "page2.txt"]


def test_get_pagenumbers_with_missing_resource_id_copilot():
    xml_content = """
    <root>
        <element type="Issue" ID="1">
            <attr type="IssueNumber">Issue1</attr>
            <element ID="2">
                <link from="2" to="3"/>
            </element>
        </element>
        <element type="Agora:Page" ID="3">
            <!-- Missing resource-id -->
        </element>
    </root>
    """
    xml = etree.fromstring(xml_content)

    returncode, issue_dict = get_pagenumbers(xml)

    assert returncode == -1  # Indicates a missing resource-id
    assert "Issue1" in issue_dict
    assert issue_dict["Issue1"] == []


# -------------------------------------------------
# Test check_for_missing_pages
# -------------------------------------------------
def test_check_for_missing_pages_no_duplicates_copilot():
    pagenos = {
        "issue1": ["page1.txt", "page2.txt", "page3.txt"],
        "issue2": ["page4.txt", "page5.txt"]
    }

    returncode, total_pages = check_for_missing_pages(pagenos)

    assert returncode == 0  # No duplicates
    assert total_pages == 5  # Total number of pages


def test_check_for_missing_pages_with_duplicates_copilot(caplog):
    pagenos = {
        "issue1": ["page1.txt", "page2.txt", "page3.txt"],
        "issue2": ["page3.txt", "page4.txt"]  # Duplicate: "page3.txt"
    }

    with caplog.at_level(logging.WARNING):
        returncode, total_pages = check_for_missing_pages(pagenos)
        assert 'DUPLICATES FOUND!' in caplog.text, caplog.text
        assert returncode == -1  # Duplicates found
        assert total_pages == 5  # Total number of pages (including duplicates)


# -------------------------------------------------
# Test cut_pagenumbers
# -------------------------------------------------
def test_cut_pagenumbers_with_small_issues_copilot():
    pagenos = {
        "issue1": ["page1", "page2", "page3"],
        "issue2": ["page4", "page5"]
    }
    max_len = 500
    max_len_warning = 1000

    result = cut_pagenumbers(pagenos, max_len, max_len_warning)

    assert len(result) == 1  # All issues fit into one chunk
    assert result[0] == pagenos  # The chunk should match the input


def test_cut_pagenumbers_with_large_issues():
    pagenos = {
        "issue1": [f"page{i}" for i in range(1, 1201)]  # 1200 pages
    }
    max_len = 500
    max_len_warning = 1000

    result = cut_pagenumbers(pagenos, max_len, max_len_warning)

    assert len(result) == 3  # The issue is split into 3 chunks
    assert len(result[0]["issue1-0"]) == 500  # First chunk has 500 pages
    assert len(result[1]["issue1-1"]) == 500  # Second chunk has 500 pages
    assert len(result[2]["issue1-2"]) == 200  # Third chunk has 200 pages


def test_cut_pagenumbers_with_warning_copilot(caplog):
    pagenos = {
        "issue1": [f"page{i}" for i in range(1, 1501)]  # 1500 pages
    }
    max_len = 500
    max_len_warning = 1000

    with caplog.at_level(logging.WARNING):
        result = cut_pagenumbers(pagenos, max_len, max_len_warning)
    assert 'Issue is longer than set maximum length, will be split at set \
length interval.' in caplog.text, caplog.text
    assert len(result) == 3  # The issue is split into 3 chunks
    assert len(result[0]["issue1-0"]) == 500  # First chunk has 500 pages
    assert len(result[1]["issue1-1"]) == 500  # Second chunk has 500 pages
    assert len(result[2]["issue1-2"]) == 500  # Third chunk has 500 pages


def test_cut_pagenumbers_with_multiple_issues_copilot():
    pagenos = {
        "issue1": [f"page{i}" for i in range(1, 501)],  # 500 pages
        "issue2": [f"page{i}" for i in range(501, 1001)],  # 500 pages
        "issue3": [f"page{i}" for i in range(1001, 1501)]  # 500 pages
    }
    max_len = 1000
    max_len_warning = 1500

    result = cut_pagenumbers(pagenos, max_len, max_len_warning)

    assert len(result) == 2  # Two chunks since max_len is 1000
    assert len(result[0]) == 2  # First chunk contains issue1 and issue2
    assert len(result[1]) == 1  # Second chunk contains issue3


# -------------------------------------------------
# Test compare_pagenames
# -------------------------------------------------
def test_compare_pagenames_matching_pages_copilot():
    year_pages = [
        "/path/to/page1.txt",
        "/path/to/page2.txt",
        "/path/to/page3.txt",
        "/path/to/page4.txt"
    ]
    page_count = 4

    assert compare_pagenames("", year_pages, page_count, "") == 0


def test_compare_pagenames_missing_pages_copilot(caplog):
    pagenos = {
        "issue1": ["page1.txt", "page2.txt"],
        "issue2": ["page3.txt", "page4.txt"]
    }
    year_pages = [
        "/path/to/page1.txt",
        "/path/to/page3.txt"
    ]
    page_count = 4
    directory = "/path/to/year"

    with caplog.at_level(logging.WARNING):
        assert compare_pagenames(
            pagenos, year_pages, page_count, directory
        ) == -1
    assert 'Splitting /path/to/year pagecount is suspicious.\
                        Pages at positions 1, 3 are missing.\
                        Max index is 4.' in caplog.text, caplog.text


def test_compare_pagenames_extra_pages_copilot(caplog):
    pagenos = {
        "issue1": ["page1.txt", "page2.txt"]
    }
    year_pages = [
        "/path/to/page1.txt",
        "/path/to/page2.txt",
        "/path/to/page3.txt"
    ]
    page_count = 2
    directory = "/path/to/year"

    with caplog.at_level(logging.WARNING):
        assert compare_pagenames(
            pagenos, year_pages, page_count, directory
        ) == -1
    assert 'Page count in data directory doesnt equal page count calculated by year splitter!' in caplog.text, caplog.text
    assert 'Splitting /path/to/year pagecount is suspicious.\
                        Pages at positions 2 are missing.\
                        Max index is 3.' in caplog.text, caplog.text

# -------------------------------------------------
# Test split_directory
# -------------------------------------------------
def test_split_directory_with_custom_xml_copilot():
    # Arrange
    directory = "/path/to/directory"
    custom_xml_path = "/path/to/custom.xml"
    mock_xml_content = """
    <root>
        <element type="Issue" ID="1">
            <attr type="IssueNumber">1</attr>
            <link from="1" to="2"/>
        </element>
        <element type="Agora:Page" ID="2">
            <resource-id>page1</resource-id>
        </element>
        <resource-list>
            <resource ID="page1">
                <attr type="Agora:Path">/path/to/page1.txt</attr>
            </resource>
        </resource-list>
    </root>
    """

    with patch("lxml.etree.parse") as mock_parse, \
         patch("glob.glob", return_value=["/path/to/page1.txt"]):

        mock_root = etree.fromstring(mock_xml_content)
        mock_parse.return_value = MagicMock(getroot=lambda: mock_root)

        result = list(split_directory(directory, "/path/to/custom.xml"))

        assert len(result) == 1
        assert result[0][0] == 0  # Chunk index
        assert result[0][1] == ["/path/to/page1.txt"]  # Page paths
        mock_parse.assert_called_once_with(custom_xml_path)


def test_split_directory_without_custom_xml_copilot():
    directory = "/path/to/directory"
    mock_xml_content = """
    <root>
        <element type="Issue" ID="1">
            <attr type="IssueNumber">1</attr>
            <link from="1" to="2"/>
        </element>
        <element type="Agora:Page" ID="2">
            <resource-id>page1</resource-id>
        </element>
        <resource-list>
            <resource ID="page1">
                <attr type="Agora:Path">/path/to/page1.txt</attr>
            </resource>
        </resource-list>
    </root>
    """

    with patch("lxml.etree.parse") as mock_parse, \
         patch("glob.glob", return_value=["/path/to/page1.txt"]), \
         patch("os.path.join", return_value="/path/to/xml.cache.prod01"):

        mock_root = etree.fromstring(mock_xml_content)
        mock_parse.return_value.getroot.return_value = mock_root

        result = list(split_directory(directory, {"DATA2_MNT": ""}))

        assert len(result) == 1
        assert result[0][0] == 0  # Chunk index
        assert result[0][1] == ["/path/to/page1.txt"]  # Page paths
