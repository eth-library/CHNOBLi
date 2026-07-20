Quick Start
===========

This page walks through running CHNOBLi on the provided example data, so
you can confirm your setup works before using your own documents.

Try It with Example Data
-------------------------

1. Tag Example Documents
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   sh scripts/tag_example.sh

On Windows:

.. code-block:: bash

   python main.py --tasks prep,tag --magazine_year_paths ./data/input_example/tjb/1955_030 --config_file configs/configurations_example.json

Output: ``data/output/tag/``

2. Link Entities
~~~~~~~~~~~~~~~~~

.. code-block:: bash

   sh scripts/link_example.sh

On Windows:

.. code-block:: bash

   python main.py --tasks finish --magazine_year_paths ./data/output/tag/tjb --config_file ./configs/configurations_example.json

Output: ``data/output/link/``

3. Evaluate Results
~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   sh scripts/eval_example.sh

On Windows:

.. code-block:: bash

   python3 main.py --tasks eval --config_file ./configs/eval_config_example.json --eval_level ref

Output: ``data/output/eval_ref_with_fuzzy/tjb/1955_030.jsonl``

Next Steps
----------

Once you've confirmed the pipeline runs correctly on the example data,
see :doc:`using_your_data` for how to bring in your own OCR output or
custom tagging results.
