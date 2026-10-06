"""
Utility functions for finding candidates via ElasticSearch
"""

import os
import threading
import unicodedata
import requests
import re
import logging
from utility.settings import settings
from pathlib import Path

# Lastname Prefix GND
BASE_DIR = Path(__file__).resolve().parent
with open(BASE_DIR / "gnd_prefix_lastnames.txt", "r", encoding="utf-8") as f:
    PREFIX = set(f.read().splitlines())

# Compiled once, at import. There are ~1178 prefixes and Python's regex cache
# holds 512, so building these patterns inside the per-lastname loop evicted
# every one of them before it could be reused: each lastname recompiled the
# whole list. Iteration order follows PREFIX, so which prefix wins is unchanged.
PREFIX_PATTERNS = [(prefix, re.compile("(^" + prefix + ")")) for prefix in PREFIX]

# One session per thread and per process, rather than one shared module-level
# session: linking runs under a process Pool over magazine-years and a thread
# pool over persons, and a socket inherited across fork would be used by parent
# and child at once.
_sessions = threading.local()

# Knowledge-base entries carrying several GND ids are a property of the entry,
# not of the mention that found it, so the same handful reappear for thousands
# of mentions. Reported once each per process instead.
_reported_multi_gid: set = set()


def warn_multiple_gids(source: str, gids: set, wikidata_id: str, person_to_search: str, note: str = "") -> list:
    """
    Reports a knowledge-base entry holding more than one GND id, once per entry.
    Sorts the gids so the results are fixed but arbitrary and returns said list.

    :param source: Index the entry came from, for example "Wikidata".
    :type source: str
    :param gids: The GND ids found on the entry.
    :type gids: set
    :param wikidata_id: Wikidata id if the source is Wikidata.
    :type wikidata_id: str
    :param person_to_search: The person name we searched for on ES.
    :type person_to_search: str
    :param note: Sentence appended to the message, defaults to "".
    :type note: str
    :return: A sorted list of GND-IDs.
    :rtype: list
    """

    key = frozenset(gids)
    # Sorted so the same entry reads the same way from run to run; iterating a
    # set of ids would order the message differently each time.
    sorted_gids = sorted(gids)
    if key not in _reported_multi_gid:
        _reported_multi_gid.add(key)
        if wikidata_id is not None:
            source = source + " " + wikidata_id
        logging.warning(
            f"{source} entry for {person_to_search} with multiple GND IDs: {sorted_gids}."
            + (f" {note}" if note else "")
        )
    return sorted_gids


def _session() -> requests.Session:
    """
    Returns this thread's Elasticsearch session, creating it if needed.

    :return: A session whose connections are safe to reuse here.
    :rtype: requests.Session
    """

    pid = os.getpid()
    session = getattr(_sessions, "session", None)
    if session is None or getattr(_sessions, "pid", None) != pid:
        session = requests.Session()
        retries = requests.adapters.Retry(
            total=20,
            connect=5,
            read=5,
            backoff_factor=1,
            status_forcelist=[500, 502, 503, 504],
        )
        session.mount("http://", requests.adapters.HTTPAdapter(max_retries=retries))
        # The cluster is reached over https; mounting only http left the
        # retrying adapter unused.
        session.mount("https://", requests.adapters.HTTPAdapter(max_retries=retries))
        _sessions.session = session
        _sessions.pid = pid
    return session


def clean_namestring(name: str) -> str:
    punct = '!"#$%&\'()*+,/:;<=>?@[\\]^_`{|}~'  # without period, dash
    name = unicodedata.normalize("NFC", name)

    # Replace everything except periods
    name = name.translate(str.maketrans("", "", punct))
    name = re.sub(r"ß", "ss", name)

    # Then check for the "correct" periods to replace with wildcard
    name = re.sub(r"(?<=\w)\.(?=[{\W}]|(?!.)|[a-zA-Z](\s|\.))", "*", name)

    # Then replace remaining periods
    name = re.sub(r"\.", "", name)

    # Replace dashes if not part of a name
    name = re.sub(r"-(?![A-Za-z]{2})|(?<![A-Za-z]{2})-", "", name)

    return name.strip()


def prep_name_for_elasticsearch_query(name: str) -> str:
    """
    Specify allowed edit distance for each word of a name
    for the elasticsearch fuzzy search functionality.

    This is based on their fuzziness:auto implementation, and depends
    on the length of the word. We do not allow more than 2 edits per word.

    :param name: Name to be searched.
    :type name: str
    :return: Name to be searched including allowed edit distances.
    :rtype: str
    :Example:
        >>> "D. Birchall" => "D* Birchall~2"
        >>> "J.P. Wittbach => J*P* Wittbach~2"
    """

    name_list = name.split(" ")
    name_list = [x for x in name_list if x != ""]
    # our own fuzziness:auto implementation
    for it, st in enumerate(name_list):
        if st[-1] == "*":
            continue
        else:
            if len(st) < 3:
                name_list[it] = name_list[it] + "~0"
            elif len(st) < 6:
                name_list[it] = name_list[it] + "~1"
            else:
                name_list[it] = name_list[it] + "~2"
    name = " ".join(name_list)
    return name


def convert_dates_wikidata(wikidata_date: str) -> str:
    """
    Throws away time part of wikidata date format.

    :param wikidata_date: Date in wikidata format.
    :type wikidata_date: str
    :return: Date in YYYY-MM-DD format.
    :rtype: str

    Example
    ::
    "+1796-10-16T00:00:00Z" => "1796-10-16"
    """

    date = wikidata_date.strip("+").split("T")[0]
    return date


def _safe_set(value) -> set:
    """
    Convert value to a set and remove None values.

    :param value: Value to convert (list, tuple, or single value)
    :return: Set with None values removed
    :rtype: set
    """
    if isinstance(value, (list, tuple)):
        return set(value) - {None}
    return {value} - {None}


def convert_wikidata_format_kibana(person_dict: dict) -> dict:
    """
    Convert the output dictionary we get from wikidata into
    the dictionary we use for the rest of the pipeline.

    :param person_dict: Dictionary containing various information\
        on a person entity.
    :type person_dict: dict
    :return: Dictionary containing various information on a person\
        entity in our own format.
    :rtype: dict
    """

    res_dict = {}

    # Handle simple set fields
    if "descriptions" in person_dict:
        res_dict["desc"] = _safe_set([person_dict["descriptions"]])
    if "placeOfBirth" in person_dict:
        res_dict["birthplaceLiteral"] = _safe_set(person_dict["placeOfBirth"])
    if "placeOfDeath" in person_dict:
        res_dict["deathplaceLiteral"] = _safe_set(person_dict["placeOfDeath"])
    if "occupation" in person_dict:
        res_dict["jobliteral"] = _safe_set(person_dict["occupation"])
    if "nickname" in person_dict:
        res_dict["varForename"] = _safe_set(person_dict["nickname"])

    # Handle preferred names
    if "birthname" in person_dict:
        res_dict.setdefault("prefVarName", set()).update(_safe_set(person_dict["birthname"]))
    if "givenName" in person_dict:
        res_dict.setdefault("prefForename", set()).update(_safe_set(person_dict["givenName"]))
    if "familyName" in person_dict:
        res_dict.setdefault("prefSurname", set()).update(_safe_set(person_dict["familyName"]))

    # Handle dates
    if "dateOfBirth" in person_dict and person_dict["dateOfBirth"]:
        res_dict["birthdate"] = _safe_set([convert_dates_wikidata(person_dict["dateOfBirth"][0])])
    if "dateOfDeath" in person_dict and person_dict["dateOfDeath"]:
        res_dict["deathdate"] = _safe_set([convert_dates_wikidata(person_dict["dateOfDeath"][0])])

    # Handle GND IDs
    if "GND_ID" in person_dict:
        res_dict.setdefault("gid", set()).update(_safe_set(person_dict["GND_ID"]))
    if "GND_ID_2" in person_dict:
        res_dict.setdefault("gid", set()).update(_safe_set(person_dict["GND_ID_2"]))

    # Handle labels and derive names if needed
    if "labels" in person_dict:
        res_dict["name"] = _safe_set([person_dict["labels"]])
        for fullname in res_dict["name"]:
            if "prefSurname" not in res_dict:
                res_dict["prefSurname"] = set([fullname.split(" ")[-1]])
            if "prefForename" not in res_dict:
                res_dict["prefForename"] = set([" ".join(fullname.split(" ")[:-1])])

    return res_dict


def convert_gnd_format_kibana(person_dict: dict) -> dict:
    """
    Convert the output dictionary we get from the gnd ES index
    into the dictionary we use for the rest of the pipeline.

    :param person_dict: Dictionary containing various information\
        on a person entity.
    :type person_dict: dict
    :return: Dictionary containing various information on a person\
        entity in our own format.
    :rtype: dict
    """

    res_dict = {}
    fullname = ""

    # Handle preferred name
    if "preferredNameEntityForThePerson" in person_dict:
        pref_name = person_dict["preferredNameEntityForThePerson"]
        if "forename" in pref_name:
            res_dict.setdefault("prefForename", set()).update(pref_name["forename"])
            fullname += " ".join(pref_name["forename"])
        if "surname" in pref_name:
            res_dict.setdefault("prefSurname", set()).update(pref_name["surname"])
            fullname += ", " + " ".join(pref_name["surname"])

    if "preferredName" in person_dict:
        fullname = person_dict["preferredName"]

    # Handle simple set fields
    if "biographicalOrHistoricalInformation" in person_dict:
        res_dict["desc"] = _safe_set(person_dict["biographicalOrHistoricalInformation"])
    if "placeOfBirth" in person_dict and "label" in person_dict["placeOfBirth"]:
        res_dict["birthplaceLiteral"] = _safe_set(person_dict["placeOfBirth"]["label"])
    if "placeOfDeath" in person_dict and "label" in person_dict["placeOfDeath"]:
        res_dict["deathplaceLiteral"] = _safe_set(person_dict["placeOfDeath"]["label"])
    if "professionOrOccupation" in person_dict and "label" in person_dict["professionOrOccupation"]:
        res_dict["jobliteral"] = _safe_set(person_dict["professionOrOccupation"]["label"])
    if "academicDegree" in person_dict:
        res_dict["academic"] = set(person_dict["academicDegree"])
    if "periodOfActivity" in person_dict:
        res_dict["activeperiod"] = set(person_dict["periodOfActivity"])
    if "affiliation" in person_dict and "label" in person_dict["affiliation"]:
        res_dict["affiliationLiteral"] = set(person_dict["affiliation"]["label"])

    # Handle variant names
    if "variantNameEntityForThePerson" in person_dict:
        var_name = person_dict["variantNameEntityForThePerson"]
        if "forename" in var_name:
            res_dict["varForename"] = _safe_set(var_name["forename"])
        if "nameAddition" in var_name:
            res_dict["varSurname"] = _safe_set(var_name["nameAddition"])
        if "surname" in var_name:
            res_dict["varSurname"] = _safe_set(var_name["surname"])
    if "variantName" in person_dict:
        res_dict["varName"] = _safe_set(person_dict["variantName"])

    # Handle dates
    if "dateOfBirth" in person_dict:
        res_dict["birthdate"] = _safe_set([person_dict["dateOfBirth"][0]])
    if "dateOfDeath" in person_dict:
        res_dict["deathdate"] = _safe_set(person_dict["dateOfDeath"])

    # Handle GND ID
    if "gndIdentifier" in person_dict:
        res_dict["gid"] = _safe_set([person_dict["gndIdentifier"]])

    return res_dict


def _es_search(index_name: str, headers: dict, json_data: dict, error_label: str) -> dict:
    """
    Executes an ElasticSearch query against the given index.

    Retries once with a longer timeout on a plain timeout, and once more
    via the shared `sess` session on an SSL error.

    :param index_name: Name of the ES index to query, e.g.\
        settings.es.index_name_gnd.
    :type index_name: str
    :param headers: Request headers.
    :type headers: dict
    :param json_data: The ES query body.
    :type json_data: dict
    :param error_label: Short label used in log messages, e.g. "GND" or\
        "Wikidata".
    :type error_label: str
    :return: Parsed JSON response from ElasticSearch, or {} if the\
        base_url isn't configured or every attempt failed.
    :rtype: dict

    :raises requests.exceptions.Timeout: If all queries time out.
    """

    if not settings.es.base_url:
        logging.error("Elasticsearch base_url is not set in settings!")
        return {}

    url = settings.es.base_url + "/" + index_name + "/_search?pretty"
    auth = (settings.es.username, settings.es.password)

    session = _session()
    try:
        data = session.get(url, headers=headers, json=json_data,
                           verify=settings.PATH_TO_CA_CERT, auth=auth, timeout=5)
    except requests.exceptions.Timeout:
        logging.warning(f"{error_label} ES Query timed out.")
        try:
            data = session.get(url, headers=headers, json=json_data,
                               verify=settings.PATH_TO_CA_CERT, auth=auth, timeout=5)
        except requests.exceptions.Timeout:
            logging.error(f"{error_label} ES query timeout. No more retries.")
            logging.info(f"Query: {json_data}")
            raise
    except requests.exceptions.SSLError:
        logging.warning(f"SSL error {error_label}")
        try:
            data = session.get(url, headers=headers, json=json_data,
                               verify=settings.PATH_TO_CA_CERT, auth=auth, timeout=5)
        except requests.exceptions.Timeout:
            logging.error(f"{error_label} ES SSL Error timeout. No more retries.")
            logging.info(f"Query: {json_data}")
            raise
    return data.json()


def _alive_before_year_filter(year: str) -> dict:
    """
    Builds the ES filter clause matching entities with no known dateOfBirth,
    or with a dateOfBirth strictly before `year`.

    Used to exclude candidates who could not plausibly be mentioned in a
    document published in that year.

    :param year: Year the magazine was published in.
    :type year: str
    :return: The bool/should filter clause.
    :rtype: dict
    """

    return {
        "bool": {
            "minimum_should_match": 1,
            "should": [
                {
                    "bool": {
                        "must_not": {
                            "bool": {
                                "should": [
                                    {"exists": {"field": "dateOfBirth"}}
                                ],
                            }
                        }
                    }
                },
                {
                    "bool": {
                        "should": [
                            {"range": {"dateOfBirth": {"lt": year + "||/y"}}}
                        ]
                    }
                }
            ],
        }
    }


def build_variant_name_query(
    fullname: str, year: str, gnd_limit=15, fuzzy=True
) -> dict | None:
    """
    Builds the Elasticsearch body for a variant-name person search.

    :param fullname: Full name of the person to search
    :type fullname: str
    :param year: Year this magazine was published in
    :type year: str
    :param gnd_limit: Number of results, defaults to 15
    :type gnd_limit: int, optional
    :param fuzzy: Whether to search for the names including some edits
    :type fuzzy: bool, optional
    :return: The query body, or None when cleaning left nothing to
        search for, or there is no room for results.
    :rtype: dict | None
    """

    if gnd_limit == 0:
        return None

    fullname = clean_namestring(fullname)
    if fullname == "":
        return None

    if fuzzy:
        fullname_wildcard = "*"+fullname+"*"
        fullname_fuzzy = prep_name_for_elasticsearch_query(fullname)
    else:
        fullname_wildcard = fullname
        fullname_fuzzy = fullname


    json_data = {
            "_source": ["gndIdentifier", "variantName"],
            "from": 0,
            "size": gnd_limit,
            "sort": [
                { "_score": "desc" },
                { "gndIdentifier.keyword": "asc" }
            ],
            "query": {
                "bool": {
                    "must": [
                        _alive_before_year_filter(year),
                        {
                            "bool": {
                                "should": [
                                    {
                                        "wildcard": {
                                            "variantName.keyword": {
                                                "value": fullname_wildcard,
                                                "case_insensitive": "true"
                                            }
                                        }
                                    },
                                    {
                                        "query_string": {
                                            "query": fullname_fuzzy,
                                            "default_field": "variantName",
                                            "default_operator": "and",
                                            "analyze_wildcard": "true"
                                        }
                                    }
                                ],
                                "minimum_should_match": 1
                            }
                        }
                    ],
                },
            }
        }
    return json_data


def parse_variant_name_response(result_json: dict, label: str = "", search_term: str = "") -> dict:
    """
    Turns one variant-name response into candidates, keyed by gnd id.

    Scores are scaled to the top hit of this response, which is what makes
    them comparable with scores from a different index.

    :param result_json: One decoded Elasticsearch response.
    :type result_json: dict
    :param label: Name of the query these hits answer, carried onto each
        candidate for the scorer. Omitted when the caller named no query.
    :type label: str
    :param search_term: The search term for the ES query.
    :type search_term: str
    :return: Dictionary of each viable candidate, keyed by gnd id.
    :rtype: dict
    """

    res_candidates = {}
    if len(result_json) == 0:
        return {}
    try:
        max_score = 0
        for hit in result_json["hits"]["hits"]:
            # score is at hit["_score"]
            person_info = convert_gnd_format_kibana(hit["_source"])
            if "gid" in person_info and len(person_info["gid"]) != 0:
                # NOTE: This should never be degenerate better to put a hard check here
                if len(person_info["gid"]) > 1:
                    person_info["gid"] = resolve_old_gids(person_info["gid"], "GND", person_to_search=search_term)
                    
                gid = person_info["gid"].pop()
                person_info["gid"] = {gid}
                person_info["score"] = hit["_score"]
                if person_info["score"] > max_score:
                    max_score = person_info["score"]
                # Which query found this candidate. Carried with the hit and not
                # read here; the scorer uses it to place the candidate. Absent when
                # the caller named no query, so an unlabelled call is unchanged.
                if label:
                    person_info["query_label"] = label
                res_candidates[gid] = person_info
    except Exception:
        logging.error("This query caused an exception: "+str(result_json))
        return {}
    # to make scores across different indexes comparable
    # scale them to 1
    for per_dict in res_candidates.values():
        per_dict["score"] = per_dict["score"]/max_score
    return res_candidates


def search_person_gnd_variantName(
    fullname: str, year: str, gnd_limit=15, fuzzy=True, label: str = ""
) -> dict:
    """
    We search for this fullname in our elasticsearch GND index.
    We return at most `gnd_limit` results.

    :param fullname: Full namestring of the person to search
    :type fullname: str
    :param year: Year this magazine was published in
    :type year: str
    :param gnd_limit: Number of results, defaults to 15
    :type gnd_limit: int, optional
    :param fuzzy: Whether to search for the names including some edits, defaults to True
    :type fuzzy: bool, optional
    :return: Dictionary of each viable candidate where the keys are the\
        gnd ids.
    :rtype: dict
    """

    json_data = build_variant_name_query(fullname, year, gnd_limit, fuzzy)
    if json_data is None:
        return {}

    headers = {"Content-Type": "application/json"}
    result_json = _es_search(settings.es.index_name_gnd, headers, json_data, "GND")
    return parse_variant_name_response(result_json, label, fullname)


def build_person_gnd_query(
    fnames: list, lastname: str, year: str, gnd_limit=15, fuzzy=True
) -> dict | None:
    """
    Builds the Elasticsearch body for a preferred-name person search.

    :param fnames: List of firstnames of the person to search
    :type fnames: list
    :param lastname: Lastname of the person to search
    :type lastname: str
    :param year: Year this magazine was published in
    :type year: str
    :param gnd_limit: Number of results, defaults to 15
    :type gnd_limit: int, optional
    :param fuzzy: Whether to search for the names including some edits
    :type fuzzy: bool, optional
    :return: The query body, or None when there is nothing worth asking for:
        no room for results, or a lastname that cleaning left empty.
    :rtype: dict | None
    """

    if gnd_limit == 0:
        return None

    if isinstance(fnames, list):
        # should even throw an exception, but I'll be nice
        fnames = " ".join(fnames)
    fnames = clean_namestring(fnames)
    if fuzzy:
        fnames = prep_name_for_elasticsearch_query(fnames)
    if fnames == "":
        fnames = "*"

    lastname = clean_namestring(lastname)
    # if after cleaning the lastname is empty, do not search
    if lastname == "":
        return None

    # If the lastname contains a prefix, split it off and search for it
    # in its own field; otherwise just clean/prep the lastname as usual.
    prefix = None
    for p, prefix_pattern in PREFIX_PATTERNS:
        split_lname = prefix_pattern.split(lastname)
        if len(split_lname) > 1:
            split_lname = [x.strip() for x in split_lname if x != ""]
            if len(split_lname) != 2:
                logging.warning(f"lastname {lastname} split by {p} splits it into more than len two {split_lname}")
                break
            if fuzzy:
                lastname = prep_name_for_elasticsearch_query(split_lname[1])
                prefix = prep_name_for_elasticsearch_query(split_lname[0])
            else:
                lastname = split_lname[1]
                prefix = split_lname[0]
            break

    if not prefix and fuzzy:
        lastname = prep_name_for_elasticsearch_query(lastname)

    must_clauses = [
        _alive_before_year_filter(year),
        {
            "query_string": {
                "default_field": "preferredNameEntityForThePerson.forename",
                "query": fnames,
                "default_operator": "and",
                "analyze_wildcard": "true"
            }
        },
        {
            "query_string": {
                "default_field": "preferredNameEntityForThePerson.surname",
                "query": lastname,
                "default_operator": "and",
                "analyze_wildcard": "true"
            }
        },
    ]

    if prefix is not None:
        must_clauses.append({
            "query_string": {
                "default_field": "preferredNameEntityForThePerson.prefix",
                "query": prefix,
                "default_operator": "and",
                "analyze_wildcard": "true"
            }
        })

    json_data = {
        "_source": ["gndIdentifier",
                    "preferredNameEntityForThePerson"],
        "from": 0,
        "size": gnd_limit,
        "sort": [{"_score": "desc"}, {"gndIdentifier.keyword": "asc"}],
        "query": {
            "bool": {
                "must": must_clauses,
            },
        }
    }

    return json_data

from functools import lru_cache

@lru_cache(maxsize=4096)
def _preferred_gids(wikidata_id: str) -> list:
    """
    Cache successfull results
    """
    # wdt: prefix makes sure only the preferred ranked entries are returned.
    req = _session().get(
        "https://query.wikidata.org/sparql",
        params={
            "query": f"""SELECT ?gndId WHERE {{
                VALUES ?gndProp {{wdt:P227 wdt:P7902 }}
                wd:{wikidata_id} ?gndProp ?gndId .}}
                GROUP BY ?gndId""",
            "format": "json",
        },
        headers={
            "User-Agent": "GND-Wikidata-resolver/1.0 (https://github.com/rashitig/gnd-wikidata-resolver; 6xchepfl0@mozmail.com)",
            "Accept": "application/sparql-results+json",
        },
        timeout=60,
    )
    req.raise_for_status()
    return [b["gndId"]["value"] for b in req.json()["results"]["bindings"]]


@lru_cache(maxsize=16384)
def _resolve_gid(gnd_id: str) -> str:
    req = requests.get(
        f"https://lobid.org/gnd/{gnd_id}.json",
        allow_redirects=False,
        headers={"Range": "bytes=0-0"},
        timeout=60,
    )

    if req.is_redirect:
        location = req.headers.get("Location", "")
        resolved = location.rstrip("/").split("/")[-1].split("?")[0]
        if resolved:
            return resolved
        raise requests.HTTPError("LOBID redirect has no usable Location", response=req)

    if not 200 <= req.status_code < 300:
        req.raise_for_status()  # Raises for 4xx/5xx.
        raise requests.HTTPError(
            f"Unexpected LOBID status: {req.status_code}", response=req
        )

    return gnd_id

def get_preferred_gnd_entry_wikidata(wikidata_id, session):
    """Gets the preferred gnd entry for the given wikidata id.
    We only do this if there are several gnd_ids associated
    with a wikidata id.

    Args:
        query (_type_): _description_

    Returns:
        _type_: _description_

    Raises:
    """
    try:
        return _preferred_gids(wikidata_id)
    except requests.RequestException as e:
        logging.error(f"Error accessing Wikidata endpoint: {e}")
    except requests.JSONDecodeError as e:
        logging.error(f"Error decoding JSON: {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
    return None


def resolve_old_gids(gids_list, data_source=None, wikidata_id=None, person_to_search=None):
    gids_list_out = []
    for gnd_id in gids_list:
        try:
            new_gnd_id = _resolve_gid(gnd_id)
            if new_gnd_id not in gids_list_out:
                gids_list_out.append(new_gnd_id)
        except requests.RequestException as e:
            logging.error(f"Error accessing LOBID endpoint: {e}")
            if gnd_id not in gids_list_out:
                gids_list_out.append(gnd_id)
        except Exception as e:
            logging.error(f"An unexpected error occurred: {e}")
            if gnd_id not in gids_list_out:
                gids_list_out.append(gnd_id)

    if len(gids_list_out) > 1:
        gids_list_out = warn_multiple_gids(data_source, gids_list_out, wikidata_id, person_to_search, "An arbitrary one is selected.")
    return gids_list_out


def parse_person_gnd_response(result_json: dict, label: str = "", search_term: str = "") -> dict:
    """
    Turns one GND response into candidates, keyed by gnd id.

    Scores are scaled to the top hit of this response, which is what makes
    them comparable with scores from a different index.

    :param result_json: One decoded Elasticsearch response.
    :type result_json: dict
    :param label: Name of the query these hits answer, carried onto each
        candidate for the scorer. Omitted when the caller named no query.
    :type label: str
    :param search_term: The search term for the ES query.
    :type search_term: str
    :return: Dictionary of each viable candidate, keyed by gnd id.
    :rtype: dict
    """

    res_candidates = {}
    if len(result_json) == 0:
        return {}
    try:
        max_score = 0
        for hit in result_json["hits"]["hits"]:
            # score is at hit["_score"]
            person_info = convert_gnd_format_kibana(hit["_source"])
            if "gid" in person_info and len(person_info["gid"]) != 0:
                # NOTE: This should never be degenerate better to put a hard check here
                if len(person_info["gid"]) > 1:
                    person_info["gid"] = resolve_old_gids(person_info["gid"], "GND", person_to_search=search_term)

                gid = person_info["gid"].pop()
                person_info["gid"] = {gid}
                person_info["score"] = hit["_score"]
                if person_info["score"] > max_score:
                    max_score = person_info["score"]
                # Which query found this candidate. Carried with the hit and not
                # read here; the scorer uses it to place the candidate. Absent when
                # the caller named no query, so an unlabelled call is unchanged.
                if label:
                    person_info["query_label"] = label
                res_candidates[gid] = person_info
    except Exception:
        logging.error("This query caused an exception: "+str(result_json))
        return {}
    # to make scores across different indexes comparable
    # scale them to 1
    for per_dict in res_candidates.values():
        per_dict["score"] = per_dict["score"]/max_score

    return res_candidates


def search_person_gnd(
    fnames: list, lastname: str, year: str, gnd_limit=15, fuzzy=True, label: str = ""
) -> dict:
    """
    We search for this firstnames lastname in our elasticsearch GND index.
    We return at most `gnd_limit` results.

    :param fnames: List of firstnames of the person to search
    :type fnames: list
    :param lastname: Lastname of the person to search
    :type lastname: str
    :param year: Year this magazine was published in
    :type year: str
    :param gnd_limit: Number of results, defaults to 15
    :type gnd_limit: int, optional
    :param fuzzy: Whether to search for the names including some edits, defaults to True
    :type fuzzy: bool, optional
    :return: Dictionary of each viable candidate where the keys are the\
        gnd ids.
    :rtype: dict
    """

    json_data = build_person_gnd_query(fnames, lastname, year, gnd_limit, fuzzy)
    if json_data is None:
        return {}

    headers = {"Content-Type": "application/json"}
    result_json = _es_search(settings.es.index_name_gnd, headers, json_data, "GND")
    return parse_person_gnd_response(result_json, label, " ".join(fnames)+" "+lastname)


def build_wikidata_query(
    search_term: str, year: str, wikidata_limit=5, fuzzy=True
) -> dict | None:
    """
    Builds the Elasticsearch body for a Wikidata label search.

    :param search_term: Full name of the person to search
    :type search_term: str
    :param year: Year this magazine was published in
    :type year: str
    :param wikidata_limit: Number of results, defaults to 5
    :type wikidata_limit: int, optional
    :param fuzzy: Whether to search for the names including some edits
    :type fuzzy: bool, optional
    :return: The query body, or None when cleaning left nothing to
        search for, or there is no room for results.
    :rtype: dict | None
    """

    if wikidata_limit == 0:
        return None
    search_term = clean_namestring(search_term)
    # if after cleaning the search term is empty, do not search
    if search_term == "":
        return None

    if fuzzy:
        search_term = prep_name_for_elasticsearch_query(search_term)


    json_data = {
        "_source": ["GND_ID", "GND_ID_2", "labels", "id"],
        "from": 0,
        "size": wikidata_limit,
        "sort": [
            { "_score": "desc" },
            { "GND_ID.keyword": "asc" },
            { "GND_ID_2.keyword": "asc" }
        ],
        "query": {
            "bool": {
                "must": [
                    _alive_before_year_filter(year),
                    {
                        "bool": {
                            "minimum_should_match": 1,
                            "should": [
                                {"exists": {"field": "GND_ID"}},
                                {"exists": {"field": "GND_ID_2"}}
                            ]
                        }
                    },
                    {
                        "query_string": {
                            "default_field": "labels",
                            "query": search_term,
                            "default_operator": "and",
                            "analyze_wildcard": "true"
                        }
                    },
                ],
            }
        }
    }
    return json_data


def parse_wikidata_response(result_json: dict, label: str = "", search_term: str = "") -> dict:
    """
    Turns one Wikidata response into candidates, keyed by gnd id.

    An entry carrying several gnd ids is registered under each of them and
    scaled only once, so the shared score is not divided twice.

    Scores are scaled to the top hit of this response, which is what makes
    them comparable with scores from a different index.

    :param result_json: One decoded Elasticsearch response.
    :type result_json: dict
    :param label: Name of the query these hits answer, carried onto each
        candidate for the scorer. Omitted when the caller named no query.
    :type label: str
    :param search_term: The search term for the ES query.
    :type search_term: str
    :return: Dictionary of each viable candidate, keyed by gnd id.
    :rtype: dict
    """

    res_candidates = {}
    if len(result_json) == 0:
        return {}
    max_score = 0
    session = _session()
    for hit in result_json["hits"]["hits"]:
        if "GND_ID" in hit["_source"] or "GND_ID_2" in hit["_source"]:
            wikidata_id = hit["_source"]["id"]
            person_info = convert_wikidata_format_kibana(hit["_source"])

            if "gid" in person_info and len(person_info["gid"]) != 0:
                person_info["score"] = hit["_score"]
                if len(person_info["gid"]) > 1:
                    pref_gnds = get_preferred_gnd_entry_wikidata(wikidata_id, session)
                    if pref_gnds:
                        person_info["gid"] = pref_gnds
                    if len(person_info["gid"]) > 1:
                        person_info["gid"] = resolve_old_gids(person_info["gid"], "wikidata", wikidata_id, person_to_search=search_term)
                for gid in person_info["gid"]:
                    # sometimes one entity is assigned several gids.
                    # this unfortunately breaks a lot of what we did logically
                    # but this cannot be fixed on our end.
                    # Which query found this candidate. Carried with the hit and not
                    # read here; the scorer uses it to place the candidate. Absent when
                    # the caller named no query, so an unlabelled call is unchanged.
                    if label:
                        person_info["query_label"] = label
                    res_candidates.setdefault(gid, person_info)
                    if person_info["score"] > max_score:
                        max_score = person_info["score"]

    # to make scores across different indexes comparable scale them to 1
    normalized_gids = set()
    for gid, per_dict in res_candidates.items():
        if gid in normalized_gids:
            continue
        normalized_gids.update(per_dict["gid"])
        per_dict["score"] = per_dict["score"] / max_score

    return res_candidates


def search_person_wikidata(search_term: str, year: str, wikidata_limit=5, fuzzy=True,
                           label: str = "") -> dict:
    """
    We search for this firstnames lastname in our elasticsearch
    Wikidata index. We return at most `wikidata_limit` results.

    :param search_term: first- and lastname of the person to search.
    :type search_term: str
    :param year: year this magazine was published in.
    :type year: str
    :param wikidata_limit: Number of results, defaults to 5
    :type wikidata_limit: int, optional
    :param fuzzy: Whether to search for the names including some edits, defaults to True
    :type fuzzy: bool, optional
    :return: Dictionary of each viable candidate where the keys are the\
        gnd ids.
    :rtype: dict
    """

    json_data = build_wikidata_query(search_term, year, wikidata_limit, fuzzy)
    if json_data is None:
        return {}

    headers = {"Content-Type": "application/json"}
    result_json = _es_search(settings.es.index_name_wikidata, headers, json_data, "Wikidata")
    return parse_wikidata_response(result_json, label, search_term)
