"""
Evaluate performance on entity and reference level
"""
import os
import logging
from datetime import datetime
from utility.evaluation_utils import Paths, Scores, evaluate_person
from utility.settings import settings


def execute_evaluation(
        eval_level: str, top_k=3, timed=True
        ) -> None:
    """
    Evaluates the F1-score of the data based on the given configuration and\
    evaluation level

    At eval_level "ent", this is done on entity level. At eval_level "ref",\
    this is done on reference level, which weighs the entities more that occur\
    more, thus should be linked correctly, since we have more context on them.

    Evaluation is done for all magazines in our ground-truth folder to make\
    the evaluations straightforward to compare. If you would like to evaluate\
    only one magazine, you need to create a new directory with only that\
    magazine's ground-truth in it, change that path in the config, and then\
    run eval.

    :param eval_level: Evaluation level to be used ("ent" or "ref").
    :type eval_level: str
    :raises NotImplementedError: If no path to GT was passed.
    :param top_k: How many candidates to truncate the results to,\
        defaults to 3.
    :type top_k: int
    :param timed: Boolean indicating whether to time the execution and log it,\
        defaults to True.
    :type timed: bool

    It creates several directories and json files in the output directory\
    specified in the config.
    """

    if timed:
        start_time = datetime.now()
        logging.info(f"Starting Evaluation at {start_time}:")

    if settings.EVAL_TOPK is not None:
        top_k = settings.EVAL_TOPK
    if settings.INKB_SCORE is not None:
        inkb_score = True if settings.INKB_SCORE == "true" else False
    else:
        inkb_score = False
    ref_level = eval_level == "ref"
    paths = Paths()
    if paths.success:
        global_scores = Scores()
        for magazine in os.listdir(paths.get(type_="gt", key="")):
            paths.update(key="magazine", value=magazine)
            magazine_scores = Scores()
            for file in os.listdir(paths.get(type_="gt", key="magazine")):
                if file.endswith(".txt"):  # these are the notes
                    continue
                paths.update(key="file", value=file)
                gt_file = paths.get_jsonl(type_="gt")
                eval_file = paths.get_jsonl(type_="link")
                counts = evaluate_person(
                    gt=gt_file, linked=eval_file,
                    ref_level=ref_level, top_k=top_k,
                    inkb_score=inkb_score
                )
                file_scores = Scores(counts_dict=counts)
                magazine_scores.update_counter(counts)
                global_scores.update_counter(counts)
                paths.save_json(
                    type_="eval",
                    key="file",
                    doc=file_scores.get_score(),
                    ref_level_name=eval_level
                )
            paths.save_json(
                type_="eval",
                key="magazine",
                doc=magazine_scores.get_score(),
                ref_level_name=eval_level
            )
        paths.save_json(
            type_="eval",
            key="",
            doc=global_scores.get_score(),
            ref_level_name=eval_level
        )
        #save the config file
        paths.state["file"] = "eval_config.json"
        paths.state["magazine"] = ""
        paths.save_json(
            type_="eval",
            key="file",
            doc=settings.model_dump(exclude={"es"}),
            ref_level_name=eval_level
        )
    else:
        logging.info(settings.model_dump(exclude={"es"}))
        raise NotImplementedError("no path to ground truth was passed")

    if timed:
        logging.info(f"Evaluation took: {datetime.now() - start_time}")
