import orjson
from unittest.mock import patch, Mock
import pytest
from src.linking import (
    prep_word,
    remove_obsolete_abbrevs,
    get_candidates,
    prep_person_entry,
    prep_person_out,
    link_person,
    find_links,
    execute_linking,
    get_person_context,
    compare_to_target_ids_multiplexed
)
from utility.settings import settings


# -------------------------------------------------
# Test prep_word
# -------------------------------------------------
@pytest.mark.parametrize(
    "word,expected",
    [
        ("Otmar M\u00e4der", 'Otmar Mäder'),
        ("P* Scha^mann", "P* Schamann"),
        ("URS CAVELTI", 'Urs Cavelti'),
        ("d'Estouilly", "dEstouilly")
    ],
)
def test_prep_word(word, expected):
    assert prep_word(word) == expected


# -------------------------------------------------
# Test remove_obsolete_abbrevs
# -------------------------------------------------
@pytest.mark.parametrize(
    "fnames, abbr_firstnames, expected",
    [
        (["Richard"], ["R."], [[]]),
        (["Richard"], ["A.", "R."], [['A.'], []]),
        (["Richard"], ["A.", "R.", "B"], [['A.'], [], ['B.']]),
        (["Richard", "Albert"], ["A.", "R.", "B"], [[], [], ['B.']]),
        (["Richard"], [], []),
    ],
)
def test_remove_obsolete_abbrevs(fnames, abbr_firstnames, expected):
    assert remove_obsolete_abbrevs(fnames, abbr_firstnames) == expected


# -------------------------------------------------
# Test get_candidates
# -------------------------------------------------
@patch("src.linking.search_person_gnd")
@patch("src.linking.search_person_wikidata")
@pytest.mark.parametrize(
    "person, year, gnd_limit, wikidata_limit, gnd_return, wikidata_return, expected",
    [
     ({"lastname": ["Cavelti"],
       "firstname": ["Urs","Josef"],
       "abbr_firstname": ["U."]},
      "2004",
      15,
      5,
      {'1066273278': {
         'desc': {'(1927-2003)'},
         'birthplaceLiteral': {'Gossau'},
         'prefForename': {'Urs'},
         'jobliteral': {'Jurist'},
         'birthdate': {'1927-09-03'},
         'deathdate': {'2003-11-04'},
         'deathplaceLiteral': {'St. Gallen'},
         'gid': {'1066273278'},
         'name': {'Urs Josef Cavelti'},
         'prefSurname': {'Cavelti'},
         'score': 23.719946
         }
       },
      {},
      {'1066273278': {
          'desc': {'(1927-2003)'},
          'birthplaceLiteral': {'Gossau'},
          'prefForename': {'Urs'},
          'jobliteral': {'Jurist'},
          'birthdate': {'1927-09-03'},
          'deathdate': {'2003-11-04'},
          'deathplaceLiteral': {'St. Gallen'},
          'gid': {'1066273278'},
          'name': {'Urs Josef Cavelti'},
          'prefSurname': {'Cavelti'},
          'score': 23.719946
        }
       }),
     ({"lastname": ["Chatterjee"],
       "firstname": [],
       "abbr_firstname": ["S."]},
      "2004",
      15,
      5,
      {'104124474': {'gid': {'104124474'},
                     'prefForename': {'Suhas'},
                     'prefSurname': {'Chatterjee'},
                     'varForename': {'S.'},
                     'varSurname': {'Chatterjee'},
                     'birthdate': {'1935'},
                     'score': 11.123201},
       '104274638': {'gid': {'104274638'},
                     'prefForename': {'Shiba P.'},
                     'prefSurname': {'Chatterjee'},
                     'academic': {'Prof.'},
                     'birthdate': {'1903'},
                     'deathdate': {'1989'},
                     'score': 11.123201},
       '143232991': {'gid': {'143232991'},
                     'prefForename': {'Samir'},
                     'prefSurname': {'Chatterjee'},
                     'varForename': {'S.'},
                     'varSurname': {'Chatterjee'},
                     'academic': {'Ph.D.'},
                     'score': 11.123201},
       '170184749': {'gid': {'170184749'},
                     'prefForename': {'Salil K.'},
                     'prefSurname': {'Chatterjee'},
                     'varForename': {'Salil Kumar'},
                     'varSurname': {'Chatterjee'},
                     'birthdate': {'1938'},
                     'score': 11.123201},
       '170050564': {'gid': {'170050564'},
                     'prefForename': {'Sangit'},
                     'prefSurname': {'Chatterjee'},
                     'score': 11.123201},
       '170446042': {'gid': {'170446042'},
                     'prefForename': {'Srikanta'},
                     'prefSurname': {'Chatterjee'},
                     'varForename': {'S.'},
                     'varSurname': {'Chatterjee'},
                     'academic': {'Prof.'},
                     'score': 11.123201},
       '170721930': {'gid': {'170721930'},
                     'prefForename': {'Sris'},
                     'prefSurname': {'Chatterjee'},
                     'varForename': {'S.'},
                     'varSurname': {'Chatterjee'},
                     'score': 11.123201},
       '170724727': {'gid': {'170724727'},
                     'prefForename': {'S. K.'},
                     'prefSurname': {'Chatterjee'},
                     'score': 11.123201},
       '170726045': {'gid': {'170726045'},
                     'prefForename': {'Shiladitya'},
                     'prefSurname': {'Chatterjee'},
                     'score': 11.123201},
       '170681866': {'gid': {'170681866'},
                     'prefForename': {'Sayan'},
                     'prefSurname': {'Chatterjee'},
                     'academic': {'Prof. of Policy'},
                     'score': 11.123201},
       '171016556': {'gid': {'171016556'},
                     'prefForename': {'Surendra N.'},
                     'prefSurname': {'Chatterjee'},
                     'varForename': {'Surendra Nath'},
                     'varSurname': {'Chatterjee'},
                     'birthdate': {'1944'},
                     'score': 11.123201},
       '171011252': {'gid': {'171011252'},
                     'prefForename': {'Shri G.'},
                     'prefSurname': {'Chatterjee'},
                     'score': 11.123201},
       '17147967X': {'gid': {'17147967X'},
                     'prefForename': {'S.'},
                     'prefSurname': {'Chatterjee'},
                     'score': 11.123201},
       '171610288': {'gid': {'171610288'},
                     'prefForename': {'Samir'},
                     'prefSurname': {'Chatterjee'},
                     'varForename': {'S. R.', 'Sam', 'Samir Ranjan'},
                     'varSurname': {'Chatterjee'},
                     'academic': {'Prof.', 'Prof. Dr.'},
                     'birthdate': {'1945'},
                     'score': 11.123201},
       '171620682': {'gid': {'171620682'},
                     'prefForename': {'Sandip'},
                     'prefSurname': {'Chatterjee'},
                     'score': 11.123201}},
      {'1253876894': {'desc': {'researcher'},
                      'jobliteral': {'Forscher'},
                      'gid': {'1253876894'},
                      'name': {'Swarn Chatterjee'},
                      'prefSurname': {'Chatterjee'},
                      'prefForename': {'Swarn'},
                      'score': 11.362046},
       '172018978': {'desc': {'Ph.D. Harvard University 1967'},
                     'birthdate': {'1938-01-01'},
                     'gid': {'172018978'},
                     'name': {'Samprit Chatterjee'},
                     'prefSurname': {'Chatterjee'},
                     'prefForename': {'Samprit'},
                     'score': 11.362046},
       '124061795X': {'prefSurname': {'Chatterjee'},
                      'jobliteral': {'Hochschullehrer', 'Informatiker'},
                      'birthdate': {'1963-00-00'},
                      'gid': {'124061795X'},
                      'name': {'Siddhartha Chatterjee'},
                      'prefForename': {'Siddhartha'},
                      'score': 11.362046},
       '1199154059': {'desc': {'researcher'},
                      'jobliteral': {'Forscher'},
                      'gid': {'1199154059'},
                      'name': {'Sangam Chatterjee'},
                      'prefSurname': {'Chatterjee'},
                      'prefForename': {'Sangam'},
                      'score': 11.362046},
       '1060392003': {'desc': {
           'Indian politician and former Speaker of the Lok Sabha (1929-2018)'
                      },
                      'birthplaceLiteral': {'Tezpur'},
                      'prefForename': {'Somnath'},
                      'prefSurname': {'Chatterjee'},
                      'jobliteral': {'Barrister', 'Politiker'},
                      'birthdate': {'1929-07-25'},
                      'deathdate': {'2018-08-13'},
                      'deathplaceLiteral': {'Kolkata'},
                      'gid': {'1060392003'},
                      'name': {'Somnath Chatterjee'},
                      'score': 11.362046}},
      {'104124474': {'birthdate': {'1935'},
                     'gid': {'104124474'},
                     'prefForename': {'Suhas'},
                     'prefSurname': {'Chatterjee'},
                     'score': 11.123201,
                     'varForename': {'S.'},
                     'varSurname': {'Chatterjee'}},
       '104274638': {'academic': {'Prof.'},
                     'birthdate': {'1903'},
                     'deathdate': {'1989'},
                     'gid': {'104274638'},
                     'prefForename': {'Shiba P.'},
                     'prefSurname': {'Chatterjee'},
                     'score': 11.123201},
       '1060392003': {'birthdate': {'1929-07-25'},
                      'birthplaceLiteral': {'Tezpur'},
                      'deathdate': {'2018-08-13'},
                      'deathplaceLiteral': {'Kolkata'},
                      'desc': {
                          'Indian politician and former Speaker of the Lok \
Sabha (1929-2018)'
                      },
                      'gid': {'1060392003'},
                      'jobliteral': {'Barrister', 'Politiker'},
                      'name': {'Somnath Chatterjee'},
                      'prefForename': {'Somnath'},
                      'prefSurname': {'Chatterjee'},
                      'score': 11.362046},
       '1199154059': {'desc': {'researcher'},
                      'gid': {'1199154059'},
                      'jobliteral': {'Forscher'},
                      'name': {'Sangam Chatterjee'},
                      'prefForename': {'Sangam'},
                      'prefSurname': {'Chatterjee'},
                      'score': 11.362046},
       '124061795X': {'birthdate': {'1963-00-00'},
                      'gid': {'124061795X'},
                      'jobliteral': {'Hochschullehrer', 'Informatiker'},
                      'name': {'Siddhartha Chatterjee'},
                      'prefForename': {'Siddhartha'},
                      'prefSurname': {'Chatterjee'},
                      'score': 11.362046},
       '1253876894': {'desc': {'researcher'},
                      'gid': {'1253876894'},
                      'jobliteral': {'Forscher'},
                      'name': {'Swarn Chatterjee'},
                      'prefForename': {'Swarn'},
                      'prefSurname': {'Chatterjee'},
                      'score': 11.362046},
       '143232991': {'academic': {'Ph.D.'},
                     'gid': {'143232991'},
                     'prefForename': {'Samir'},
                     'prefSurname': {'Chatterjee'},
                     'score': 11.123201,
                     'varForename': {'S.'},
                     'varSurname': {'Chatterjee'}},
       '170050564': {'gid': {'170050564'},
                     'prefForename': {'Sangit'},
                     'prefSurname': {'Chatterjee'},
                     'score': 11.123201},
       '170184749': {'birthdate': {'1938'},
                     'gid': {'170184749'},
                     'prefForename': {'Salil K.'},
                     'prefSurname': {'Chatterjee'},
                     'score': 11.123201,
                     'varForename': {'Salil Kumar'},
                     'varSurname': {'Chatterjee'}},
       '170446042': {'academic': {'Prof.'},
                     'gid': {'170446042'},
                     'prefForename': {'Srikanta'},
                     'prefSurname': {'Chatterjee'},
                     'score': 11.123201,
                     'varForename': {'S.'},
                     'varSurname': {'Chatterjee'}},
       '170681866': {'academic': {'Prof. of Policy'},
                     'gid': {'170681866'},
                     'prefForename': {'Sayan'},
                     'prefSurname': {'Chatterjee'},
                     'score': 11.123201},
       '170721930': {'gid': {'170721930'},
                     'prefForename': {'Sris'},
                     'prefSurname': {'Chatterjee'},
                     'score': 11.123201,
                     'varForename': {'S.'},
                     'varSurname': {'Chatterjee'}},
       '170724727': {'gid': {'170724727'},
                     'prefForename': {'S. K.'},
                     'prefSurname': {'Chatterjee'},
                     'score': 11.123201},
       '170726045': {'gid': {'170726045'},
                     'prefForename': {'Shiladitya'},
                     'prefSurname': {'Chatterjee'},
                     'score': 11.123201},
       '171011252': {'gid': {'171011252'},
                     'prefForename': {'Shri G.'},
                     'prefSurname': {'Chatterjee'},
                     'score': 11.123201},
       '171016556': {'birthdate': {'1944'},
                     'gid': {'171016556'},
                     'prefForename': {'Surendra N.'},
                     'prefSurname': {'Chatterjee'},
                     'score': 11.123201,
                     'varForename': {'Surendra Nath'},
                     'varSurname': {'Chatterjee'}},
       '17147967X': {'gid': {'17147967X'},
                     'prefForename': {'S.'},
                     'prefSurname': {'Chatterjee'},
                     'score': 11.123201},
       '171610288': {'academic': {'Prof.', 'Prof. Dr.'},
                     'birthdate': {'1945'},
                     'gid': {'171610288'},
                     'prefForename': {'Samir'},
                     'prefSurname': {'Chatterjee'},
                     'score': 11.123201,
                     'varForename': {'S. R.', 'Sam', 'Samir Ranjan'},
                     'varSurname': {'Chatterjee'}},
       '171620682': {'gid': {'171620682'},
                     'prefForename': {'Sandip'},
                     'prefSurname': {'Chatterjee'},
                     'score': 11.123201},
       '172018978': {'birthdate': {'1938-01-01'},
                     'desc': {'Ph.D. Harvard University 1967'},
                     'gid': {'172018978'},
                     'name': {'Samprit Chatterjee'},
                     'prefForename': {'Samprit'},
                     'prefSurname': {'Chatterjee'},
                     'score': 11.362046},
       })
     ],
)
def test_get_candidates(mock_search_person_gnd,
                        mock_search_person_wikidata,
                        person,
                        year,
                        gnd_limit,
                        wikidata_limit,
                        expected,
                        gnd_return,
                        wikidata_return):
    # Mock GND and Wikidata search results
    mock_search_person_gnd.return_value = gnd_return
    mock_search_person_wikidata.return_value = wikidata_return

    assert get_candidates(person, year, gnd_limit, wikidata_limit) == expected


def test_get_candidates_no_lastname():
    assert not get_candidates({"lastname": []}, "", 15, 5)


def test_get_candidates_no_firstname_or_abbr():
    """
    The result of this test depends on your ES index content and your
    vector database.
    """
    assert get_candidates(
        {"lastname": ["A", "B"], "firstname": [], "abbr_firstname": []},
        "0000", 15, 5
        ) == {
        '1032302453': {
            'gid': {'1032302453'},
            'score': 1.0},
        '1157696392': {
            'gid': {'1157696392'},
            'score': 1.0},
        '144005565': {
            'gid': {'144005565'},
            'score': 1.0},
        '170307417': {
            'gid': {'170307417'},
            'score': 1.0},
        '170001083': {
            'gid': {'170001083'},
            'score': 1.0},
        '1193434378': {
            'gid': {'1193434378'},
            'score': 1.0}
        }


def test_get_candidates_short_lastname():
    assert not get_candidates(
        {"lastname": ["B"],
         "firstname": [["Alice"]],
         "abbr_firstname": ["A."]}, "", 15, 5
    )


# -------------------------------------------------
# Test prep_person_entry
# -------------------------------------------------
@pytest.mark.parametrize(
    "person, expected",
    [
        ({"firstname": ["ALLIE Marie"],
          "lastname": "K^ann MEIÉR",
          "abbr_firstname": "",
          "profession": ["Schauspielerin", "Musikerin"],
          "other": [],
          "id": 0},
         {'firstname': ['Allie', 'Marie'],
          'lastname': ['Kann', 'Meiér'],
          'abbr_firstname': [],
          'other': [],
          'profession': ['Musikerin', 'Schauspielerin'],
          "id": 'a:b:0'})
    ],
)
def test_prep_person_entry(person, expected):
    prep_person_entry(person, "abc_2025")
    assert person == expected


# -------------------------------------------------
# Test prep_person_out
# -------------------------------------------------
@pytest.mark.parametrize(
    "person,expected",
    [ # gnd ids is empty
        ({'firstname': ['Allie', 'Marie'],
            'lastname': ['Kann', 'Meiér'],
            'abbr_firstname': [],
            'profession': ['Musikerin', 'Schauspielerin'],
            "gnd_ids": []},
         {'firstname': ['Allie', 'Marie'],
            'lastname': 'Kann Meiér',
            'abbr_firstname': [],
            'profession': ['Musikerin', 'Schauspielerin'],
            "gnd_ids": [],
            "gnd_confidence": 5}),
        ({'firstname': [['Allie', 'Marie']],
            'lastname': ['Kann', 'Meiér'],
            'abbr_firstname': [],
            'profession': ['Musikerin', 'Schauspielerin'],
            "gnd_ids": [],
            "gnd_ids_scores_dist": []},
         {'firstname': [['Allie', 'Marie']],
            'lastname': 'Kann Meiér',
            'abbr_firstname': [],
            'profession': ['Musikerin', 'Schauspielerin'],
            "gnd_ids": [],
            "gnd_confidence": 3}),
        ({'firstname': [['Allie', 'Marie']],
            'lastname': ['Kann', 'Meiér'],
            'abbr_firstname': [],
            'profession': ['Musikerin', 'Schauspielerin'],
            "gnd_ids": [],
            "gnd_ids_scores_sim": []},
         {'firstname': [['Allie', 'Marie']],
            'lastname': 'Kann Meiér',
            'abbr_firstname': [],
            'profession': ['Musikerin', 'Schauspielerin'],
            "gnd_ids": [],
            "gnd_confidence": 4}),
        # gnd ids is not empty
        ({'firstname': [['Allie', 'Marie']],
            'lastname': ['Kann', 'Meiér'],
            'abbr_firstname': [],
            'profession': ['Musikerin', 'Schauspielerin'],
            "gnd_ids": ["1"]},
         {'firstname': [['Allie', 'Marie']],
            'lastname': 'Kann Meiér',
            'abbr_firstname': [],
            'profession': ['Musikerin', 'Schauspielerin'],
            "gnd_ids": ["1"],
            "gnd_confidence": 5}),
        ({'firstname': [['Allie', 'Marie']],
            'lastname': ['Kann', 'Meiér'],
            'abbr_firstname': [],
            'profession': ['Musikerin', 'Schauspielerin'],
            "gnd_ids": ["1"],
            "gnd_ids_scores_dist": []},
         {'firstname': [['Allie', 'Marie']],
            'lastname': 'Kann Meiér',
            'abbr_firstname': [],
            'profession': ['Musikerin', 'Schauspielerin'],
            "gnd_ids": ["1"],
            "gnd_confidence": 4}),
        ({'firstname': [['Allie', 'Marie']],
            'lastname': ['Kann', 'Meiér'],
            'abbr_firstname': [],
            'profession': ['Musikerin', 'Schauspielerin'],
            "gnd_ids": ["1", "2"]},
         {'firstname': [['Allie', 'Marie']],
            'lastname': 'Kann Meiér',
            'abbr_firstname': [],
            'profession': ['Musikerin', 'Schauspielerin'],
            "gnd_ids": ["1", "2"],
            "gnd_confidence": 4}),
        ({'firstname': [['Allie', 'Marie']],
            'lastname': ['Kann', 'Meiér'],
            'abbr_firstname': [],
            'profession': ['Musikerin', 'Schauspielerin'],
            "gnd_ids": ["1", "2"],
            "gnd_ids_scores_dist": []},
         {'firstname': [['Allie', 'Marie']],
            'lastname': 'Kann Meiér',
            'abbr_firstname': [],
            'profession': ['Musikerin', 'Schauspielerin'],
            "gnd_ids": ["1", "2"],
            "gnd_confidence": 3})
    ],
)
def test_prep_person_out(person, expected):
    prep_person_out(person)
    assert person == expected


# -------------------------------------------------
# Test link_person
# -------------------------------------------------
@patch("src.linking.get_candidates")
def test_link_person_with_valid_data(mock_get_candidates):
    person = {
        "lastname": "Doe",
        "firstname": ["John"],
        "abbr_firstname": ["J."],
        "address": ["123 Main St"],
        "titles": ["Dr."],
        "profession": ["Engineer"],
        "other": [],
        "references": {
            "1": {"refs": [{"sent": "Example sentence", "coords": "0,0"}]}
        },
        "type": "PER",
        "id": 1,
    }

    mock_get_candidates.return_value = {
        "1111": {"prefForename": {"John"}, "score": 15},
        "2222": {"prefForename": {"John"}, "score": 25},
        "3333": {"prefForename": {"J."}, "score": 30},
    }
    settings.GND_LIMIT =  15
    settings.WIKIDATA_LIMIT = 5
    settings.LINKED_PERSONS_LIMIT = 10
    result = link_person(
        (
            ("obl", "2004_000"),
            "2004",
            person,
            ["page1", "page2"]
        )
    )

    assert "gnd_ids" in result
    # the results from get gnd/wikidata values are assumed to be
    # sorted by score, so we do not sort them again.
    assert result["gnd_ids"] == ["1111", "2222", "3333"]
    assert result["firstname"] == ["John"]
    assert result["lastname"] == "Doe"
    assert mock_get_candidates.called


def test_link_person_with_no_candidates_copilot():
    person = {
        "lastname": "Doe",
        "firstname": ["John"],
        "abbr_firstname": ["J."],
        "address": ["123 Main St"],
        "titles": ["Dr."],
        "profession": ["Engineer"],
        "other": [],
        "references": {
            "1": {"refs": [{"sent": "Example sentence", "coords": "0,0"}]}
        },
        "type": "PER",
        "id": 1,
    }

    # Mock candidates returned by get_candidates
    mock_get_candidates = patch("src.linking.get_candidates").start()
    mock_get_candidates.return_value = {}
    settings.GND_LIMIT =  15
    settings.WIKIDATA_LIMIT = 5
    settings.LINKED_PERSONS_LIMIT = 10
    result = link_person(
        (
            ("abc", "1234_000"),
            "1234",
            person,
            ["page1", "page2"]
        )
    )

    assert "gnd_ids" in result
    assert result["gnd_ids"] == []  # No candidates found
    assert result["firstname"] == ["John"]
    assert result["lastname"] == "Doe"
    mock_get_candidates.stop()


def test_link_person_with_abbr_firstname_filtering():
    person = {
        "lastname": "Doe",
        "firstname": ["John"],
        "abbr_firstname": ["J."],
        "address": ["123 Main St"],
        "titles": ["Dr."],
        "profession": ["Engineer"],
        "other": [],
        "references": {
            "1": {"refs": [{"sent": "Example sentence", "coords": "0,0"}]}
        },
        "type": "PER",
        "id": 1,
    }

    # Mock candidates returned by get_candidates
    mock_get_candidates = patch("src.linking.get_candidates").start()
    mock_get_candidates.return_value = {
        "12345": {"prefForename": {"John"}, "score": 20},
        "67890": {"prefForename": {"Kane"}, "score": 15},
    }
    settings.GND_LIMIT =  15
    settings.WIKIDATA_LIMIT = 5
    settings.LINKED_PERSONS_LIMIT = 1
    result = link_person(
        (
            ("abc", "1234_000"),
            "1234",
            person,
            ["page1", "page2"]
        )
    )

    assert "gnd_ids" in result
    # Filtered by matching abbr_firstname
    assert result["gnd_ids"] == ["12345"]
    assert result["firstname"] == ["John"]
    assert result["lastname"] == "Doe"
    mock_get_candidates.stop()


# -------------------------------------------------
# Test find_links
# -------------------------------------------------
@patch("src.linking.link_person")
@patch("src.linking.save_data_intermediate")
def test_find_links(mock_save_data_intermediate, mock_link_person):
    mag_year = ("abc", "2023_000")
    data = [
        {
            "lastname": "Doe",
            "firstname": ["John"],
            "abbr_firstname": ["J."],
            "address": ["123 Main St"],
            "titles": ["Dr."],
            "profession": ["Engineer"],
            "other": [],
            "references": {
                "1": {"refs": [{"sent": "Example sentence", "coords": "0,0"}]}
            },
            "type": "PER",
            "id": 1,
        },
        {
            "lastname": "Smith",
            "firstname": ["Alice"],
            "abbr_firstname": ["A."],
            "address": ["456 Elm St"],
            "titles": ["Prof."],
            "profession": ["Scientist"],
            "other": [],
            "references": {
                "2": {"refs": [{"sent": "Another example", "coords": "1,1"}]}
            },
            "type": "PER",
            "id": 2,
        },
    ]
    settings.GND_LIMIT =  5
    settings.WIKIDATA_LIMIT = 10
    settings.LINKED_PERSONS_LIMIT = 3
    settings.PATH_TO_OUTFILE_FOLDER = "./tests/test_data/output/"
    settings.VD_QUERY_CHUNK_LEN = 30
    settings.BATCH_SIZE = 1

    mock_link_person.side_effect = lambda x: {
        **x[2], "gnd_ids": ["12345", "67890"]
    }

    # Patch Pool so pytest doesn't spawn subprocesses (which break mocks)
    with patch("src.linking.Pool") as mock_pool:
        mock_pool.return_value.__enter__.return_value.map = (
            lambda func, args: [func(x) for x in args]
        )
        result = find_links((mag_year, data, ["page1", "page2"]))

    assert len(result) == 3
    assert len(result[1]) == 2
    assert result[0] == mag_year
    assert result[2] == ["page1", "page2"]
    assert result[1][0]["gnd_ids"] == ["12345", "67890"]
    assert result[1][1]["gnd_ids"] == ["12345", "67890"]

    # Verify that link_person was called for each person
    assert mock_link_person.call_count == 2


# -------------------------------------------------
# Test execute_linking
# TODO another test like this but one that triggers calling the VD
# -------------------------------------------------
@patch("src.linking.find_links")
@patch("src.linking.save_data_intermediate")
def test_execute_linking(mock_save_data_intermediate, mock_find_links):
    """
    All this function does is call find links (tested above)
    and save the intermediate data (tested in test_utils)
    """
    with pytest.raises(Exception) as excinfo:
        execute_linking(None, ["post", "link"])
    assert str(excinfo.value) == "'post,agg,link' must be called together, \
or call 'finish' instead."

    data = {
        ("abc", "2023_000"):
            {"agg_data": [{
                    "lastname": "Doe",
                    "firstname": ["John"],
                    "abbr_firstname": ["J."],
                    "address": ["123 Main St"],
                    "titles": ["Dr."],
                    "profession": ["Engineer"],
                    "other": [],
                    "references": {
                        "1": {"refs": [{"sent": "Example sentence", "coords": "0,0"}]}
                    },
                    "type": "PER",
                    "id": 1,
                },
                {
                    "lastname": "Smith",
                    "firstname": ["Alice"],
                    "abbr_firstname": ["A."],
                    "address": ["456 Elm St"],
                    "titles": ["Prof."],
                    "profession": ["Scientist"],
                    "other": [],
                    "references": {
                        "2": {"refs": [{"sent": "Another example", "coords": "1,1"}]}
                    },
                    "type": "PER",
                    "id": 2,
                }],
             "paths": ["2", "1"]}
    }
    settings.GND_LIMIT =  5
    settings.WIKIDATA_LIMIT = 10
    settings.LINKED_PERSONS_LIMIT = 3
    settings.PATH_TO_OUTFILE_FOLDER = "./tests/test_data/output/"
    settings.VD_QUERY_CHUNK_LEN = 30
    settings.BATCH_SIZE = 1

    # Patch Pool so pytest doesn't spawn subprocesses (which break mocks)
    """
    @patch("src.linking.compare_to_target_ids_multiplexed")
    -> is this even a case for multiplexing??
    @patch("src.linking.get_person_context")
    """
    with patch("src.linking.Pool") as mock_pool, \
         patch("builtins.open", create=True) as mock_open_:
        mock_pool.return_value.__enter__.return_value.map = (
            lambda func, args: [func(x) for x in args]
        )
        execute_linking(data, ["finish"])  # Can't check the result, returns None
    mock_open_.assert_called()  # Ensure logs were written

    # Verify that find_links was called for each person
    assert mock_find_links.call_count == 1

    # Verify that save_data_intermediate was called with the correct arguments
    mock_save_data_intermediate.assert_called_once_with(
        [mock_find_links.return_value[0][0], mock_find_links.return_value[0][1]],
        mock_find_links.return_value[1],
        "link"
    )

# -------------------------------------------------
# Test get_person_context
# TODO another test like this but one where we have different
# pages which have the same coordinates for some token
# -------------------------------------------------
@pytest.fixture
def tagging_file(tmp_path):
    # Create a tagging output file with two tokens and coords
    page = {"page1": [[
        {"token": "Alice", "coord": "c1:0"},
        {"token": ",", "coord": "c2:1"},
        {"token": "Bob", "coord": "c3:2"},
        {"token": ".", "coord": "c4:3"},
    ]]}
    file_path = tmp_path / "tagging.jsonl"
    with open(file_path, "wb") as f:
        f.write(orjson.dumps(page))
        f.write(b"\n")
    return str(file_path), page


def test_get_person_context_basic(tagging_file):
    per = {
        "references": {
            "page1": {
                "refs": [
                    {"coords": ["c1:0"]}
                ]
            }
        }
    }
    context = get_person_context(per, [tagging_file[0]])
    # Should include "Alice" and some context (window)
    assert "Alice" in context


def test_get_person_context_multiple_mentions(tagging_file):
    per = {
        "references": {
            "page1": {
                "refs": [
                    {"coords": ["c1:0"]},
                    {"coords": ["c3:2"]}
                ]
            }
        }
    }
    context = get_person_context(per, [tagging_file[0]])
    assert "Alice" in context
    assert "Bob" in context


def test_get_person_context_missing_coord(tagging_file):
    per = {
        "references": {
            "page1": {
                "refs": [
                    {"coords": ["c999:0"]}  # coord not in file
                ]
            }
        }
    }
    context = get_person_context(per, [tagging_file[0]])
    assert context == ""


def test_get_person_context_empty_references(tagging_file):
    per = {"references": {}}
    context = get_person_context(per, [tagging_file[0]])
    assert context == ""


def test_get_person_context_invalid_file(tmp_path):
    per = {"references": {}}
    invalid_path = tmp_path / "does_not_exist.jsonl"
    with pytest.raises(Exception):
        get_person_context({"VD_CONTEXT_WINDOW_LEN": 30}, per, str(invalid_path))


# -------------------------------------------------
# Test compare_to_target_ids_multiplexed
# -------------------------------------------------
sample_args_multi = {
    "text": ["test text 1", "test text 2"],
    "target_text_ids": [["id11", "id12"], ["id21", "id22"]],
    "backend_url": "http://localhost:8000/embeddings/compare_to_text_ids_multiplexed",
    "collection_name": "test_collection",
    "model": "ollama",
    "model_name": "jina/jina-embeddings-v2-base-de"
}


def test_compare_to_target_ids_multiplexed_success():
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.text = '{"results": [{"text_id": "id1", "distance": 0.1}]}'
    mock_response.json = (lambda: {"access_token": 0})
    with patch("requests.post", return_value=mock_response) as mock_post:
        result = compare_to_target_ids_multiplexed(
            [1, 2],
            sample_args_multi["text"],
            sample_args_multi["target_text_ids"],
            sample_args_multi["backend_url"],
            sample_args_multi["collection_name"],
            sample_args_multi["model"],
            sample_args_multi["model_name"]
        )
        assert result == [{"text_id": "id1", "distance": 0.1}]
        assert mock_post.call_count == 2
        _, kwargs = mock_post.call_args
        assert kwargs["json"]["content"][0]["query_text"] == sample_args_multi["text"][0]
        assert kwargs["json"]["content"][1]["query_text"] == sample_args_multi["text"][1]
        assert kwargs["json"]["content"][0]["reference_text_ids"] == sample_args_multi["target_text_ids"][0]
        assert kwargs["json"]["content"][1]["reference_text_ids"] == sample_args_multi["target_text_ids"][1]


def test_compare_to_target_ids_multiplexed_failure_logs(caplog):
    mock_response = Mock()
    mock_response.status_code = 400
    mock_response.text = "Bad Request"
    mock_response.json = (lambda: {"access_token": 0})
    with patch("requests.post", return_value=mock_response):
        with pytest.raises(Exception) as excinfo:
            result = compare_to_target_ids_multiplexed(
                [1, 2],
                sample_args_multi["text"],
                sample_args_multi["target_text_ids"],
                sample_args_multi["backend_url"],
                sample_args_multi["collection_name"],
                sample_args_multi["model"],
                sample_args_multi["model_name"]
            )
            assert result is None
            assert "Authentication failed with status 400" in str(excinfo.value)
