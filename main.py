#! /usr/bin/python3

"""
NER pipeline.
"""
import os
import orjson
import logging
from rich.logging import RichHandler
from datetime import datetime
from multiprocessing import cpu_count

from src.preprocessing.preprocess import execute_preprocessing
from src.aggregation import execute_aggregation
from src.postprocess import get_data_paths_iterative, execute_postprocessing

from src.linking import execute_linking
from src.evaluation import execute_evaluation
from utility.utils import parse_arguments, check_gpu, save_data_intermediate
from utility.settings import settings

# Set up logger
PRINT_LOGS_TO_CONSOLE = True
os.makedirs(os.path.dirname(f'logs/{settings.JOB_ID}.log'), exist_ok=True)
handlers = [logging.FileHandler(f"logs/{settings.JOB_ID}.log", encoding="utf-8")]
if PRINT_LOGS_TO_CONSOLE:
    handlers.append(RichHandler(rich_tracebacks=True, markup=True))
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="[%X]",
    handlers=handlers,
)


def finish_data(tasks: list) -> None:
    """
    Executes the final steps of the pipeline, including postprocessing,
    aggregation, and linking.

    :param tasks: List of tasks to execute.
    :type tasks: list
    """

    start_time = datetime.now()
    print("Starting Finish at", start_time, ":")
    logging.info(f"Starting Finish at {start_time} :")
    if settings.CUSTOM_PATHS is None:
        settings.PATH_TO_INPUT_FOLDERS = settings.PATH_TO_OUTFILE_FOLDER + "tag/"
    if settings.BATCH_SIZE is None:
        settings.BATCH_SIZE = cpu_count() - 1

    if settings.CUSTOM_TAG_PATH is None:
        magazines = get_data_paths_iterative()
        # post
        postprocessed_data = execute_postprocessing(magazines, tasks)
    else:
        with open(settings.CUSTOM_TAG_PATH) as f:
            postprocessed_data = [("3000", orjson.loads(f.read()), [])]
    # agg
    aggregated_data = execute_aggregation(postprocessed_data, tasks)
    # link
    execute_linking(aggregated_data, tasks)
    logging.info(f"Finish took: {datetime.now() - start_time}")
    print("Finish took: ", datetime.now() - start_time)


def main():
    # Parse command-line arguments
    args = parse_arguments()

    tasks = args.tasks.split(",")
    paths = args.magazine_year_paths
    config_file = args.config_file
    eval_level = args.eval_level
    fuzzy = args.fuzzy
    gpu_num = check_gpu(args)

    if config_file:
        import os
        os.environ["NLA_CONFIG_FILE"] = config_file
        # Re-initialize a temporary settings object to re-run the whole Pydantic
        # resolution logic (Env vars > JSON configs > defaults)
        new_settings = settings.__class__()
        # Safely update the singleton in place so other modules see the updated values
        for key, value in new_settings.__dict__.items():
            setattr(settings, key, value)

    if settings.BATCH_SIZE is None:
        settings.BATCH_SIZE = cpu_count() - 1

    if "eval" in tasks:
        if fuzzy:
            settings.PATH_TO_GROUND_TRUTH = settings.PATH_TO_GROUND_TRUTH_FUZZY
        else:
            settings.PATH_TO_GROUND_TRUTH = settings.PATH_TO_GROUND_TRUTH_NOTFUZZY

    if paths:
        paths = paths.split(",")
        settings.CUSTOM_PATHS = paths
        if tasks == "eval":
            logging.warning(
                "Careful! You have selected the task 'eval' as well as"
                " giving a custom path. Evaluation is always done on"
                " all the magazines we have ground-truth data for."
            )

    if "prep" in tasks:
        preprocessed_data = execute_preprocessing()
        # If we are not going to tag, we save the preprocessed data
        if "tag" not in tasks:
            for year, files in preprocessed_data:
                save_data_intermediate(year, files, "prep")

    if "tag" in tasks:
        from src.tag_flair import execute_tagging

        # DO NOT MOVE THIS IMPORT!!! It makes the code extremely slow
        # because flair is imported there.
        execute_tagging(preprocessed_data, tasks, gpu_num)

    if "post" in tasks:
        postprocessed_data = execute_postprocessing(tasks)

    if "agg" in tasks:
        aggregated_data = execute_aggregation(postprocessed_data, tasks)

    if "link" in tasks:
        execute_linking(aggregated_data, tasks)

    if "eval" in tasks:
        execute_evaluation(eval_level, fuzzy)

    if "finish" in tasks:
        finish_data(tasks)


if __name__ == "__main__":
    main()
