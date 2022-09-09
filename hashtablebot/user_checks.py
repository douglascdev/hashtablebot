from twitchio import Chatter, PartialChatter


# TODO: find a better way to do this, maybe a boolean attribute in BotUser
_admins = {"hash_table"}


def is_bot_admin(user: Chatter):
    return user.name in _admins


def is_bot_admin_or_mod(user: Chatter):
    return user and user.is_mod or is_bot_admin(user)


def is_chatter(user: Chatter | PartialChatter | None):
    return user and type(user) == Chatter
