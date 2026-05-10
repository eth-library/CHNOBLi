"""
Evaluation functions for linking output.
"""

import os
from utility.settings import settings
import orjson
from collections import Counter
import logging
MAX_ROUNDING = 3


class Paths:
    """
    Defines a "Paths" class to build the various paths to ground-truth, linking output, evaluation output and
    input files.
    """
    def __init__(self):
        if settings.PATH_TO_GROUND_TRUTH is not None and settings.PATH_TO_OUTFILE_FOLDER is not None:
            self.paths = {
                "gt": settings.PATH_TO_GROUND_TRUTH,
                "link": os.path.join(settings.PATH_TO_OUTFILE_FOLDER, "link"),
                "eval": os.path.join(settings.PATH_TO_OUTFILE_FOLDER, "eval"),
                "input": settings.PATH_TO_INPUT_FOLDERS,
            }
            self.state = {
                "magazine": "",
                "file": ""
            }
            self.success = True
        else:
            self.success = False

    def update(self, key, value):
        self.state[key] = value

    def get(self, type_, key, ref_level_name="", gt_fuzziness_name=""):
        _TYPES = ["gt", "link", "eval", "input"]
        KEY_TYPES = ["magazine", "file", ""]
        REF_LEVEL_TYPES = ["ent", "ref", ""]
        GT_FUZZINESS_TYPES = ["with_fuzzy", "without_fuzzy", ""]
        assert type_ in _TYPES, f"'{type_}' is not in {_TYPES}"
        assert key in KEY_TYPES, f"'{key}' is not in {KEY_TYPES}"
        assert ref_level_name in REF_LEVEL_TYPES, f"'{ref_level_name}' is not in {REF_LEVEL_TYPES}"
        assert gt_fuzziness_name in GT_FUZZINESS_TYPES, f"'{gt_fuzziness_name}' is not in {GT_FUZZINESS_TYPES}"

        if type_ == "input":
            if ref_level_name != "":
                logging.warning(
                    "Careful! You selected the input folder but also a reference level.\
                    There are no reference levels at input, this value is ignored."
                )
                ref_level_name = ""
            elif gt_fuzziness_name != "":
                logging.warning(
                    "Careful! You selected the input folder but also a gt fuzziness level.\
                    There are no fuziness levels at input, this value is ignored."
                )
                gt_fuzziness_name = ""

        if type_ == "gt" and gt_fuzziness_name != "":
            logging.warning(
                    "Careful! You selected the ground truth folder but also a gt fuzziness level.\
                    The folder already determines the fuzziness level, this value is ignored."
            )
            gt_fuzziness_name = ""

        if ref_level_name != "":
            ref_level_name = "_"+ref_level_name
        if gt_fuzziness_name != "":
            gt_fuzziness_name = "_"+gt_fuzziness_name

        if key == "magazine":
            return os.path.join(
                self.paths[type_] + ref_level_name + gt_fuzziness_name,
                self.state["magazine"])
        if key == "file":
            return os.path.join(
                self.paths[type_] + ref_level_name + gt_fuzziness_name,
                self.state["magazine"],
                self.state["file"])
        return os.path.join(
            self.paths[type_] + ref_level_name + gt_fuzziness_name)

    def get_jsonl(self, type_):
        path = self.get(type_=type_, key="file")
        with open(path, "r", encoding="utf-8") as f:
            content = []
            for i in f:
                content.append(orjson.loads(i))
        return content

    def check_and_create(self, type_, key, ref_level_name, gt_fuzziness_name):
        if type_ == "input":
            raise Exception("Cannot create input files")

        if key == "file":
            path = self.get(type_=type_,
                            key="file",
                            ref_level_name=ref_level_name,
                            gt_fuzziness_name=gt_fuzziness_name)
            if os.path.exists(os.path.dirname(path)):
                return path
            else:
                path = os.path.dirname(path)
        else:
            path = self.get(type_=type_,
                            key=key,
                            ref_level_name=ref_level_name,
                            gt_fuzziness_name=gt_fuzziness_name)
            if os.path.exists(path):
                return path
        split = path.split("/")
        curr_path = ""
        for split_i in split:
            curr_path = os.path.join(curr_path, split_i)
            if os.path.isdir(curr_path):
                pass
            else:
                os.mkdir(curr_path)  # this creates the magazine directories

        if key == "file":  # we created the dict before, now we add the file to the path
            path = self.get(type_=type_,
                            key="file",
                            ref_level_name=ref_level_name,
                            gt_fuzziness_name=gt_fuzziness_name)
        return path

    def save_json(self, type_, key, doc, ref_level_name, fuzziness_name):
        if key == "file":
            with open(
                self.check_and_create(
                    type_=type_,
                    key=key,
                    ref_level_name=ref_level_name,
                    gt_fuzziness_name=fuzziness_name), "wb") as f:
                f.write(orjson.dumps(doc))
        else:
            with open(
                self.check_and_create(
                    type_=type_,
                    key=key,
                    ref_level_name=ref_level_name,
                    gt_fuzziness_name=fuzziness_name) + ".json", "wb") as f:
                f.write(orjson.dumps(doc))


class Scores:
    """
    Scores class for the recall, precision, f1 scores.
    """
    def __init__(self, counts_dict={"tp": 0, "fp": 0, "fn": 0, "tn": 0}):
        self.counter = Counter(counts_dict)
        self.precision = 0
        self.recall = 0
        self.f1 = 0
        self.accuracy = 0

    def compute_scores(self):
        self.precision = self.counter["tp"]/(
            self.counter["tp"] + self.counter["fp"]
        ) if self.counter["tp"] + self.counter["fp"] != 0 else 0
        self.recall = self.counter["tp"]/(
            self.counter["tp"] + self.counter["fn"]
        ) if self.counter["tp"] + self.counter["fn"] != 0 else 0
        self.f1 = 2 * self.counter["tp"]/(
            2*self.counter["tp"] + self.counter["fp"] + self.counter["fn"]
        ) if self.counter["tp"] + self.counter["fp"] + self.counter["fn"] != 0 else 0
        self.accuracy = ((self.counter["tp"]+self.counter["tn"]) / (
            self.counter["tp"]+self.counter["tn"] + self.counter["fp"]+self.counter["fn"]
        ) if (self.counter["tp"]+self.counter["tn"] + self.counter["fp"]+self.counter["fn"]) != 0 else 0)

    def update_counter(self, counts_dict):
        self.counter.update(counts_dict)

    def get_score(self, round_to=MAX_ROUNDING):
        self.compute_scores()
        result = {
            "tp": self.counter["tp"],
            "fp": self.counter["fp"],
            "fn": self.counter["fn"],
            "tn": self.counter["tn"],
            "Precision": round(self.precision, round_to),
            "Recall": round(self.recall, round_to),
            "F1": round(self.f1, round_to),
            "Accuracy": round(self.accuracy, round_to)
        }
        return result


def clean_raw(raw: list, top_k, is_gt=False) -> list:
    """
    Given a list of entity dictionaries cleans up said dictionaries
    by unifying the references to make comparisons easier.

    :param raw:  List of entity dictionaries.
    :type raw: list
    :param top_k: How many gnd candidates to take into account.
    :type top_k: _type_
    :param is_gt: Whether the entity dictionaries are from a\
        GT file. Defaults to False., defaults to False
    :type is_gt: bool, optional
    :return: List of entity dictionaries, cleaned up to make comparisons\
        easier, especially between the coordinates.
    :rtype: list
    """

    result = []
    for ent in raw:
        if "type" in ent and ent["type"] == "PER":
            ent_mentions = []
            dictionary = {}
            if "lastname" in ent:
                dictionary["lastname"] = ent["lastname"]
            else:
                dictionary["lastname"] = ""
            if "firstname" in ent and ent["firstname"]:
                dictionary["firstname"] = " ".join(ent["firstname"])
            else:
                dictionary["firstname"] = ""
            if "abbr_firstname" in ent:
                dictionary["abbr_firstname"] = ent["abbr_firstname"]
            else:
                dictionary["abbr_firstname"] = []
            if "other" in ent:
                dictionary["other"] = ent["other"]
            else:
                dictionary["other"] = []
            dictionary["name"] = get_main_name(per_dict=dictionary)
            if "profession" in ent:
                dictionary["profession"] = ent["profession"]
            else:
                dictionary["profession"] = []
            places = []
            if "places" in ent:
                for place in ent["places"]:
                    if "name" in place:
                        places.append(place["name"])
            else:
                dictionary["places"] = []
            dictionary["places"] = places

            if is_gt:
                dictionary["gt_gnd_id"] = []
                if "gt_gnd_id" in ent:
                    dictionary["gt_gnd_id"] = ent["gt_gnd_id"]
            else:
                dictionary["gnd_candidates"] = []
                if "gnd_ids" in ent:
                    dictionary["gnd_candidates"] = ent["gnd_ids"][:top_k]

            if "references" in ent:
                for page, refs in ent["references"].items():
                    dictionary.update({
                        "page": page,
                        "year": page.split("_")[1]
                    })
                    if "refs" in refs:
                        # old linking files are set up slightly differently.
                        curr_list = refs["refs"]
                    else:
                        curr_list = refs
                    for ref in curr_list:
                        if "coords" in ref:
                            normalized_coords = set()
                            for coord in ref["coords"]:

                                coord_clean = str(coord).split(":", maxsplit=1)[0]
                                coord_clean = str(coord_clean).split(";")
                                for i in coord_clean:
                                    normalized_coords.add(i)

                            for coord in normalized_coords:
                                aux = dictionary.copy()
                                aux.update({"coord": coord})
                                ent_mentions.append(aux)

            result.append(ent_mentions)
    return result


def get_main_name(per_dict: dict) -> str:
    """
    Given a person dictionary returns the persons name as a string.


    :param per_dict: Person entity dictionary.
    :type per_dict: dict
    :return: Name of the person.
    :rtype: str
    :Example:
    >>> {"lastname":"Müller", "firstname": "Otto"} => "Otto Müller"
    >>> {"lastname":"Müller", "abbr_firstname": "O."} => "O. Müller"
    """

    if "lastname" in per_dict and per_dict["lastname"]:
        if "firstname" in per_dict and per_dict["firstname"]:
            return per_dict["firstname"] + " " + per_dict["lastname"]
        if "abbr_firstname" in per_dict and per_dict["abbr_firstname"]:
            return " ".join(
                per_dict["abbr_firstname"]
            ) + " " + per_dict["lastname"]
    elif "firstname" in per_dict and per_dict["firstname"]:
        if "abbr_firstname" in per_dict and per_dict["abbr_firstname"]:
            return per_dict["firstname"] + " " + " ".join(
                per_dict["abbr_firstname"]
            )
    elif "abbr_firstname" in per_dict and per_dict["abbr_firstname"]:
        return " ".join(per_dict["abbr_firstname"])
    elif "other" in per_dict:
        for other_elem in per_dict["other"]:
            return " ".join(other_elem)
    return "--"


def label_entity(ent: dict, gt: list) -> str:
    """
    Given an entity and a list of ground-truth entities,
    checks if they refer to the same person and returns what
    the ground truth gndid would be.

    :param ent: Person dictionary.
    :type ent: dict
    :param gt: List of person dictionaries in the ground-truth files.
    :type gt: list
    :return: Ground-truth gnd_id, or "" if none exists.
    :rtype: str
    """

    for g in gt:
        for f in g:
            if ent["page"] == f["page"] and ent["coord"] == f["coord"]:
                return f["gt_gnd_id"]
    return ""


def eval_entity(entity: dict) -> dict:
    """
    Get evaluation dictionary for given entity and its candidates.

    :param entity: Person entity dictionary.
    :type entity: dict
    :return: Dictionary of "tp", "fp", "tn", "fn" counts.
    :rtype: dict
    """

    counts = {"tp": 0, "fp": 0, "tn": 0, "fn": 0}

    gnd_candidates = []
    for x in entity["candidates"]:
        if x == []:
            gnd_candidates.append("")
        else:
            gnd_candidates += x
    if entity["label"] == "":
        if all([x == "" for x in gnd_candidates]):
            counts["tn"] += 1
        else:
            counts["fp"] += 1
    else:
        if entity["label"] not in gnd_candidates:
            if all([x == "" for x in gnd_candidates]):
                counts["fn"] += 1
            else:
                counts["fp"] += 1
        else:
            counts["tp"] += 1

    return counts


def eval_entity_inkb(entity: dict) -> dict:
    """
    Get evaluation dictionary for given entity and its candidates.
    Only evaluates disambiguation, so if a person does not have a GT gnd-id
    they are not considered for this score.

    :param entity: Person entity dictionary.
    :type entity: dict
    :return: Dictionary of "tp", "fp", "tn", "fn" counts.
    :rtype: dict
    """

    counts = {"tp": 0, "fp": 0, "tn": 0, "fn": 0}

    gnd_candidates = []
    for x in entity["candidates"]:
        if x == []:
            gnd_candidates.append("")
        else:
            gnd_candidates += x
    if entity["label"] != "":
        if entity["label"] not in gnd_candidates:
            if all([x == "" for x in gnd_candidates]):
                counts["fn"] += 1
            else:
                counts["fp"] += 1
        else:
            counts["tp"] += 1

    return counts


def eval_references(entity: dict) -> dict:
    """
    Get evaluation dictionary for given entity and its candidates.
    Count not just the entities but the references, in order to give more
    weight to entities which occur often.

    :param entity: Person entity dictionary.
    :type entity: dict
    :return: Dictionary of "tp", "fp", "tn", "fn" counts.
    :rtype: dict
    """

    counts = {"tp": 0, "fp": 0, "tn": 0, "fn": 0}

    gnd_candidates = []
    for x in entity["candidates"]:
        if x == []:
            gnd_candidates.append([""])
        else:
            gnd_candidates.append(x)
    for i, label in enumerate(entity["labels"]):
        if label == "":
            if all([x == "" for x in gnd_candidates[i]]):
                counts["tn"] += 1
            else:
                counts["fp"] += 1
        else:
            if label in gnd_candidates[i]:
                counts["tp"] += 1
            else:
                if all([x == "" for x in gnd_candidates[i]]):
                    counts["fn"] += 1
                else:
                    counts["fp"] += 1
                    counts["fn"] += 1
    return counts


def eval_references_inkb(entity: dict) -> dict:
    """
    Get evaluation dictionary for given entity and its candidates.
    Count not just the entities but the references, in order to give more
    weight to entities which occur often.
    Only evaluates disambiguation, so if a person does not have a GT gnd-id
    they are not considered for this score.

    :param entity: Person entity dictionary.
    :type entity: dict
    :return: Dictionary of "tp", "fp", "tn", "fn" counts.
    :rtype: dict
    """

    counts = {"tp": 0, "fp": 0, "tn": 0, "fn": 0}

    gnd_candidates = []
    for x in entity["candidates"]:
        if x == []:
            gnd_candidates.append([""])
        else:
            gnd_candidates.append(x)
    for i, label in enumerate(entity["labels"]):
        if label != "":
            if label in gnd_candidates[i]:
                counts["tp"] += 1
            else:
                if all([x == "" for x in gnd_candidates[i]]):
                    counts["fn"] += 1
                else:
                    counts["fp"] += 1
                    counts["fn"] += 1
    return counts


def evaluate_person(gt: list, linked: list, ref_level=True,
                    top_k=3, inkb_score=False) -> dict:
    """
    This function returns the true and false positives, as well as the true
    and false negatives of the linked file based on the ground-truth file.

    The evaluation can be done on reference level (every time a person
    is mentioned) and on entity level (every person counts only once).

    Special care has to be taken for entities with several ground-truth ids,
    which can happen when aggregation changed and now what used to be two
    person entities became one.

    :param gt: List of ground-truth entities.
    :type gt: list
    :param linked: List of linked entities.
    :type linked: list
    :param ref_level: If the evaluation should be done on\
        reference-level. If False, it is done on entity level,\
        defaults to True
    :type ref_level: bool, optional
    :param top_k: How many of the gnd candidates to take into\
        account, defaults to 3
    :type top_k: int, optional
    :param inkb_score: Whether to only evaluate disambiguation,\
        so only count if a person does have a GND entry, defaults to False
    :type inkb_score: bool, optional
    :return: Dictionary describing the true and false positives, and true\
        and false negatives of this particular magazine-year.
    :rtype: dict
    """

    references_counter = Counter({"tp": 0, "fp": 0, "fn": 0, "tn": 0})
    entities_counter = Counter({"tp": 0, "fp": 0, "fn": 0, "tn": 0})

    # clean up data
    gt_data = []
    linked_data = []

    input_linked = linked
    gt = clean_raw(gt, is_gt=True, top_k=top_k)
    gt_data += gt
    input_linked = clean_raw(input_linked, top_k=top_k)

    # due to non-determinism in the flair NER:
    all_refs_gt = [
        ent["page"]+ent["coord"] for gt_elems in gt for ent in gt_elems
    ]
    all_refs_linked = [
        ent["page"]+ent["coord"] for li_el in input_linked for ent in li_el
    ]
    all_valid_refs = set(all_refs_gt).intersection(set(all_refs_linked))

    for ent_variations in input_linked:
        ent_instances = []
        for ent in ent_variations:
            if ent["page"]+ent["coord"] in all_valid_refs:
                ent_instances.append({
                    "ent": ent, "label": label_entity(ent, gt)
                })
        if ent_instances:
            linked_data.append(ent_instances)

    # but now linked_data is on reference level, we want to aggregate them:
    ent_cand_label = []
    for entity_list in linked_data:
        coord_list = []
        label_list = []
        candidates_list = []
        # now i need the candidates, in the rulebased case we only have access
        # to the gnd_ids
        for ent_dict in entity_list:
            ent = ent_dict["ent"]
            coord_list.append({
                "page": ent.pop("page", ""),
                "coords": ent.pop("coord", "")
            })
            label_list.append(ent_dict["label"])
            candidates_list.append(ent["gnd_candidates"])
        ent_cand_label.append({
            "entity": ent,
            "candidates": candidates_list,
            "occurences": coord_list,
            "labels": label_list
        })

    list_of_good_entities = []
    list_of_problematic_entities = []
    for ent_dict in ent_cand_label:
        if len(set(ent_dict["labels"])) > 1:
            for label in set(ent_dict["labels"]):
                ent_dict["label"] = label
                list_of_problematic_entities.append(ent_dict.copy())
        else:
            ent_dict["label"] = set(ent_dict["labels"]).pop()
            list_of_good_entities.append(ent_dict)

    list_of_all_entities = list_of_good_entities+list_of_problematic_entities

    if ref_level:
        scores_mention = Scores()

        for entity in list_of_all_entities:
            if inkb_score:
                scores_mention.update_counter(counts_dict=eval_references_inkb(entity))
            else:
                scores_mention.update_counter(counts_dict=eval_references(entity))

        references_counter["tp"] = scores_mention.get_score()["tp"]
        references_counter["fp"] = scores_mention.get_score()["fp"]
        references_counter["tn"] = scores_mention.get_score()["tn"]
        references_counter["fn"] = scores_mention.get_score()["fn"]

        return references_counter
    scores_entity = Scores()
    for entity in list_of_all_entities:
        if inkb_score:
            scores_entity.update_counter(counts_dict=eval_entity_inkb(entity))
        else:
            scores_entity.update_counter(counts_dict=eval_entity(entity))

    entities_counter["tp"] = scores_entity.get_score()["tp"]
    entities_counter["fp"] = scores_entity.get_score()["fp"]
    entities_counter["tn"] = scores_entity.get_score()["tn"]
    entities_counter["fn"] = scores_entity.get_score()["fn"]

    return entities_counter
