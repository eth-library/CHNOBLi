import os
from utility.compare import compare_linking
from main import (
    finish_data
)

conf = {
    "PATH_TO_INPUT_FOLDERS": "./tests/test_data/input/",
    "PATH_TO_NER_MODEL_1": "./models/ner-bio.pt",
    "PATH_TO_NER_MODEL_2": "./models/ner-det.pt",
    "PATH_TO_OUTFILE_FOLDER": "./tests/test_data/output/",
    "PATH_TO_ABBREVIATION_FILE": "./src/preprocessing/abbrevs.txt",
    "GND_LIMIT": 15,
    "WIKIDATA_LIMIT": 5,
    "LINKED_PERSONS_LIMIT": 10,
    "PATH_TO_GROUND_TRUTH": "./data/ground_truth_linked/with_fuzzy_matching/"
}


# # -------------------------------------------------
# # 1. Test finish_data
# TODO mock the output
# # -------------------------------------------------
# def test_finish_data():
#     """
#     This is just "finish", so we need to have a "tag" file in
#     "path to outfile folder" already!!
#     """
#     output_path_post = conf["PATH_TO_OUTFILE_FOLDER"]+"link/obl/2004_000.json"
#     if not os.listdir('/mnt/data2'):  # check if data2 is mounted
#         output_path_pre = "./tests/test_data/output_before/link/obl/2004_000_nodata2.json"
#     else:
#         output_path_pre = "./tests/test_data/output_before/link/obl/2004_000_data2.json"

#     finish_data(conf, ["finish"])
#     assert compare_linking(output_path_pre, output_path_post)
#     os.remove(output_path_post)
