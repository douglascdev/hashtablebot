Hash Table Bot
==============

Installation
------------

1. `Install python3.10 <https://www.python.org/downloads/>`_
2. Clone the project's repository:

.. code-block:: sh

    git clone https://github.com/douglascdev/hashtablebot


3. Open your terminal application on the project's root folder and run:

.. code-block:: sh

    pip install --user .


For a dev setup, you should instead install using the editable flag, to reflect your changes to the code:

.. code-block:: sh

    pip install -e .


Usage
-----

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
