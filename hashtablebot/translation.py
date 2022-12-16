import dataclasses
import logging
from enum import StrEnum, auto

import translators as tss
from translators.servers import TranslatorError
from twitchio import User, Channel, Message

DEFAULT_SOURCE_LANG = "auto"
DEFAULT_TARGET_LANG = "en"


@dataclasses.dataclass
class TranslatedUser:
    """
    A user that gets every message they type in the channel's chat
    translated by the bot from source to target language.
    """

    user: User
    source_lang: str
    target_lang: str
    channel: Channel


class TranslationType(StrEnum):
    """
    First argument passed to the translate command.
    """

    # Translate all following arguments as text
    text = auto()
    # Add user to _translated_users, translating every message they type
    adduser = auto()
    # Remove user from _translated_users
    rmuser = auto()
    # Remove all users from _translated_users
    rmall = auto()

    @staticmethod
    def types() -> str:
        """
        :return: comma-separated string with valid translation types
        """
        return ", ".join((t for t in TranslationType))


def translate_text(
    text, source_lang=DEFAULT_SOURCE_LANG, target_lang=DEFAULT_TARGET_LANG
) -> str:
    """
    Directly calls the translation API with text and source and target language, and returns
    the translated text or gives an exception.
    :param text: text to be translated
    :param source_lang: language the text is in
    :param target_lang: language to translate it to
    :return: translated text
    :raises TranslatorError
    """
    logging.debug(f"Translating from '{source_lang}' to '{target_lang}' text '{text}'.")

    if not text:
        raise TranslatorError

    return tss.google(text, source_lang, target_lang)


class Translator:
    def __init__(self):
        # Dictionary mapping (channel_name, user_id) to TranslatedUser object
        self._translated_users: dict[tuple[str, int], TranslatedUser] = dict()

    async def translate(self, ctx, args) -> str:
        """
        Receives arguments passed to the translate command, validates the type
        and calls the appropriate method according to the TranslationType
        :param ctx: context
        :param args: arguments passed to the translate command
        :return: string with the answer(error or translation)
        """
        args: tuple[str, ...]

        try:
            translation_type, *other_args = args
            translation_type: TranslationType = TranslationType[translation_type]
        except (KeyError, ValueError) as e:
            return (
                f"invalid translation type. Accepted values: {TranslationType.types()}"
            )

        if len(args) == 1 and translation_type != TranslationType.rmall:
            return "not enough arguments."

        match translation_type:
            case TranslationType.text:
                """
                Sending the translated message directly to chat allows users to execute
                twitch commands using the bot. Don't remove the 'Translation' part.
                """
                return "Translation: " + await self._translate_message_text(other_args)

            case TranslationType.adduser:
                return await self._add_translated_user(ctx, other_args)

            case TranslationType.rmuser:
                return await self._remove_translated_user(ctx, other_args)

            case TranslationType.rmall:
                return await self._remove_all_translated_users(ctx)

    async def translate_user_message(self, message: Message) -> None:
        """
        Checks if message author is in the _translated_users list and
        if so, send the translated message in chat.
        """
        try:
            user: TranslatedUser = self._translated_users[
                (message.channel.name, int(message.author.id))
            ]

        except KeyError:
            logging.debug(f"No translation found for user {message.author.name}")
            return

        try:
            logging.debug(
                f"Translating '{message.content}' from '{user.source_lang}' to '{user.target_lang}'"
            )
            translated_msg = tss.google(
                message.content, user.source_lang, user.target_lang
            )
        except Exception as e:
            logging.exception(e)
            return

        await message.channel.send(f"{message.author.name}: {translated_msg}")

    async def _translate_message_text(self, other_args) -> str:
        try:
            source_lang, target_lang, *text = other_args
            text = " ".join(text)

        except ValueError:
            if not other_args:
                return "no text was given for translation."

            source_lang = DEFAULT_SOURCE_LANG
            target_lang = DEFAULT_TARGET_LANG
            logging.debug(
                f"No source or target languages passed, using {source_lang} and {target_lang}"
            )
            text = " ".join(other_args)

        try:
            return translate_text(text, source_lang, target_lang)
        except TranslatorError:
            logging.debug("Initial translation failed, attempting with default values")

            """
            Assume user didn't pass a valid source/target, so use the default values
            and treat all arguments as text
            """
            source_lang = DEFAULT_SOURCE_LANG
            target_lang = DEFAULT_TARGET_LANG
            text = " ".join(other_args)

            try:
                return translate_text(text, source_lang, target_lang)
            except TranslatorError:
                return "an unexpected error occurred on translation."

    async def _add_translated_user(self, ctx, other_args):
        try:
            target_user_name, source_lang, target_lang = other_args
        except ValueError:
            return "not enough arguments. Include user, source language and target language"

        try:
            (target_user,) = await ctx.bot.fetch_users(names=[target_user_name])
        except Exception:
            return "user not found."

        new_user = TranslatedUser(target_user, source_lang, target_lang, ctx.channel)
        self._translated_users[(ctx.channel.name, target_user.id)] = new_user
        return (
            f"Now translating user {new_user.user.name}. "
            f"Use {await ctx.bot._prefix(self, ctx.message)}tl rmuser <user> to stop translating."
        )

    async def _remove_translated_user(self, ctx, other_args):
        try:
            (target_user_name,) = other_args
        except ValueError:
            return "please include the target user."

        try:
            (target_user,) = await ctx.bot.fetch_users(names=[target_user_name])
        except Exception:
            return f"could not find user {target_user_name}"

        try:
            del self._translated_users[(ctx.channel.name, target_user.id)]
            return f"stopped translating user '{target_user_name}'."
        except KeyError:
            msg = f"there's no active translation for user {target_user.name}."
            logging.exception(msg)
            return msg

    async def _remove_all_translated_users(self, ctx):
        if not ctx.author.is_mod:
            return "you're not a moderator."

        self._translated_users = dict()
        return "the user translation list was reset."
