from twitchio import Chatter, PartialChatter


def is_bot_admin(user: Chatter):
    admins = {"hash_table"}
    return user.name in admins


def is_bot_admin_or_mod(user: Chatter):
    return user and user.is_mod or is_bot_admin(user)


def is_chatter(user: Chatter | PartialChatter | None):
    return user and type(user) == Chatter
