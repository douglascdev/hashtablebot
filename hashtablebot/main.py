import logging
import click
from twitchio import AuthenticationError

from hashtablebot.hash_table_bot import HashTableBot


@click.command(help="HashTableBot")
@click.option(
    "--token",
    envvar="TOKEN",
    help="OAuth Access Token provided by twitch(see https://dev.twitch.tv/docs/authentication/getting-tokens-oauth). "
    "Can also be passed with the TOKEN environment variable",
    required=True,
)
@click.option(
    "--channels",
    envvar="CHANNELS",
    help="A comma-separated list of twitch channels the bot should join. "
    "Can also be passed with the CHANNELS environment variable.",
    required=True,
)
@click.option(
    "--log_level",
    envvar="LOG_LEVEL",
    default="INFO",
    help="Set the logging level, default is INFO. Can also be passed with the LOG_LEVEL environment variable.",
    type=(
        click.Choice(("CRITICAL", "FATAL", "ERROR", "WARN", "WARNING", "INFO", "DEBUG"))
    ),
)
def main(token, channels, log_level):
    """
    The entry point for the bot's code.

    Installing the bot with pip or setup.py and running "hashtablebot" should lead to this function executing,
    as specified in the project's `setup file <https://github.com/douglascdev/hashtablebot/blob/343154016d1e32002ab417ab8f52456e967fe803/setup.py#L21>`_

    The parameters/environment variables are gathered here by `Click <https://click.palletsprojects.com/en/8.1.x/>`_
    and passed to the HashTableBot class.

    :param token: the `OAuth Access Token<https://dev.twitch.tv/docs/authentication/getting-tokens-oauth>`_ given by twitch.
    :param channels: A comma-separated list of twitch channels the bot should join
    :param log_level: set the `logging level <https://docs.python.org/3/library/logging.html#levels>`_
    :return:
    """
    logging.basicConfig(level=log_level)

    bot = HashTableBot(token, channels.split(","))

    try:
        bot.run()
    except AuthenticationError:
        logging.error("An invalid or expired token was passed.")


if __name__ == "__main__":
    main()
