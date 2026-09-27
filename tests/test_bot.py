import asyncio
import datetime
from types import SimpleNamespace

import bot as bot_module


class FakeAsset:
    url = "https://cdn.discordapp.com/avatars/123/avatar.png"

    def is_animated(self):
        return False

    def replace(self, **kwargs):
        return self


class FakeUser:
    id = 123
    name = "test-user"
    display_name = "Test User"
    global_name = "Test User"
    bot = False
    system = False
    accent_color = None
    banner = None
    display_avatar = FakeAsset()
    public_flags = SimpleNamespace()
    created_at = datetime.datetime(2024, 1, 1, tzinfo=datetime.timezone.utc)


class FakeResponse:
    def __init__(self, steps):
        self.steps = steps
        self.defer_kwargs = None
        self.message_kwargs = None

    async def defer(self, **kwargs):
        self.steps.append("defer")
        self.defer_kwargs = kwargs

    async def send_message(self, **kwargs):
        self.steps.append("send_message")
        self.message_kwargs = kwargs


class FakeInteraction:
    def __init__(self):
        self.steps = []
        self.user = FakeUser()
        self.response = FakeResponse(self.steps)
        self.edited_embed = None

    async def edit_original_response(self, *, embed):
        self.steps.append("edit_original_response")
        self.edited_embed = embed


class CaptureResponse:
    def __init__(self):
        self.kwargs = None

    async def send_message(self, *args, **kwargs):
        self.kwargs = dict(kwargs)
        if args:
            self.kwargs["content"] = args[0]


class CaptureInteraction:
    def __init__(self):
        self.response = CaptureResponse()


def test_all_commands_are_registered_for_both_install_types_and_contexts():
    commands = bot_module.bot.tree.get_commands()
    assert {command.name for command in commands} == {
        "userid", "userinfo", "avatar", "timestamp", "ping", "shortcuts", "help"
    }

    for command in commands:
        payload = command.to_dict(bot_module.bot.tree)
        assert payload["contexts"] == [0, 1, 2]
        assert payload["integration_types"] == [0, 1]


def test_userinfo_defers_before_fetch_and_edits_ephemeral_response(monkeypatch):
    interaction = FakeInteraction()

    async def fake_fetch_user(user_id):
        interaction.steps.append("fetch_user")
        assert user_id == interaction.user.id
        return FakeUser()

    monkeypatch.setattr(bot_module.bot, "fetch_user", fake_fetch_user)

    asyncio.run(bot_module.userinfo.callback(interaction))

    assert interaction.steps == ["defer", "fetch_user", "edit_original_response"]
    assert interaction.response.defer_kwargs == {"ephemeral": True, "thinking": True}
    assert interaction.edited_embed.title == "Your Info"


def test_shortcuts_use_current_key_name_and_bookmark_wording():
    interaction = CaptureInteraction()
    asyncio.run(bot_module.shortcuts.callback(interaction))

    embed = interaction.response.kwargs["embed"]
    shortcuts = next(field.value for field in embed.fields if field.name == "Desktop Keyboard Shortcuts")
    tips = next(field.value for field in embed.fields if field.name == "🔧 Handy Tricks")
    assert "Shift+↑` (Windows) / `Option+↑` (Mac)" in shortcuts
    assert "Ctrl+Shift+Alt" not in shortcuts
    assert "Bookmark Message" in tips
    assert "Star ⭐" not in tips


def test_timestamp_rejects_invalid_date_ephemerally():
    interaction = CaptureInteraction()
    asyncio.run(
        bot_module.timestamp.callback(
            interaction, year=2025, month=2, day=30, hour=0, minute=0
        )
    )

    assert interaction.response.kwargs["ephemeral"] is True
    assert interaction.response.kwargs["content"].startswith("Invalid date:")
