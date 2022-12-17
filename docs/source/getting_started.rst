.. _getting_started:

Getting started
===============

Installation
------------

1. Install `Docker compose <https://docs.docker.com/compose/install/>`_
2. Clone the project's repository:

.. code-block:: sh

    git clone https://github.com/douglascdev/hashtablebot

3. Change to the repository's folder on your terminal:

.. code-block:: sh

    cd hashtablebot

4. Create a file called :code:`.env` with the following contents:

.. code-block:: sh

    POSTGRES_USER=hashtablebot
    POSTGRES_PASSWORD=hashtablebot
    POSTGRES_DB=hashtablebot
    POSTGRES_HOST=postgres

    LOG_LEVEL=INFO
    CHANNELS=<your twitch channel>
    TOKEN=<your twitch token>

Note that the :code:`TOKEN` (see the Getting a token section below) and :code:`CHANNELS` values must be changed.

5. Run the containers:

.. code-block:: sh
    docker compose up

If the :code:`.env` values were setup correctly, this should startup the bot and the database.

Developer setup
---------------

Running the bot without docker might be preferable to developers.
If that's your case, do these in addition to the installation instructions:

1. `Install python3.11 <https://www.python.org/downloads/>`_
2. Open your terminal application on the project's root folder and run:

.. code-block:: sh

    pip install -e .[dev]

3. Instead of running both containers, run only the database:

.. code-block:: sh

    docker compose up postgres

4. Set the environment variables defined previously in :code:`.env`. On Linux, you can use :code:`source` to load
the variables you set on the file:

.. code-block:: sh

    set -o allexport && source .env && set +o allexport

5. Run the bot

.. code-block:: sh

    hashtablebot


Options
-------

The bot can be called with the `hashtablebot` command, with the following options:

.. code-block::


          --token TEXT                    OAuth Access Token provided by twitch(see ht
                                          tps://dev.twitch.tv/docs/authentication/gett
                                          ing-tokens-oauth). Can also be passed with
                                          the TOKEN environment variable  [required]
          --channels TEXT                 A comma-separated list of twitch channels
                                          the bot should join. Can also be passed with
                                          the CHANNELS environment variable.
                                          [required]
          --log_level [CRITICAL|FATAL|ERROR|WARN|WARNING|INFO|DEBUG]
                                          Set the logging level, default is INFO. Can
                                          also be passed with the LOG_LEVEL
                                          environment variable.
          --help                          Show this message and exit.

The arguments can also be passed using environment variables, to make cloud deployment easier.

Getting a token
---------------

Until a proper authorization grant flow is implemented as part of the bot, the easiest way to get an OAuth token is to
use `Twitch Token Generator <https://twitchtokengenerator.com/>`_.

.. WARNING::
   As a security measure, DO NOT request scopes besides reading and writing to chat.

Alternatively, copy the following url and replace `MY_CLIENT_ID` with your client id and set your app's redirect URI on
twitch's dev dashboard to `http://localhost`.

.. code-block::

        https://id.twitch.tv/oauth2/authorize?response_type=token&client_id=MY_CLIENT_ID&redirect_uri=http://localhost&scope=chat%3Aread+chat%3Aedit


After accessing the URL and authorizing access, you'll be redirected to
`localhost` and the OAuth token will be part of the URL.

Usage
-----

Here are some usage examples:

.. code-block:: sh


        # Join a single channel, only logging INFO messages
        hashtablebot --token ABC123 --channels sodapoppin

        # Join two channels, logging DEBUG-level messages
        hashtablebot --token ABC123 --channels sodapoppin,forsen --log_level=DEBUG

        # By setting environment variables
        export CHANNELS=sodapoppin
        export LOG_LEVEL=DEBUG
         export TOKEN=ABC123
        hashtablebot
