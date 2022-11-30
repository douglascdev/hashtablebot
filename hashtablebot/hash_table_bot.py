import dataclasses
import logging
import random
import sys
from enum import StrEnum, auto

import translators as tss
from sqlalchemy.exc import NoResultFound
from translators.servers import TranslatorError
from twitchio import User, Message, Channel
from twitchio.ext import commands

from twitchio.ext.commands import Bot, MissingRequiredArgument, BadArgument

from hashtablebot.banking.bank import Bank
from hashtablebot.banking.commands import Deposit, Withdrawal, Batch
from hashtablebot.bot_exceptions import (
    NotEnoughCoinError,
    InvalidPointAmountError,
    ExceptionWithChatMessage,
)
from hashtablebot.entity.bot_user import BotUser
from hashtablebot.memory_entity.no_prefix_command import DefaultNoPrefix
from hashtablebot.memory_entity.point_amount import PointAmountConverter
from hashtablebot.persistence.bot_user_dao import BotUserDao
from hashtablebot.user_checks import is_bot_admin_or_mod


@dataclasses.dataclass
class TranslatedUser:
    user: User
    source_lang: str
    target_lang: str
    channel: Channel


class TranslationType(StrEnum):
    text = auto()
    adduser = auto()
    rmuser = auto()
    rmall = auto()


class HashTableBot(Bot):
    """
    The main bot class, inheriting from twitchio.ext.commands.Bot and adding all of HashTableBot's commands.

    Any method decorated with @commands.command gets added automatically as a twitchio command.

    Commands without prefix are of the DefaultNoPrefix class. The objects of this class are added to a list
    in the constructor and "manually" handled when a message is sent.
    """

    DEFAULT_COOLDOWN_RATE = 2
    DEFAULT_COOLDOWN_TIME = 30

    def __init__(self, token, initial_channels):
        super().__init__(token=token, prefix="$", initial_channels=initial_channels)
        self._no_prefix_commands = (
            DefaultNoPrefix("Robert", "NekoPray Robert"),
            DefaultNoPrefix("NekoPray Robert", "NekoPray Robert"),
            DefaultNoPrefix("elisElis elisTime", "elisElis elisTime"),
            DefaultNoPrefix("elisElis", "elisElis"),
        )
        self._chatting_message_reward = 1
        self._join_channel_message = ""
        self._translated_users: dict[tuple[str, int], TranslatedUser] = dict()
        self._pyramid_length_bounds = (1, 20)

    async def event_ready(self):
        """
        Event called when the Bot has logged in and is ready. Only used for logging purposes.
        """
        logging.info(f"Logged in as {self.nick}")
        logging.info(f"User id is {self.user_id}")

    async def event_channel_joined(self, channel: Channel):
        """
        Event called when the Bot has joined a channel.

        If the _join_channel_message variable is set, it's content gets sent to the joined channel.

        :param channel: the joined channel
        """
        logging.info(f"Joined channel {channel.name}")

        if self._join_channel_message:
            await channel.send(f"{self._join_channel_message}")

    async def event_message(self, message: Message):
        """
        Event called when a message is received.
        Used to check for commands without a prefix and give point rewards.

        :param message:
        """
        # Ignore messages sent by the bot
        if message.echo:
            return

        # Process command-decorated functions and custom commands with no prefix
        invoked_no_prefix_command = False

        for cmd in self._no_prefix_commands:
            if await cmd.is_a_match(message):
                invoked_no_prefix_command = True
                await cmd.respond(message)
                break

        message_is_not_command = (
            not invoked_no_prefix_command
            and not message.content.startswith(self._prefix)
        )
        if message_is_not_command:
            # Distribute point reward for chatting
            try:
                Bank().reward_chatter(message.author, self._chatting_message_reward)

            except Exception as e:
                logging.exception(e)

            await self.translate_user_message(message)

        elif not invoked_no_prefix_command:
            try:
                # Handle default decorated commands
                await self.handle_commands(message)

            except MissingRequiredArgument as e:
                logging.exception(e)
                await message.channel.send("An argument is missing elisStand")

            except BadArgument as e:
                logging.exception(e)
                await message.channel.send(f"Not a valid argument elisStand")

    async def translate_user_message(self, message: Message):
        try:
            user: TranslatedUser = self._translated_users[
                (message.channel.name, int(message.author.id))
            ]

        except KeyError:
            logging.info(f"No translation found for user {message.author.name}")
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

    @commands.cooldown(
        rate=DEFAULT_COOLDOWN_RATE,
        per=DEFAULT_COOLDOWN_TIME,
        bucket=commands.Bucket.channel,
    )
    @commands.command()
    async def bonk(self, ctx: commands.Context, target: User):
        """
        Command to bonk the target user(pings the user with some bonk emotes)
        :param ctx:
        :param target: user that should be bonked
        :return:
        """
        await ctx.send(f"koroneBonk koroneBonk koroneBonk {target.name}")

    @commands.cooldown(
        rate=DEFAULT_COOLDOWN_RATE,
        per=DEFAULT_COOLDOWN_TIME,
        bucket=commands.Bucket.channel,
    )
    @commands.command(aliases=["gamble"])
    async def gamba(self, ctx: commands.Context, amount: str):
        """
        Gamble the specified amount of coins with a 50% chance of winning.
        :param ctx:
        :param amount: amount of coins to bet
        :return:
        """
        try:
            author: BotUser = BotUserDao.get_by_id(int(ctx.author.id))
        except NoResultFound as e:
            # If the user is not in the database, they have no coin
            exception = NotEnoughCoinError(e)
            await ctx.reply(exception.get_chat_message())
            logging.exception(exception)
            return

        try:
            amount = PointAmountConverter.convert(amount, author)
        except InvalidPointAmountError as e:
            await ctx.reply(e.get_chat_message())
            logging.exception(e)
            return

        try:
            if random.randint(0, 1):
                Bank().execute(Deposit(bot_user=author, amount=amount))
                message = f"{ctx.author.name} won {amount} coins elisCoin !!! POGGERS They now have {author.balance}"
            else:
                Bank().execute(Withdrawal(bot_user=author, amount=amount))
                message = f"{ctx.author.name} lost {amount} coins...  peepoSad They now have {author.balance}"

        except ExceptionWithChatMessage as e:
            await ctx.reply(e.get_chat_message())
            logging.exception(e)
            return
        except Exception as e:
            await ctx.reply("Something went wrong peepoSad")
            logging.exception(e)
            return

        BotUserDao.update(author)
        await ctx.send(message)

    @commands.cooldown(
        rate=DEFAULT_COOLDOWN_RATE,
        per=DEFAULT_COOLDOWN_TIME,
        bucket=commands.Bucket.channel,
    )
    @commands.command(aliases=["eliscoin", "points", "coin", "coins"])
    async def eliscoins(self, ctx: commands.Context, target: User = None):
        """
        Tells you how many coins the target user has.
        If no target was specified, tells how many the author has.
        :param ctx:
        :param target:
        :return:
        """
        if not target:
            target = ctx.message.author

        try:
            author: BotUser = BotUserDao.get_by_id(target.id)
        except NoResultFound:
            eliscoins = 0
        else:
            eliscoins = author.balance

        if eliscoins <= 500:
            reaction = " hakaseLaughingAtYou "
        elif eliscoins <= 1000:
            reaction = " elisYes "
        else:
            reaction = " PagChomp "

        await ctx.reply(f"User {target.name} owns {eliscoins} elisCoin ! {reaction}")

    @commands.cooldown(
        rate=DEFAULT_COOLDOWN_RATE,
        per=DEFAULT_COOLDOWN_TIME,
        bucket=commands.Bucket.channel,
    )
    @commands.command()
    async def give(self, ctx: commands.Context, target_user: User, amount: str):
        """
        Give the amount of coins to the target user
        :param ctx:
        :param target_user:
        :param amount:
        :return:
        """
        author_id = ctx.message.author.id

        try:
            author_bot_user: BotUser = BotUserDao.get_by_id(author_id)
        except NoResultFound as e:
            # If the user is not in the database, they have no coin
            exception = NotEnoughCoinError(e)
            logging.exception(exception)
            await ctx.reply(exception.get_chat_message())
            return

        try:
            amount = PointAmountConverter.convert(amount, author_bot_user)
        except InvalidPointAmountError as e:
            logging.exception(e)
            await ctx.reply(e.get_chat_message())
            return

        try:
            target_bot_user: BotUser = BotUserDao.get_by_id(target_user.id)
        except NoResultFound:
            # If the target user doesn't exist, we should create it
            target_bot_user: BotUser = BotUser(id=target_user.id)

        Bank().execute(
            Batch(
                [
                    Withdrawal(bot_user=author_bot_user, amount=amount),
                    Deposit(bot_user=target_bot_user, amount=amount),
                ]
            )
        )

        BotUserDao.update(target_bot_user, author_bot_user)

        await ctx.send(
            f"{ctx.message.author.name} gave {amount} elisCoin to {target_user.name} POGGERS"
        )

    @commands.cooldown(
        rate=DEFAULT_COOLDOWN_RATE,
        per=DEFAULT_COOLDOWN_TIME,
        bucket=commands.Bucket.channel,
    )
    @commands.command(aliases=["commands"])
    async def help(self, ctx: commands.Context):
        """
        Reply listing all bot commands
        :param ctx:
        :return:
        """
        try:
            commands_name_list = [
                f"{self._prefix}{name}" for name, cmd in self.commands.items()
            ]
            commands_name_list += [
                f"'{' '.join(cmd.names)}'" for cmd in self._no_prefix_commands
            ]
            await ctx.reply(f" Commands: {', '.join(commands_name_list)}.")
        except Exception as e:
            logging.exception(e)
            await ctx.reply("Something went wrong peepoSad")

    @commands.cooldown(
        rate=DEFAULT_COOLDOWN_RATE,
        per=DEFAULT_COOLDOWN_TIME,
        bucket=commands.Bucket.channel,
    )
    @commands.command(aliases=["tl"])
    async def translate(self, ctx: commands.Context, *args):
        args: tuple[str, ...]

        try:
            translation_type, *other_args = args
            translation_type: TranslationType = TranslationType[translation_type]
        except (KeyError, ValueError):
            valid_types = ", ".join((t for t in TranslationType))
            await ctx.reply(f"Invalid translation type. Accepted values: {valid_types}")
            return

        match translation_type:
            case TranslationType.text:
                try:
                    source_lang, target_lang, *text = other_args
                    text = " ".join(text)

                except ValueError:
                    if not other_args:
                        await ctx.reply("No text was given for translation.")
                        return

                    source_lang = "auto"
                    target_lang = "en"
                    logging.debug(
                        f"No source or target languages passed, using {source_lang} and {target_lang}"
                    )
                    text = " ".join(other_args)

                try:
                    logging.debug(
                        f"Translating '{text}' from '{source_lang}' to '{target_lang}'"
                    )
                    await ctx.send(tss.google(text, source_lang, target_lang))
                except TranslatorError:
                    logging.debug(
                        "Initial translation failed, attempting with default values"
                    )

                    # User didn't pass a valid source/target, so default to auto and english
                    source_lang = "auto"
                    target_lang = "en"
                    text = " ".join(other_args)

                    try:
                        logging.debug(
                            f"Translating '{text}' from '{source_lang}' to '{target_lang}'"
                        )
                        await ctx.send(tss.google(text, source_lang, target_lang))
                    except TranslatorError as e:
                        await ctx.reply("an unexpected error occurred on translation.")
                        logging.exception(e)

            case TranslationType.adduser:
                try:
                    target_user_name, source_lang, target_lang = other_args
                except ValueError:
                    await ctx.reply(
                        "not enough arguments. Include user, source language and target language"
                    )
                    return

                try:
                    (target_user,) = await self.fetch_users(names=[target_user_name])
                except Exception:
                    await ctx.reply(f"could not find user {target_user_name}")
                    return

                new_user = TranslatedUser(
                    target_user, source_lang, target_lang, ctx.channel
                )
                self._translated_users[(ctx.channel.name, target_user.id)] = new_user
                await ctx.reply(
                    f"Now translating user {new_user.user.name}. "
                    f"Use {self._prefix}tl rmuser <user> to stop translating."
                )

            case TranslationType.rmuser:
                try:
                    (target_user_name,) = other_args
                except ValueError:
                    await ctx.reply("please include the target user.")
                    return

                try:
                    (target_user,) = await self.fetch_users(names=[target_user_name])
                except Exception:
                    await ctx.reply(f"could not find user {target_user_name}")
                    return

                try:
                    del self._translated_users[(ctx.channel.name, target_user.id)]
                except KeyError:
                    msg = f"there's no active translation for user {target_user.name}."
                    await ctx.reply(msg)
                    logging.exception(msg)

            case TranslationType.rmall:
                if not ctx.author.is_mod:
                    await ctx.reply("you're not a moderator.")
                    return

                self._translated_users = dict()
                await ctx.reply("the user translation list was reset.")

    @commands.cooldown(
        rate=DEFAULT_COOLDOWN_RATE,
        per=DEFAULT_COOLDOWN_TIME,
        bucket=commands.Bucket.channel,
    )
    @commands.command()
    async def pyramid(self, ctx: commands.Context, emote: str, length: int):
        min_length, max_length = self._pyramid_length_bounds

        if length > max_length:
            await ctx.reply(f"I can only count to {max_length} menheraLost")
            return

        if length < min_length:
            await ctx.reply(f"minimum length is {min_length} menheraLost")
            return

        if not ctx.author.is_mod:
            await ctx.reply("only mods are allowed to do this.")
            return

        first_half = [" ".join([emote] * i) for i in range(1, length + 1)]

        for line in first_half:
            await ctx.send(line)

        reversed_iter = reversed(first_half)
        next(reversed_iter)

        for line in reversed_iter:
            await ctx.send(line)

    @commands.command()
    async def shutdown(self, ctx: commands.Context):
        """
        Turn off the bot
        :param ctx:
        :return:
        """
        try:
            if is_bot_admin_or_mod(ctx.author):
                await ctx.reply("elisLost bye")
                sys.exit(0)
        except Exception as e:
            logging.exception(e)
            await ctx.reply("Something went wrong peepoSad")

    """
    Some possible new commands

    async def vote(self, ctx: commands.Context):
    async def listen(self, ctx: commands.Context, spotify_link??: str):
    async def loan
    """
