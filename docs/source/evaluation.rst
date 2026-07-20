How to Evaluate
===============
To evaluate the output of this system, you need:

**1. Ground-Truth Data**

There are two sets of ground-truth data, both describing select years and pages of the same magazines [cmt, edu, fsi, gfr, hvg, obl, rep, tjb, woh, zlp, zut]. One set was created "with fuzzy matching", i.e., minor misspellings of the entity name are tolerated when looking for the corresponding GND entry, while the other was created "without fuzzy matching", so only the name on the screen was considered.

To select which ground-truth dataset you would like to evaluate against, set the command-line argument `--fuzzy True` or `--fuzzy False`. If nothing is set, the default is `--fuzzy True`.

Your configuration file then specifies where the ground-truth data for the fuzzy level is located:

    .. code-block:: bash

        nla/configs/eval_config.json

**2. Evaluation Level**

Evaluation can be done at an entity or reference level. To select which level of evaluation you would like to see, set the command-line argument `--eval_level ref` or `--eval_level ent`.

**3. Run Evaluation**

    You can simply run the script:

    .. code-block:: bash

        sh scripts/eval.sh

The `magazine_year_paths` argument describes the path to the directory where the data to be evaluated is located. Don't worry if that directory contains even more linked files, only the ones for which a corresponding ground-truth file exists are compared.

**Note, however, that for each ground-truth file, there must exist a corresponding linked file.** If you would like to exclude some ground-truth files, you must remove them from the ground-truth data directory. This is to ensure that your model is tested against a variety of magazines and can be fairly compared to previous runs.

**4. Analyze Evaluation**

In the `PATH_TO_OUTFILE_FOLDER` specified in your `configurations.json`, you can find the evaluations for each magazine in the corresponding file, for each year in a separate file under the magazine directory, and aggregated for all magazines and years under, for example, `eval_ent_with_fuzzy.json`.

How to Test
===========
Our workflow ensures that you pass all the unit tests as you commit, but if you would like to check for yourself whether some integration tests work:

**1. scripts/test_linking.sh**

This script uses the tagging output of the system before your changes were made and runs linking on them. Then it compares it to a given magazine (default is obl-2004) and raises an exception if something changed. It only checks the data in `nla/data/test_data`.

**NOTE:** Unfortunately, the results change based on whether or not `data2` is mounted. That is because it provides structure information which changes our aggregation. Thus we have two test data files: `data2` and `nodata2`.

**2. scripts/test_tagging.sh**

This script uses the raw text files of the obl magazine and runs your tagging on them. It then compares the output to `nla/data/test_data/output_before`, where we keep the previous output of obl for comparison purposes. It raises an exception if anything changed.

**3. scripts/test_end_to_end.sh**

This script runs tagging and linking on the raw text files. It then compares the output to `nla/data/test_data/output_before`, where we keep the previous output of obl for comparison purposes. It raises an exception if anything changed.

**4. Manual Testing**

If you would like to compare manually, compare the two JSON files (previous output in `output_before` and new output) with a program such as `meld` or the VS Code comparator.

For the VS Code comparator, select the two files, right-click, select *Compare Selected*, then in each document, right-click and select *Format Document*.

Note that some differences may be due to re-ordering, and some are due to the fact that the rule-based system is not entirely deterministic.