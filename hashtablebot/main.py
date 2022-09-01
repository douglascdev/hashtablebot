import logging
import os

from hashtablebot.hash_table_bot import HashTableBot

if __name__ == "__main__":
    # Get token and initial channels and log level from environment variables
    twitch_token = os.environ.get("TWITCH_TOKEN")
    comma_separated_initial_channels = os.environ.get(
        "COMMA_SEPARATED_INITIAL_CHANNELS"
    )
    log_level = os.environ.get("LOG_LEVEL", "INFO")
    logging.basicConfig(level=log_level)

    bot = HashTableBot(twitch_token, comma_separated_initial_channels.split(","))
    bot.run()
