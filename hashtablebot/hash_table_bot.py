import logging
import random
import sys
import time
from asyncio import CancelledError

from sqlalchemy.exc import NoResultFound
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
from hashtablebot.translation import Translator
from hashtablebot.user_checks import is_bot_admin_or_mod


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
        super().__init__(token=token, prefix=self._get_bot_prefix)
        self._no_prefix_commands = (
            DefaultNoPrefix("Robert", "NekoPray Robert"),
            DefaultNoPrefix("NekoPray Robert", "NekoPray Robert"),
            DefaultNoPrefix("elisElis elisTime", "elisElis elisTime"),
            DefaultNoPrefix("elisElis", "elisElis"),
        )
        self._chatting_message_reward = 1
        self._initial_channels = initial_channels
        self._join_channel_message = ""
        self._pyramid_length_bounds = (1, 20)
        self._translator = Translator()
        self._duel_wait_until_go_in_seconds = 6
        self._duel_timeout_in_seconds = 2
        self._channel_id_to_prefix: dict[int, str] = dict()

    async def _get_bot_prefix(self, _: Bot, message: Message):
        try:
            channel_id = (await message.channel.user()).id
            return self._channel_id_to_prefix[channel_id]
        except Exception as e:
            logging.exception(e)
            return "$"

    async def event_ready(self):
        """
        Event called when the Bot has logged in and is ready.
        """
        logging.info(f"Logged in as {self.nick}")
        logging.info(f"User id is {self.user_id}")

        joined_channel_bot_users = BotUserDao.get_all_joined_channels()

        for channel_bot_user in joined_channel_bot_users:
            self._channel_id_to_prefix[int(channel_bot_user.id)] = channel_bot_user.bot_command_prefix

        joined_channel_ttv_users = await self.fetch_users(
            ids=[bot_user.id for bot_user in joined_channel_bot_users]
        )
        names = {
            ttv_user.name
            for ttv_user in joined_channel_ttv_users
        }
        names = names.union(self._initial_channels)

        await self.join_channels(list(names))

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
            and not message.content.startswith(await self._prefix(self, message))
        )
        if message_is_not_command:
            # Distribute point reward for chatting
            try:
                Bank().reward_chatter(message.author, self._chatting_message_reward)

            except Exception as e:
                logging.exception(e)

            await self._translator.translate_user_message(message)

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
    @commands.command()
    async def join(self, ctx: commands.Context):
        """
        Join message author's channel. The joined status is persisted.
        """
        try:
            author: BotUser = BotUserDao.get_by_id(int(ctx.author.id))
        except NoResultFound:
            author: BotUser = BotUser(id=int(ctx.author.id))

        if author.bot_joined_channel:
            await ctx.reply("already joined channel.")
            return

        author.bot_joined_channel = True
        BotUserDao.update(author)

        await self.join_channels((ctx.author.name,))
        await ctx.reply(f"joined channel '{ctx.author.name}'")

    @commands.cooldown(
        rate=DEFAULT_COOLDOWN_RATE,
        per=DEFAULT_COOLDOWN_TIME,
        bucket=commands.Bucket.channel,
    )
    @commands.command()
    async def setprefix(self, ctx: commands.Context, prefix: str):
        """
        Set the bot's prefix for this channel
        """
        if not ctx.author.is_mod:
            await ctx.reply("only moderators are allowed to set my prefix.")
            return

        try:
            channel_ttv_user = await ctx.channel.user()
        except Exception as e:
            logging.exception(e)
            await ctx.reply("could not fetch channel user.")
            return

        try:
            channel_bot_user: BotUser = BotUserDao.get_by_id(int(channel_ttv_user.id))
        except NoResultFound:
            channel_bot_user: BotUser = BotUser(id=int(ctx.author.id))

        self._channel_id_to_prefix[channel_bot_user.id] = prefix
        channel_bot_user.bot_command_prefix = prefix
        BotUserDao.update(channel_bot_user)

        await ctx.reply(f"prefix set to '{prefix}'.")

    @commands.cooldown(
        rate=DEFAULT_COOLDOWN_RATE,
        per=DEFAULT_COOLDOWN_TIME,
        bucket=commands.Bucket.channel,
    )
    @commands.command()
    async def leave(self, ctx: commands.Context):
        """
        Leave message author's channel. The joined status is persisted.
        """
        try:
            author: BotUser = BotUserDao.get_by_id(int(ctx.author.id))
            assert author.bot_joined_channel is True
        except (NoResultFound, AssertionError):
            await ctx.reply("I have not joined your channel.")
            return

        author.bot_joined_channel = False
        BotUserDao.update(author)

        await ctx.reply(f"left channel '{ctx.author.name}'.")
        await self.part_channels((ctx.author.name,))

    @commands.cooldown(
        rate=DEFAULT_COOLDOWN_RATE,
        per=DEFAULT_COOLDOWN_TIME,
        bucket=commands.Bucket.channel,
    )
    @commands.command(aliases=["gamba"])
    async def gamble(self, ctx: commands.Context, amount: str):
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
    async def setpoints(self, ctx: commands.Context, target_user: User, amount: int):
        if not ctx.author.is_mod:
            await ctx.reply("you're not a moderator...")
            return

        try:
            target_bot_user: BotUser = BotUserDao.get_by_id(target_user.id)
        except NoResultFound:
            # If the target user doesn't exist, we should create it
            target_bot_user: BotUser = BotUser(id=target_user.id)

        target_bot_user.balance = amount

        BotUserDao.update(target_bot_user)

        await ctx.send(f"{ctx.message.author.name} now has {amount} points!")

    @commands.cooldown(
        rate=DEFAULT_COOLDOWN_RATE,
        per=DEFAULT_COOLDOWN_TIME,
        bucket=commands.Bucket.channel,
    )
    @commands.command(aliases=["leaderboards", "lb"])
    async def leaderboard(self, ctx: commands.Context):
        bot_users: list[BotUser] = BotUserDao.get_until_limit_order_by_balance_desc(5)
        twitch_users: list[User] = await self.fetch_users(
            ids=[user.id for user in bot_users]
        )
        id_to_name = {user.id: user.name for user in twitch_users}
        leaderboard_list = [
            f"{i}. {id_to_name[bot_user.id]}: {bot_user.balance}"
            for i, bot_user in enumerate(bot_users, start=1)
        ]
        await ctx.send(" ".join(leaderboard_list))

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
                f"{await self._prefix(self, ctx.message)}{name}" for name, cmd in self.commands.items()
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
        message = await self._translator.translate(ctx, args)
        await ctx.send(message.capitalize())

    @commands.cooldown(
        rate=DEFAULT_COOLDOWN_RATE,
        per=DEFAULT_COOLDOWN_TIME,
        bucket=commands.Bucket.channel,
    )
    @commands.command()
    async def duel(self, ctx: commands.Context, duel_target: User, amount: str):
        """
        Duel with target user on rock, paper scissors
        :param ctx:
        :param duel_target:
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
            duel_target_bot_user: BotUser = BotUserDao.get_by_id(duel_target.id)
        except NoResultFound:
            # If the target user doesn't exist, we should create it
            duel_target_bot_user: BotUser = BotUser(id=duel_target.id)

        for bot_user, name in (duel_target_bot_user, duel_target.name), (
            author_bot_user,
            ctx.author.name,
        ):
            if bot_user.balance < amount:
                await ctx.reply(f"user {name} only has {amount} points!")
                return

        valid_answers = "rock", "paper", "scissors"
        await ctx.send(
            f"@{duel_target.name} @{ctx.author.name} write your answer as {', '.join(valid_answers)} "
            f"and wait until I say GO to sent it."
        )

        time.sleep(self._duel_wait_until_go_in_seconds)

        await ctx.send("GO!!!!!!!!!!!!!!!!!!")

        target_answer = None
        author_answer = None

        def store_answer(msg: Message):
            nonlocal target_answer
            nonlocal author_answer

            if msg.echo:
                return False

            if msg.author.id == str(duel_target.id):
                target_answer = msg.content.lower()
                logging.debug(f"target answer set to {target_answer}")
            elif msg.author.id == ctx.author.id:
                author_answer = msg.content.lower()
                logging.debug(f"author answer set to {author_answer}")

            return target_answer and author_answer

        timeout_time = self._duel_timeout_in_seconds

        try:
            await self.wait_for("message", store_answer, timeout=timeout_time)
        except TimeoutError:
            await ctx.send(
                f"Answers were not given in {timeout_time} seconds, duel cancelled."
            )

        for name, answer in (duel_target.name, target_answer), (
            ctx.author.name,
            author_answer,
        ):
            if answer not in valid_answers:
                logging.debug(f"Answer {answer} by {name} is not in {valid_answers}")
                await ctx.send(
                    f"User {name} did not give a valid answer, so the duel was cancelled. "
                    f"The valid answers are {', '.join(valid_answers)}."
                )
                return

        if author_answer == target_answer:
            await ctx.send("It's a tie!")
            return

        wins = {("rock", "scissors"), ("paper", "rock"), ("scissors", "paper")}

        answer = author_answer, target_answer
        author_won = answer in wins

        if author_won:
            Bank().execute(
                Batch(
                    [
                        Deposit(bot_user=author_bot_user, amount=amount),
                        Withdrawal(bot_user=duel_target_bot_user, amount=amount),
                    ]
                )
            )

            BotUserDao.update(duel_target_bot_user, author_bot_user)

            await ctx.send(f"@{ctx.author.name} won the duel and got {amount} points!")
        else:
            Bank().execute(
                Batch(
                    [
                        Withdrawal(bot_user=author_bot_user, amount=amount),
                        Deposit(bot_user=duel_target_bot_user, amount=amount),
                    ]
                )
            )

            BotUserDao.update(duel_target_bot_user, author_bot_user)

            await ctx.send(f"@{duel_target.name} won the duel and got {amount} points!")

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
