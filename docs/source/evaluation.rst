How to Evaluate
===============
To evaluate the output of this system, you need:

1. Ground-Truth Data
~~~~~~~~~~~~~~~~~~~~

The ground-truth data, consisting of select years and pages of the magazines [cmt, edu, fsi, gfr, hvg, obl, rep, tjb, woh, zut] was created "with fuzzy matching", i.e., minor misspellings of the entity name are tolerated when looking for the corresponding GND entry.

Your configuration file then specifies where the ground-truth data for the fuzzy level is located:

    .. code-block:: bash

        nla/configs/eval_config.json

2. Evaluation Level
~~~~~~~~~~~~~~~~~~~

Evaluation can be done at an entity or reference level. To select which level of evaluation you would like to see, set the command-line argument `--eval_level ref` or `--eval_level ent`.

3. Run Evaluation
~~~~~~~~~~~~~~~~~

    You can simply run the script:

    .. code-block:: bash

        sh scripts/eval.sh

The `magazine_year_paths` argument describes the path to the directory where the data to be evaluated is located. Don't worry if that directory contains even more linked files, only the ones for which a corresponding ground-truth file exists are compared.

**Note, however, that for each ground-truth file, there must exist a corresponding linked file.** If you would like to exclude some ground-truth files, you must remove them from the ground-truth data directory. This is to ensure that your model is tested against a variety of magazines and can be fairly compared to previous runs.

4. Analyze Evaluation
~~~~~~~~~~~~~~~~~~~~~

In the `PATH_TO_OUTFILE_FOLDER` directory specified in your `eval_config.json`, you can find the evaluations for each magazine in the corresponding file, for each year in a separate file under the magazine directory, and aggregated for all magazines and years under, for example, `eval_ent_with_fuzzy.json`.
