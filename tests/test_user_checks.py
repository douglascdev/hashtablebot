from unittest import TestCase
from unittest.mock import PropertyMock, patch

from hashtablebot import user_checks


class Test(TestCase):
    def test_is_bot_admin_or_mod(self):
        # Not admin or mod
        with patch("hashtablebot.user_checks.Chatter") as patched_chatter:
            type(patched_chatter.return_value).is_mod = PropertyMock(return_value=False)
            type(patched_chatter.return_value).name = PropertyMock(
                return_value="NotAdminName"
            )
            self.assertFalse(user_checks.is_bot_admin_or_mod(patched_chatter()))

        # Not admin but is mod
        with patch("hashtablebot.user_checks.Chatter") as patched_chatter:
            type(patched_chatter.return_value).is_mod = PropertyMock(return_value=True)
            type(patched_chatter.return_value).name = PropertyMock(
                return_value="NotAdminName"
            )
            self.assertTrue(user_checks.is_bot_admin_or_mod(patched_chatter()))

        # Not mod but is admin
        with patch("hashtablebot.user_checks.Chatter") as patched_chatter:
            admin_name = next(iter(user_checks._admins))
            type(patched_chatter.return_value).is_mod = PropertyMock(return_value=False)
            type(patched_chatter.return_value).name = PropertyMock(
                return_value=admin_name
            )
            self.assertTrue(user_checks.is_bot_admin_or_mod(patched_chatter()))

        # Is both mod and admin
        with patch("hashtablebot.user_checks.Chatter") as patched_chatter:
            admin_name = next(iter(user_checks._admins))
            type(patched_chatter.return_value).is_mod = PropertyMock(return_value=True)
            type(patched_chatter.return_value).name = PropertyMock(
                return_value=admin_name
            )
            self.assertTrue(user_checks.is_bot_admin_or_mod(patched_chatter()))
