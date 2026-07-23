#! /usr/bin/python3

"""
Read entities, then aggregate them.

Update 09.03.:
We do not append full articles anymore, because we'd need to attach
too much information which bloats the file.
Instead, we only append the article-ID, so in the other steps like
aggregation, linking and prep_import we can simply use that id to get the
article information from the xml.
"""

import orjson
import glob
from multiprocessing import Pool
import os
from datetime import datetime
import logging
from lxml import etree
from utility.utils import save_data_intermediate
from utility.settings import settings


def initialize_found_entry() -> dict:
    """Returns an empty person entity dictionary."""
    entity = {
        "info": {
            "lastnames": [],
            "firstnames": [],
            "abbr_firstnames": [],
            "occupations": [],
            "titles": [],
            "address": [],
            "others": []
            },
        "pid": [],
        "pageNames": [],
        "pageNo": [],
        "sentenceNo": [],
        "positions": []
    }
    return entity


def initialize_found_place_entry() -> dict:
    """Returns an empty place entity dictionary."""
    entity = {
        "tokens": [],
        "type": "",
        "pid": [],
        "pageNames": [],
        "pageNo": [],
        "sentenceNo": [],
        "positions": []
    }
    return entity


def add_info_to_entity(entity: dict,
                       tag: str,
                       token: dict,
                       pageNo: str,
                       sentNo: str,
                       pageName: str,
                       articles: list,
                       pid: int) -> None:
    """
    Adds information to a person entity based on the provided token dictionary\
    and metadata about the page.

    :param entity: The person entity dictionary to update.
    :type entity: dict
    :param tag: The type of the entity information (e.g., "LN" for last\
        name, "FN" for first name).
    :type tag: str
    :param token: A dictionary containing token information, including\n
        - "token" (str): The token text.\n
        - "coord" (tuple): The coordinates of the token.\n
    :type token: dict
    :param pageNo: The page number where the entity is located.
    :type pageNo: str
    :param sentNo: The sentence number where the entity is located.
    :type sentNo: str
    :param pageName: The name of the page where the entity is located.
    :type pageName: str
    :param articles: A list of articles associated with the page.
    :type articles: list
    :param pid: The physical ID of the page.
    :type pid: int

    Notes:
        - Updates the `info` dictionary in the entity with the token text\
            based on the tag.
        - Appends metadata such as `pid`, `pageNames`, `positions`, `pageNo`,\
            and `sentenceNo` to the entity.
        - Sets the `type` of the entity to "PER" (person).
        - Processes and adds article information to the entity if not already\
            present.
        - Logs a warning if an unknown tag is encountered.
    """

    if tag == "LN":
        entity["info"]["lastnames"].append(token["token"])
    elif tag == "FN" and token["token"][-1] != ".":
        entity["info"]["firstnames"].append(token["token"])
    elif tag == "FN":
        entity["info"]["abbr_firstnames"].append(token["token"])
    elif tag == "OC":
        entity["info"]["occupations"].append(token["token"])
    elif tag == "TL":
        entity["info"]["titles"].append(token["token"])
    elif tag == "AN":
        entity["info"]["address"].append(token["token"])
    elif tag == "OT":
        entity["info"]["others"].append(token["token"])
    elif tag == "COM":
        pass
    else:
        entity["info"]["others"].append(token["token"])
        logging.info("UNKNOWN TAG ENCOUNTERED: "+tag)
    entity["pageNames"].append(pageName)
    entity["pid"].append(pid)
    entity["positions"].append(token["coord"])
    entity["pageNo"].append(pageNo)
    entity["sentenceNo"].append(sentNo)
    entity["type"] = "PER"

    # Add information about structure, only needs to be done once
    if "articles" not in entity:
        articles = decide_articles(articles)
        entity["articles"] = articles


def add_info_to_place_entity(entity: dict,
                             tag: str,
                             token: dict,
                             pageNo: str,
                             sentNo: str,
                             pageName: str,
                             articles: list,
                             pid: int) -> None:
    """
    Adds information to a place entity based on the provided token dict and\
    metadata about the page.

    :param entity: The place entity dictionary to update.
    :type entity: dict
    :param tag: The type of the place entity (e.g., "LOC").
    :type tag: str
    :param token: A dictionary containing token information, including\n
        - "token" (str): The token text.\n
        - "coord" (tuple): The coordinates of the token.\n
    :type token: dict
    :param pageNo: The page number where the entity is located.
    :type pageNo: str
    :param sentNo: The sentence number where the entity is located.
    :type sentNo: str
    :param pageName: The name of the page where the entity is located.
    :type pageName: str
    :param articles: A list of articles associated with the page.
    :type articles: list
    :param pid: The physical ID of the page.
    :type pid: int

    Notes:
        - Updates the `tokens` list in the entity with the token text.
        - Sets the `type` of the entity to the provided tag.
        - Appends metadata such as `pid`, `pageNames`, `positions`, `pageNo`,\
        and `sentenceNo` to the entity.
        - Processes and adds article information to the entity if not already\
        present.
    """

    entity["tokens"].append(token["token"])
    entity["type"] = tag
    entity["pid"].append(pid)
    entity["pageNames"].append(pageName)
    entity["positions"].append(token["coord"])
    entity["pageNo"].append(pageNo)
    entity["sentenceNo"].append(sentNo)
    # Add information about structure, only needs to be done once
    if "articles" not in entity:
        articles = decide_articles(articles)
        entity["articles"] = articles


def decide_articles(articles: list) -> list:
    """
    Given a list of lists, only keeps the entries that are exactly length 2.\
    Or, if the input is only length one, keeps it unchanged.

    :param articles: List of articles
    :type articles: list
    :return: Cleaned list of pages where we only keep the articles with\
            exactly two pages.
    :rtype: list
    """

    if len(articles) == 1:
        return articles
    pages = [r for r in articles if len(r) == 2]

    return pages


def adjust_information(entitylist: list) -> None:
    """
    Adjusts page information in the given entity list.\
    Only keeps first value in "pageNames", "pageNo", "sentenceNo", and "pid".\
    Logs a warning if there are several values for these entries.\
    If an entity has no "pid", this entry is removed.

    :param entitylist: List of entity dictionaries, where each dict\
            contains page information on where this entity appears.
    :type entitylist: list
    """

    for entity in entitylist:
        for key in ["pageNames", "pageNo", "sentenceNo", "pid"]:
            value = entity[key]
            set_value = set(value)
            if len(set_value) > 1:
                logging.warning(
                 "WHY DOES THIS REFERENCE CONTAIN MULTIPLE SENTENCES"
                )
            if len(set_value) > 0:
                entity[key] = list(set_value)[0]
            elif key == "pid":
                # if no pids were appended, we delete that entry as it's only
                # used for the frontend and Kai informed me not to write it if
                # not used
                del entity[key]


def get_article_info(article):
    article_dict = {}
    for c in article:
        if "type" in c.attrib:
            article_dict["elementType"] = c.attrib["type"]
        for d in article[0]:
            if "type" in d.attrib:
                if 'Title' in d.attrib["type"]:
                    article_dict["title"] = d.text
                if "Author" in d.attrib["type"]:
                    article_dict.setdefault("authors", []).append(d.text)
                if "DOI" in d.attrib["type"]:
                    article_dict["doi"] = d.text
    return article_dict


def get_structure_info(year: tuple, custom_path=None) -> dict:
    """
    Retrieves structural information for a given year from an XML file.

    :param year:
        - short (str): The shortname of the journal (e.g., "bse").\n
        - year (str): The year of the journal (e.g., "2025").
    :type year: tuple
    :param custom_path: Path to a custom XML file for debugging, defaults to None
    :type custom_path: _type_, optional
    :return: A dictionary where keys are page filenames (e.g., "page1.txt")\
        and values are tuples\n
            - pid (str): The physical ID of the page (e.g., "doc123:page1").
            - articles (list): A list of article IDs associated with the page.
            - pagenum (str): The physical page number.
    :rtype: dict

    Notes:
        - If `custom_path` is provided, it is used to parse the XML file.
        - If `custom_path` is not provided, the function constructs the path\
        to the XML file based on the `year` tuple.
        - Handles cases where the XML file is missing or inaccessible by\
        returning an empty dictionary.
        - Skips journal-level connections and focuses on article-level\
        connections.
        - Extracts the filename for each page by replacing the `.jpg`\
        extension with `.txt`.
    """

    short, year = year

    if custom_path:
        # We can use this for local debugging
        root = etree.parse(custom_path).getroot()
    else:
        if short.startswith("bse"):
            xml_storage = os.path.join(
                settings.DATA2_MNT,
                "xml.cache.prod01",
                short,
                f"{short.upper()}-{year}.xml"
            )
        else:
            xml_storage = os.path.join(
                settings.DATA2_MNT,
                "xml.cache.prod01",
                short,
                f"{short}_{year}.xml"
            )

        try:
            root = etree.parse(xml_storage).getroot()
        except Exception:
            try:
                xml_storage = xml_storage.replace("prod01", "staging01")
                root = etree.parse(xml_storage).getroot()
            except Exception:
                return {}

    pages_to_articles = {}

    document_id = root.find("./element-list/element[@type='Agora:Document']/attr[@type='Agora:DocumentID']").text

    page_elems = root.findall("./element-list/element[@type='Agora:ImageSet']/element[@type='Agora:Page']")

    for page_elem in page_elems:
        articles = []
        idx = page_elem.get("ID")
        pagenum = page_elem.find("./attr[@type='Agora:PhysicalNo']").text
        links = root.findall("./link-list/link[@to='{0}']".format(idx))
        for link in links:
            article_idx = link.get("from")
            # NOTE: Journal-level connections should usually be uninteresting,
            # so we skip them specifically. For completeness sake, we might
            # take them in as well though.
            is_journal = root.find("./element-list/element[@type='Journal'][@ID='{0}']".format(article_idx))
            if is_journal:
                continue
            article = root.find("./element-list/element[@type='Journal']//element[@ID='{0}']".format(article_idx))
            articles.append({article_idx: get_article_info([article])})

            # if the first element found was not an article
            # we look for the first ancestor being one
            if article.get("type") == "Article":
                continue

            article_ancestor = article.xpath(
                "ancestor::element[@type='Article']"
            )
            if not article_ancestor:
                continue

            ancestor_idx = article_ancestor[0].get("ID")
            ancestor_article = root.findall(f".//*[@ID='{ancestor_idx}']")
            articles.append({ancestor_idx: get_article_info(ancestor_article)})

        resource_id = page_elem.find("./resource-id").text
        path = root.find("./resource-list/resource[@ID='{0}']/attr[@type='Agora:Path']".format(resource_id)).text
        filename = os.path.basename(path).replace(".jpg", ".txt").lower()
        pages_to_articles[filename] = (
            document_id + ":" + idx,
            articles,
            pagenum
        )

    return pages_to_articles


def process_page(page: str,
                 sentences: list,
                 entitylist: list,
                 placeEntitylist: list,
                 structure_info: dict,
                 i: int) -> None:
    """
    Processes a single page of tagged sentences to extract entity information.

    :param page: The name of the page being processed.
    :type page: str
    :param sentences: A list of sentences, where each sentence is a list\
        of tokens. Each token is a dictionary containing information such\
        as "tag", "token", and "coord".
    :type sentences: list
    :param entitylist: A list to store extracted person entities.
    :type entitylist: list
    :param placeEntitylist: A list to store extracted place entities.
    :type placeEntitylist: list
    :param structure_info: A dictionary containing structural information\
        for the page. Keys are page names, and values are tuples of\
        (pid, articles, pagenum).
    :type structure_info: dict
    :param i: A fallback page number to use if no structural information is\
        available.
    :type i: int

    Notes:
        - Extracts person entities (tagged with "PER") and place entities\
        (tagged with other tags).
        - Uses BIO tagging format to identify the beginning ("B-") and\
        continuation ("I-") of entities.
        - Updates the `entitylist` and `placeEntitylist` with extracted\
        entities.
        - Handles cases where structural information is missing by using the\
        fallback page number.
        - Logs warnings for unknown tags encountered during processing.
    """
    # In this new format, enumeration will not suffice. Use PhysicalID from
    # the structural information!
    # The reason for this is that for efficiency reasons, a page might be
    # split into multiple lines in the jsonl.

    # look up structure information for this page in the dictionary
    if page in structure_info:
        # We use the PhysicalNo of the page if it's available
        pid, articles, pagenum = structure_info[page]
        i = int(pagenum)
    else:
        articles = []
        pid = None

    for j, sentence in enumerate(sentences):
        entity = None
        current_tag = None
        for token in sentence:
            tag = token["tag"]
            if tag[2:5] == "PER":
                tagstart = tag[:6]
                tagend = tag[6:]
                if tagstart.startswith("B-"):
                    if entity:
                        if current_tag == "PER":
                            entitylist.append(entity)
                        elif placeEntitylist is not None:
                            placeEntitylist.append(entity)
                    entity = initialize_found_entry()
                    add_info_to_entity(
                        entity, tagend, token, i, j, page, articles, pid
                    )
                elif tagstart.startswith("I-"):
                    if not entity:
                        entity = initialize_found_entry()
                    elif current_tag != "PER" and placeEntitylist is not None:
                        placeEntitylist.append(entity)
                        entity = initialize_found_entry()
                    add_info_to_entity(
                        entity, tagend, token, i, j, page, articles, pid
                    )
                else:
                    logging.info("UNKNOWN TAG ENCOUNTERED: "+tag)
                current_tag = "PER"
            elif tag == "O" or tag.endswith("adj"):
                # ADJ tags will be ignored for the moment
                # Consider resetting BIO reset here
                # current_tag = "O"
                continue
            elif placeEntitylist is not None:  # all place tags
                tagstart = tag[:2]
                tagend = tag[2:]
                if tagstart.startswith("B-"):
                    if entity:
                        if current_tag == "PER":
                            entitylist.append(entity)
                        else:
                            placeEntitylist.append(entity)
                    entity = initialize_found_place_entry()
                    add_info_to_place_entity(
                        entity, tagend, token, i, j, page, articles, pid
                    )
                elif tagstart.startswith("I-"):
                    if not entity:
                        entity = initialize_found_place_entry()
                    elif current_tag != tagend:
                        placeEntitylist.append(entity)
                        entity = initialize_found_place_entry()
                    elif current_tag == "PER":
                        entitylist.append(entity)
                        entity = initialize_found_place_entry()
                    add_info_to_place_entity(
                        entity, tagend, token, i, j, page, articles, pid
                    )
                else:
                    logging.info("UNKNOWN TAG ENCOUNTERED: "+tag)
                current_tag = tagend
        if entity:
            if current_tag == "PER":
                entitylist.append(entity)
            elif placeEntitylist is not None:
                placeEntitylist.append(entity)


def get_found_names(items: tuple) -> list:
    """
    Extracts and processes entity information (person and place names) from
    tagged files.

    :param items:
        - year (tuple): A tuple of journal shortname and year as strings
          (e.g., ("abc", "2025")).
        - pages (str or list): Either a single string for the tagging
          output file or a list of paths to the tagging output files.
        - places (bool): If places should be considered as well.
    :type items: tuple
    :return: The first entry is a list of all found entities (person and
        place names) with their associated metadata. The second is the
        year information (journal shortname and year). The third is a
        list of all the tagged files that belong to this year.
    :rtype: tuple (list, tuple)

    .. note::
        - Person names and place names are written in the same file but
          are sorted before printing (person names first).
        - When looking up the structure information for the pages, we use
          the information given by the raw data folder structure at the
          moment. This means that in rare cases two actually different
          volumes might have the same short-year combination, causing
          problems when linking pages to structure elements. This will
          change only once structure files become the initial pipeline
          input, which requires a larger rework — for now some
          information will simply be missing at the start.
        - Handles cases where tagged files are split into multiple lines
          for efficiency.
        - Adjusts entity information to remove duplicates and ensure
          consistency.
        - Missing structure information may result in incomplete metadata
          for some entities.
    """

    year, pages, places = items
    # get structure information per page in dictionary form (key: pagenumber,
    # value: (information about the structure, pagenumber))
    structure_info = get_structure_info(year)

    entitylist = []
    if places:
        placeEntitylist = []
    else:
        placeEntitylist = None

    # handle old files
    if isinstance(pages, str):
        with open(pages, encoding="utf8") as inf:
            p = orjson.loads(inf.read())
            for i, (page, sentences) in enumerate(p.items()):
                process_page(
                    page,
                    sentences,
                    entitylist,
                    placeEntitylist,
                    structure_info,
                    i
                )
        pages = [pages]
    else:
        for path in pages:
            with open(path, encoding="utf8") as inf:
                for line in inf:
                    line = orjson.loads(line)
                    for i, (page, sentences) in enumerate(line.items()):
                        process_page(
                            page,
                            sentences,
                            entitylist,
                            placeEntitylist,
                            structure_info,
                            i
                        )

    adjust_information(entitylist)

    if places:
        adjust_information(placeEntitylist)
        entitylist = entitylist + placeEntitylist

    return entitylist, year, pages


def populate_year_dict(year_dict: dict, file_list: list) -> None:
    """
    Populates a dictionary with year-wise data paths for processing.

    :param year_dict: A dictionary to be populated. Keys are tuples of\
        (magazine shortname, year), and values are file paths or lists of\
        file paths.
    :type year_dict: dict
    :param file_list: A list of file paths to be processed. The files can\
        be in `.json` or `.jsonl` format.
    :type file_list: list

    Notes:
        - For `.json` files, the file path is directly added to the dictionary.
        - For `.jsonl` files, all matching files are globbed and added as a\
            list.
        - Unsupported file types are ignored.
    """

    for filename in file_list:
        filetype = "." + filename.split(".")[-1]
        if filetype == ".json":
            value = filename
        elif filetype == ".jsonl":
            value = sorted(glob.glob(filename.replace(".jsonl", "*.jsonl")))
        else:
            continue
        year_dict[
            (
                os.path.normpath(filename).split(os.sep)[-2],
                os.path.basename(filename).replace(filetype, ""),
            )
        ] = value


def get_data_paths_iterative():
    """
    Generates year-wise data paths for processing based on the settings.

    :raises Exception: If no valid data paths are found in the configuration.
    :raises Exception: If an input path generated with the configuration is\
        neither a valid directory nor a valid file. This means the data paths\
        are valid, but nothing useful is in there.
    :returns: Yields: A dictionary where keys are tuples of (magazine shortname, year)\
        and values are file paths or lists of file paths.
    :rtype: Iterator[:class:`dict`]
    """

    if settings.CUSTOM_PATHS:
        inputs = settings.CUSTOM_PATHS
    else:
        # in this case instead of using custom paths we use paths to infile
        # and thus get magazine directories instead of magazine-year dirs

        LEN_MAGAZINE_SHORTNAME = 3
        inconsistent_magazine_names = [
            "bse-cr",
            "bse-me",
            "bse-pe",
            "bse-re",
            "aan-normal.zip",
            "aan-speichern.zip",
            "aan-ultra.zip",
            "grs.zip",
            'szg.zip"',
        ]
        inputs_magazine_year_level = []

        magazine_folder = sorted(glob.glob(settings.PATH_TO_INPUT_FOLDERS+"/*"))
        for magazine in magazine_folder:
            if (
                len(os.path.basename(magazine)) == LEN_MAGAZINE_SHORTNAME
                or os.path.basename(magazine) in inconsistent_magazine_names
            ):
                # it's a magazine directory.
                year_directories = sorted(glob.glob(magazine + "/*"))
                inputs_magazine_year_level += year_directories
        inputs = inputs_magazine_year_level

    year_dict = {}

    if (
        isinstance(inputs, str)
        and (
            inputs.split("/")[-1] == "tag"
            or (inputs.split("/")[-1] == ""
                and inputs.split("/")[-2] == "tag")
        )
    ):
        # process everything in the tag folder
        inputs = glob.glob(inputs + "/*")

    if inputs == []:
        raise Exception(f"No valid data paths found in {settings.model_dump(exclude={"es"})}")

    for mag_year_path in inputs:
        if os.path.isdir(mag_year_path):
            populate_year_dict(year_dict, glob.glob(mag_year_path + "/*"))
        elif os.path.isfile(mag_year_path):
            populate_year_dict(year_dict, [mag_year_path])
        else:
            raise Exception(f'The given input: {inputs} is neither a valid directory, nor a valid file.')
        if len(year_dict) >= settings.BATCH_SIZE:
            yield year_dict
            year_dict = {}
    yield year_dict


def execute_postprocessing(magazines, tasks: list, timed=True, places=False) -> None:
    """Postprocesses data based on the given configuration and tasks.

    :param magazines: Generator object containing the magazines. The object\
        is a dictionary where keys are tuples of (magazine shortname, year)\
        and the values are file paths or lists of file paths.
    :type magazines: iterator
    :param tasks: List of tasks to be performed during postprocessing.
    :type tasks: list
    :param timed: Boolean indicating whether to time the execution and log it,\
        defaults to True.
    :type timed: bool
    :param places: Boolean indicating whether to process place entities as well,\
        defaults to False.
    :type places: bool
    :returns: a list of tuples. The first value of the tuple is another\
        tuple, consisting of the year of the magazine and the shortname of\
        the magazine. The second value of the tuple is a dictionary\
        describing the data.
    :rtype: list

    Notes:
        - Logs the start and end time of the postprocessing.
        - If "CUSTOM_PATHS" is not in the settings, sets the input folder \
            path to the output folder path with "tag" appended.
        - Loads data iteratively based on the configuration.
        - Executes postprocessing on the loaded data.
        - Saves intermediate data if "agg" is not in the tasks list.
    """

    if timed:
        start_time = datetime.now()
        logging.info(f"Starting Postprocessing at {start_time}:")

    if settings.CUSTOM_PATHS is None:
        settings.PATH_TO_INPUT_FOLDERS = settings.PATH_TO_OUTFILE_FOLDER + "tag"

    postprocessed_data = []
    for data in magazines:
        if settings.BATCH_SIZE == 1:
            postprocessed_years = [get_found_names((x[0], x[1], places)) for x in data.items()]
        else:
            with Pool(settings.BATCH_SIZE) as p:
                postprocessed_years = p.map(get_found_names, [(x[0], x[1], places) for x in data.items()])
        for data, year, paths in postprocessed_years:
            logging.info(f"Postprocessed: {year}")
            postprocessed_data.append((year, data, paths))

            if "agg" not in tasks and tasks != ["finish"]:
                save_data_intermediate(year, data, "post")

    if timed:
        logging.info(f"Postprocessing took: {datetime.now() - start_time}")

    return postprocessed_data
