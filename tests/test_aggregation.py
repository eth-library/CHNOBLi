import pytest
from .test_data import params
from src.aggregation import (
    create_new_aggregated_unit,
    merge_to_existing_aggregated_unit,
    decide_candidates,
    full_firstname_match,
    aggregate_with,
    abbrev_firstname_match,
    only_lastname_match,
    only_firstname_match,
    only_abbrev_firstname_match,
    others_match,
    clean_up_aggregation,
    map_genitive_versions,
    map_genitive_places,
    find_place_match,
    aggregate_places,
    aggregate_place,
    create_new_aggregated_place,
    clean_up_aggregation_places,
    clean_lastname,
    aggregate_names,
    execute_aggregation
)
from utility.settings import settings


# -------------------------------------------------
# Test create_new_aggregated_unit
# -------------------------------------------------
def test_create_new_aggregated_unit_copilot():
    reference = {
        "info": {
            "lastnames": ["Doe"],
            "firstnames": "John",
            "abbr_firstnames": "J.",
            "address": ["123 Main St"],
            "titles": ["Dr."],
            "occupations": ["Engineer"],
            "others": ["AdditionalInfo"]
        },
        "pageNo": 1,
        "pageNames": "Page1",
        "pid": "pid1",
        "sentenceNo": 5,
        "positions": "pos1",
        "articles": "article1"
    }

    result = create_new_aggregated_unit(reference)

    assert result["lastname"] == ["Doe"]
    assert result["firstname"] == {("John",)}
    assert result["abbr_firstname"] == {("J.",)}
    assert result["address"] == {("123 Main St",)}
    assert result["titles"] == {("Dr.",)}
    assert result["profession"] == {("Engineer",)}
    assert result["other"] == {("AdditionalInfo",)}
    assert result["references"] == {
        (1, "Page1", "pid1"): [(5, "pos1", "article1")]
    }


# -------------------------------------------------
# Test merge_to_existing_aggregated_unit
# TODO add cases where the jobs are the same or something.
# -------------------------------------------------
def test_merge_to_existing_aggregated_unit_copilot():
    match = {
        "firstname": {("John",)},
        "abbr_firstname": {("J.",)},
        "titles": {("Dr.",)},
        "other": {("OtherInfo",)},
        "address": {("123 Street",)},
        "profession": {("Engineer",)},
        "references": {
            (1, "Page1", "pid1"): [(1, "pos1", "article1")]
        }
    }
    reference = {
        "info": {
            "firstnames": "Jane",
            "abbr_firstnames": "J.",
            "titles": ["Prof."],
            "others": ["AdditionalInfo"],
            "address": ["456 Avenue"],
            "occupations": ["Scientist"]
        },
        "pageNo": 2,
        "pageNames": "Page2",
        "pid": "pid2",
        "sentenceNo": 5,
        "positions": "pos2",
        "articles": "article2"
    }

    merge_to_existing_aggregated_unit(match, reference)

    assert ("Jane",) in match["firstname"]
    assert ("J.",) in match["abbr_firstname"]
    assert ("Prof.",) in match["titles"]
    assert ("AdditionalInfo",) in match["other"]
    assert ("456 Avenue",) in match["address"]
    assert ("Scientist",) in match["profession"]
    assert (2, "Page2", "pid2") in match["references"]
    assert match["references"][(2, "Page2", "pid2")] == [
        (5, "pos2", "article2")
    ]
    assert len(match["references"]) == 2


# -------------------------------------------------
# Test aggregate_with
# -------------------------------------------------
@pytest.mark.parametrize(
  "namepart_dict, aggregated_names, namepart, expected",
  params.PARAMS_test_aggregate_with
)
def test_aggregate_with(namepart_dict,
                        aggregated_names,
                        namepart,
                        expected):
    aggregate_with(namepart_dict, aggregated_names, namepart)
    assert aggregated_names == expected, aggregated_names


# -------------------------------------------------
# Test decide_candidates
# -------------------------------------------------
def test_decide_candidates_no_candidates_copilot():
    reference = {
        "pageNo": 1,
        "sentenceNo": 5,
        "info": {
            "lastnames": "Doe",
            "firstnames": "John",
            "abbr_firstnames": "J.",
            "address": [],
            "titles": [],
            "occupations": [],
            "others": []
        },
        "pageNames": "Page1",
        "pid": "123",
        "positions": [10, 20],
        "articles": ["Article1"]
    }
    candidates = []
    aggregated_names = []

    decide_candidates(reference, candidates, aggregated_names)

    assert len(aggregated_names) == 1
    assert aggregated_names[0]["lastname"] == "Doe"
    assert ("John",) in aggregated_names[0]["firstname"]


def test_decide_candidates_single_best_candidate_copilot():
    reference = {
        "pageNo": 2,
        "sentenceNo": 10,
        "info": {
            "lastnames": "Smith",
            "firstnames": "Alice",
            "abbr_firstnames": "A.",
            "address": [],
            "titles": [],
            "occupations": [],
            "others": []
        },
        "pageNames": "Page2",
        "pid": "456",
        "positions": [30, 40],
        "articles": ["Article2"]
    }
    candidates = [
        {
            "lastname": "Smith",
            "firstname": {("Alice",)},
            "titles": {()},
            "address": {()},
            "profession": {()},
            "other": {()},
            "abbr_firstname": {("A.",)},
            "references": {
                (1, "Page1", "123"): [(5, [10, 20], ["Article1"])]
            }
        }
    ]
    aggregated_names = []

    decide_candidates(reference, candidates, aggregated_names)

    assert len(aggregated_names) == 0
    assert len(candidates[0]["references"]) == 2
    assert (2, "Page2", "456") in candidates[0]["references"]


def test_decide_candidates_multiple_candidates_copilot():
    reference = {
        "pageNo": 3,
        "sentenceNo": 15,
        "info": {
            "lastnames": "Brown",
            "firstnames": "Charlie",
            "abbr_firstnames": "C.",
            "address": [],
            "titles": [],
            "occupations": [],
            "others": []
        },
        "pageNames": "Page3",
        "pid": "789",
        "positions": [50, 60],
        "articles": ["Article3"]
    }
    candidates = [
        {
            "lastname": "Brown",
            "firstname": {("Charlie",)},
            "abbr_firstname": {("C.",)},
            "titles": {()},
            "address": {()},
            "profession": {()},
            "other": {()},
            "references": {
                (2, "Page2", "456"): [(10, [30, 40], ["Article2"])]
            }
        },
        {
            "lastname": "Brown",
            "firstname": {("Charlie",)},
            "abbr_firstname": {("C.",)},
            "titles": {()},
            "address": {()},
            "profession": {()},
            "other": {()},
            "references": {
                (1, "Page1", "123"): [(5, [10, 20], ["Article1"])]
            }
        }
    ]
    aggregated_names = []

    decide_candidates(reference, candidates, aggregated_names)

    assert len(aggregated_names) == 0
    assert len(candidates[0]["references"]) == 2
    assert (3, "Page3", "789") in candidates[0]["references"]
    assert len(candidates[1]["references"]) == 1


# -------------------------------------------------
# Test full_firstname_match
# -------------------------------------------------
@pytest.mark.parametrize(
  "reference, aggregated_names, expected",
  params.PARAMS_test_full_firstname_match
)
def test_full_firstname_match(reference,
                              aggregated_names,
                              expected):
    assert full_firstname_match(reference, aggregated_names) == expected


# -------------------------------------------------
# Test abbrev_firstname_match
# -------------------------------------------------
@pytest.mark.parametrize(
  "reference, aggregated_names, expected",
  params.PARAMS_abbrev_firstname_match
)
def test_abbrev_firstname_match(reference,
                                aggregated_names,
                                expected):
    assert abbrev_firstname_match(reference, aggregated_names) == expected


# -------------------------------------------------
# Test only_lastname_match
# -------------------------------------------------
@pytest.mark.parametrize(
  "reference, aggregated_names, expected",
  params.PARAMS_only_lastname_match
)
def test_only_lastname_match(reference,
                             aggregated_names,
                             expected):
    assert only_lastname_match(reference, aggregated_names) == expected


# -------------------------------------------------
# Test only_firstname_match
# TODO add one more test here where the matching worked
# -------------------------------------------------
@pytest.mark.parametrize(
  "reference, aggregated_names, expected",
  [({"info": {"lastnames": "z", "firstnames": "Anna",
              "abbr_firstnames": "",
              "titles": "", "address": "", "occupations": "",
              "others": "e"},
     "pageNo": 4, "sentenceNo": 5, "pageNames": "", "pid": "",
     "positions": "", "articles": "", 'type': 'PER'
     },
    [{'firstname': {('Anna', 'Maria')},
      "lastname": "Müller",
      "abbr_firstname": {("A")},
      "titles": {("Frau", "Dr.")},
      "address": {("a", "b")},
      "profession": {("c", "d")},
      "other": {("e")},
      "references": {
               (4, "abc", 2): [(5, "123", "123"), (6, "456", "456")]
           }
      },
    {"firstname": {("Kat", "Man")},
     "lastname": "Bil",
     "abbr_firstname": set(),
     "titles": {("Herr", "Prof")},
     "address": {("a", "b")},
     "profession": {("c", "d")},
     "other": {},
     "references": {
              (4, "abc", 2): [(5, "123", "123"), (6, "456", "456")]
          }
     }],
      []
    )]
)
def test_only_firstname_match(reference,
                              aggregated_names,
                              expected):
    assert only_firstname_match(reference, aggregated_names) == expected


# -------------------------------------------------
# Test only_abbrev_firstname_match
# -------------------------------------------------
@pytest.mark.parametrize(
  "reference, aggregated_names, expected",
  params.PARAMS_only_abbrev_firstname_match
)
def test_only_abbrev_firstname_match(reference,
                                     aggregated_names,
                                     expected):
    assert only_abbrev_firstname_match(reference, aggregated_names) == expected


# -------------------------------------------------
# Test others_match
# -------------------------------------------------
@pytest.mark.parametrize(
  "reference, aggregated_names, expected",
  params.PARAMS_others_match
)
def test_others_match(reference, aggregated_names, expected):
    assert others_match(reference, aggregated_names) == expected


# -------------------------------------------------
# Test clean_up_aggregation
# -------------------------------------------------
@pytest.mark.parametrize(
  "aggregated_names, expected",
  params.PARAMS_clean_up_aggregation
)
def test_clean_up_aggregation(aggregated_names, expected):
    res = clean_up_aggregation(aggregated_names)
    for i, r in enumerate(res):
        assert r["abbr_firstname"] == expected[i]["abbr_firstname"]
        assert sorted(r["address"]) == sorted(expected[i]["address"])
        assert r["firstname"] == expected[i]["firstname"]
        assert r["id"] == expected[i]["id"]
        assert r["lastname"] == expected[i]["lastname"]
        assert sorted(r["other"]) == sorted(expected[i]["other"])
        assert sorted(r["profession"]) == sorted(expected[i]["profession"])
        assert sorted(r["references"]) == sorted(expected[i]["references"])
        assert sorted(r["titles"]) == sorted(expected[i]["titles"])


# -------------------------------------------------
# Test map_genitive_versions
# -------------------------------------------------
@pytest.mark.parametrize(
  "all_names, lastname_dict, key, expected",
  [(["wyss", "müller", "krasniqi"],
    {"krasniqis": [{"info": {"lastnames": "krasniqis"}}],
     "müllers": [{"info": {"lastnames": "müllers"}}],
     "wyss": [{"info": {"lastnames": "wyss"}}]},
    "lastnames",
    {"krasniqis": [{"info": {"lastnames": "krasniqi"}}],
     "müllers": [{"info": {"lastnames": "müller"}}],
     "wyss": [{"info": {"lastnames": "wyss"}}]}
    )]
)
def test_map_genitive_versions(all_names, lastname_dict, key, expected):
    map_genitive_versions(all_names, lastname_dict, key)
    assert lastname_dict == expected


# -------------------------------------------------
# Test map_genitive_places
# -------------------------------------------------
@pytest.mark.parametrize(
  "all_names, place_list, expected",
  params.PARAMS_map_genitive_places
)
def test_map_genitive_places(all_names, place_list, expected):
    map_genitive_places(all_names, place_list)
    assert place_list == expected


# -------------------------------------------------
# Test find_place_match
# -------------------------------------------------
@pytest.mark.parametrize(
  "place_name, place_type, aggregated_places, expc",
  params.PARAMS_find_place_match
)
def test_find_place_match(place_name, place_type, aggregated_places,
                          expc):
    assert find_place_match(place_name, place_type, aggregated_places) == expc


# -------------------------------------------------
# Test aggregate_places
# -------------------------------------------------
@pytest.mark.parametrize(
  "all_places, aggregated_places, expected_all, expected_agg",
  params.PARAMS_aggregate_places
)
def test_aggregate_places(all_places, aggregated_places,
                          expected_all, expected_agg):
    aggregate_places(all_places, aggregated_places)
    assert all_places == expected_all
    assert aggregated_places == expected_agg


# -------------------------------------------------
# Test aggregate_place
# -------------------------------------------------
@pytest.mark.parametrize(
  "found, place, expected",
  params.PARAMS_aggregate_place
)
def test_aggregate_place(found, place, expected):
    aggregate_place(found, place)
    assert found == expected


# -------------------------------------------------
# Test create_new_aggregated_place
# -------------------------------------------------
@pytest.mark.parametrize(
  "reference, expected",
  [
    (
     {"tokens": ["ZÜRICH"],
      "type": "LOC",
      "pageNo": 4,
      "pageNames": "abc",
      "pid": 2,
      "sentenceNo": 5,
      "positions": "123",
      "articles": "123"
      },
     {"name": "Zürich",
      "tokens": ["ZÜRICH"],
      "type": "LOC",
      "references": {
              (4, "abc", 2): [(5, "123", "123")]
          }
      }
    )
  ]
)
def test_create_new_aggregated_place(reference, expected):
    assert create_new_aggregated_place(reference) == expected


# -------------------------------------------------
# Test clean_up_aggregation_places
# -------------------------------------------------
@pytest.mark.parametrize(
  "aggregated_places, last_index, expc",
  params.PARAMS_clean_up_aggregation_places
)
def test_clean_up_aggregation_places(aggregated_places, last_index, expc):
    assert clean_up_aggregation_places(aggregated_places, last_index) == expc


# -------------------------------------------------
# Test clean_lastname
# -------------------------------------------------
@pytest.mark.parametrize(
  "word, expected",
  [
    ("müller<---", "müller"),
    ("mülle<---r", "mülle<---r"),
    ("-----müller<   ---", "müller"),
    ("-----müller<   -r--", "müller<   -r"),
  ]
)
def test_clean_lastname(word, expected):
    assert clean_lastname(word) == expected


# -------------------------------------------------
# Test aggregate_names
# -------------------------------------------------
@pytest.mark.parametrize(
    "data, expected",
    params.PARAMS_aggregate_names
)
def test_aggregate_names(data, expected):
    res, year, paths = aggregate_names(data)

    for entry in res:
        entry.pop("id")  # id depends on the order

    for entry in expected:  # the order is not deterministic
        entry.pop("id")
        assert entry in res, entry


# -------------------------------------------------
# Test aggregate_and_save_data
# -------------------------------------------------
def test_aggregate_and_save_data():
    data = [
        (("abc", "2025"), [
            {
                "info": {
                    "lastnames": ["Doe"],
                    "firstnames": ["John"],
                    "abbr_firstnames": ["J."],
                    "address": ["123 Main St"],
                    "titles": ["Dr."],
                    "occupations": ["Engineer"],
                    "others": ["AdditionalInfo"]
                },
                "pageNo": 1,
                "pageNames": "Page1",
                "pid": "pid1",
                "sentenceNo": 5,
                "positions": "pos1",
                "articles": [{"article1": {}}]
            },
            {
                "info": {
                    "lastnames": ["Doe"],
                    "firstnames": [""],
                    "abbr_firstnames": ["J."],
                    "address": [""],
                    "titles": [""],
                    "occupations": [""],
                    "others": [""]
                },
                "pageNo": 3,
                "pageNames": "Page3",
                "pid": "pid3",
                "sentenceNo": 20,
                "positions": "pos5",
                "articles": [{"article4": {}}]
            }
        ], ["page1", "page2"])
    ]

    settings.BATCH_SIZE=1
    result = execute_aggregation(data, ["post", "agg", "link"])

    assert ("abc", "2025") in result
    assert len(result[("abc", "2025")]) == 2
    assert result[("abc", "2025")]["paths"] == ["page1", "page2"]
    assert len(result[("abc", "2025")]["agg_data"]) == 1
    aggregated_unit = result[("abc", "2025")]["agg_data"][0]
    assert aggregated_unit["lastname"] == "Doe"
    assert aggregated_unit["firstname"] == ["John"]
    assert aggregated_unit["abbr_firstname"] == ["J."]
    assert aggregated_unit["address"] == ["123 Main St"]
    assert set(aggregated_unit["titles"]) == set(["Dr."])
    assert aggregated_unit["profession"] == ["Engineer"]
    assert set(aggregated_unit["other"]) == set(["AdditionalInfo"])
    assert aggregated_unit["references"] == {
        "Page1": {
            "pid": "pid1",
            "refs": [{"sent": 5, "coords": "pos1"}],
            "elements": [{"elementId": "pid1:article1"}]
        },
        "Page3": {
            "pid": "pid3",
            "refs": [{"sent": 20, "coords": "pos5"}],
            "elements": [{"elementId": "pid3:article4"}]
        }
    }


def test_aggregate_and_save_data_input():
    with pytest.raises(Exception) as excinfo:
        execute_aggregation([], {}, "agg,link")
    assert str(excinfo.value) == "'post,agg,link' must be called together. Alternatively, you can call 'finish'."
