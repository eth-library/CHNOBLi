import pytest
from unittest.mock import patch, MagicMock
from .test_data import params
from utility.linking_utils import (
    clean_namestring,
    prep_name_for_elasticsearch_query,
    search_person_gnd,
    convert_dates_wikidata,
    convert_wikidata_format_kibana,
    convert_gnd_format_kibana,
    search_person_wikidata
)


# -------------------------------------------------
# Test clean_namestring
# -------------------------------------------------
@pytest.mark.parametrize(
    "name,expected",
    [
        ("D. Birchall", 'D* Birchall'),
        ("J.F. Bitschnau", 'J*F* Bitschnau'),
        ("Wyß", "Wyss"),
        ("]osef", "osef"),
        ("hel.lo", "hello")
    ],
)
def test_clean_namestring(name, expected):
    """
    This is just a function to prepare the search terms for the
    elasticsearch queries.
    """
    assert clean_namestring(name) == expected


# -------------------------------------------------
# Test prep_name_for_elasticsearch_query
# -------------------------------------------------
@pytest.mark.parametrize(
    "name,expected",
    [
        ("D* Birchall", 'D* Birchall~2'),
        ("J*F* Bitschnau", 'J*F* Bitschnau~2'),
        ("Viktor Amadeus", 'Viktor~2 Amadeus~2'),
        (" Hiilimann", 'Hiilimann~2'),
        ("Urs fosef Cavelti", 'Urs~1 fosef~1 Cavelti~2'),
        # his name is actually Urs Josef Cavelti
        ("David", "David~1"),
        ("Wyss", "Wyss~1")
    ],
)
def test_prep_name_for_elasticsearch_query(name, expected):
    """
    This is just a function to prepare the search terms for the
    fuzzy elasticsearch queries.
    """
    assert prep_name_for_elasticsearch_query(name) == expected


# -------------------------------------------------
# Test search_person_gnd
# -------------------------------------------------
@pytest.mark.parametrize(
    "fnames, lastname, year, gnd_limit, fuzzy, expected, get_res",
    params.PARAMS_search_person_gnd,
)
@patch("utility.linking_utils.requests.get")
def test_search_person_gnd(
     mock_get, fnames, lastname, year, gnd_limit, fuzzy, expected, get_res
     ):
    """
    We check
    (1) Do we get results even for misspelled or abbreviated entities.
    (2) Does it return at most gnd_limit results
    """
    mock_response = MagicMock()
    mock_response.json.return_value = get_res

    mock_get.return_value = mock_response

    res = search_person_gnd(fnames, lastname, year, gnd_limit, fuzzy)
    assert res == expected
    assert len(res) <= gnd_limit


# # -------------------------------------------------
# Test convert_dates
# -------------------------------------------------
@pytest.mark.parametrize(
    "wikidata_date, expected",
    [
        ("+1796-10-16T00:00:00Z", "1796-10-16"),  # day
        ("+2025-02-00T00:00:00Z", "2025-02-00"),  # month
        ("+2025-00-00T00:00:00Z", "2025-00-00"),  # year
        ("+2010-00-00T00:00:00Z", "2010-00-00"),  # decade
        ("+2025-02-11T20:21:22Z", "2025-02-11")  # second
    ],
)
def test_convert_dates(wikidata_date, expected):
    """
    We check if the dates are converted properly.
    """
    assert convert_dates_wikidata(wikidata_date) == expected


# -------------------------------------------------
# Test search_person_wikidata
# -------------------------------------------------
@pytest.mark.parametrize(
    "search_term, year, wikidata_limit, fuzzy, expected, get_res",
    params.PARAMS_search_person_wikidata,
)
@patch("utility.linking_utils.requests.get")
def test_search_person_wikidata(
    mock_get, search_term, year, wikidata_limit, fuzzy, expected, get_res
     ):
    """
    We check
    (1) Do we get results even for misspelled or abbreviated entities.
    (2) Does it return at most GND_LIMIT results.
    (3) dob of the resulting candidates are before the publishing year
    of the magazine.
    """
    mock_response = MagicMock()
    mock_response.json.return_value = get_res

    mock_get.return_value = mock_response
    assert search_person_wikidata(search_term, year, wikidata_limit, fuzzy) == expected
    assert len(
        search_person_wikidata(search_term, year, wikidata_limit, fuzzy)
    ) <= wikidata_limit


# -------------------------------------------------
# Test convert_wikidata_format_kibana
# -------------------------------------------------
@pytest.mark.parametrize(
    "person_dict, expected",
    params.PARAMS_convert_wikidata_format_kibana,
)
def test_convert_wikidata_format_kibana(person_dict, expected):
    assert convert_wikidata_format_kibana(person_dict) == expected


# -------------------------------------------------
# Test convert_gnd_format_kibana
# -------------------------------------------------
@pytest.mark.parametrize(
    "person_dict, expected",
    params.PARAMS_convert_gnd_format_kibana,
)
def test_convert_gnd_format_kibana(person_dict, expected):
    assert convert_gnd_format_kibana(person_dict) == expected
