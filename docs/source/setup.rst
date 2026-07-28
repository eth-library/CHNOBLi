Setup
=====

This page describes how to install and configure CHNOBLi, a named entity
linking pipeline for retro-digitized documents.

Quick Setup (Recommended)
--------------------------

The easiest way to set up the project is using the interactive setup wizard:

.. code-block:: bash

   git clone git@github.com:eth-library/CHNOBLi.git
   cd CHNOBLi
   make setup

The wizard will guide you through:

1. Creating your ``.env`` configuration file.
2. Choosing between:

   - **Minimal Setup** (using remote APIs), or
   - **Full Local Setup** (cloning and setting up local databases).
     Once the databases are running, you can import the required data
     using:

     .. code-block:: bash

        make import-data

Manual Setup
------------

If you prefer to set everything up manually, follow the steps below.

Step 1: Clone the Repository
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   git clone git@github.com:eth-library/CHNOBLi.git
   cd CHNOBLi

Step 2: Create an Environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Option A: Using Conda**

.. code-block:: bash

   conda create -n env_chnobli python=3.12 ipython
   conda activate env_chnobli

**Option B: Using venv**

.. code-block:: bash

   python3.12 -m venv .env_chnobli   # Windows: py -3.12 -m venv .env_chnobli
   source .env_chnobli/bin/activate  # Windows: .env_chnobli\\Scripts\\activate

Step 3: Install Dependencies
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   pip install -r requirements.txt

Step 4: Download Models
~~~~~~~~~~~~~~~~~~~~~~~~

Download the tagging models from the
`ETH Research Collection (DOI: 10.3929/ethz-c-000799811) <https://doi.org/10.3929/ethz-c-000799811>`_
and save them to the ``models/`` directory.

Alternative to Steps 2-4: Docker
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Instead of setting up the environment yourself, you can run:

.. code-block:: bash

   docker compose --file docker-compose-dev.yml up

This automatically sets up the environment for you, although you still
need to set up your own vector database and ElasticSearch index. To run
linking, call:

.. code-block:: bash

   docker exec -it linking sh scripts/link_example.sh

Step 5: Configure ElasticSearch
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A public API endpoint is coming soon. To set up your own:

1. Follow the setup guide in
   `CHNOBLi-elasticsearch <https://github.com/eth-library/CHNOBLi-elasticsearch>`_.
2. Update ``CHNOBLi/.env_template`` with your endpoints and index names.
3. Rename the file to ``.env``.
4. Copy the certificate hierarchy ``secrets/certs/ca/ca.crt`` from the
   CHNOBLi-elasticsearch directory into this repository.

Step 6: Configure Milvus
~~~~~~~~~~~~~~~~~~~~~~~~~

A public API endpoint is coming soon. To set up your own:

1. Set up Milvus following the setup guide in
   `CHNOBLi-vectordb <https://github.com/eth-library/CHNOBLi-vectordb>`_.
2. Update ``CHNOBLi/.env_template`` with your host and port.
3. Rename the file to ``.env``.

Managing the Project with the Makefile
----------------------------------------

The project includes a ``Makefile`` to simplify common tasks and ensure
consistent environments (especially regarding file permissions).

Setup & Data
~~~~~~~~~~~~

- ``make setup``: Run the interactive configuration wizard.
- ``make import-data``: Interactive tool to download and import Wikidata,
  GND, and Milvus data.

Container Management
~~~~~~~~~~~~~~~~~~~~~

- ``make build``: Build the Docker images from source.
- ``make up``: Start the linking pipeline in the background.
- ``make down``: Stop and remove all containers.
- ``make logs``: Tail the logs from all running services.

Interactive Access
~~~~~~~~~~~~~~~~~~~

- ``make shell``: Drop into a bash shell inside the ``linking`` container.
- ``make shell-root``: Same as above, but with root privileges.

Next Steps
----------

Once setup is complete, see :doc:`quickstart` to try the pipeline on the
provided example data.