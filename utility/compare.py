"""
Comparison functions for Person entities
"""
import argparse
import orjson
import logging


def compare_gnd_info(entity_pre: dict, entity_post: dict) -> bool:
    """
    Checks if the gnd ids are the same after some code changes occurred.

    :param entity_pre: The entity before any changes were made to the code.
    :type entity_pre: dict
    :param entity_post: The entity after code changes.
    :type entity_post: dict
    :raises Exception: Throws an exception if the gnds do not match.
    :return: True if nothing changed, throws an exception in all other cases.
    :rtype: bool
    """

    if set(entity_pre["gnd_ids"]) != set(entity_post["gnd_ids"]):
        raise Exception("The found gnd_ids of at least one entity changed.")

    return True


def compare_references(entity_pre: dict, entity_post: dict) -> bool:
    """
    Checks if the references are the same after some code changes occurred.

    :param entity_pre: The entity before any changes were made to the code.
    :type entity_pre: dict
    :param entity_post: The entity after code changes.
    :type entity_post: dict
    :raises Exception: If any of the fields do not match, throws an exception\
        indicating where the mismatch was.
    :return: True if nothing changed, throws an exception in all other cases.
    :rtype: bool
    """

    if entity_post["references"].keys() != entity_pre["references"].keys():
        raise Exception("The page references do not match for at least one entity")

    for page in entity_pre["references"]:
        if (len(entity_pre["references"][page]["refs"])
           != len(entity_post["references"][page]["refs"])):
            raise Exception("The number of references for this entity changed.")
        for idy, refs_pre in enumerate(entity_pre["references"][page]["refs"]):
            if (refs_pre["sent"] !=
               entity_post["references"][page]["refs"][idy]["sent"]):
                raise Exception("The number of the sentence where at least one entity is mentioned changed.")
            if (refs_pre["coords"] !=
               entity_post["references"][page]["refs"][idy]["coords"]):
                raise Exception("The coordinates where at least one entity is mentioned changed.")
    return True


def compare_linking_person(list_pre: list, list_post: list) -> bool:
    """
    Compares the list of entities before and after code changes.

    :param list_pre: List of entities before any code changes.
    :type list_pre: list
    :param list_post: List of entities after code changes.
    :type list_post: list
    :raises Exception: If any of the fields do not match, throws an exception\
        indicating where the mismatch was. The order of the found\
        entities matters.
    :return: True if nothing changed, throws an exception in all other cases.
    :rtype: bool
    """

    for idx, entity_pre in enumerate(list_pre):
        if entity_pre["type"] == "PER":
            entity_post = list_post[idx]

            if entity_pre["lastname"] != entity_post["lastname"]:
                raise Exception("The last name of at least one entity changed.")
            if entity_pre["firstname"] != entity_post["firstname"]:
                # ordering matters!
                raise Exception("The first names of at least one entity changed.")
            if entity_pre["abbr_firstname"] != entity_post["abbr_firstname"]:
                # ordering matters!
                raise Exception("The abbreviated first names of at least one entity changed.")
            if set(entity_pre["address"]) != set(entity_post["address"]):
                # order does not matter
                raise Exception("The address of at least one entity changed.")
            if set(entity_pre["titles"]) != set(entity_post["titles"]):
                # titles have a specified order but some magazines don't
                # adhere to that
                raise Exception("The titles of at least one entity changed.")
            if set(entity_pre["profession"]) != set(entity_post["profession"]):
                raise Exception("The profession of at least one entity changed.")
            if (set([x for y in entity_pre["other"] for x in y]) !=
               set([x for y in entity_post["other"] for x in y])):
                raise Exception("The 'other' field of at least one entity changed.")
            if entity_pre["type"] != entity_post["type"]:
                raise Exception("The type of at least one entity changed.")
            if entity_pre["id"] != entity_post["id"]:
                raise Exception("The id of at least one entity changed.")

            compare_references(entity_pre, entity_post)
            compare_gnd_info(entity_pre, entity_post)

    return True


def compare_linking_places(list_pre: list, list_post: list) -> bool:
    """
    Compares the places lists before and after code changes.

    :param list_pre: List of entities before any code changes.
    :type list_pre: list
    :param list_post: List of entities after code changes.
    :type list_post: list
    :raises Exception: If any of the fields do not match, throws an exception\
        indicating where the mismatch was. The order of the found\
        entities matters.
    :return: True if nothing changed, throws an exception in all other cases.
    :rtype: bool
    """

    for idx, entity_pre in enumerate(list_pre):
        if (entity_pre["type"] == "CIT" or entity_pre["type"] == "CTR"
           or entity_pre["type"] == "GEO"):
            entity_post = list_post[idx]

            # compare keys
            if entity_pre.keys() != entity_post.keys():
                raise Exception("The entity keys have changed.")
            if entity_pre["name"] != entity_post["name"]:
                raise Exception("The name of at least one entity changed.")
            if set(entity_pre["tokens"]) != set(entity_post["tokens"]):
                raise Exception("The tokens of at least one entity changed.")
            if entity_pre["type"] != entity_post["type"]:
                raise Exception("The type of at least one entity changed.")
            if entity_pre["id"] != entity_post["id"]:
                raise Exception("The id of at least one entity changed.")

            compare_references(entity_pre, entity_post)
            compare_gnd_info(entity_pre, entity_post)

    return True


def compare_linking(output_path_pre: str, output_path_post: str) -> bool:
    """Compares linking output of two jsons at the given paths.

    :param output_path_pre: Path to the linking output json before any\
        changes were made.
    :type output_path_pre: str
    :param output_path_post: Path to the linking output json after changes\
        were made.
    :type output_path_post: str
    :raises Exception: If any of the fields do not match, throws an exception\
        indicating where the mismatch was. The order of the found\
        entities matters.
    :return: True if nothing changed, throws an exception in all other cases.
    :rtype: bool
    """

    with open(output_path_pre, encoding="utf8") as json_pre:
        linking_data_pre = orjson.loads(json_pre.read())

    with open(output_path_post, encoding="utf8") as json_post:
        linking_data_post = orjson.loads(json_post.read())

    # sanity check
    if len(linking_data_pre) != len(linking_data_post):
        raise Exception("The number of entities found changed")

    # compare
    if (compare_linking_person(linking_data_pre, linking_data_post) and
       compare_linking_places(linking_data_pre, linking_data_post)):
        logging.info("Success! Nothing changed about the linking output.")

    return True


def compare_tagging(output_path_pre: str, output_path_post: str) -> bool:
    """
    Compares tagging output of two jsons at the given paths.

    :param output_path_pre: Path to the tagging output json before any\
        changes were made.
    :type output_path_pre: str
    :param output_path_post: Path to the tagging output json after changes\
        were made.
    :type output_path_post: str
    :raises Exception: If any of the fields do not match, throws an exception\
        indicating where the mismatch was. The order of the found\
        entities matters.
    :return: True if nothing changed, throws an exception in all other cases.
    :rtype: bool
    """

    with open(output_path_pre, 'r', encoding='utf-8') as json_file_pre:
        json_list_pre = list(json_file_pre)

    with open(output_path_post, 'r', encoding='utf-8') as json_file_post:
        json_list_post = list(json_file_post)

    # sanity check
    if len(json_list_pre) != len(json_list_post):
        raise Exception("The tagging output is not the same length.")

    for idx, json_str_pre in enumerate(json_list_pre):
        result_pre = orjson.loads(json_str_pre)
        result_post = orjson.loads(json_list_post[idx])
        # dict of page.txt to a list of lists

        # sanity check
        if result_pre.keys() != result_post.keys():
            raise Exception("The pages processed are not the same.")

        # compare
        for page in result_pre:
            # sanity check
            if len(result_pre[page]) != len(result_post[page]):
                raise Exception("The lists of processed tokens are not the same.")
            for idy, entry in enumerate(result_pre[page]):
                for idz, token_dict in enumerate(entry):
                    if (token_dict["token"] !=
                       result_post[page][idy][idz]["token"]):
                        raise Exception("At least one token changed.")
                    if (token_dict["coord"] !=
                       result_post[page][idy][idz]["coord"]):
                        raise Exception("The coordinate of at least one token changed.")
                    if (token_dict["normalized"] !=
                       result_post[page][idy][idz]["normalized"]):
                        raise Exception("At least one token changed.")
                    if (token_dict["tag"] !=
                       result_post[page][idy][idz]["tag"]):
                        raise Exception("At least one token changed.")

    logging.info("Success! Nothing changed about the tagging output.")
    return True


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--magazine", type=str, default="obl")
    parser.add_argument("--year", type=str, default="2004_000")
    parser.add_argument("--task", type=str, default="prep,tag,finish")

    args = parser.parse_args()

    mag_year_json = args.magazine + "/" + args.year + ".json"
    task = args.task

    output_path_pre = "./data/test_data/output_before/"+task+"/"+mag_year_json
    output_path_post = "./data/test_data/output/"+task+"/"+mag_year_json

    if task == "prep,tag,finish":
        output_path_pre = "./data/test_data/output_before/tag/"+mag_year_json+"l"
        output_path_post = "./data/test_data/output/tag/"+mag_year_json+"l"
        compare_tagging(output_path_pre, output_path_post)

        output_path_pre = "./data/test_data/output_before/link/"+mag_year_json
        output_path_post = "./data/test_data/output/link/"+mag_year_json
        compare_linking(output_path_pre, output_path_post)

    elif task == "link":
        compare_linking(output_path_pre, output_path_post)

    elif task == "tag":
        compare_tagging(output_path_pre.replace(".json", ".jsonl"),
                        output_path_post.replace(".json", ".jsonl"))
    else:
        raise Exception("Please specify a valid task: 'prep,tag,finish', 'link' or 'tag'.")


if __name__ == "__main__":
    main()
