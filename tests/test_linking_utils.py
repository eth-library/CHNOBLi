import threading
from unittest.mock import MagicMock, patch

import pytest
import requests
import utility.linking_utils as lu
from utility.linking_utils import (
    _alive_before_year_filter,
    _es_search,
    _preferred_gids,
    _resolve_gid,
    _safe_set,
    _session,
    build_person_gnd_query,
    build_variant_name_query,
    build_wikidata_query,
    clean_namestring,
    convert_dates_wikidata,
    convert_gnd_format_kibana,
    convert_wikidata_format_kibana,
    get_preferred_gnd_entry_wikidata,
    parse_person_gnd_response,
    parse_variant_name_response,
    parse_wikidata_response,
    prep_name_for_elasticsearch_query,
    resolve_old_gids,
    search_person_gnd,
    search_person_gnd_variantName,
    search_person_wikidata,
    warn_multiple_gids,
)

from .test_data import params


# -------------------------------------------------
# Test clean_namestring
# -------------------------------------------------
@pytest.mark.parametrize(
    "name,expected",
    [
        ("D. Birchall", "D* Birchall"),
        ("J.F. Bitschnau", "J*F* Bitschnau"),
        ("Wyß", "Wyss"),
        ("]osef", "osef"),
        ("hel.lo", "hello"),
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
        ("D* Birchall", "D* Birchall~2"),
        ("J*F* Bitschnau", "J*F* Bitschnau~2"),
        ("Viktor Amadeus", "Viktor~2 Amadeus~2"),
        (" Hiilimann", "Hiilimann~2"),
        ("Urs fosef Cavelti", "Urs~1 fosef~1 Cavelti~2"),
        # his name is actually Urs Josef Cavelti
        ("David", "David~1"),
        ("Wyss", "Wyss~1"),
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
@patch("utility.linking_utils._session")
def test_search_person_gnd(
    mock_session, fnames, lastname, year, gnd_limit, fuzzy, expected, get_res
):
    """
    We check
    (1) Do we get results even for misspelled or abbreviated entities.
    (2) Does it return at most gnd_limit results
    """
    mock_response = MagicMock()
    mock_response.json.return_value = get_res

    mock_session.return_value.get.return_value = mock_response

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
        ("+2025-02-11T20:21:22Z", "2025-02-11"),  # second
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
@patch("utility.linking_utils._session")
def test_search_person_wikidata(
    mock_session, search_term, year, wikidata_limit, fuzzy, expected, get_res
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

    mock_session.return_value.get.return_value = mock_response
    res = search_person_wikidata(search_term, year, wikidata_limit, fuzzy)
    assert res == expected
    assert len(res) <= wikidata_limit


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


# -------------------------------------------------
# Test _safe_set
# -------------------------------------------------
def test_safe_set():
    assert _safe_set(["a", None, "b", "a"]) == {"a", "b"}
    assert _safe_set("a") == {"a"}
    assert _safe_set(None) == set()


# -------------------------------------------------
# Test _alive_before_year_filter
# -------------------------------------------------
def test_alive_before_year_filter():
    clause = _alive_before_year_filter("1900")
    assert clause["bool"]["minimum_should_match"] == 1
    assert {"range": {"dateOfBirth": {"lt": "1900||/y"}}} in (
        clause["bool"]["should"][1]["bool"]["should"]
    )


# -------------------------------------------------
# Test warn_multiple_gids
# -------------------------------------------------
def test_warn_multiple_gids_warns_once_per_gids_set():
    """
    Per process: Only warn about a gnd-ids set with mutliple gnd-ids which
    seem to be associated with only one wikidata id once.
    """
    _reported_multi_gid = lu._reported_multi_gid
    _reported_multi_gid.clear()
    try:
        with patch("utility.linking_utils.logging.warning") as warning:
            assert warn_multiple_gids("Wikidata", {"gnd-1", "gnd-2"}, "Q1", "Ada") == [
                "gnd-1",
                "gnd-2",
            ]
            assert warn_multiple_gids("Wikidata", {"gnd-2", "gnd-1"}, "Q1", "Ada") == [
                "gnd-1",
                "gnd-2",
            ]

        warning.assert_called_once()
    finally:
        lu._reported_multi_gid.clear()


# -------------------------------------------------
# Test _session
# -------------------------------------------------
def test_session_reuses_session_in_thread(monkeypatch):
    monkeypatch.setattr(lu, "_sessions", threading.local())
    created = MagicMock()
    with patch("utility.linking_utils.requests.Session", return_value=created):
        assert _session() is created
        assert _session() is created


def test_session_is_recreated_after_process_change(monkeypatch):
    monkeypatch.setattr(lu, "_sessions", threading.local())
    lu._sessions.session = MagicMock()
    lu._sessions.pid = 100
    monkeypatch.setattr(lu.os, "getpid", lambda: 200)

    fresh_session = MagicMock()
    with patch("utility.linking_utils.requests.Session", return_value=fresh_session):
        assert _session() is fresh_session
        assert lu._sessions.pid == 200


# -------------------------------------------------
# Test build_variant_name_query
# -------------------------------------------------
def test_build_variant_name_query():
    query = build_variant_name_query("Ada Lovelace", "1850", fuzzy=False)
    assert query["size"] == 15
    assert "variantName" in query["_source"]
    assert (
        query["query"]["bool"]["must"][1]["bool"]["should"][0]["wildcard"][
            "variantName.keyword"
        ]["value"]
        == "Ada Lovelace"
    )


@pytest.mark.parametrize(
    "args",
    [
        ("", "1850", 15, True),
        ("Ada", "1850", 0, True),
    ],
)
def test_build_variant_name_query_returns_none_for_empty_or_zero_limit(args):
    assert build_variant_name_query(*args) is None


# -------------------------------------------------
# Test parse_variant_name_response
# -------------------------------------------------
def test_parse_variant_name_response_normalizes_score_and_label():
    response = {
        "hits": {
            "hits": [
                {
                    "_score": 4.0,
                    "_source": {
                        "gndIdentifier": "g1",
                        "preferredName": "Ada Lovelace",
                    },
                }
            ]
        }
    }
    result = parse_variant_name_response(
        response, label="surname", search_term="Lovelace"
    )
    assert result["g1"]["score"] == 1.0
    assert result["g1"]["query_label"] == "surname"


def test_parse_variant_name_response_logs_malformed_response_and_returns_empty(caplog):
    with caplog.at_level("ERROR"):
        result = parse_variant_name_response({"hits": {"hits": None}})

    assert result == {}
    assert any(record.levelname == "ERROR" for record in caplog.records)


# -------------------------------------------------
# Test build_person_gnd_query
# -------------------------------------------------
def test_build_person_gnd_query_returns_none_for_empty_lastname():
    assert build_person_gnd_query(["Ada"], "!!!", "1850") is None
    assert build_person_gnd_query(["Ada"], "Lovelace", "1850", gnd_limit=0) is None


def test_build_person_gnd_query_includes_year_and_name_fields():
    query = build_person_gnd_query(["Ada"], "Lovelace", "1850", fuzzy=False)
    assert query["size"] == 15
    must = query["query"]["bool"]["must"]
    assert len(must) >= 3
    assert must[1]["query_string"]["query"] == "Ada"
    assert must[2]["query_string"]["query"] == "Lovelace"


# -------------------------------------------------
# Test _preferred_gids
# -------------------------------------------------
def test_preferred_gids_does_not_cache_request_exception():
    _preferred_gids.cache_clear()
    try:
        with patch("utility.linking_utils._session") as session:
            session.return_value.get.side_effect = requests.ConnectionError("offline")

            for _ in range(2):
                with pytest.raises(requests.ConnectionError):
                    _preferred_gids("Q-failing")

            assert session.return_value.get.call_count == 2
    finally:
        _preferred_gids.cache_clear()


def test_preferred_gids_cached_result_is_immutable():
    lu._preferred_gids.cache_clear()
    response = MagicMock()
    response.json.return_value = {
        "results": {"bindings": [{"gndId": {"value": "gnd-1"}}]}
    }
    try:
        with patch("utility.linking_utils._session") as session:
            session.return_value.get.return_value = response

            first = lu._preferred_gids("Q-test")
            assert first == ("gnd-1",)
            with pytest.raises(AttributeError):
                first.append("injected-id")

            assert lu._preferred_gids("Q-test") == ("gnd-1",)
            session.return_value.get.assert_called_once()
    finally:
        lu._preferred_gids.cache_clear()


# -------------------------------------------------
# Test _resolve_gid
# -------------------------------------------------
def test_resolve_gid_returns_original_for_success():
    _resolve_gid.cache_clear()
    try:
        response = MagicMock(status_code=200, is_redirect=False)
        with patch("utility.linking_utils.requests.get", return_value=response):
            assert _resolve_gid("g1") == "g1"
    finally:
        _resolve_gid.cache_clear()


def test_resolve_gid_rejects_redirect_without_location():
    _resolve_gid.cache_clear()
    response = MagicMock(status_code=301, is_redirect=True, headers={})

    try:
        with (
            patch("utility.linking_utils.requests.get", return_value=response),
            pytest.raises(requests.HTTPError),
        ):
            _resolve_gid("redirect-without-location")
    finally:
        _resolve_gid.cache_clear()


@pytest.mark.parametrize("status_code", [404, 429, 500])
def test_resolve_gid_does_not_cache_http_errors(status_code):
    _resolve_gid.cache_clear()
    response = MagicMock(status_code=status_code, is_redirect=False)
    response.raise_for_status.side_effect = requests.HTTPError(str(status_code))

    try:
        with patch("utility.linking_utils.requests.get", return_value=response) as get:
            for _ in range(2):
                with pytest.raises(requests.HTTPError):
                    _resolve_gid(f"error-{status_code}")
            assert get.call_count == 2
    finally:
        _resolve_gid.cache_clear()


def test_resolve_gid_strips_json_suffix_from_redirect():
    lu._resolve_gid.cache_clear()
    response = MagicMock(
        status_code=301,
        is_redirect=True,
        headers={"Location": "https://lobid.org/gnd/1234567-8.json?format=json"},
    )
    try:
        with patch("utility.linking_utils.requests.get", return_value=response):
            assert lu._resolve_gid("old-id") == "1234567-8"
    finally:
        lu._resolve_gid.cache_clear()


# -------------------------------------------------
# Test get_preferred_gnd_entry_wikidata
# -------------------------------------------------
def test_get_preferred_gnd_entry_wikidata_logs_failure(caplog):
    with patch(
        "utility.linking_utils._preferred_gids", side_effect=requests.ConnectionError
    ):
        assert get_preferred_gnd_entry_wikidata("Q1") is None
    assert "Error accessing Wikidata endpoint" in caplog.text


def test_get_preferred_gnd_entry_wikidata_returns_multiple_gids():
    gids = ["gnd-1", "gnd-2"]
    with patch("utility.linking_utils._preferred_gids", return_value=gids):
        assert get_preferred_gnd_entry_wikidata("Q1") == gids


# -------------------------------------------------
# Test resolve_old_gids
# -------------------------------------------------
def test_resolve_old_gids_keeps_original_on_lookup_failure():
    with patch(
        "utility.linking_utils._resolve_gid", side_effect=requests.ConnectionError
    ):
        assert resolve_old_gids(["g1"]) == ["g1"]


def test_resolve_old_gids_returns_multiple_ids_sorted():
    resolved = {"gnd-2": "gnd-2", "gnd-1": "gnd-1"}

    with (
        patch(
            "utility.linking_utils._resolve_gid",
            side_effect=resolved.__getitem__,
        ),
        patch(
            "utility.linking_utils.warn_multiple_gids",
            side_effect=lambda source, gids, wikidata_id, person, note: sorted(gids),
        ) as warn,
    ):
        result = resolve_old_gids(
            ["gnd-1", "gnd-2"],
            data_source="wikidata",
            wikidata_id="1",
            person_to_search="Ada",
        )

    assert result == ["gnd-1", "gnd-2"]
    warn.assert_called_once()


def test_resolve_old_gids_deduplicates_ids_that_resolve_to_same_gid():
    with patch("utility.linking_utils._resolve_gid", return_value="gnd-1"):
        result = resolve_old_gids(["old-1", "old-2"])

    assert result == ["gnd-1"]


# -------------------------------------------------
# Test parse_person_gnd_response
# -------------------------------------------------
def test_parse_person_gnd_response_normalizes_score_and_label():
    response = {
        "hits": {
            "hits": [
                {
                    "_score": 2.0,
                    "_source": {
                        "gndIdentifier": "g1",
                        "preferredName": "Ada Lovelace",
                    },
                }
            ]
        }
    }
    result = parse_person_gnd_response(response, label="surname")
    assert result["g1"]["score"] == 1.0
    assert result["g1"]["query_label"] == "surname"


# -------------------------------------------------
# Test build_wikidata_query
# -------------------------------------------------
def test_build_wikidata_query_returns_none_for_empty_or_zero_limit():
    assert build_wikidata_query("!!!", "1900") is None
    assert build_wikidata_query("Ada", "1900", wikidata_limit=0) is None


def test_build_wikidata_query_includes_gnd_filter():
    query = build_wikidata_query("Ada Lovelace", "1900", fuzzy=False)
    assert query["size"] == 5
    must = query["query"]["bool"]["must"]
    assert any("should" in clause.get("bool", {}) for clause in must)


# -------------------------------------------------
# Test parse_wikidata_response
# -------------------------------------------------
def test_parse_wikidata_response_single_gid():
    response = {
        "hits": {
            "hits": [
                {
                    "_score": 2.0,
                    "_source": {
                        "id": "Q1",
                        "GND_ID": "g1",
                        "labels": "Ada Lovelace",
                    },
                }
            ]
        }
    }

    with patch("utility.linking_utils.resolve_old_gids", return_value=["g1"]):
        result = parse_wikidata_response(response, label="name")

    assert result["g1"]["score"] == 1.0
    assert result["g1"]["query_label"] == "name"


def test_wikidata_parser_for_malformed_response_empty():
    assert parse_wikidata_response({}) == {}


def test_wikidata_parser_raises_for_malformed_response():
    with pytest.raises(TypeError):
        parse_wikidata_response({"hits": {"hits": None}})


def test_wikidata_parser_raise_for_hits_missing_required_fields():
    with pytest.raises(KeyError):
        parse_wikidata_response(
            {"hits": {"max_score": 1.0, "hits": [{}]}},
        )


def test_parse_wikidata_response_normalizes_shared_multi_gid_candidate_once():
    response = {
        "hits": {
            "hits": [
                {
                    "_score": 2.0,
                    "_source": {
                        "id": "Q1",
                        "GND_ID": ["old-1", "old-2"],
                        "labels": "Ada Lovelace",
                    },
                }
            ]
        }
    }

    with (
        patch(
            "utility.linking_utils.get_preferred_gnd_entry_wikidata",
            return_value=["gnd-1", "gnd-2"],
        ) as preferred_lookup,
        patch(
            "utility.linking_utils.resolve_old_gids",
            return_value=["gnd-1", "gnd-2"],
        ) as resolve_gids,
    ):
        result = parse_wikidata_response(
            response, label="person-name", search_term="Ada Lovelace"
        )

    preferred_lookup.assert_called_once_with("Q1")
    resolve_gids.assert_called_once_with(
        ["gnd-1", "gnd-2"],
        "wikidata",
        "Q1",
        person_to_search="Ada Lovelace",
    )

    assert set(result) == {"gnd-1", "gnd-2"}
    for candidate in result.values():
        assert candidate["gid"] == ["gnd-1", "gnd-2"]
        assert candidate["score"] == 1.0
        assert candidate["name"] == {"Ada Lovelace"}
        assert candidate["query_label"] == "person-name"


def test_parse_wikidata_response_keeps_original_ids_if_preferred_lookup_fails():
    response = {
        "hits": {
            "hits": [
                {
                    "_score": 2.0,
                    "_source": {
                        "id": "Q1",
                        "GND_ID": ["gnd-1", "gnd-2"],
                        "labels": "Ada Lovelace",
                    },
                }
            ]
        }
    }

    with (
        patch(
            "utility.linking_utils.get_preferred_gnd_entry_wikidata",
            return_value=None,
        ) as preferred_lookup,
        patch(
            "utility.linking_utils.resolve_old_gids",
            side_effect=lambda gids, *args, **kwargs: sorted(gids),
        ) as resolve_gids,
    ):
        result = parse_wikidata_response(response)

    preferred_lookup.assert_called_once_with("Q1")
    assert set(resolve_gids.call_args.args[0]) == {"gnd-1", "gnd-2"}
    assert set(result) == {"gnd-1", "gnd-2"}


# -------------------------------------------------
# Test search_person_gnd_variantName
# -------------------------------------------------
def test_search_person_gnd_variant_name_skips_empty_query():
    with (
        patch("utility.linking_utils.build_variant_name_query", return_value=None),
        patch("utility.linking_utils._es_search") as es_search,
    ):
        assert search_person_gnd_variantName("", "1900") == {}
        es_search.assert_not_called()


def test_search_person_gnd_variant_name_calls_search_and_parser():
    with (
        patch(
            "utility.linking_utils.build_variant_name_query", return_value={"query": {}}
        ),
        patch(
            "utility.linking_utils._es_search", return_value={"hits": {}}
        ) as es_search,
        patch(
            "utility.linking_utils.parse_variant_name_response", return_value={"g1": {}}
        ) as parser,
    ):
        assert search_person_gnd_variantName("Ada", "1900", label="name") == {"g1": {}}
        es_search.assert_called_once()
        parser.assert_called_once_with({"hits": {}}, "name", "Ada")


# -------------------------------------------------
# Test _es_search
# -------------------------------------------------
def test_es_search_returns_empty_if_base_url_missing(monkeypatch):
    monkeypatch.setattr(lu.settings.es, "base_url", "")
    assert _es_search("index", {}, {}, "GND") == {}


def test_es_search_returns_json_response(monkeypatch):
    monkeypatch.setattr(lu.settings.es, "base_url", "https://example.test")
    monkeypatch.setattr(lu.settings.es, "index_name_gnd", "gnd", raising=False)
    monkeypatch.setattr(lu.settings, "PATH_TO_CA_CERT", "", raising=False)
    monkeypatch.setattr(lu.settings.es, "username", "user", raising=False)
    monkeypatch.setattr(lu.settings.es, "password", "pass", raising=False)

    response = MagicMock()
    response.json.return_value = {"hits": {"hits": []}}
    with patch("utility.linking_utils._session") as session:
        session.return_value.get.return_value = response
        assert _es_search("gnd", {}, {"query": {}}, "GND") == {"hits": {"hits": []}}
        session.return_value.get.assert_called_once()


def test_es_search_raises_for_invalid_json(monkeypatch):
    monkeypatch.setattr(lu.settings.es, "base_url", "https://example.test")
    monkeypatch.setattr(lu.settings, "PATH_TO_CA_CERT", "", raising=False)
    monkeypatch.setattr(lu.settings.es, "username", "user", raising=False)
    monkeypatch.setattr(lu.settings.es, "password", "pass", raising=False)

    response = MagicMock()
    response.json.side_effect = requests.exceptions.JSONDecodeError(
        "invalid JSON", "not json", 0
    )

    with patch("utility.linking_utils._session") as session:
        session.return_value.get.return_value = response
        with pytest.raises(requests.exceptions.JSONDecodeError):
            _es_search("gnd", {}, {"query": {}}, "GND")


def test_es_search_retries_timeout_with_longer_timeout(monkeypatch):
    monkeypatch.setattr(lu.settings.es, "base_url", "https://example.test")
    monkeypatch.setattr(lu.settings, "PATH_TO_CA_CERT", "", raising=False)
    monkeypatch.setattr(lu.settings.es, "username", "user", raising=False)
    monkeypatch.setattr(lu.settings.es, "password", "pass", raising=False)

    response = MagicMock()
    response.json.return_value = {"hits": {"hits": []}}

    with patch("utility.linking_utils._session") as session:
        session.return_value.get.side_effect = [requests.Timeout(), response]

        result = _es_search("gnd", {}, {"query": {}}, "GND")

    assert result == {"hits": {"hits": []}}
    calls = session.return_value.get.call_args_list
    assert len(calls) == 2

    def timeout_size(timeout):
        return max(timeout) if isinstance(timeout, tuple) else timeout

    assert timeout_size(calls[1].kwargs["timeout"]) > timeout_size(
        calls[0].kwargs["timeout"]
    )


def test_es_search_raises_for_http_error_status(monkeypatch):
    monkeypatch.setattr(lu.settings.es, "base_url", "https://example.test")
    monkeypatch.setattr(lu.settings, "PATH_TO_CA_CERT", "", raising=False)

    response = MagicMock()
    response.raise_for_status.side_effect = requests.HTTPError("400 Bad Request")

    with patch("utility.linking_utils._session") as session:
        session.return_value.get.return_value = response
        with pytest.raises(requests.HTTPError):
            _es_search("gnd", {}, {"query": {}}, "GND")

    response.json.assert_not_called()


def test_es_search_raises_after_two_timeouts(monkeypatch):
    monkeypatch.setattr(lu.settings.es, "base_url", "https://example.test")
    monkeypatch.setattr(lu.settings, "PATH_TO_CA_CERT", "", raising=False)

    with patch("utility.linking_utils._session") as session:
        session.return_value.get.side_effect = [
            requests.Timeout(),
            requests.Timeout(),
        ]
        with pytest.raises(requests.Timeout):
            _es_search("gnd", {}, {"query": {}}, "GND")

    assert session.return_value.get.call_count == 2


def test_es_search_retries_ssl_error(monkeypatch):
    monkeypatch.setattr(lu.settings.es, "base_url", "https://example.test")
    monkeypatch.setattr(lu.settings, "PATH_TO_CA_CERT", "", raising=False)

    response = MagicMock()
    response.json.return_value = {"hits": {"hits": []}}

    with patch("utility.linking_utils._session") as session:
        session.return_value.get.side_effect = [
            requests.exceptions.SSLError(),
            response,
        ]
        assert _es_search("gnd", {}, {"query": {}}, "GND") == {"hits": {"hits": []}}

    assert session.return_value.get.call_count == 2


# -------------------------------------------------
# Test parse_person_gnd_response, parse_variant_name_response, parse_wikidata_response
# -------------------------------------------------
@pytest.mark.parametrize(
    "parser,response_args",
    [
        (parse_person_gnd_response, {"label": "surname"}),
        (
            parse_variant_name_response,
            {"label": "surname", "search_term": "Lovelace"},
        ),
        (parse_wikidata_response, {}),
    ],
)
def test_parsers_return_empty_result_for_no_hits(parser, response_args):
    assert parser({"hits": {"hits": []}}, **response_args) == {}


@pytest.mark.parametrize(
    "parser,hit,response_args",
    [
        (
            parse_person_gnd_response,
            {"_score": 0.0, "_source": {"gndIdentifier": "g1"}},
            {"label": "surname"},
        ),
        (
            parse_variant_name_response,
            {"_score": 0.0, "_source": {"gndIdentifier": "g1"}},
            {"label": "surname", "search_term": "Lovelace"},
        ),
        (
            parse_wikidata_response,
            {
                "_score": 0.0,
                "_source": {"id": "Q1", "GND_ID": "g1", "labels": "Ada"},
            },
            {},
        ),
    ],
)
def test_parsers_handle_zero_max_score(parser, hit, response_args):
    response = {"hits": {"hits": [hit]}}
    result = parser(response, **response_args)
    assert result["g1"]["score"] == 0.0


@pytest.mark.parametrize(
    "parse_func,hit,args",
    [
        (parse_person_gnd_response, {}, {}),
        (parse_variant_name_response, {}, {"search_term": "Lovelace"}),
    ],
)
def test_gnd_parsers_log_malformed_hit_and_return_empty(parse_func, hit, args, caplog):
    response = {"hits": {"max_score": 1.0, "hits": [hit]}}
    with caplog.at_level("ERROR"):
        result = parse_func(response, **args)

    assert result == {}
    assert any(record.levelname == "ERROR" for record in caplog.records)
