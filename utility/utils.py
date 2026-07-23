"""
Utility functions
"""
import argparse
import subprocess
import os
import orjson
import logging
import xml.etree.ElementTree as ET
from .settings import settings


def set_default(obj):
    """
    Helper function to translate all sets in the aggregated dictionaries into
    lists when dumping them to files.
    """
    if isinstance(obj, set):
        return list(obj)
    raise TypeError


def str2bool(value: str) -> bool:
    """
    Casts a string to a boolean value

    :param value: String input to be cast.
    :type value: str
    :raises argparse.ArgumentTypeError: If the string value cannot be cast\
        to a boolean, this error is raised.
    :return: Boolean value of the given string.
    :rtype: bool
    """

    value = str(value)
    if value.lower() in {"true", "1"}:
        return True
    if value.lower() in {"false", "0"}:
        return False
    raise argparse.ArgumentTypeError(
        "Boolean value expected (true/false, 1/0)"
    )


def positive_int(value: str) -> int:
    """Custom type function for argparse that ensures a positive integer."""
    ivalue = int(value)
    if ivalue <= 0:
        raise argparse.ArgumentTypeError(f"{value} is not a positive integer")
    return ivalue


def parse_arguments() -> argparse.Namespace:
    """
    Parses command-line arguments for the script.

    :return: An object containing the parsed command-line\
        arguments.
    :rtype: argparse.Namespace

    Command-line Arguments:
        - tasks (str): Comma-separated list of tasks to perform.\
        Default is "prep,tag,finish".\n
        - gpu (str): GPU identifier to use. Default is "0".\n
        - magazine_year_paths (str): Paths to magazine year data.\n
        - eval_level (str): Evaluation level. Default is "ref".\n
    """

    parser = argparse.ArgumentParser()
    parser.add_argument("--tasks", type=str, default="finish")
    parser.add_argument("--gpu", type=positive_int, default=0)
    parser.add_argument("--magazine_year_paths", type=str)
    parser.add_argument(
        "--config_file", type=str, default="./configs/configurations.json"
    )
    parser.add_argument(
        "--eval_level", type=str, default="ref", choices=["ref", "ent"]
    )

    args = parser.parse_args()
    return args


def check_gpu(args: argparse.Namespace) -> int:
    """
    Checks if an Nvidia GPU is available and sets the GPU number accordingly.

    :param args: An object containing the GPU argument. It should have an
        attribute 'gpu' which is a string representing the GPU number.
    :type args: argparse.Namespace
    :return: The GPU number to be used. If no Nvidia GPU is detected,
        it returns 0 indicating that the code will run on CPU.
    :rtype: int
    """

    if args.gpu != 0:
        try:
            subprocess.check_output("nvidia-smi")
        except Exception:
            logging.info("No Nvidia GPU detected, the code will run on CPU.")
            return 0
    return args.gpu


def save_data_intermediate(year: list, files: dict, taskname: str):
    """
    Saves the data given in a "taskname" folder in the oufile folder
    specified in the configurations. If the "taskname" folder doesn't exist,
    one is created. As opposed to "save_data", this function combines all the
    years for a magazine instead of saving each year individually into a file.

    :param year: A list [mag, year, ..-] where the first entry is\
        the magazine shortname and the following entry (or entries) is the\
        year (or the years) we processed.
    :type year: list
    :param files: A dictionary containing the intermediate results of\
        the given taskname.
    :type files: dict
    :param taskname: The task at hand, for example "link" or "tag".
    :type taskname: str
    """

    from utility.settings import settings
    outfolder = settings.PATH_TO_OUTFILE_FOLDER
    magfolder = os.path.join(outfolder, taskname, year[0])
    if not os.path.exists(magfolder):
        os.makedirs(magfolder)
    with open(os.path.join(magfolder, "".join(year[1:]) + ".jsonl"), mode="wb") as out:
        for entry in files:
            out.write(orjson.dumps(entry, default=set_default))
            out.write(b"\n")


def save_data(data: dict, taskname: str):
    """
    Saves the data given in a "taskname" folder in the oufile folder
    specified in the configurations. If the "taskname" folder doesn't exist,
    one is created.

    :param data: The keys are magazine-year tuples, the values are given\
        by the task.
    :type data: dict
    :param taskname: The task at hand, for example "link" or "tag".
    :type taskname: str
    """

    logging.info("Reached saveData")
    from utility.settings import settings
    outfolder = settings.PATH_TO_OUTFILE_FOLDER
    prepfolder = os.path.join(outfolder, taskname)
    if not os.path.exists(prepfolder):
        os.makedirs(prepfolder)
    for batch in data:
        for year, d in batch.items():
            yearfolder = os.path.join(prepfolder, year[0])
            if not os.path.exists(yearfolder):
                os.makedirs(yearfolder)
            with open(os.path.join(yearfolder, year[1] + ".jsonl"), mode="wb") as out:
                for entry in d:
                    out.write(orjson.dumps(entry, default=set_default))
                    out.write(b"\n")


def transkribus_xml_to_approx_word_coord(xml_path,
                                         schema="{http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15}") -> str:
    """
    Transforms Transkribus xml output which only has baseline level coordinates
    into word-level coordinates by naively splitting the length by number of words.

    :param schema: XML schema, defaults to "{http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15}"
    :type schema: str, optional
    :param xml_path: Path to the XML structure file.
    :type xml_path: str, optional
    :return: The string of similar format to ABBYY FineReader output.
    :rtype: str
    """

    root = ET.parse(xml_path).getroot()
    out_str = ""
    for a in root.findall(schema+'Page'):
        image_width = a.attrib["imageWidth"]
        image_height = a.attrib["imageHeight"]
        out_str += f"{image_width}, {image_height}\n"
        for b in a.findall(schema+"TextRegion"):
            for c in b.findall(schema+"TextLine"):
                found_coord = False
                for d in c.findall(schema+"Coords"):
                    points = d.get("points").split(" ")[:4]
                    [c1,c2], [c3,c4], [c5,c6], [c7,c8] = [x.split(",") for x in points]
                    y = min(int(float(c6)), int(float(c8)))
                    h = max(int(float(c2)), int(float(c4)))-y
                    x = min(int(float(c1)), int(float(c7)))
                    w = max(int(float(c3)), int(float(c5)))
                    found_coord = True
                if found_coord:
                    for d in c.findall(schema+"TextEquiv"):
                        text = d.find(schema+"Unicode").text
                        text = text.split(" ")
                        len_text = len(text)
                        for idx, word in enumerate(text):
                            out_str += f"{word} {x+w//len_text*idx},{y},{w//len_text*(idx+1)},{h}\n"
            out_str += "<EOS>\n"
    return out_str


def erara_xml_to_word_coord(xml_path,
                            schema='{http://www.loc.gov/standards/alto/ns-v3#}') -> str:
    """
    Transforms E-Rara xml output into pipeline-compliant input.

    :param schema: XML schema, defaults to '{http://www.loc.gov/standards/alto/ns-v3#}'
    :type schema: str, optional
    :param xml_path: Path to the XML structure file.
    :type xml_path: str, optional
    :return: The string of similar format to ABBYY FineReader output.
    :rtype: str
    """
    root = ET.parse(xml_path).getroot()
    out_str = ""
    for z in root.findall(schema+'Layout'):
        for a in z.findall(schema+'Page'):
            # if a.attrib["ID"] == "p703360":  # for a certain page
            image_width = a.attrib["WIDTH"]
            image_height = a.attrib["HEIGHT"]
            out_str += f"{image_width}, {image_height}\n"
            for b in a.findall(schema+"PrintSpace"):
                for c in b.findall(schema+"TextBlock"):
                    for d in c.findall(schema+"TextLine"):
                        for e in d.findall(schema+"String"):
                            y = e.attrib["VPOS"]
                            h = e.attrib["HEIGHT"]
                            x = e.attrib["HPOS"]
                            w = e.attrib["WIDTH"]
                            text = e.attrib["CONTENT"]
                            out_str += f"{text} {x},{y},{w},{h}\n"
                out_str += "<EOS>\n"
    return out_str


def txt_file_to_word_coord(txt_path: str) -> str:
    """
    Transforms .txt OCR output (like for instance from Tesseract)
    into pipeline-compliant input. The "coordinates" are unique
    4-tuples so they can be used for the pipeline but are **not**
    coordinates on the page.

    :param txt_path: Path to the txt file.
    :type txt_path: str
    :return: The string of similar format to ABBYY FineReader output.
    :rtype: str
    """

    with open(txt_path, "r", encoding="utf-8") as f:
        input_str = f.read()

    out_str = ""
    running_idx = 0
    for c in input_str.split("\n\n\n"):
        for i, a in enumerate(c.split("\n")):
            for j, b in enumerate(a.split(" ")):
                x = input_str.find(b, running_idx)
                y = x + len(b)
                w = i
                h = j
                running_idx += len(b)+1
                text = b
                out_str += f"{text} {x},{y},{w},{h}\n"
        out_str += "<EOP>\n"
    return out_str


def offset_len_to_linking_input(mention_list: list[dict]):
    """
    Transforms tagging output that contains the mention,
    offset, length and the document name into a tagging
    output that can be used by the CHNOBLi system.

    :param mention_list: List of mention dictionaries.
    :type mention_list: list[dict]
    :return: A list of dictionaries of the format used\
        by the CHNOBli system.
    :rtype: list[dict]
    """

    chnobli_tagging = []
    for idx, mention in enumerate(mention_list):
        out = {
            "info": {
                "lastnames": [mention["mention"].split(" ")[-1]],
                "firstnames": mention["mention"].split(" ")[:-1],
                "abbr_firstnames": [],
                "address": [],
                "titles": [],
                "occupations": [],
                "others": [],
                "type": "PER",
                "id": idx
            },
            "pageNo": 0,
            "pageNames": mention["docName"],
            "pid": mention["docName"],
            "sentenceNo": 0,
            "positions": f"{mention["offset"]}:{mention["length"]}",
            "articles": "",
            "context": ""
            }
        with open(mention["docName"], encoding="utf-8") as f:
            text = f.read()
            out["context"] = text[
                max(mention["offset"]-settings.VD_CONTEXT_WINDOW_LEN*4, 0):
                min(mention["offset"]+mention["length"]+settings.VD_CONTEXT_WINDOW_LEN*4, len(text))
            ]
            out["context"] = out["context"].strip()
        chnobli_tagging.append(out)
    return chnobli_tagging
