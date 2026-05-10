#! /usr/bin/python3

"""
Includes functions to tag files using flairNLP.
Version 31.08.2020: Updated to use new tagging system which uses 2 models at
once.
"""

import orjson
from collections import defaultdict
from datetime import datetime
import logging
import os
from utility.settings import settings
import flair
from flair.data import Sentence, Token, Label
from flair.models import MultitaskModel
from flair.nn import Classifier
from torch import device as torch_device
from torch.cuda import is_available as cuda_is_available


class CustomToken(Token):
    def __init__(self, text, coords, orig):
        super().__init__(text)
        self.coords = coords
        self.orig = orig


class CustomSentence(Sentence):
    def __init__(self, filename=None, text=None):
        """
        Create a sentence object by passing either a text or a list of tokens.

        :param filename: Name of the file this sentence appeared in, defaults\
            to None.
        :type filename: str, optional
        :param text:  Either pass the text as a string, or provide an already\
            tokenized text as either a list of strings or a list of Token\
            objects. use_tokenizer: You can optionally specify a custom\
            tokenizer to split the text into tokens. By default we use\
            `flair.tokenization.SegtokTokenizer`. If use_tokenizer is set\
            to False, `flair.tokenization.SpaceTokenizer` will be used\
            instead. The tokenizer will be ignored, if text refers to\
            pretokenized tokens, defaults to None.
        :type text: _type_, optional
        """
        super().__init__(text)
        self.filename = filename if filename is not None else ""


def decide_tag_no_tag_lower_prio(labels: list) -> Label:
    """
    Combining the tags of the two tagging models.
    If there is disagreement between the two models, "O" always loses.

    :param labels: A list of tags for an entity with at most 2 entries.\
        If there are two, the first entry corresponds to the bio label\
        model and the second to the det label model.\
        If there is only one entry, the model is detected based on the\
        labeling scheme.
    :type labels: list
    :raises Exception: If the labels list is empty, an exception is raised.
    :return: The Label object is the new combined label\
        for this entity, the dictionary
    :rtype: Label
    """

    # If there is disagreement between the two models, "O" always loses
    # TODO replace this by tag_dictionary directly from the models
    bio_tags = [
        '<unk>', 'O', 'B-PER', 'I-PER', 'B-CIT', 'B-CTR', 'I-CIT', 'B-CITadj',
        'B-CTRadj', 'I-CTRadj', 'I-CTR', 'B-GEOadj', 'B-GEO', 'I-GEO',
        'I-GEOadj', 'B-STR', 'I-STR', 'I-CITadj', 'B-EXT', 'I-OT', '<START>',
        '<STOP>'
    ]
    det_per_labels = ["AN", "OC", "FN", "LN", "COM", "OT"]
    if len(labels) == 2:
        bio_label = labels[0]
        det_label = labels[1]
    elif len(labels) == 1:
        if labels[0].value in bio_tags:  # bio
            bio_label = labels[0]
            det_label = Label(bio_label.data_point, value="O", score=0)
        else:  # det
            det_label = labels[0]
            bio_label = Label(det_label.data_point, value="O", score=0)
    else:
        raise Exception("Empty list of labels was passed.")
    # check if the labels agree
    if bio_label.value[2:] == "PER" and det_label.value[2:] in det_per_labels:
        new_label = bio_label.value + det_label.value[1:]
    elif bio_label.value[2:] == det_label.value[2:]:
        new_label = bio_label.value
    else:  # if they don't agree, O always loses
        if (
            det_label.value == "O"
            or
            (
                bio_label.score > det_label.score and bio_label.value != "O"
            )
        ):
            if bio_label.value[2:] == "PER":
                new_label = bio_label.value + "-OT"
            else:
                new_label = bio_label.value
        else:
            if det_label.value[2:] in det_per_labels:
                new_label = "B-PER" + det_label.value[1:]
            else:
                new_label = det_label.value

    return new_label


def add_sentences(new_data: dict, collected_sentences: list) -> None:
    """
    Given the sentences tagged with both models, combines their tags
    and updates the new_data dictionary with the new sentences.

    :param new_data: A dictionary where the keys are the filenames and\
        the values are the tagged sentences in said file.
    :type new_data: dict
    :param collected_sentences: A list of sentences tagged by both models.
    :type collected_sentences: list
    """

    for sentence in collected_sentences:
        new_sentence = []
        for token in sentence:
            if token.labels == []:
                new_token = {
                    "token": token.orig,
                    "coord": token.coords,
                    "normalized": token.text,
                    "tag": "O"
                }
            else:
                tag = decide_tag_no_tag_lower_prio(token.labels)
                new_token = {
                    "token": token.orig,
                    "coord": token.coords,
                    "normalized": token.text,
                    "tag": tag,
                }
            new_sentence.append(new_token)
        new_data[sentence.filename].append(new_sentence)


def write_sentences_to_outfile(outfile, data: dict) -> None:
    """
    For each SENTENCE_BATCH_SIZE (set in the config file) batch of
    sentences, we write out the sentences into the outfile.
    This helps with our memory restrictions.

    This has the side-effect that the data dictionary is cleared with each time
    we call this function.

    :param outfile: Text stream we can write our\
        intermediate results into.
    :type outfile: TextIOWrapper
    :param data: Dictionary of filenames, tagged sentences.
    :type data: dict
    """
    for filename, sentences in data.items():
        out_dict = {filename: sentences}
        outfile.write(orjson.dumps(out_dict) + b"\n")
    
    data.clear()


def tag_year_data_and_save(collection: dict,
                           tagger: MultitaskModel,
                           outfile_path: str,
                           sentence_batch_size: int) -> None:
    """
    Runs tagging on the collection and saves the result
    into the outfile_path.

    :param collection: A dictionary where the keys are the filenames and\
        the values are the sentences in said file.
    :type collection: dict
    :param tagger: The MultitaskModel containing both\
        tagging models (ner-det and ner-bio).
    :type tagger: MultitaskModel
    :param outfile_path: String of the outfile path where the tagged file\
        will be saved.
    :type outfile_path: str
    :param sentence_batch_size: Number of sentences, after which we start\
        writing the intermediate results into the outfile.
    :type sentence_batch_size: int
    """

    # open outfile
    outfile = open(outfile_path, mode="wb")

    new_data = defaultdict(list)
    collected_sentences = []
    for filename, sentences in collection.items():
        for sentence in sentences:
            # Use slicing to handle chunking of large sentences
            for i in range(0, len(sentence), 250):
                chunk = sentence[i : i + 250]
                if not chunk:
                    continue

                # Create Flair tokens for this chunk
                flair_tokens = [
                    CustomToken(
                        text=(t["normalized"] if "normalized" in t else t["token"]),
                        coords=t["coord"],
                        orig=t["token"],
                    )
                    for t in chunk
                ]

                # Create sentence with tokens and metadata immediately
                # to avoid empty sentence warnings
                new_sentence = CustomSentence(filename, flair_tokens)
                collected_sentences.append(new_sentence)

                if len(collected_sentences) >= sentence_batch_size:
                    tagger.predict(
                        collected_sentences,
                        verbose=False,
                        mini_batch_size=4,
                        force_token_predictions=True,
                    )
                    add_sentences(new_data, collected_sentences)
                    collected_sentences = []

                # Create Flair tokens for this chunk
                flair_tokens = [
                    CustomToken(
                        text=(t["normalized"] if "normalized" in t else t["token"]),
                        coords=t["coord"],
                        orig=t["token"],
                    )
                    for t in chunk
                ]

                # Create sentence with tokens and metadata immediately
                # to avoid empty sentence warnings
                new_sentence = CustomSentence(filename, flair_tokens)
                collected_sentences.append(new_sentence)

                if len(collected_sentences) >= sentence_batch_size:
                    tagger.predict(
                        collected_sentences,
                        verbose=False,
                        mini_batch_size=4,
                        force_token_predictions=True,
                    )
                    add_sentences(new_data, collected_sentences)
                    collected_sentences = []

                    write_sentences_to_outfile(outfile, new_data)

    if collected_sentences:
        tagger.predict(
            collected_sentences,
            verbose=False,
            mini_batch_size=4,
            force_token_predictions=True,
        )
        add_sentences(new_data, collected_sentences)

        write_sentences_to_outfile(outfile, new_data)

    outfile.close()


def setup_flair_tagger(gpu_num: int) -> MultitaskModel:
    """
    Sets up and returns a Flair MultitaskModel for two NER models.

    :param gpu_num: The GPU number to use for the Flair models.
    :type gpu_num: int
    :return: An instance of Flair's MultitaskModel\
        loaded with the specified NER models.
    :rtype: MultitaskModel
    """

    flair.device = (
        torch_device(int(gpu_num)) if cuda_is_available() else torch_device("cpu")
    )
    logging.info(f"Using device: {flair.device}")

    logging.info(f"Loading Flair model: {settings.PATH_TO_NER_MODEL_1}")
    ner_tagger_1 = Classifier.load(settings.PATH_TO_NER_MODEL_1)
    logging.info(f"Loading Flair model: {settings.PATH_TO_NER_MODEL_2}")
    ner_tagger_2 = Classifier.load(settings.PATH_TO_NER_MODEL_2)
    flair_tagger = MultitaskModel([ner_tagger_1, ner_tagger_2])
    return flair_tagger


def package_generator_output_paths(generator, batch_size):
    """
    Packages the output from a generator into batches of a specified size.

    :param generator: An iterable that yields tuples, where the first\
        element is a year and the second element is a\
        list of files.
    :type generator: iterable
    :param batch_size: The number of items to include in each batch.
    :type batch_size: int
    :returns: Yields: A dictionary where the keys are years and the values are lists\
        of files, with the number of items in the dictionary not\
        exceeding the batch size.
    :rtype: Iterator[:class:`dict`]

    **Example:**\n
    >>> generator = [(2020, ['file1', 'file2']), (2021, ['file3', 'file4'])]
    >>> batch_size = 1
    >>> for batch in packageGeneratorOutput(generator, batch_size):
    >>>     print(batch)
        # Output:
        # {2020: ['file1', 'file2']}
        # {2021: ['file3', 'file4']}
    """

    year_dict = {}
    for year, files in generator:
        year_dict[year] = files
        if len(year_dict) >= batch_size:
            yield year_dict
            year_dict = {}

    if year_dict:
        yield year_dict


def execute_tagging(preprocessed_data,
                    tasks: list,
                    gpu_num: int) -> None:
    """
    Tags the preprocessed data using the provided flair tagger and
    configuration.

    :param preprocessed_data: The data to be tagged, usually loaded or passed\
        from preprocessing.
    :param tasks: List of tasks to be performed.
    :type tasks: list
    :param gpu_num: GPU number to use. If it's 0, CPU is used.
    :type gpu_num: int
    :raises Exception: If 'prep' is not included in the tasks list, an\
        exception is raised indicating that 'prep,tag' must be called together.
    """

    flair_tagger = setup_flair_tagger(gpu_num)
    start_time = datetime.now()
    logging.info(f"Starting Tagging at {datetime.now()}:")
    if "prep" not in tasks:  # TODO this cannot be called seperately
        raise Exception("'prep,tag' must be called together.")
        # this is supposed to make prep,tag independent, does not work yet
        # conf["PATH_TO_INPUT_FOLDERS"] += "/tag/"
        # preprocessed_data = loadDataIterative(conf)
    preprocessed_data = package_generator_output_paths(
        preprocessed_data, settings.BATCH_SIZE
    )
    for magazine in preprocessed_data:
        for year, data in magazine.items():
            logging.info(f"Tagging {year}")
            outfolder = settings.PATH_TO_OUTFILE_FOLDER
            yearfolder = os.path.join(outfolder, "tag", year[0])
            if not os.path.exists(yearfolder):
                os.makedirs(yearfolder)
            outfile_path = os.path.join(yearfolder,
                                        "".join(year[1:]) + ".jsonl")
            tag_year_data_and_save(
                data,
                flair_tagger,
                outfile_path,
                int(settings.SENTENCE_BATCH_SIZE)
            )
            logging.info(f"Finished tagging {year}.")
    logging.info(f"Tagging took: {datetime.now() - start_time}")
