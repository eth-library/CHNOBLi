#! /usr/bin/python3
"""
Aggregation module
"""
from collections import defaultdict
import re
import pprint as pp
from datetime import datetime
import logging
from multiprocessing import Pool
from germalemma import GermaLemma
from utility.utils import save_data
from utility.settings import settings

PREPATTERN = re.compile(r"^[\W_]+", flags=re.UNICODE)
POSTPATTERN = re.compile(r"[\W_]+$", flags=re.UNICODE)


def create_new_aggregated_unit(ref: dict) -> dict:
    """
    Create a new aggregated unit for a person entity.

    Transforms a person entity reference into an aggregated format where
    values are converted to sets of tuples for efficient tracking of where
    the person appears in the journal.

    :param ref: Dictionary containing person entity information and where
        the person appeared in the journal
    :type ref: dict
    :return: Dictionary with the same structure but values converted to sets
        of tuples for aggregation
    :rtype: dict
    """

    info = ref["info"]
    out_dict = {
        "lastname": info["lastnames"],
        "firstname": set([tuple(info["firstnames"].split())]),
        "abbr_firstname": set([tuple(info["abbr_firstnames"].split())]),
        "address": set([tuple(info["address"])]),
        "titles": set([tuple(info["titles"])]),
        "profession": set([tuple(info["occupations"])]),
        "other": set([tuple(info["others"])]),
        "references": {},
        "type": "PER"
        }

    if "context" in ref:  # custom tag output
        out_dict["references"] = {
            (ref["pageNo"], ref["pageNames"], ref["pid"]): [
                (ref["sentenceNo"], ref["positions"], ref["articles"], ref["context"])
            ]
        }
    else:
        out_dict["references"] = {
                (ref["pageNo"], ref["pageNames"], ref["pid"]): [
                    (ref["sentenceNo"], ref["positions"], ref["articles"])
                ]
            }
    for k in out_dict:
        for t in k:
            if len(t) == 0:
                k.remove(t)

    return out_dict


def merge_to_existing_aggregated_unit(match_in: dict, ref: dict) -> None:
    """
    Merge reference information into an existing aggregated unit.

    Updates the `match_in` dictionary in place by adding entity information
    from the `reference`.

    :param match_in: The existing aggregated unit to update
    :type match_in: dict
    :param ref: Dictionary containing person entity information and where
        the person appeared in the journal
    :type ref: dict
    """

    info = ref["info"]
    match_in["firstname"].add(tuple(info["firstnames"].split()))
    #for fname in info["firstnames"].split():
    #    if tuple([fname]) not in match_in["firstname"]:
    #        match_in["firstname"].add(tuple([fname]))
    if tuple() in match_in["firstname"]:
        match_in["firstname"].remove(tuple())

    match_in["abbr_firstname"].add(tuple(info["abbr_firstnames"].split()))
    if tuple() in match_in["abbr_firstname"]:
        match_in["abbr_firstname"].remove(tuple())
    match_in["titles"].add(tuple(info["titles"]))
    if tuple() in match_in["titles"]:
        match_in["titles"].remove(tuple())
    match_in["other"].add(tuple(info["others"]))
    if tuple() in match_in["other"]:
        match_in["other"].remove(tuple())
    match_in["address"].add(tuple(info["address"]))
    if tuple() in match_in["address"]:
        match_in["address"].remove(tuple())
    match_in["profession"].add(tuple(info["occupations"]))
    if tuple() in match_in["profession"]:
        match_in["profession"].remove(tuple())

    if "context" in ref:
        page_tri = (ref["pageNo"], ref["pageNames"], ref["pid"])
        sent_q = (ref["sentenceNo"], ref["positions"], ref["articles"], ref["context"])
        if page_tri in match_in["references"]:
            if sent_q not in match_in["references"][page_tri]:
                match_in["references"][page_tri].append(sent_q)
        else:
            match_in["references"][page_tri] = [sent_q]
    else:
        page_tri = (ref["pageNo"], ref["pageNames"], ref["pid"])
        sent_tri = (ref["sentenceNo"], ref["positions"], ref["articles"])
        if page_tri in match_in["references"]:
            if sent_tri not in match_in["references"][page_tri]:
                match_in["references"][page_tri].append(sent_tri)
        else:
            match_in["references"][page_tri] = [sent_tri]


def decide_candidates(ref: dict,
                      candidates: list,
                      aggregated_names: list,
                      verbose=False) -> None:
    """
    Select the best matching candidate and merge, or create a new unit.

    Evaluates potential candidate matches for a person entity reference. If
    a suitable match is found, merges the reference into that aggregated unit
    in-place. Otherwise, creates a new aggregated unit and adds it to the list.

    :param ref: A dictionary containing information about the person\
        entity and where the person appeared in the journal
    :type ref: dict
    :param candidates: A list of dictionaries representing existing\
        aggregated units that are potential matches for the reference
    :type candidates: list
    :param aggregated_names: List of all aggregated units, modified in place
        by adding new units or updating existing ones
    :type aggregated_names: list
    :param verbose: If True, prints detailed information about\
        the reference and the selected candidate, defaults to False
    :type verbose: bool, optional
    """

    if verbose:
        pp.pprint(ref)
    best_candidate = None
    for c in candidates:
        # get page and sentence number
        c_pos_list = [(page[0], entry[0]) for page, pagelist in
                      c["references"].items() for entry in pagelist]
        diff = [
                (
                    ref["pageNo"] - c_pos[0], ref["sentenceNo"] - c_pos[1]
                ) for c_pos in c_pos_list if ref["pageNo"] - c_pos[0] > 0
                or
                (
                    (ref["pageNo"] - c_pos[0] == 0)
                    and
                    (ref["sentenceNo"] - c_pos[1] >= 0)
                )
        ]
        if diff:
            diff = min(diff)
        else:
            continue
        if best_candidate is None:
            best_candidate = (c, diff[0], diff[1])
        else:
            if best_candidate[1] > diff[0]:
                best_candidate = (c, diff[0], diff[1])
            elif best_candidate[1] == diff[0]:
                if best_candidate[2] > diff[1]:
                    best_candidate = (c, diff[0], diff[1])
    if best_candidate is None:
        aggregated_names.append(create_new_aggregated_unit(ref))
    else:
        match = best_candidate[0]
        merge_to_existing_aggregated_unit(match, ref)
        if verbose:
            pp.pprint(match)


def full_firstname_match(ref: dict, aggregated_names: list) -> dict:
    """
    Find an exact match by full first name and last name.

    Searches the aggregated names for an entry that matches both the complete
    first name and last name of the reference.

    :param ref: Dictionary containing the reference person entity information
    :type ref: dict
    :param aggregated_names: List of existing aggregated units to search
    :type aggregated_names: list
    :return: The matching aggregated unit if found, else `None`
    :rtype: dict
    """

    for entry in aggregated_names:
        if [x.lower() for x in ref["info"]["lastnames"]] == [x.lower() for x in entry["lastname"]]:
            if {
                x.lower() for x in ref["info"]["firstnames"].split() if x != ""
            }.isdisjoint([y.lower() for x in entry["firstname"] for y in x]):
                continue
            return entry
    return None


def aggregate_with(namepart_dict: dict,
                   aggregated_names: list,
                   namepart: str) -> None:
    """
    Aggregate person entity references by a specified name part.

    Processes references grouped by a name part (e.g., last name) and either
    merges them into existing aggregated units or creates new units where
    appropriate.

    :param namepart_dict: Dictionary mapping name parts to lists of person
        entity references. Keys are name parts (e.g., last names), values are
        lists of reference dictionaries
    :type namepart_dict: dict
    :param aggregated_names: List of existing aggregated units, modified in
        place by merging or adding new units
    :type aggregated_names: list
    :param namepart: The type of name part to use for aggregation (e.g.,
        'lastname', 'firstname')
    :type namepart: str
    :raises Exception: If the provided `namepart` is not recognized
    """

    # order the entities according to pageno and sentenceno
    try:
        for k, v in namepart_dict.items():
            namepart_dict[k] = sorted(v, key=lambda x: (x["pageNo"], x["sentenceNo"]))
    except KeyError:
        # custom tagging output won't have these keys, keep them unordered
        pass

    for value in namepart_dict.values():
        for reference in value:
            if namepart == "fullfirstnames":
                # Aggregate all persons that have a matching lastname and at
                # least one matching firstname.
                # "Hans Mueller" <=> "Hans Friedrich Mueller"
                match = full_firstname_match(reference, aggregated_names)
                if not match:
                    candidates = []
                else:
                    candidates = [match]
            elif namepart == "abbrevs":
                # Aggregate all persons that have a matching lastname and at
                # least one matching firstname.
                # "H. Mueller" <=> "Hans Friedrich Mueller"
                # Also check for matching gender (or no gender info)
                # This time, we need to collect candidates, then take the one
                # that appeared the closest last time.
                candidates = abbrev_firstname_match(reference,
                                                    aggregated_names)
            elif namepart == "onlylastnames":
                # Aggregate with matching lastnames, if multiple candidates
                # choose last seen.
                candidates = only_lastname_match(reference, aggregated_names)
            elif namepart == "onlyfirstnames":
                candidates = only_firstname_match(reference, aggregated_names)
            elif namepart == "onlyabbrevfirstnames":
                candidates = only_abbrev_firstname_match(reference,
                                                         aggregated_names)
            elif namepart == "others":
                candidates = others_match(reference, aggregated_names)
            else:
                raise Exception(f"This namepart: {namepart} is unknown.")

            if len(candidates) == 0:
                aggregated_names.append(create_new_aggregated_unit(reference))
            elif len(candidates) == 1:
                match = candidates[0]
                merge_to_existing_aggregated_unit(match, reference)
            else:
                decide_candidates(reference, candidates, aggregated_names)


def abbrev_firstname_match(reference: dict, aggregated_names: list) -> list:
    """
    Find matches by abbreviated first name and last name.

    Searches the aggregated names for entries where both the abbreviated
    first name and last name match the reference.

    :param reference: Dictionary containing the reference person entity
        information
    :type reference: dict
    :param aggregated_names: List of existing aggregated units to search
    :type aggregated_names: list
    :return: List of matching aggregated units; empty list if no matches found
    :rtype: list
    """

    matches = []
    for entry in aggregated_names:
        if [x.lower() for x in reference["info"]["lastnames"]] == [x.lower() for x in entry["lastname"]]:
            set_abbr_fnames = set(
                [
                    x[0]+".".lower()
                    for x in reference["info"]["abbr_firstnames"].split()
                    if x != ""
                ]
            )
            if (
                set_abbr_fnames.isdisjoint(
                    [
                        y[0]+".".lower() for x in entry["firstname"] for y in x
                    ]
                ) and set_abbr_fnames.isdisjoint(
                    [
                        y[0]+".".lower() for x in entry["abbr_firstname"] for y in x
                    ]
                )
            ):
                continue
            matches.append(entry)
    return matches


def only_lastname_match(reference: dict, aggregated_names: list) -> list:
    """
    Find matches by last name only.

    Searches the aggregated names for entries where the last name matches
    the reference, regardless of first name.

    :param reference: Dictionary containing the reference person entity
        information
    :type reference: dict
    :param aggregated_names: ist of existing aggregated units to search
    :type aggregated_names: list
    :return: List of matching aggregated units. Empty list if no matches found
    :rtype: list
    """

    matches = []
    for entry in aggregated_names:
        if [x.lower() for x in reference["info"]["lastnames"]] == [x.lower() for x in entry["lastname"]]:
            matches.append(entry)
    return matches


def only_firstname_match(ref: dict, aggregated_names: list) -> list:
    """
    Find matches by first name only.

    Searches the aggregated names for entries where the first name matches
    the reference, regardless of last name.

    :param ref: Dictionary containing the reference person entity
        information
    :type ref: dict
    :param aggregated_names: List of existing aggregated units to search
    :type aggregated_names: list
    :return: List of matching aggregated units. Empty list if no matches found
    :rtype: list
    """

    matches = []
    for entry in aggregated_names:
        if (
            set([x.lower() for x in ref["info"]["firstnames"].split(" ")])
            ==
            set(y.lower() for x in entry["firstname"] for y in x)
        ):
            matches.append(entry)
    return matches


def only_abbrev_firstname_match(ref: dict,
                                aggregated_names: list) -> list:
    """
    Find matches by abbreviated first name only.

    Searches the aggregated names for entries where the abbreviated first
    name matches the reference, regardless of last name.

    :param ref: Dictionary containing the reference person entity
        information
    :type ref: dict
    :param aggregated_names: List of existing aggregated units to search
    :type aggregated_names: list
    :return: List of matching aggregated units. Empty list if no matches found
    :rtype: list
    """

    matches = []
    for entry in aggregated_names:
        if (
            set([x.lower() for x in ref["info"]["abbr_firstnames"]])
            ==
            set(y.lower() for x in entry["abbr_firstname"] for y in x)
        ):
            matches.append(entry)
    return matches


def others_match(reference: dict, aggregated_names: list) -> list:
    """
    Find matches by the 'others' field only.

    Searches the aggregated names for entries where the 'others' field
    matches the reference, regardless of first or last name.

    :param reference: Dictionary containing the reference person entity
        information
    :type reference: dict
    :param aggregated_names: List of existing aggregated units to search
    :type aggregated_names: list
    :return: List of matching aggregated units; empty list if no matches found
    :rtype: list
    """

    matches = []
    for entry in aggregated_names:
        for other in reference["info"]["others"]:
            if other.lower() in [y.lower() for x in entry["other"] for y in x]:
                matches.append(entry)
    return matches


def clean_up_aggregation(aggregated_names: list) -> list:
    """
    Clean and restructure the aggregated person list.

    Sorts the aggregated person entities and reformats the internal data
    structure of their references for consistency.

    :param aggregated_names: List of aggregated person entity dictionaries
    :type aggregated_names: list
    :return: Cleaned and restructured list of aggregated person entities
    :rtype: list
    """

    aggregated_names = sorted(
        aggregated_names, key=lambda k: (k["lastname"], k["firstname"])
    )
    for i, entry in enumerate(aggregated_names):
        # sort functions may be deleted for performance improvements, only
        # added for test reasons (easier to compare files when they are the
        # same each run)
        entry["id"] = i
        entry["firstname"] = sorted(
            [" ".join(fname) for fname in entry["firstname"] if fname]
        )
        entry["abbr_firstname"] = sorted(
            [" ".join(fname) for fname in entry["abbr_firstname"] if fname]
        )
        entry["titles"] = [" ".join(reversed(x)) for x in entry["titles"] if x and x != ('',)]
        entry["titles"] = list(set(entry["titles"]))
        entry["address"] = [y for x in entry["address"] if x for y in x if y and y != ('',)]
        entry["address"] = list(set(entry["address"]))
        entry["profession"] = [y for x in entry["profession"] if x for y in x if y and y!= ('',)]
        entry["profession"] = list(set(entry["profession"]))
        entry["other"] = sorted(
            [" ".join(ot) for ot in entry["other"] if ot and " ".join(ot)!=""]
        )
        new_references = defaultdict(list)

        for k, v in sorted(entry["references"].items()):
            elements = set()
            elements_info = dict()
            for x in v:
                for y in x[2]:
                    for el, el_info in y.items():
                        elements.add(el)
                        elements_info.setdefault(el, el_info)
                        elements_info[el].setdefault("elementId", k[2]+":"+el)
            elements = list(elements)
            elements = sorted(elements)
            new_references[k[1]] = {
                "pid": k[2],
                "refs": [{"sent": x[0], "coords": x[1], "context": x[3]} if len(x)==4 else {"sent": x[0], "coords": x[1]} for x in v],
                "elements": [elements_info[e] for e in elements]
            }

        for r_k, r_v in new_references.items():
            new_references[r_k]["refs"] = sorted(r_v["refs"], key=lambda x: x["sent"])
        entry["references"] = new_references
    return aggregated_names


def map_genitive_versions(all_names: list,
                          lastname_dict: dict,
                          key: str) -> None:
    """
    Map genitive name forms to their base forms.

    Converts genitive versions of names (ending in 's') to their non-genitive
    base forms by removing the trailing 's' where appropriate, updating the
    lastname_dict in place.

    :param all_names: List of person names mentioned in the journal
    :type all_names: list
    :param lastname_dict: Dictionary of last names, modified in place to map
        genitive forms to base forms
    :type lastname_dict: dict
    :param key: The name part to process (e.g., 'lastname', 'firstname')
    :type key: str
    """

    for lastname in lastname_dict:
        if (
            lastname.endswith("s")
            and len(lastname) > 1
            and lastname[-2] != 's'
            and lastname[:-1] in all_names
        ):
            for entry in lastname_dict[lastname]:
                entry["info"][key] = entry["info"][key][:-1]


def map_genitive_places(all_names: list, place_list: list) -> None:
    """
    Map genitive place name forms to their base forms.

    Converts genitive versions of place names (ending in 's') to their
    non-genitive base forms by removing the trailing 's' where appropriate,
    updating place_list in place.

    :param all_names: List of place names mentioned in the journal
    :type all_names: list
    :param place_list: List of places, modified in place to map genitive
        forms to base forms
    :type place_list: list
    """

    MINIMUMGENITIVELENGTH = 4

    for place in place_list:
        for i in range(len(place["tokens"])):
            if (
                place["tokens"][i].lower().endswith("s")
                and len(place["tokens"][i]) > MINIMUMGENITIVELENGTH
                and place["tokens"][i][-2].lower() != "s"
                and place["tokens"][i][:-1].lower() in all_names
            ):
                # pp.pprint(place["tokens"][i])
                place["tokens"][i] = place["tokens"][i][:-1]
                # pp.pprint(place["tokens"][i])


def find_place_match(place_name: str,
                     place_type: str,
                     aggregated_places: list) -> dict:
    """
    Find an exact match for a place name.

    Searches the aggregated place names for an entry that exactly matches
    both the place name and type.

    :param place_name: The place name string to match
    :type place_name: str
    :param place_type: The entity type of the place (e.g., 'GPE', 'LOC')
    :type place_type: str
    :param aggregated_places: List of existing aggregated place units to
        search
    :type aggregated_places: list
    :return: The matching aggregated place unit if found, else `None`
    :rtype: dict or None
    """

    for entry in aggregated_places:
        if (
            " ".join(entry["tokens"]).lower() == place_name
            and entry["type"] == place_type
        ):
            return entry
    return False


def aggregate_places(all_places: list, aggregated_places: list):
    """
    Aggregate place entity references into unified units.

    Processes all place entity references and either merges them into
    existing aggregated units or creates new units as appropriate, updating
    the aggregated places list in place.

    :param all_places: List of place entity dictionaries containing place
        information and their location references in the journal
    :type all_places: list
    :param aggregated_places: List of existing aggregated place units,
        modified in place by merging or adding new units
    :type aggregated_places: list
    """

    for place in all_places:
        place_name = " ".join(place["tokens"]).lower()
        found_place = find_place_match(
            place_name, place["type"], aggregated_places
        )
        if found_place:
            aggregate_place(found_place, place)
        else:
            aggregated_places.append(create_new_aggregated_place(place))


def aggregate_place(found: dict, place: dict) -> None:
    """
    Merge place reference information into an existing aggregated unit.

    Updates an existing `found` dictionary in place by adding 
    the information from the `place` reference.

    :param found: The existing aggregated place unit to update
    :type found: dict
    :param place: Dictionary containing place entity information and its
        location references in the journal
    :type place: dict
    """

    # type needs no aggregation
    if (
        place["pageNo"], place["pageNames"], place["pid"]
       ) in found["references"]:
        found["references"][(place["pageNo"],
                             place["pageNames"],
                             place["pid"])].append(
                                 (
                                     place["sentenceNo"],
                                     place["positions"],
                                     place["articles"]
                                 )
                            )
    else:
        found["references"][(place["pageNo"],
                             place["pageNames"],
                             place["pid"])] = [
                                 (
                                     place["sentenceNo"],
                                     place["positions"],
                                     place["articles"]
                                 )
                            ]


def create_new_aggregated_place(reference: dict) -> dict:
    """
    Create a new aggregated unit for a place entity.

    Transforms a place entity reference into an aggregated format where
    values are converted to sets of tuples for efficient tracking of where
    the place appears in the journal.

    :param reference: Dictionary containing place entity information and its
        location references in the journal
    :type reference: dict
    :return: Dictionary with the same structure but values converted to sets
        of tuples for aggregation
    :rtype: dict
    """

    return {
        "name": " ".join([x.title() if x.isupper else x for x in
                         reference["tokens"]]),
        "tokens": reference["tokens"],
        "type": reference["type"],
        "references": {
                (reference["pageNo"],
                 reference["pageNames"],
                 reference["pid"]): [(reference["sentenceNo"],
                                      reference["positions"],
                                      reference["articles"])]
            }
        }


def clean_up_aggregation_places(aggregated_places: list,
                                last_index: int) -> list:
    """
    Clean and restructure the aggregated places list.

    Sorts the aggregated place entities and reformats the internal data
    structure of their references for consistency.

    :param aggregated_places: List of aggregated place entity dictionaries
    :type aggregated_places: list
    :param last_index: Index of the last place entity processed
    :type last_index: int
    :return: Cleaned and restructured list of aggregated place entities
    :rtype: list
    """

    aggregated_places = sorted(aggregated_places, key=lambda k: k["name"])
    for i, entry in enumerate(aggregated_places):
        entry["id"] = i + last_index + 1
        new_references = defaultdict(list)
        # for k, v in entry["references"].items():
        #    new_references[k[1]].extend([{"sent": x[0], "coords":x[1],
        #                                  "articles":x[2]} for x in v])
        for k, v in sorted(entry["references"].items()):
            elements = set()
            for x in v:
                for el in x[2]:
                    elements.add(el)
            elements = list(elements)
            elements = sorted(elements)
            new_references[k[1]] = {
                "pid": k[2],
                "refs": [{"sent": x[0], "coords": x[1]} for x in v],
                "elements": elements
            }
        entry["references"] = new_references
    return aggregated_places


def clean_lastname(word: str) -> str:
    """
    Remove prefix and suffix patterns from a last name.

    Applies global PRE and POSTPATTERN regex patterns to strip common
    prefixes and suffixes from the given word.

    :param word: The last name string to clean
    :type word: str
    :return: The cleaned last name with patterns removed
    :rtype: str
    """
    word = PREPATTERN.sub("", word)
    word = POSTPATTERN.sub("", word)
    return word


def aggregate_names(input_triplet) -> list:
    """
    Aggregate person entity mentions into unified entities.

    Groups multiple mentions of the same person into single aggregated units
    based on name matching and contextual information from the journal.

    :param input_triplet: Triplet consisting of (in this order):
        * Tuple (mag, year)
        * List of person entity dictionaries to aggregate
        * List of paths for the tagging output files of this mag-year tuple
    :type input_triplet: tuple
    :return: Triplet consisting of (in this order):
        * List of aggregated person entities with consolidated mentions
        * Tuple (mag, year)
        * List of paths for the tagging output files of this mag-year tuple
    :rtype: list
    """
    (year, data, paths) = input_triplet
    lemmatizer = GermaLemma()

    place_data = [x for x in data if "info" not in x]
    data = [x for x in data if "info" in x]

    # do persons first
    all_last_names = {y for x in data for y in x["info"]["lastnames"]}
    all_first_names = {y for x in data for y in x["info"]["firstnames"]}
    lastnames_with_firstnames = defaultdict(list)
    lastnames_with_abbrev = defaultdict(list)
    lastnames_only = defaultdict(list)
    firstnames_only = defaultdict(list)
    abbrev_firstnames_only = defaultdict(list)
    others_only = defaultdict(list)
    debug_list = []  # just collect all remaining entities
    for entry in data:
        info = entry["info"]
        lastname = " ".join([clean_lastname(x) for x in info["lastnames"]])
        info["lastnames"] = lastname
        info["firstnames"] = " ".join(info["firstnames"])
        info["abbr_firstnames"] = " ".join(info["abbr_firstnames"])

        # lemmatize descriptors
        # We assume all occupations are nouns
        info["occupations"] = [
            lemmatizer.find_lemma(x, "N") for x in info["occupations"]
        ]
        # We assume all titles are nouns
        info["titles"] = [
            lemmatizer.find_lemma(x, "N") for x in info["titles"]
        ]
        # We assume all address are nouns
        info["address"] = [
            lemmatizer.find_lemma(x, "N") for x in info["address"]
        ]

        if len(lastname) == 0:
            if len(info["firstnames"]) > 0:
                firstnames_only[info["firstnames"]].append(entry)
            elif len(info["abbr_firstnames"]) > 0:
                abbrev_firstnames_only[info["abbr_firstnames"]].append(entry)
            elif len(info["others"]) > 0:
                others_only[tuple(info["others"])].append(entry)
            else:
                debug_list.append(entry)
        else:
            if len(info["firstnames"]) > 0:
                lastnames_with_firstnames[lastname].append(entry)
            # these lines were commented out, but why?
            elif len(info["abbr_firstnames"]) > 0:
                lastnames_with_abbrev[lastname].append(entry)
            else:
                lastnames_only[lastname].append(entry)

    map_genitive_versions(all_last_names, lastnames_with_firstnames, "lastnames")
    map_genitive_versions(all_last_names, lastnames_with_abbrev, "lastnames")
    map_genitive_versions(all_last_names, lastnames_only, "lastnames")
    map_genitive_versions(all_first_names, firstnames_only, "firstnames")

    aggregated_names = []
    aggregate_with(lastnames_with_firstnames, aggregated_names, "fullfirstnames")
    aggregate_with(lastnames_with_abbrev, aggregated_names, "abbrevs")
    aggregate_with(lastnames_only, aggregated_names, "onlylastnames")
    aggregate_with(firstnames_only, aggregated_names, "onlyfirstnames")
    # this below might do more damage than good
    aggregate_with(abbrev_firstnames_only, aggregated_names, "onlyabbrevfirstnames")
    aggregate_with(others_only, aggregated_names, "others")

    aggregated_names = clean_up_aggregation(aggregated_names)

    # do places second
    all_place_names = set([y.lower() for x in place_data for y in x["tokens"]])
    map_genitive_places(all_place_names, place_data)
    aggregated_places = []
    aggregate_places(place_data, aggregated_places)
    aggregated_places = clean_up_aggregation_places(
        aggregated_places, len(aggregated_names)
    )

    aggregated_names = aggregated_names + aggregated_places

    return aggregated_names, year, paths


def execute_aggregation(postprocessed_data,
                        tasks: list,
                        timed=True):
    """
    Aggregate postprocessed data and optionally log execution time.

    :param postprocessed_data: Postprocessed entity data ready for aggregation
    :type postprocessed_data: list of triplets (year, data, paths)
    :param tasks: List of tasks to perform during aggregation
    :type tasks: list
    :param timed: If True, logs execution time. Defaults to True
    :type timed: bool, optional
    :return: Generator yielding dictionaries of aggregated data, each
        containing a dictionary with keys "agg_data" containing tagged people
        and places and a key "paths" with a list of all the tagged files that\
        belong to this year
    :rtype: Iterator[dict]
    :raises Exception: If 'post' is not included in the tasks list, an\
        exception is raised indicating that 'post,agg,link' must be called\
        together.
    """

    if timed:
        start_time = datetime.now()
        logging.info(f"Starting Aggregation at {start_time}:")

    if "post" not in tasks and tasks != ["finish"]:
        raise Exception("'post,agg,link' must be called together. Alternatively, you can call 'finish'.")

    aggregated_data = {}
    #for year, d, paths in postprocessed_data:
    #    logging.info("Aggregating: %s", year)
    #    aggregated = aggregate_names(d, year, paths)
    #    aggregated_data[year] = {"agg_data": aggregated, "paths": paths}
    if settings.BATCH_SIZE == 1:
        out = [aggregate_names(x) for x in postprocessed_data]
    else:
        with Pool(settings.BATCH_SIZE) as p:
            out = p.map(aggregate_names, postprocessed_data)
    for aggregated, year, paths in out:
        aggregated_data[year] = {"agg_data": aggregated, "paths": paths}

    if timed:
        logging.info(f"Aggregation took: {datetime.now() - start_time}")

    if "link" not in tasks and "finish" not in tasks:
        save_data([aggregated_data],  "agg")

    return aggregated_data
