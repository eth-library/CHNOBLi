#! /usr/bin/python3
"""
principles of this script:
The main point of connection is (obviously) the lastname.
The firstname is important as well, but can possibly be omitted.
Further criteria are the dates of birth and death.
Also Titles (if applicable, in the database, the field for biographical infos
sometimes contains that information.)
Ultimately, and maybe most importantly, we are interested in the occupations.
"""
import re
import unicodedata
import logging
import warnings

# Suppress noisy third-party SyntaxWarning from the 'pattern' library (bug in Python 3.12)
warnings.filterwarnings("ignore", category=SyntaxWarning, module="pattern")

from datetime import datetime
from multiprocessing import Pool
from concurrent.futures import ThreadPoolExecutor
import orjson
import string
import os
from copy import deepcopy
import time
import requests
from utility.utils import save_data_intermediate
from utility.linking_utils import search_person_wikidata, search_person_gnd
from utility.settings import settings
from itertools import batched, takewhile
# Until we can set up the API
import numpy as np
from pymilvus import MilvusClient  # type: ignore
from collections import OrderedDict
from sentence_transformers import SentenceTransformer
from typing import List
import torch
import gc

MAX_YEAR_STR = "3000"

# GPU device handling
_DEVICE =  None
# Limit number of models cached in GPU to avoid memory fragmentation
_MAX_GPU_MODELS = 1
_model_cache: OrderedDict[str, SentenceTransformer] = OrderedDict()


def prep_word(word: str) -> str:
    """Normalizes and cleans up given string.

    :param word: String to normalize.
    :type word: str
    :return: Normalized string.
    :rtype: str
    :Example: 'OTMAR M\u00e4der' -> 'Otmar Mäder'
    """
    word = word.replace("^", "")
    word = unicodedata.normalize("NFC", word)
    word = word.title() if word.isupper() else word
    word = re.sub("""["']""", '', word)  # this removes ' within a word
    return word


def update_per_dict_score(dict_in: dict, dict_to_add: dict, strategy="max") -> dict:
    for k, v in dict_to_add.items():
        if k in dict_in:
            if strategy == "max":
                if v["score"] > dict_in[k]["score"]:
                    dict_in[k]["score"] = v["score"]
            elif strategy == "min":
                if v["score"] < dict_in[k]["score"]:
                    dict_in[k]["score"] = v["score"]
            elif strategy == "avg":
                dict_in[k]["score"] = (v["score"]+dict_in[k]["score"])/2
            else:
                raise ValueError("Not a valid strategy. Choose: max, min, avg.")
        else:
            dict_in[k] = v
    return dict_in


def remove_obsolete_abbrevs(fnames: list, abbr_firstnames: list) -> list:
    """
    Removes abbreviated firstnames that are already covered by full\
    firstnames.

    :param fnames: List of firstnames
    :type fnames: list
    :param abbr_firstnames: List of abbreviated firstnames
    :type abbr_firstnames: list
    :return: List of firstnames where the obsolete abbreviated firstnames\
            have been removed.
    :rtype: list
    :Example: fnames = ["R.", "Richard"] => fnames = ["Richard"]
    """

    cleaned_abbr_fnames = []
    for abbr_group in abbr_firstnames:
        cleaned_abbr_group = []
        for abbr in abbr_group:
            is_obsolete = False
            abbr = abbr.rstrip(".")
            for fname in fnames:
                if fname.lower().startswith(abbr.lower()):
                    is_obsolete = True
            if not is_obsolete:
                cleaned_abbr_group.append(abbr + ".")
        cleaned_abbr_fnames.append(cleaned_abbr_group)
    return cleaned_abbr_fnames


def get_candidates(person: dict, year: str, gnd_limit: int, wikidata_limit: int) -> dict:
    """Searches the GND and Wikidata index for candidates of a given person.

    :param person: A dictionary with various information on the given\
        person entity.
    :type person: dict
    :param year: The year in which this magazine was published.
    :type year: str
    :param gnd_limit: The number of candidates to truncate our GND candidate\
        list to.
    :type gnd_limit: int
    :param wikidata_limit: The number of candidates to truncate out wikidata\
        candidate list to.
    :type wikidata_limit: int
    :return: Dictionary of candidates for the given person, containing\
        information on the candidates themselves.
    :rtype: dict
    """

    if (
        len(person["lastname"]) == 0
        or (len(" ".join(person["lastname"])) < 3)
        or ((not person["firstname"] and not person["abbr_firstname"])
            and len(person["lastname"]) < 2)  # if the lastname is two words long, might be identifiable
       ):
        return {}

    lastname = person["lastname"]
    if len(lastname) > 1:
        lastname = " ".join(lastname)
    else:
        lastname = lastname[0]

    full_name = " ".join(person["firstname"]) + " " + lastname

    candidate_dict = dict()
    if person["abbr_firstname"] and not person["firstname"]:
        # If we have an abbr_fnames we usually don't have fnames
        # or they don't overlap in some way.
        full_name_abbr = " ".join(person["abbr_firstname"]) + " " + lastname
        candidate_dict = update_per_dict_score(candidate_dict, search_person_gnd(person["abbr_firstname"], lastname, year, gnd_limit, False), "max")
        candidate_dict = update_per_dict_score(candidate_dict, search_person_wikidata(full_name_abbr, year, wikidata_limit, False), "max")
        if settings.ADD_FUZZY_SEARCH == "True":
            candidate_dict = update_per_dict_score(candidate_dict, search_person_gnd(person["abbr_firstname"], lastname, year, gnd_limit), "max")
            candidate_dict = update_per_dict_score(candidate_dict, search_person_wikidata(full_name_abbr, year, wikidata_limit), "max")

    res_dict_fullname = {}
    res_dict_fullname = update_per_dict_score(res_dict_fullname, search_person_gnd(person["firstname"], lastname, year, gnd_limit, False), "max")
    res_dict_fullname = update_per_dict_score(res_dict_fullname, search_person_wikidata(full_name, year, wikidata_limit, False), "max")
    if settings.ADD_FUZZY_SEARCH == "True":
        res_dict_fullname = update_per_dict_score(res_dict_fullname, search_person_gnd(person["firstname"], lastname, year, gnd_limit), "max")
        res_dict_fullname = update_per_dict_score(res_dict_fullname, search_person_wikidata(full_name, year, wikidata_limit), "max")
    candidate_dict = update_per_dict_score(candidate_dict, res_dict_fullname, "max")
    return candidate_dict


def prep_person_entry(person: dict, mag_year: str) -> None:
    """
    Normalizes and cleans up proper names in the given person dictionary.

    :param person:  A person dictionary containing at least the keys\
        "firstname", "abbr_firstname", "lastname", and "profession".
    :type person: dict
    :param mag_year: Shortname of the magazine this person is mentioned\
        in. Of the form ("obl", "2004_000").
    :type mag_year: tuple
    """

    person["firstname"] = [
        [prep_word(y) for y in x.split()] for x in person["firstname"]
    ]
    fnames_flat = [x.lower() for y in person["firstname"] for x in y]
    person["firstname"] = [x.title() for x in dict.fromkeys(fnames_flat)]  # slower than list(set(items)) but keeps the order

    person["abbr_firstname"] = [
        [prep_word(y) for y in x.split()] for x in person["abbr_firstname"]
    ]
    abbr_fnames_trunc = remove_obsolete_abbrevs(
        person["firstname"], person["abbr_firstname"]
    )
    abbr_fnames_flat = [x for y in abbr_fnames_trunc for x in y]
    person["abbr_firstname"] = list(dict.fromkeys(abbr_fnames_flat))  # slower than list(set(items)) but keeps the order

    person["lastname"] = [prep_word(x) for x in person["lastname"].split()]
    person["lastname"] = [prep_word(y) for x in person["lastname"] for y in x.split("-")]
    person["profession"] = [prep_word(x) for x in person["profession"]]
    person["profession"].sort()
    person["other"] = [prep_word(x) for x in person["other"]]
    person["other"] = [x for x in person["other"] if x not in string.punctuation]
    person["id"] = mag_year[0]+":"+mag_year[1].replace("_", ":")+":"+str(person["id"])


def prep_person_out(person: dict) -> None:
    """For a given dictionary, joins the fields "firstname", "abbr_firstname"\
    and "lastname" repectively to make them strings. Maps the candidate scores
    to a "confidence score" on a scale from 1 to 5 for the frontend.

    :param person: A person dictionary containing at least the keys\
        "firstname", "abbr_firstname", and "lastname".
    :type person: dict
    """

    person["lastname"] = " ".join(person["lastname"])
    # precision 5 is excellent, 4 is very good, 3 is good, 2 is medium, 1 is minimal and 0 is experimental
    # oh experimental i like that
    # and 4 is max_confidence:4-5
    # and 5 is max_confidence:5-5
    # the "gnd_confidence" are only full numbers 0,1,2,3,4,5
    #for key in ["same_score_cand", "context", "gnd_ids_scores_dist", "gnd_ids_scores_sim"]:
    #    person.pop(key, None)
    # if we have a same_score_cand what does that mean? that we called the vd
    # if we have gnd_ids_scores_dist that means we called the vd
    # if we have gnd_ids_scores_sim that means the similarity of the names
    # so if we have
    # Confidence that this person cannot be linked
    if person["gnd_ids"] == []:
        if "gnd_ids_scores_dist" not in person:
            if "gnd_ids_scores_sim" not in person:
                person["gnd_confidence"] = 5
            else:
                person["gnd_confidence"] = 4
        else:
            person["gnd_confidence"] = 3
    else:
        if len(person["gnd_ids"]) == 1:
            if "gnd_ids_scores_dist" not in person:
                person["gnd_confidence"] = 5
            else:
                person["gnd_confidence"] = 4
        else:
            if "gnd_ids_scores_dist" not in person:
                person["gnd_confidence"] = 4
            else:
                person["gnd_confidence"] = 3

    for key in ["same_score_cand", "context", "gnd_ids_scores_dist", "gnd_ids_scores_sim"]:
        person.pop(key, None)

    # For the frontend: delete pid if it's None
    if "references" in person:
        for ref in person["references"]:
            if "pid" in person["references"][ref] and person["references"][ref]["pid"] is None:
                del person["references"][ref]["pid"]


def link_person(data_in) -> dict:
    """
    Searches GND and Wikidata for candidates, sets a field "gnd_ids" in the\
    person dictionary with at most `linked_persons_limit` candidates.

    :param data_in:
        * mag_year (tuple): Shortname of the magazine this person is mentioned\
            in. Of the form ("obl", "2004_000").\n
        * year (str): The year this magazine was published in.\n
        * person (dict): A dictionary with keys "lastname", "firstname",\
            "abbr_firstname", "address", "titles", "profession", "other",\
            "references", "type" and "id".\n

          - fields up until "references" are lists, except for lastname which\
                is a string\n
          - references is a defaultdict(list), a list of page_names where each\
                page_name has coords and sentences associated with it where\
                the candidate was mentioned\n
          - type is a string denoting the entity type\n
          - id is an internal id\n

        * tagging_paths (list): List of paths to the tagging output files for
            this magazine-year.
    :type data_in: 4-tuple
    :return: The changed person dictionary, now containing the gnd_ids
        if there are no candidates or exactly one candidate,\
        else "context" and "same_score_cand".
    :rtype: dict


    If the list of candidates is longer than `linked_persons_limit`,\
    we check if the first letters of the firstnames match the abbreviated\
    firstnames. If not, those candidates are deleted first, before we\
    truncate to `linked_persons_limit`.
    """
    mag_year, year, person, tagging_paths = data_in
    prep_person_entry(person, mag_year)
    candidates = get_candidates(person, year, settings.GND_LIMIT, settings.WIKIDATA_LIMIT)
    if len(candidates) == 0:
        person["gnd_ids"] = []
        prep_person_out(person)
        return person

    most_imp_sc = candidates[list(candidates)[0]]["score"]
    # if several of the first gnds have the same score,
    # take all of them and re-rank with our vdb
    same_score_cand = list(takewhile(
        lambda c: candidates[c]["score"] == most_imp_sc,
        candidates
    ))

    if len(same_score_cand) > 1:
        person_context_dict = deepcopy(person)
        context = get_person_context(
            person_context_dict,
            tagging_paths
        )

        person["context"] = context
        person["same_score_cand"] = same_score_cand
        return person

    person["gnd_ids"] = list(candidates.keys())[:settings.LINKED_PERSONS_LIMIT]
    person["gnd_ids_scores_sim"] = [candidates[x]["score"] for x in person["gnd_ids"]]
    prep_person_out(person)
    return person


def find_links(data_in) -> list:
    """
    Links all the people in the given data.

    :param data_in:\n
        - mag_year (tuple): A tuple contaning the magazine shortname and\
            year of the journal we're currently processing in that order.\n
        - data (list): The list of dictionaries created through\
            aggregating PER entities in our magazine-year tuple.\n
        - tagging_paths (list): The list of paths to the tagging output of this
            magazine_year tuple.
    :type data_in: 3-tuple
    :return: The same 4-tuple, but the data list is now an ordered list of \
             person entity dictionaries containing a\
             "gnd_ids" key with the candidates list if there are no candidates,\
             or exactly one candidate, else "context" and "same_score_cand".
    :rtype: tuple
    """
    mag_year, data, tagging_paths = data_in

    year = re.match(r"\d{4}", mag_year[1])
    if year is None:
        year = MAX_YEAR_STR
    else:
        year = year.group(0)

    person_list = [
        (
            mag_year,
            year,
            x,
            tagging_paths
        ) for x in data if x["type"] == "PER"]

    if settings.BATCH_SIZE == 1:
        person_list = [link_person(x) for x in person_list]
    else:
        with ThreadPoolExecutor(max_workers=settings.BATCH_SIZE) as executor:
            running_tasks = [executor.submit(link_person, x) for x in person_list]
            person_list_out = []
            for running_task in running_tasks:
                person_list_out.append(running_task.result())
        person_list = person_list_out
    # batch within link person not batch link person
    # like create a dict for one batch and then multiplex that
    # then batch size can be higher as well
    # with Pool(conf["BATCH_SIZE"]) as p:
    #     person_list = p.map(link_person, person_list)

    return mag_year, person_list, tagging_paths


def execute_linking(data: dict, tasks: list, timed=True) -> None:
    """
    Links the aggregated data based on the given configuration and tasks.

    :param data: The data that has been aggregated and is ready for\
        linking. The keys are the magazine-year shortnames, the values\
        are the dictionaries of the aggregated entities.
    :type data: dict
    :param tasks: List of tasks to be performed during linking.
    :type tasks: list
    :param timed: Boolean indicating whether to time the execution and log it,\
        defaults to True.
    :type timed: bool
    :raises Exception: If the tasks list doesn't include 'finish' or if 'agg'\
        and 'post' is not included in the tasks list, an exception is\
        raised indicating that 'post,agg,link' or 'finish' must be\
        called together.
    """

    if timed:
        start_time = datetime.now()
        logging.info(f"Starting Linking at {start_time} :")

    if (
        ("finish" not in tasks)
        or
        ("link" in tasks and ("agg" not in tasks or "post" not in tasks))
       ):
        raise Exception("'post,agg,link' must be called together, or call 'finish' instead.")

    # NOTE this cannot be called seperately after the aggregation step,
    # "post,agg,link" need to be called together after "tag",
    # or you could just call "finish"
    logging.info("executeLinking reached")
    logging.info("Linking now: " + ", ".join(["-".join(x) for x in data.keys()]))

    links = [
        [
            k,  # tuple of (mag, year) like ("cmt", "1998_076")
            v["agg_data"],  # list of person dictionaries
            v["paths"]  # list of paths to the tagging files for this year
        ] for (k, v) in data.items()
    ]
    #for idx, i in enumerate(links):
    #    links[idx][1] = find_links(i)  # I basically update v
    if settings.BATCH_SIZE == 1:
        links = [find_links(x) for x in links]
    else:
        with Pool(settings.BATCH_SIZE) as p:
            links = p.map(find_links, links)
    # vorschlag
    # for k,v in data.items():
    #     data[k] = find_links((k,v,conf))
    # Extract all person entries that have context
    context_entries = [
        (idx, idy, y)
        for idx in range(len(links))
        for idy in range(len(links[idx][1]))
        for y in [links[idx][1][idy]]
        if "context" in y
    ]
    logging.info(f"The context entries have length: {len(context_entries)}")

    link_folder = os.path.join(settings.PATH_TO_OUTFILE_FOLDER, "link")
    os.makedirs(link_folder, exist_ok=True)
    config_path = os.path.join(link_folder, f"configurations_{settings.JOB_ID}.json")

    with open(config_path, "wb") as f:
        f.write(orjson.dumps(settings.model_dump(exclude={"es"})))

    batched_queryids = list(batched([0 | (idx | idy << 32) for idx, idy, _ in context_entries], settings.VD_QUERY_CHUNK_LEN))
    batched_text = list(batched([y["context"] for _, _, y in context_entries], settings.VD_QUERY_CHUNK_LEN))
    batched_targettextids = list(batched([y["same_score_cand"] for _, _, y in context_entries], settings.VD_QUERY_CHUNK_LEN))
    assert len(batched_queryids) == len(batched_text)
    assert len(batched_queryids) == len(batched_targettextids)
    for i in range(len(batched_queryids)):
        response = compare_to_target_ids_multiplexed(
            batched_queryids[i],
            batched_text[i],
            batched_targettextids[i],
            settings.EMBEDDINGS_ENDPOINT+"/compare_to_text_ids_multiplexed", #TODO replace by an entry in an .env file.
            "gnd_de_snowflakearctic",
            "huggingface",
            "Snowflake/snowflake-arctic-embed-l-v2.0"
        )

        if response != []:
            for resp_dict in response:
                try:
                    response_i = [
                        k["reference_text_id"] for k in
                        sorted(resp_dict["distances"], key=lambda item: item["distance"])
                        if k["distance"] < settings.VD_MAX_DIST
                    ]
                    response_d = [
                        k["distance"] for k in
                        sorted(resp_dict["distances"], key=lambda item: item["distance"])
                        if k["distance"] < settings.VD_MAX_DIST
                    ]
                    idx_i = resp_dict["query_id"] & 0xFFFFFFFF
                    idx_j = (resp_dict["query_id"] & 0xFFFFFFFFFFFFFFFF) >> 32
                except Exception:
                    logging.error(f"Could not order responses {response} by distance.")
                    raise
                links[idx_i][1][idx_j]["gnd_ids"] = response_i[:settings.LINKED_PERSONS_LIMIT]
                links[idx_i][1][idx_j]["gnd_ids_scores_dist"] = response_d[:settings.LINKED_PERSONS_LIMIT]
                prep_person_out(links[idx_i][1][idx_j])

    for i in links:
        save_data_intermediate([i[0][0], i[0][1]], i[1], "link")

    if timed:
        logging.info("Linking took: "+str(datetime.now() - start_time))


def get_person_context(per: dict, tagging_output_paths: list) -> str:
    """
    Retrieve and concatenate context surrounding all person mentions.

    Extracts the text surrounding each reference to the given person and
    concatenates all context windows into a single string.

    :param per: Person entity dictionary containing a "references" key with
        mention locations
    :type per: dict
    :param tagging_output_paths: List of the paths to the tagging output files
    :type tagging_output_paths: list
    :return: Concatenated context text from all references to the person
    :rtype: str
    :raises Exception: If the tagging output path is not a valid path
    """
    all_context = ""

    for page in per["references"]:
        for r in per["references"][page]["refs"]:
            if "context" in r:  # custom tagging output has context already
                all_context += ";" + r["context"] + " "

    all_relevant_pages = per.get("references", {}).keys()

    # go over all the files
    for p in tagging_output_paths:  # for custom tagging output this is empty so skipped
        # check in the person references if this page / path is even relevant
        # then do the rest below.
        try:
            if p.endswith(".jsonl"):
                with open(p, "r", encoding="utf-8") as f:
                    pages = [orjson.loads(line) for line in f]
            else:
                with open(p, "r", encoding="utf-8") as f:
                    pages = [orjson.loads(f.read())]
        except Exception:
            raise Exception(f"Tagging output: {p} is not a valid path.")

        # Each line should be exactly one page
        if not all([len(x) == 1 for x in pages]):
            # flatten it
            pages = [{k: v} for subpages_dict in pages for (k, v) in subpages_dict.items()]
            assert all([len(x) == 1 for x in pages]), list(pages[0].keys())
        # Only keep pages relevant to the person
        pages = [x for x in pages if list(x.keys())[0] in all_relevant_pages]

        # Flatten all tokens into a single list for fast lookup
        all_tokens = []
        for page in pages:
            for sent_lists in page.values():
                for sent in sent_lists:
                    all_tokens.extend(sent)

        # Build a string of the full text for context extraction
        full_text = ""
        token_offsets = []
        for token in all_tokens:
            start = len(full_text)
            if token["token"] in string.punctuation:
                full_text += token["token"]
            else:
                full_text += " " + token["token"]
            end = len(full_text)
            token_offsets.append((token, start, end))

        # Helper: find token indices by coord
        coord_to_indices = {}
        for idx, (token, _, _) in enumerate(token_offsets):
            coord = token.get("coord", "").split(":")[0]
            if coord:
                coord_to_indices.setdefault(coord, []).append(idx)

        for ref_list in per.get("references", {}).values():
            # TODO check if it's an issue that I don't check
            # if the page is correct
            # it's unlikely that two tokens on different pages have
            # the exact same coordinates but what happens if they do?
            for ref in ref_list.get("refs", []):
                if "coords" in ref and len(ref["coords"]) > 0:
                    coords = [
                        x.split(":")[0]
                        if isinstance(x, str) else x.get("c", "")
                        for x in ref["coords"]
                    ]
                    indices = [coord_to_indices.get(x, []) for x in coords]
                    if indices == [[]]:
                        continue

                    start = max(0, token_offsets[min(indices)[0]][1]-(settings.VD_CONTEXT_WINDOW_LEN+(max(indices)[0]-min(indices)[0])))
                    end = min(len(full_text), token_offsets[max(indices)[0]][2]+(settings.VD_CONTEXT_WINDOW_LEN+(max(indices)[0]-min(indices)[0])))
                    extract = full_text[start:end].strip()
                    all_context += ";" + extract + " "
                    # I'm fine with overlap, works better this way
    all_context = all_context[1:]
    # return " ".join(all_context.strip().split(" ")[:1024])
    return all_context[:2048]  # https://huggingface.co/Snowflake/snowflake-arctic-embed-l-v2.0/discussions/3#6751e3b48409e4c1b2330c2d


def get_person_context_reflevel(per: dict, tagging_output_path: str) -> list:
    """
    Retrieve context surrounding all person mentions.

    Extracts the text surrounding each reference to the given person and
    returns them as a list.

    :param per: Person entity dictionary containing a "references" key with
        mention locations
    :type per: dict
    :param tagging_output_path: Path to the tagging output file
    :type tagging_output_path: str
    :return: List of context window strings, one per reference to the person
    :rtype: list
    :raises Exception: If the tagging output path is not a valid path
    """

    try:
        with open(tagging_output_path, "r", encoding="utf-8") as f:
            pages = [orjson.loads(line) for line in f]
    except Exception:
        raise Exception(f"Tagging output: {tagging_output_path} is not a valid path.")

    # Flatten all tokens into a single list for fast lookup
    all_tokens = []
    for page in pages:
        for sent_lists in page.values():
            for sent in sent_lists:
                all_tokens.extend(sent)

    # Build a string of the full text for context extraction
    full_text = ""
    token_offsets = []
    for token in all_tokens:
        start = len(full_text)
        if token["token"] in string.punctuation:
            full_text += token["token"]
        else:
            full_text += " " + token["token"]
        end = len(full_text)
        token_offsets.append((token, start, end))

    # Helper: find token indices by coord
    coord_to_indices = {}
    for idx, (token, _, _) in enumerate(token_offsets):
        coord = token.get("coord", "").split(":")[0]
        if coord:
            coord_to_indices.setdefault(coord, []).append(idx)

    all_context = []
    for ref_list in per.get("references", {}).values():
        for ref in ref_list.get("refs", []):
            if "coords" in ref and len(ref["coords"]) > 0:
                coords = [
                    x.split(":")[0]
                    if isinstance(x, str) else x.get("c", "")
                    for x in ref["coords"]
                ]
                indices = [coord_to_indices.get(x, []) for x in coords]
                if indices == [[]]:
                    continue

                start = max(0, token_offsets[min(indices)[0]][1]-(settings.VD_CONTEXT_WINDOW_LEN+(max(indices)[0]-min(indices)[0])))
                end = min(len(full_text), token_offsets[max(indices)[0]][2]+(settings.VD_CONTEXT_WINDOW_LEN+(max(indices)[0]-min(indices)[0])))
                extract = full_text[start:end].strip()
                all_context.append(extract[:8192])  # https://huggingface.co/Snowflake/snowflake-arctic-embed-l-v2.0/discussions/3#6751e3b48409e4c1b2330c2d
    return all_context


def compare_to_target_ids_multiplexed(queryids: list[int],
                                      text: list[str],
                                      target_text_ids: list[list[str]],
                                      backend_url: str,
                                      collection_name: str,
                                      model: str,
                                      model_name: str):
    """
    Compare query texts to target texts using embeddings and return distances.

    Sends text queries to an embedding backend to compute similarity distances
    between the query texts and a specified list of target text IDs.

    :param queryids: List of query identifiers
    :type queryids: list[int]
    :param text: List of text strings to embed and compare
    :type text: list[str]
    :param target_text_ids: List of target text ID lists to compare against
    :type target_text_ids: list[list[str]]
    :param backend_url: URL of the embedding backend service
    :type backend_url: str
    :param collection_name: Name of the collection in the backend
    :type collection_name: str, optional
    :param model: Model backend to use for generating embeddings
    :type model: str
    :param model_name: Specific model name to use
    :type model_name: str
    :return: List of results, else logs error
    :rtype: list
    """

    content = []
    for idx, t, idy in zip(queryids, text, target_text_ids):
        data = {}
        data["query_id"] = idx
        data["query_text"] = t
        data["reference_text_ids"] = idy
        content.append(data)

    if settings.EMBEDDINGS_ENDPOINT and settings.EMBEDDINGS_ENDPOINT != "":
        response = backend_api_call(content, model, model_name, collection_name, backend_url)
        return orjson.loads(response)["results"]
    else:
        from embedding_engine.embeddings import generate_embedding
        vectors = generate_embedding(texts=[x["query_text"] for x in content], backend="huggingface", model_name=model_name)
        return compare_vector_to_text_ids_multiplexed(content, vectors, collection_name)


def get_paramanera_token() -> str | None:
    """Fetches an OAuth token for the Paramanera API if configured."""
    if not settings.OIDC_TOKEN_URL or not settings.CLIENT_ID or not settings.CLIENT_SECRET:
        return None

    payload = {
        "grant_type": "client_credentials",
        "client_id": settings.CLIENT_ID,
        "client_secret": settings.CLIENT_SECRET
    }
    try:
        response = requests.post(settings.OIDC_TOKEN_URL, data=payload, timeout=10)
        if response.status_code == 200:
            return response.json().get("access_token")
    except Exception as e:
        logging.error(f"Failed to fetch OIDC token: {e}")
    return None


def backend_api_call(content, model, model_name, collection_name, backend_url):
    """
    We call our API backend. If OIDC_TOKEN_URL is set, it performs the Paramanera
    handshake and attaches the Bearer token.
    """
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
    }

    if settings.OIDC_TOKEN_URL:
        token = get_paramanera_token()
        if token:
            headers["Authorization"] = f"Bearer {token}"

    payload = {
        "content": content,
        "model": model,
        "model_name": model_name,
        "collection_name": collection_name
    }

    try:
        response = requests.post(backend_url, json=payload, headers=headers, timeout=60)
    except Exception:
        logging.warning(f"Querying the VD timed out once with payload: {payload}")
        response = requests.post(backend_url, json=payload, headers=headers, timeout=120)

    # retry until it works.
    retries = 0
    while response.status_code != 200 and retries < settings.VD_MAX_RETRIES:
        retries += 1
        time.sleep(2)
        logging.warning(f"Querying the VD failed or timed out {retries} times with payload: {payload}")
        try:
            response = requests.post(backend_url, json=payload, headers=headers, timeout=60)
        except requests.exceptions.ReadTimeout:
            # Try one more time, huggingface might be down
            # If this also causes an exception, execution should be stopped to investigate
            response = requests.post(backend_url, json=payload, headers=headers, timeout=120)

        if response.status_code == 200:
            return response.text

    if response.status_code == 200:
        return response.text
    logging.error(f"Max retries exceeded. Failed to retrieve distances: {response.status_code} - {response.text}")
    return '{"results": []}'


def compare_vector_to_text_ids_multiplexed(  # type: ignore
    input: list[dict],
    vectors: list[list[float]],
    collection_name:str,
    distance_metric:str = "cosine"
) -> list[dict]:
    """
    Compare query embeddings to candidate embeddings stored in Milvus,
    restricted by reference_text_ids per query.

    input: list of dicts with keys "query_id": int, "query_text": str, "reference_text_ids": list[str]
    vectors: list of embeddings (aligned with input order)
    collection_name: Milvus collection
    ditance_metric: "cosine" | "l2" | "ip"
    """

    # Initialize the modern MilvusClient
    client = MilvusClient(uri=f"http://{settings.MILVUS_HOST}:{settings.MILVUS_PORT}")
    client.load_collection(collection_name)

    # Collect all candidate IDs across all queries
    all_ids = set()
    for item in input:
        all_ids.update(item["reference_text_ids"])
    all_ids = list(all_ids)  # type: ignore

    if not all_ids:
        return [{"query_id": item["query_id"], "distances": []} for item in input]

    # single Milvus query using modern client
    expr = f"text_id in {all_ids}"
    candidate_rows = client.query(
        collection_name=collection_name,
        filter=expr,
        output_fields=["text_id", "embedding"]
    )

    id_to_emb = {
        row["text_id"]: np.array(row["embedding"], dtype=np.float32)
        for row in candidate_rows
    }

    results = []

    # compute distances
    for i, item in enumerate(input):
        query_id = item["query_id"]
        candidate_ids = item["reference_text_ids"]
        query_vec = np.array(vectors[i], dtype=np.float32)

        # Keep only candidates that exist in DB
        cand_embs = []
        cand_ids = []
        for tid in candidate_ids:
            if tid in id_to_emb:
                cand_ids.append(tid)
                cand_embs.append(id_to_emb[tid])
        if not cand_embs:
            results.append({"query_id": query_id, "distances": []})
            continue

        cand_embs = np.vstack(cand_embs)  # type: ignore

        # Distance computation
        if distance_metric == "cosine":
            q = query_vec / np.linalg.norm(query_vec)
            C = cand_embs / np.linalg.norm(cand_embs, axis=1, keepdims=True)
            sims = np.dot(C, q)
            dists = 1 - sims
        elif distance_metric == "l2":
            dists = np.linalg.norm(cand_embs - query_vec, axis=1)
        elif distance_metric == "ip":
            dists = -np.dot(cand_embs, query_vec)  # higher dot = closer
        else:
            raise ValueError(f"Unsupported distance metric: {distance_metric}")

        # Rank results
        ranked = sorted(zip(cand_ids, dists), key=lambda x: x[1])
        results.append(
            {
                "query_id": query_id,
                "distances": [
                    {"reference_text_id": tid, "distance": float(dist)}
                    for tid, dist in ranked
                ],
            }
        )

    client.release_collection(collection_name)
    return results

