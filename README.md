# Lime Bot

A lightweight Discord utility bot with slash commands for servers, bot DMs, and private channels. Responses are ephemeral, so only the person who runs a command can see the result.

## Commands

| Command | Description |
|---|---|
| `/userid` | Get your own or another user's Discord ID |
| `/userinfo` | View account details, public badges, avatar, banner, and account age |
| `/avatar` | Get an avatar with PNG, WebP, and (for animated avatars) GIF links |
| `/timestamp` | Convert a date and time into Discord timestamp formats |
| `/ping` | Check the bot's WebSocket latency |
| `/shortcuts` | View desktop shortcuts and Markdown tips |
| `/help` | List available commands |

## Requirements

- Python 3.8 or newer
- `discord.py` 2.7.1 (the current release pinned in [`requirements.txt`](requirements.txt))
- A Discord application and bot token

## Setup

1. Create a Discord application and bot in the [Discord Developer Portal](https://discord.com/developers/applications).
2. In **Installation**, enable both **Guild Install** and **User Install**. Set the `applications.commands` scope for both installation types; for Guild Install also enable the `bot` scope. The bot needs permission to send messages and embeds in guild channels.
3. Create and activate a virtual environment, then install the pinned dependency.

   **Linux/macOS:**

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

   **Windows PowerShell:**

   ```powershell
   py -3 -m venv .venv
   .venv\Scripts\Activate.ps1
   ```

   Then, on either platform:

   ```bash
   python -m pip install -r requirements.txt
   ```

4. Set the bot token as an environment variable. Do not commit it.

   **Linux/macOS:**

   ```bash
   export DISCORD_TOKEN="your-bot-token"
   ```

   **Windows PowerShell:**

   ```powershell
   $env:DISCORD_TOKEN = "your-bot-token"
   ```

5. Start the bot:

   ```bash
   python bot.py
   ```

The application command decorators enable guild, bot-DM, and private-channel contexts. Discord's Developer Portal installation settings must also support the selected install types; see [Discord's user-installable app guide](https://docs.discord.com/developers/tutorials/developing-a-user-installable-app).

## Development and checks

Install test dependencies and run the checks with:

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q
python -W error::SyntaxWarning -m compileall -q bot.py tests
```

GitHub Actions runs these checks on pushes and pull requests. A scheduled dependency audit checks the pinned package and its transitive dependencies; Dependabot checks weekly for package and action updates.

## Notes

- `/userinfo` fetches the full Discord user object to retrieve banner and accent-color data and defers its ephemeral response while that API request completes.
- “Nitro indicators” (such as animated avatars and profile banners) are only observable hints, not authoritative subscription data.
- Badge detection is based on `public_flags` and can vary with Discord API availability.
- `/shortcuts` reflects Discord's current [keyboard-shortcut guide](https://support.discord.com/hc/en-us/articles/31232432266647-Discord-Commands-Shortcuts-and-Navigation-Guide). Bookmark availability is limited and may depend on Discord account eligibility.

---

Made by **Lime** — [Portfolio](https://lime.is-a.dev/)
