"""
Utility functions for finding candidates via ElasticSearch
"""
import unicodedata
import requests
import re
import logging

# Lastname Prefix GND
with open("utility/gnd_prefix_lastnames.txt", "r", encoding="utf-8") as f:
    PREFIX = set(f.read().splitlines())

# ES sessions
sess = requests.Session()
adapter = requests.adapters.HTTPAdapter(max_retries=20)
sess.mount('http://', adapter)

from utility.settings import settings


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

    # Handle dates
    if "dateOfBirth" in person_dict:
        res_dict["birthdate"] = _safe_set([person_dict["dateOfBirth"][0]])
    if "dateOfDeath" in person_dict:
        res_dict["deathdate"] = _safe_set(person_dict["dateOfDeath"])

    # Handle GND ID
    if "gndIdentifier" in person_dict:
        res_dict["gid"] = _safe_set([person_dict["gndIdentifier"]])

    return res_dict


def search_person_gnd(fnames: list, lastname: str, year: str, gnd_limit=15, fuzzy=True) -> dict:
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

    if gnd_limit == 0:
        return {}

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
        return {}

    headers = {"Content-Type": "application/json"}

    # If the lastname contains a prefix, split it
    found_prefix = False
    for p in PREFIX:
        split_lname = re.split("(^"+p+")", lastname)
        if len(split_lname) > 1:
            found_prefix = True
            split_lname = [x.strip() for x in split_lname if x != ""]
            if len(split_lname) != 2:
                logging.warning(f"lastname {lastname} split by {p} splits it into more than len two {split_lname}")
                found_prefix = False
                break
            if fuzzy:
                lastname = prep_name_for_elasticsearch_query(split_lname[1])
                prefix = prep_name_for_elasticsearch_query(split_lname[0])
            else:
                lastname = split_lname[1]
                prefix = split_lname[0]
            json_data = {
                "_source": ["gndIdentifier"],
                "from": 0,
                "size": gnd_limit,
                "query": {
                    "bool": {
                        "must": [
                            {
                                "bool": {
                                    "minimum_should_match": 1,
                                    "should": [
                                        {
                                            "bool": {
                                                "must_not": {
                                                    "bool": {
                                                        "should": [
                                                            {
                                                                "exists": {
                                                                    "field": "dateOfBirth"
                                                                }
                                                            }
                                                        ],
                                                    }
                                                }
                                            }
                                        },
                                        {
                                            "bool": {
                                                "should": [
                                                    {
                                                        "range": {
                                                            "dateOfBirth": {
                                                                "lt": year+"||/y"
                                                            }
                                                        }
                                                    }
                                                ]
                                            }
                                        }
                                    ],
                                }
                            },
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
                            {
                                "query_string": {
                                    "default_field": "preferredNameEntityForThePerson.prefix",
                                    "query": prefix,
                                    "default_operator": "and",
                                    "analyze_wildcard": "true"
                                }
                            }
                        ],
                    },
                }
            }
            break

    if not found_prefix:
        if fuzzy:
            lastname = prep_name_for_elasticsearch_query(lastname)
        json_data = {
            "_source": ["gndIdentifier"],
            "from": 0,
            "size": gnd_limit,
            "query": {
                "bool": {
                    "must": [
                        {
                            "bool": {
                                "minimum_should_match": 1,
                                "should": [
                                    {
                                        "bool": {
                                            "must_not": {
                                                "bool": {
                                                    "should": [
                                                        {
                                                            "exists": {
                                                                "field": "dateOfBirth"
                                                            }
                                                        }
                                                    ],
                                                }
                                            }
                                        }
                                    },
                                    {
                                        "bool": {
                                            "should": [
                                                {
                                                    "range": {
                                                        "dateOfBirth": {
                                                            "lt": year+"||/y"
                                                        }
                                                    }
                                                }
                                            ]
                                        }
                                    }
                                ],
                            }
                        },
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
                        }
                    ],
                },
            }
        }
    res_candidates = {}
    if not settings.es.base_url:
        logging.error("Elasticsearch base_url is not set in settings!")
        return {}
    try:
        data = requests.get(
            settings.es.base_url + "/" + settings.es.index_name_gnd + "/_search?pretty",
            headers=headers,
            json=json_data,
            verify=settings.PATH_TO_CA_CERT,
            auth=(settings.es.username, settings.es.password),
            timeout=0.5)
    except requests.exceptions.Timeout:
        logging.warning("GND ES Query timed out.")
        try:
            data = requests.get(
                settings.es.base_url + "/" + settings.es.index_name_gnd + "/_search?pretty",
                headers=headers,
                json=json_data,
                verify=settings.PATH_TO_CA_CERT,
                auth=(settings.es.username, settings.es.password),
                timeout=5)
        except requests.exceptions.Timeout:
            logging.error("GND ES query timeout. No more retries.")
            logging.info(f"Query: {json_data}")
            pass
    except requests.exceptions.SSLError:
        logging.warning("SSL error GND")
        try:
            data = sess.get(
                settings.es.base_url + "/" + settings.es.index_name_gnd + "/_search?pretty",
                headers=headers,
                json=json_data,
                verify=settings.PATH_TO_CA_CERT,
                auth=(settings.es.username, settings.es.password),
                timeout=5)
        except requests.exceptions.Timeout:
            logging.error("GND ES SSL Error timeout. No more retries.")
            logging.info(f"Query: {json_data}")
            pass

    result_json = data.json()
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
                    logging.error(
                        f"GND entry with multiple GND IDs: {person_info['gid']}. "
                        "An arbitrary one is selected."
                    )
                gid = person_info["gid"].pop()
                person_info["gid"] = {gid}
                person_info["score"] = hit["_score"]
                if person_info["score"] > max_score:
                    max_score = person_info["score"]
                res_candidates[gid] = person_info
    except Exception:
        logging.error("This query caused an exception: "+str(result_json))
        return {}
    # to make scores across different indexes comparable
    # scale them to 1
    for per_dict in res_candidates.values():
        per_dict["score"] = per_dict["score"]/max_score

    return res_candidates


def search_person_wikidata(search_term: str, year: str, wikidata_limit=5, fuzzy=True) -> dict:
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

    if wikidata_limit == 0:
        return {}
    search_term = clean_namestring(search_term)
    # if after cleaning the search term is empty, do not search
    if search_term == "":
        return {}

    if fuzzy:
        search_term = prep_name_for_elasticsearch_query(search_term)

    headers = {"Content-Type": "application/json"}

    json_data = {
        "_source": ["GND_ID", "GND_ID_2"],
        "from": 0,
        "size": wikidata_limit,
        "query": {
            "bool": {
                "must": [
                    {
                        "bool": {
                            "minimum_should_match": 1,
                            "should": [
                                {
                                    "bool": {
                                        "must_not": {
                                            "bool": {
                                                "should": [
                                                    {
                                                        "exists": {
                                                           "field": "dateOfBirth"
                                                        }
                                                    }
                                                ],
                                            }
                                        }
                                    }
                                },
                                {
                                    "bool": {
                                        "should": [
                                            {
                                                "range": {
                                                    "dateOfBirth": {
                                                        "lt": year+"||/y"
                                                    }
                                                }
                                            }
                                        ]
                                    }
                                }
                            ],
                        }

                    },
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
    res_candidates = {}
    if not settings.es.base_url:
        logging.error("Elasticsearch base_url is not set in settings!")
        return {}
    try:
        data = requests.get(
            settings.es.base_url + "/" + settings.es.index_name_wikidata + "/_search?pretty",
            headers=headers,
            json=json_data,
            verify=settings.PATH_TO_CA_CERT,
            auth=(settings.es.username, settings.es.password),
            timeout=0.5)
    except requests.exceptions.Timeout:
        logging.warning("Wikidata ES Query timed out.")
        try:
            data = requests.get(
                settings.es.base_url + "/" + settings.es.index_name_wikidata + "/_search?pretty",
                headers=headers,
                json=json_data,
                verify=settings.PATH_TO_CA_CERT,
                auth=(settings.es.username, settings.es.password),
                timeout=5)
        except requests.exceptions.Timeout:
            logging.error("Wikidata ES query timeout. No more retries.")
            logging.info(f"Query: {json_data}")
            pass
    except requests.exceptions.SSLError:
        logging.warning("SSL error wikidata")
        try:
            data = sess.get(
                settings.es.base_url + "/" + settings.es.index_name_wikidata + "/_search?pretty",
                headers=headers,
                json=json_data,
                verify=settings.PATH_TO_CA_CERT,
                auth=(settings.es.username, settings.es.password),
                timeout=5)
        except requests.exceptions.Timeout:
            logging.error("Wikidata ES query SSL Error timeout. No more retries.")
            logging.info(f"Query: {json_data}")
            pass
    result_json = data.json()
    if len(result_json) == 0:
        return {}
    max_score = 0
    for hit in result_json["hits"]["hits"]:
        if "GND_ID" in hit["_source"] or "GND_ID_2" in hit["_source"]:
            person_info = convert_wikidata_format_kibana(hit["_source"])

            if "gid" in person_info and len(person_info["gid"]) != 0:
                person_info["score"] = hit["_score"]
                if len(person_info["gid"]) > 1:
                    logging.warning(
                        f"Wikidata entry with multiple GND IDs: {person_info['gid']}."
                    )
                for gid in person_info["gid"]:
                    # sometimes one entity is assigned several gids.
                    # this unfortunately breaks a lot of what we did logically
                    # but this cannot be fixed on our end.
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
