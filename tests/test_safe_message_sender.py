from unittest import IsolatedAsyncioTestCase

from hashtablebot.message_sender import AbstractTwitchContext, SafeMessageSender


class TestSafeMessageSender(IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        class TwitchContext:
            async def send(self, message: str):
                pass

            async def reply(self, message: str):
                pass

        class ConcreteNamed:
            name = "asd"

        self.context: AbstractTwitchContext = TwitchContext()
        self.context.author = self.context.channel = ConcreteNamed()

    async def test_command_injection_empty_char(self):
        unicode_empty_characters = (
            "\u0020",
            "\u00A0",
            "\u2000",
            "\u2001",
            "\u2002",
            "\u2003",
            "\u2004",
            "\u2005",
            "\u2006",
            "\u2007",
            "\u2008",
            "\u2009",
            "\u200A",
            "\u2028",
            "\u205F",
            "\u3000",
        )

        for character in unicode_empty_characters:
            result = await SafeMessageSender.send(self.context, f"{character}/ban user")
            assert result.startswith("#")
