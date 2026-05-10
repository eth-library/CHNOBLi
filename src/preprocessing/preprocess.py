#! /usr/bin/python3

"""
Includes all functions necessary to preprocess files.

TODO:
- Verbesserte Auflösung von Abkürzungen implementieren
    - "d.h.", "et al."

- Ordinalzahlen zusammenbehalten
    - XVII und so
"""

import orjson
import os
import pprint as pp
import re
import string
import sys
import logging
import glob
from datetime import datetime

from collections import defaultdict, OrderedDict
from dataclasses import dataclass, field
from pathlib import Path
from typing import List
from utility.settings import settings
from multiprocessing import Pool
from utility import split_year


@dataclass
class PreprocessConfig:
    """Class for the preprocess configuration
    """

    ABBREVIATION_FILE: str = None
    ABBREVIATION_LIST: defaultdict = field(
        default_factory=lambda: defaultdict(list))
    KONJ: list = field(
        default_factory=lambda: [
            "und", "in", "oder", "&", "u.", "während", "auch"
        ]
    )
    PUNC: str = re.escape(string.punctuation + "«»„—¦¬")
    IN_WORD_SPLITTERS: str = re.escape("/")
    SENTENCE_ENDING: list = field(default_factory=lambda: [".", "!", "?"])

    def load_abbrevs(self) -> defaultdict:
        """
        Load abbreviations from a file and build a context dictionary.

        Reads abbreviations from the file and creates a dictionary where each word
        (including abbreviations) is mapped to its surrounding context. This allows
        for quick lookup of whether a word appears as an abbreviation and what
        words typically appear before and after it.

        :return: A dictionary mapping each word to a list of context dictionaries.
            Each context dictionary contains 'before' and 'after' keys with lists
            of surrounding words.
        :rtype: defaultdict

        **Example:**\n
        If the input file contains::

            "Dr. John Smith"
            "Prof. Jane Doe"

        The returned dictionary will be::

            {"dr.": [{"before": [], "after": ["john", "smith"]}],
            "john": [{"before": ["dr."], "after": ["smith"]}],
            "smith": [{"before": ["dr.", "john"], "after": []}],
            "prof.": [{"before": [], "after": ["jane", "doe"]}],
            "jane": [{"before": ["prof."], "after": ["doe"]}],
            "doe": [{"before": ["prof.", "jane"], "after": []}]}

        Each entry follows this structure::

            {"word": [{"before": [...], "after": [...]}]}

        This structure also helps prevent duplicate entries.
        """
        with open(self.ABBREVIATION_FILE, encoding="utf8") as inf:
            for line in inf:
                line = line.rstrip()
                line = line.split()
                words_in_abbrev = []
                for word in line:
                    word = re.sub(
                        r"([{}])".format(self.IN_WORD_SPLITTERS), r" \1 ", word
                    )
                    word = re.sub(r"(\.)[{}]*".format(self.PUNC), r"\1 ", word)
                    word = word.rstrip()
                    for w in word.split(" "):
                        words_in_abbrev.append(w)

                for pos, word in enumerate(words_in_abbrev):
                    self.ABBREVIATION_LIST[word].append(
                        {
                            "before": words_in_abbrev[:pos],
                            "after": words_in_abbrev[pos + 1:],
                        }
                    )


def fuse_hyphens(content: str, preprocess_data: PreprocessConfig) -> list:
    """
    Merge words that were split across lines by hyphens in OCR output.

    Processes OCR text to reunite words that were broken by line breaks and
    hyphenation. Each word's coordinate metadata is preserved and combined
    during the fusion process.

    :param content: Raw text containing words and their coordinate\
        metadata
    :type content: str
    :param preprocess_data: Configuration object containing
        preprocessing settings, including sentence-ending punctuation
    :type preprocess_data: PreprocessConfig
    :return: A list of dictionaries, each containing a "word" key (the fused
        text) and a "coord" key (list of associated coordinates)
    :rtype: list

    **Example:**\n
    >>> sample_text = "Hel¬ 001122\\nlo 12345\\nWorld 67890"
    >>> fuse_hyphens(sample_text)
    # output: [{'word': 'Hello', 'coord': ['001122', '12345']},
    #          {'word': 'World', 'coord': ['67890']}]

    **Processing logic:**\n
        1. Lines with fewer than two tokens are skipped
        2. Words ending with special markers (like trailing hyphens) are fused
           with the following token
        3. Coordinate metadata from both parts is combined and preserved
        4. Returns fully assembled words with their merged coordinates
    """

    output = []
    lastword = None  # There might be multiple ones possible
    maybe_lastword = None
    lastcoord = []
    for line in content.split("\n"):
        line = line.split()
        if len(line) < 2:
            continue
        word = line[0]
        coord = [line[1]]
        if lastword is not None:
            word = lastword + word
            coord = lastcoord + coord
            lastword = None
            lastcoord = []
        elif maybe_lastword is not None:
            if word not in preprocess_data.KONJ and word[0].islower():
                word = maybe_lastword + word
                coord = lastcoord + coord
            elif word not in preprocess_data.KONJ and word[0].isupper():
                # this indicates a concatenated word like "Fischli-Boson",
                # "Greig-Gould" etc.
                word = maybe_lastword + "-" + word
                coord = lastcoord + coord
            else:
                output.append({"word": maybe_lastword + "-",
                               "coord": lastcoord})
            maybe_lastword = None
            lastcoord = []
        if word[-1] == "¬":
            lastword = word[:-1]
            lastcoord = coord
        elif word[-1] == "-" and len(word) > 1:
            maybe_lastword = word[:-1]
            lastcoord = coord
        else:
            output.append({"word": word, "coord": coord})
    if lastword is not None:
        output.append({"word": lastword, "coord": lastcoord})
    elif maybe_lastword is not None:
        output.append({"word": maybe_lastword, "coord": lastcoord})
    return output


def check_for_abbrev(pos: int,
                     text,
                     preprocess_data: PreprocessConfig) -> bool:
    """
    Determine whether the token at a given position is an abbreviation.

    Checks if the token at the specified index matches a known abbreviation
    and verifies that the surrounding words match the expected context
    patterns (words before and after) defined for that abbreviation.

    :param pos: The index position of the token to check within the text list
    :type pos: int
    :param text: Tokenized text where each element is a tuple containing the
        word and possibly other metadata
    :type text: list of tuples
    :param preprocess_data: Configuration object containing preprocessing
        settings, including sentence-ending punctuation
    :type preprocess_data: PreprocessConfig
    :return: True if the token is a recognized abbreviation with matching
        context; else False
    :rtype: bool
    """

    word = text[pos][0].lower()
    if word not in preprocess_data.ABBREVIATION_LIST:
        return False
    for option in preprocess_data.ABBREVIATION_LIST[word]:
        before_is_valid = True
        for i, token in enumerate(reversed(option["before"])):
            before_position = pos - i - 1
            if before_position < 0:
                before_is_valid = False
                break
            relevant_word = text[before_position][0]
            if relevant_word.lower() != token:
                before_is_valid = False
                break
        if not before_is_valid:
            continue
        after_is_valid = True
        for i, token in enumerate(option["after"]):
            after_position = pos + i + 1
            if after_position >= len(text):
                after_is_valid = False
                break
            relevant_word = text[after_position][0]
            if relevant_word.lower() != token:
                after_is_valid = False
                break
        if not after_is_valid:
            continue

        return True

    return False


def check_roman_numeral(word: str) -> bool:
    """
    Check if a word matches the format for lowercase Roman numerals.
    
    Determines whether the input string ends with a period and contains only
    the lowercase Roman numeral characters 'i', 'v', or 'x' before the period.
    
    :param word: The input string to check
    :type word: str
    :return: True if the word ends with a period and is preceded only by
        lowercase 'i', 'v', or 'x' characters; else False
    :rtype: bool
    """

    word = word.lower()
    word_list_bool = [x in ["x", "v", "i"] for x in word[:-1]]
    return word[-1] == "." and word_list_bool != [] and all(word_list_bool)


def tokenize(content: list, preprocess_data: PreprocessConfig) -> list:
    """
    Tokenize words and split punctuation from a list of word-coordinate pairs.

    Processes a list of dictionaries containing words and their coordinates,
    separating punctuation and normalizing text while preserving coordinate
    metadata.

    **Input format:**

    Each dictionary must contain::

        {"word": "ExampleWord", "coord": "ExampleCoordinate"}

    **Tokenization process:**

        1. Separates leading and trailing punctuation from words, except periods
           in abbreviations
        2. Splits certain mid-word punctuation (e.g., semicolons, dashes) into
           separate tokens
        3. Converts fully uppercase tokens to title case (e.g., "HANS" → "Hans")
        4. Handles periods at word endings as either abbreviations or separate
           tokens

    **Example:**\n
    Input::

        [{"word": "Hello", "coord": "1209745"},
         {"word": "v.a.", "coord": "1908234"}]

    Output::

        [{"token": "Hello", "coord": "1;2;0;9;7;4;5:main",
          "normalized": "Hello"},
         {"token": "v.", "coord": "1;9;0;8;2;3;4:main"},
         {"token": "a.", "coord": "1;9;0;8;2;3;4:main"}]

    :param content: List of dictionaries, each containing:\n
        - "word" (str): The raw text token\n
        - "coord" (str): The coordinate or reference string for the token\n
    :type content: list of dict
    :param preprocess_data: Configuration object containing preprocessing
        settings, including sentence-ending punctuation
    :type preprocess_data: PreprocessConfig
    :return: List of dictionaries, each containing:\n
        - "token" (str): The processed token string\n
        - "coord" (str): The coordinate string with type suffix
          (e.g., ':main', ':lpunc', ':rpunc')\n
        - "normalized" (str, optional): Title-cased version if originally
          uppercase\n
    :rtype: list of dict
    """

    output = []
    temp_word_list = []
    for element in content:
        word = element["word"]
        coord = element["coord"]
        rp = re.match(
            r"([{}]*)(.+?\.?)([{}]*)$".format(
                preprocess_data.PUNC, preprocess_data.PUNC.replace("-", "")
            ), word
        )
        lpunc = ""
        if len(rp.group(1)) > 0:
            lpunc = rp.group(1)
        rpunc = ""
        if len(rp.group(3)) > 0:
            rpunc = rpunc + rp.group(3)
        word = rp.group(2)

        # splits = re.split(r"({}+)".format(PUNC.replace(".", "")), word)
        # if len(splits) > 1:
        #     pp.pprint(splits)
        #     word = " ".join([x for x in splits if len(x) > 0])
        word = re.sub(r"([{}])".format(preprocess_data.IN_WORD_SPLITTERS), r" \1 ", word)
        word = re.sub(r"(\.)[{}]*".format(preprocess_data.PUNC), r"\1 ", word)

        word = word.rstrip()
        words = word.split(" ")
        words = [x for x in words if x]
        for i, word in enumerate(words):
            if i == 0 and i + 1 == len(words):
                temp_word_list.append((word, coord, rpunc, lpunc))
            elif i == 0:
                temp_word_list.append((word, coord, "", lpunc))
            elif i + 1 == len(words):
                temp_word_list.append((word, coord, rpunc, ""))
            else:
                temp_word_list.append((word, coord, "", ""))

    for pos, (word, coord, rpunc, lpunc) in enumerate(temp_word_list):
        if lpunc:
            output.append({"token": lpunc, "coord": ";".join(coord)+":lpunc"})
        # word is abbreviated
        if (
            check_for_abbrev(pos, temp_word_list, preprocess_data)
            or check_roman_numeral(word.lower())
            or (len(word) < 5 and word.istitle() and word[-1] == ".")
            or re.match(r"\d{1,2}\.", word)
        ):
            word_dict = {"token": word, "coord": ";".join(coord) + ":main"}
            if word.isupper():
                word_dict["normalized"] = word.title()
            output.append(word_dict)
        # word is not abbreviated, but had period
        elif word[-1] == ".":
            word = word[:-1]
            word_dict = {"token": word, "coord": ";".join(coord) + ":main"}
            if word.isupper():
                word_dict["normalized"] = word.title()
            output.append(word_dict)
            output.append({"token": ".", "coord": ";".join(coord) + ":rpunc"})
        # no period
        else:
            word_dict = {"token": word, "coord": ";".join(coord) + ":main"}
            if word.isupper():
                word_dict["normalized"] = word.title()
            output.append(word_dict)

        if len(rpunc) > 0:
            output.append({"token": rpunc, "coord": ";".join(coord)+":rpunc"})

    return output


def split_sentences(content: list, preprocess_data: PreprocessConfig) -> list:
    """
    Split a list of tokens into sentences based on ending punctuation.

    Segments tokens into separate sentences by identifying sentence-ending
    punctuation marks as defined in the preprocessing configuration.

    :param content: List of token dictionaries, each containing token
        information
    :type content: list
    :param preprocess_data: Configuration object containing preprocessing
        settings, including sentence-ending punctuation
    :type preprocess_data: PreprocessConfig
    :return: List of sentences, where each sentence is a list of token
        dictionaries
    :rtype: list
    """

    sentences = []
    sentence = []
    for token in content:
        if token["coord"].endswith("rpunc") and \
                token["token"][-1] in preprocess_data.SENTENCE_ENDING:
            sentence.append(token)
            sentences.append(sentence)
            sentence = []
        else:
            sentence.append(token)
    if sentence:
        sentences.append(sentence)

    return sentences


def preprocess_file(infile: str) -> list:
    """
    Preprocess OCR output file and return structured sentences.

    Reads and processes an OCR-generated file, applying tokenization and
    sentence segmentation to produce a structured list of sentences.

    :param infile: Path to the input file to preprocess
    :type infile: str
    :return: List of sentences, where each sentence is a list of token
        dictionaries
    :rtype: list
    :raises: FileNotFoundError: If the input file does not exist
    :raises: KeyError: If the configuration dictionary is missing required keys

    **Example:**\n
    >>> sentences = preprocess_file("/path/to/input/file")
    """

    preprocess_data = PreprocessConfig(
        ABBREVIATION_FILE=settings.PATH_TO_ABBREVIATION_FILE
    )
    preprocess_data.load_abbrevs()
    with open(infile, encoding="utf8") as inf:
        content = inf.read()
    content = fuse_hyphens(content, preprocess_data)
    content = tokenize(content, preprocess_data)
    sentences = split_sentences(content, preprocess_data)

    return sentences


def get_year_chunk_paths(year: str) -> list:
    """
    Retrieve and group page paths for a given year into chunks.

    Takes a year folder path and organizes its page files into chunks,
    returning them as grouped lists.

    :param year: Path to the year folder
    :type year: str
    :return: List of chunks, where each chunk is a list of file paths
    :rtype: list
    """

    infiles = sorted(glob.glob(year + "/*.txt"))
    MAX_INFILES_SIZE = 1000
    if len(infiles) > MAX_INFILES_SIZE:
        chunk_list = split_year.split_directory(year)
        return [
            (
                tuple(
                    os.path.normpath(year).split(os.sep)[-2:]
                    + ["-", str(chunk_name).zfill(2)]
                ),
                pagepaths,
            )
            for chunk_name, pagepaths in chunk_list
        ]
    return [(tuple(os.path.normpath(year).split(os.sep)[-2:]), infiles)]


def prep_year_data_for_tagging(data: tuple) -> tuple:
    """
    Prepare year data for the tagging process.
    TODO this is the fourth function that just "starts" the preprocessing.
    Surely we can do better.

    Processes input files for a specific year and structures the data in a
    format ready for tagging operations.

    :param data: Tuple containing three elements:\n
        - Year (str): The year being processed\n
        - Paths (list): List of input file paths for that year\n
        - Config (dict): Configuration dictionary\n
    :type data: tuple
    :return: Tuple containing two elements:\n
        - Data dictionary (dict): Keys are years, values are prepared tagging
          data\n
        - Year (str): The year that was processed\n
    :rtype: tuple
    """

    year, infiles = data
    logging.info(f"Prepping {year}")
    od = OrderedDict()
    for infile in infiles:
        # TODO this could be parallelized, probably
        od[os.path.basename(infile)] = preprocess_file(infile)
    return od, year


def start_preprocessing(year_directories: List[str]):
    """
    Preprocess files from multiple year directories in chunks.
    TODO this is the third function that just "starts" the preprocessing.
    Surely we can do better.

    Iterates through year directories and processes their files in manageable
    chunks, yielding results for each year as they complete.

    :param year_directories: List of year directory paths to process
    :type year_directories: List[str]
    :return: Generator yielding tuples for each year:\n
        - Year (str): The year directory being processed\n
        - Data (dict): Dictionary of preprocessed data for that year\n
    :rtype: Iterator[tuple]
    """

    chunked_years = []
    for year in year_directories:
        logging.info(f"Chunking {year}")
        chunked_years.extend(get_year_chunk_paths(year))

    for i in range(0, len(chunked_years), settings.BATCH_SIZE):
        year_chunk = chunked_years[i: i + settings.BATCH_SIZE]
        packaged = [(y[0], y[1]) for y in year_chunk]
        with Pool(settings.BATCH_SIZE) as p:
            # removing imap can improve ram requirements again
            for files, year in p.imap(prep_year_data_for_tagging, packaged):
                yield year, files


def execute_preprocessing() -> list:
    """
    Execute preprocessing on files specified in the configuration.

    Processes all files defined in the configuration dictionary and yields
    preprocessed results for each year as they complete.

    :return: Generator yielding tuples for each year:\n
        - Year (str): The year being processed\n
        - Data (dict): Dictionary of preprocessed data for that year\n
    :rtype: Iterator[tuple]
    """

    if settings.CUSTOM_PATHS is not None:
        # custom path has format magazine/year
        # meaning we only want to process some specific years
        year_directories = settings.CUSTOM_PATHS
        for year, files in start_preprocessing(year_directories):
            yield year, files
    else:
        magazine_folder = sorted(
            glob.glob(settings.PATH_TO_INPUT_FOLDERS + "/*"))
        for magazine in magazine_folder:
            # If RAM is still not enough, consider cutting this further down,
            # e.g. processing chunks of 20 year at the same time
            year_directories = sorted(glob.glob(magazine + "/*"))
            # put all year_folder in a worker pool
            for year, files in start_preprocessing(year_directories):
                yield year, files


def timed_execute_preprocessing() -> dict:
    """Runs execute preprocessing but also logs the time it took to run."""
    start_time = datetime.now()
    logging.info(f"Starting Preprocessing at {start_time}:")
    preprocessed_data = execute_preprocessing()
    logging.info(f"Preprocessing took: {datetime.now() - start_time}")
    return preprocessed_data


def main():
    # NOTE this is for debugging purposes
    preprocess_data = PreprocessConfig()
    preprocess_data.load_abbrevs()
    infolder = sorted(glob.glob("{}/*/*/*.txt".format(sys.argv[1])))

    filelist = []
    for infile in infolder:
        pp.pprint(infile)
        sentences = preprocess_file(infile, {})
        if not sentences:
            continue
        text = " <EOS>\n".join(
            [
                " ".join(
                    [
                        x["normalized"] if "normalized" in x else x["token"]
                        for x in sentence
                    ]
                )
                for sentence in sentences
            ]
        )
        filedict = {}
        filedict["text"] = text
        filedict["labels"] = []
        path = Path(infile)
        filedict["meta"] = {
            "collection": str(path.parent).rsplit("\\", maxsplit=1)[-1],
            "filename": os.path.basename(infile),
        }
        filelist.append(orjson.dumps(filedict))

    with open(sys.argv[2], mode="wb") as outf:
        for entry in filelist:
            outf.write(entry)
            outf.write(b"\n")

    """
    outfile = open("vertical.txt", mode="w", encoding="utf8")
    for infile in infolder:
        sentences = preprocess_file(infile)
        for sentence in sentences:
            for token in sentence:
                if "normalized" in token.keys():
                    outfile.write(token["normalized"]+"\n")
                else:
                    outfile.write(token["token"]+"\n")
            outfile.write("\n")

    outfile.close()
    """


if __name__ == "__main__":
    main()
