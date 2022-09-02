import logging
import random
import sys

from sqlalchemy.exc import NoResultFound
from twitchio import User, Message, Channel
from twitchio.ext import commands

from twitchio.ext.commands import MissingRequiredArgument, BadArgument

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


class HashTableBot(commands.Bot):
    DEFAULT_COOLDOWN_RATE = 1
    DEFAULT_COOLDOWN_TIME = 30

    def __init__(self, token, initial_channels):
        super().__init__(token=token, prefix="$", initial_channels=initial_channels)
        self._no_prefix_commands = (
            DefaultNoPrefix(("Robert",), "NekoPray Robert"),
            DefaultNoPrefix(("NekoPray", "Robert"), "NekoPray Robert"),
            DefaultNoPrefix(("elisElis", "elisTime"), "elisElis elisTime"),
            DefaultNoPrefix(("elisElis",), "elisElis"),
        )
        self._chatting_message_reward = 1
        self._join_channel_message = ""

    async def event_ready(self):
        logging.info(f"Logged in as {self.nick}")
        logging.info(f"User id is {self.user_id}")

    async def event_channel_joined(self, channel: Channel):
        logging.info(f"Joined channel {channel.name}")

        if self._join_channel_message:
            await channel.send(f"{self._join_channel_message}")

    async def event_message(self, message: Message):
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

    @commands.cooldown(rate=DEFAULT_COOLDOWN_RATE, per=DEFAULT_COOLDOWN_TIME, bucket=commands.Bucket.channel)
    @commands.command()
    async def bonk(self, ctx: commands.Context):
        if ctx.message.content:
            pos = ctx.message.content.find(" ")

            if pos >= 0:
                await ctx.send(
                    f"koroneBonk koroneBonk koroneBonk {ctx.message.content[pos:]}"
                )
            else:
                await ctx.reply(f"who am I suppose to bonk elisHuh ")

    @commands.cooldown(rate=DEFAULT_COOLDOWN_RATE, per=DEFAULT_COOLDOWN_TIME, bucket=commands.Bucket.channel)
    @commands.command(aliases=["gamble"])
    async def gamba(self, ctx: commands.Context, amount: str):
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

    @commands.cooldown(rate=DEFAULT_COOLDOWN_RATE, per=DEFAULT_COOLDOWN_TIME, bucket=commands.Bucket.channel)
    @commands.command(aliases=["eliscoin", "points"])
    async def eliscoins(self, ctx: commands.Context):
        try:
            author: BotUser = BotUserDao.get_by_id(int(ctx.author.id))
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

        await ctx.reply(f"You have {eliscoins} elisCoin ! {reaction}")

    @commands.cooldown(rate=DEFAULT_COOLDOWN_RATE, per=DEFAULT_COOLDOWN_TIME, bucket=commands.Bucket.channel)
    @commands.command()
    async def give(self, ctx: commands.Context, target_user: User, amount: str):
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

    @commands.cooldown(rate=DEFAULT_COOLDOWN_RATE, per=DEFAULT_COOLDOWN_TIME, bucket=commands.Bucket.channel)
    @commands.command(aliases=["commands"])
    async def help(self, ctx: commands.Context):
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

    @commands.command()
    async def shutdown(self, ctx: commands.Context):
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