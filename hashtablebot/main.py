import logging
import os

from hashtablebot.hash_table_bot import HashTableBot


def main():
    # Get token and initial channels and log level from environment variables
    twitch_token = os.environ.get("TWITCH_TOKEN")
    comma_separated_initial_channels = os.environ.get(
        "COMMA_SEPARATED_INITIAL_CHANNELS", "hash_table"
    )
    log_level = os.environ.get("LOG_LEVEL", "INFO")
    logging.basicConfig(level=log_level)

    bot = HashTableBot(twitch_token, comma_separated_initial_channels.split(","))
    bot.run()


if __name__ == "__main__":
    main()
