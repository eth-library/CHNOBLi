Using Your Own Data
====================

This page describes how to run CHNOBLi on your own documents, whether
they come from OCR software or from an existing entity extraction
pipeline.

Input Format: OCR Data
------------------------

The tagging component expects word coordinates, as produced by ABBYY
FineReader. If your OCR comes from another source, CHNOBLi provides
transformation utilities for several common formats.

Transkribus
~~~~~~~~~~~

.. code-block:: python

   from utility.utils import transkribus_xml_to_approx_word_coord

E-Rara
~~~~~~

.. code-block:: python

   from utility.utils import erara_xml_to_word_coord

Tesseract or Plain Text
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from utility.utils import txt_file_to_word_coord

.. note::
   **Contributing:** Have a transformation function for another format?
   Please submit a pull request!

Once your data has been transformed, you can run the pipeline just as
you did with the example data in :doc:`quickstart`.

Custom Tagging Output
------------------------

If you already have entity extractions (e.g., from SpaCy), you can
transform them into CHNOBLi's expected format instead of running the
tagging step yourself.

Transformation
~~~~~~~~~~~~~~~

Input example:

.. code-block:: json

   {
      "mention": "Kamal Kharrazi",
      "offset": 237,
      "length": 14,
      "docName": "APW19981109_0464.htm"
   }

Transform using:

.. code-block:: python

   from utility.utils import offset_len_to_linking_input

This produces output like:

.. code-block:: json

   {
      "info": {
         "lastnames": ["Kharrazi"],
         "firstnames": ["Kamal"],
         "abbr_firstnames": [],
         "address": [],
         "titles": [],
         "occupations": [],
         "others": [],
         "type": "PER",
         "id": 0,
         "gt_wikipedia": "Kamal_Kharazi",
         "gt_wikidata": "Q435799",
         "gt_gnd": "1222390949"
      },
      "pageNo": 0,
      "pageNames": "APW19981109_0464.htm",
      "pid": "APW19981109_0464.htm",
      "sentenceNo": 0,
      "positions": "237:14",
      "articles": "",
      "context": "al bodies about the U.S.-funded Radio Free Europe, the Iran Daily reported Monday. It quoted Foreign Minister Kamal Kharrazi as saying the radio \"was set up to interfere in Iran's internal affairs.\" It did not say when the complaints wil"
   }

Linking
~~~~~~~~

1. **Configure your data path.** Edit
   ``configs/configurations_customtag.json`` and set
   ``CUSTOM_TAGGING_OUTPUT`` to your data path.

2. **Run aggregation (with linking):**

   .. code-block:: bash

      python main.py --tasks finish --config_file configs/configurations_customtag.json

   Or skip aggregation and only link:

   .. code-block:: bash

      python main.py --tasks link --config_file configs/configurations_customtag.json

.. note::
   **On context:** The pipeline reads context from ABBYY FineReader
   format, which is why for custom data you must include the
   ``"context"`` key with the context string explicitly. If your data
   doesn't include context, simply omit the ``"context"`` key and
   disambiguation via the vector database will be skipped.

.. note::
   **On dates:** The publication year is used for sanity checks (e.g.,
   not considering people born after that year). For custom data, this
   defaults to year 3000 — adjust as needed in ``main.py``.
