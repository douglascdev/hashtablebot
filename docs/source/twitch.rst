.. _twitch:

Twitch
======

The bot uses the `TwitchIO` library to handle twitch functionality.
Check out their `documentation <https://twitchio.dev/en/latest>`_ for more details.

.. WARNING::
   Sending user input directly with `ctx.send` without any preceding text allows users to inject twitch commands,
   which then get executed using the same level of permission as the bot.

   If the API scopes include moderation permissions and the bot is a mod, a non-mod could, for example,
   use `/ban <user>`.

   To prevent that, never start the `ctx.send` argument string with user input.
