# 🐼 Panda Bot

A lightweight Discord utility bot with slash commands that work in servers, DMs, and private channels. All responses are ephemeral — only the user who runs the command can see them.

---

## Commands

| Command | Description |
|---|---|
| `/userid` | Get your own or another user's Discord ID |
| `/userinfo` | Full account info — badges, avatar, banner, account age, Nitro indicators |
| `/avatar` | Fetch anyone's full-res avatar with PNG, WebP, and GIF download links |
| `/timestamp` | Convert any date into Discord's `<t:>` timestamp format with all styles |
| `/ping` | Check the bot's WebSocket latency |
| `/shortcuts` | Discord keyboard shortcuts and markdown cheatsheet |
| `/help` | List all available commands |

---

## Tech Stack

- **Language:** Python
- **Library:** [discord.py](https://github.com/Rapptz/discord.py)
- **Command Type:** Slash commands via `app_commands`
- **Hosting:** Runs on any platform that supports Python + environmen

---

## Notes

- The bot uses `fetch_user()` in `/userinfo` to retrieve banner and accent color data, which requires a full API call beyond the cache.
- Nitro detection is based on observable indicators (animated avatar, profile banner) not account data, since that's private.
- Badge detection uses Discord's `public_flags` and may not reflect all badges depending on API availability.

---


Made by **Panda** — [Portfolio](https://panda-404.netlify.app/)
