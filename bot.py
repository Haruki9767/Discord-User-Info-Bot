import discord
from discord import app_commands
from discord.ext import commands
import datetime
import os

# bot setup
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# Helper
def user_app():
    #Decorator shorthand
    def decorator(func):
        func = app_commands.allowed_installs(guilds=True, users=True)(func)
        func = app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)(func)
        return func
    return decorator


# bot ready
@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
        print(f"✅ Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"❌ Sync failed: {e}")
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")



# Get a user's Discord ID 

@bot.tree.command(name="userid", description="📋 Shows a user's Discord ID")
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@app_commands.describe(user="The user to get the ID of (leave blank for yourself)")
async def userid(interaction: discord.Interaction, user: discord.User = None):
    target = user or interaction.user
    label = "Your User ID" if target == interaction.user else f"{target.display_name}'s User ID"
    embed = discord.Embed(
        title=label,
        description=f"```{target.id}```",
        color=0x5865F2,
    )
    embed.set_thumbnail(url=target.display_avatar.url)
    embed.set_footer(text="Made by Panda • [Portfolio](https://panda-404.netlify.app/)")
    await interaction.response.send_message(embed=embed, ephemeral=True)


# Get a user information
@bot.tree.command(name="userinfo", description="🪪 Shows info about a Discord user")
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@app_commands.describe(user="The user to look up (leave blank for yourself)")
async def userinfo(interaction: discord.Interaction, user: discord.User = None):
    # Fetch full user object to get banner/accent color
    target_id = (user or interaction.user).id
    try:
        target = await bot.fetch_user(target_id)
    except Exception:
        target = user or interaction.user

    # Account age
    created_ts = int(target.created_at.timestamp())
    now = datetime.datetime.now(datetime.timezone.utc)
    age_days = (now - target.created_at).days
    age_str = (
        f"{age_days // 365}y {(age_days % 365) // 30}m {age_days % 30}d" if age_days >= 365
        else f"{age_days // 30}m {age_days % 30}d" if age_days >= 30
        else f"{age_days}d"
    )

    label = "Your Info" if target.id == interaction.user.id else f"User Info — {target.display_name}"
    embed = discord.Embed(
        title=label,
        color=target.accent_color or 0x5865F2,
    )
    embed.set_thumbnail(url=target.display_avatar.url)

    # Identity
    embed.add_field(name="🏷️ Username",        value=f"`{target.name}`",               inline=True)
    embed.add_field(name="✨ Display Name",     value=f"`{target.display_name}`",        inline=True)
    # Global name (pomelo system) differs from display_name only for legacy users
    global_name = target.global_name or "—"
    embed.add_field(name="🌐 Global Name",      value=f"`{global_name}`",                inline=True)

    embed.add_field(name="🆔 User ID",          value=f"`{target.id}`",                  inline=True)
    embed.add_field(name="🤖 Bot Account",      value="Yes ✅" if target.bot else "No ❌", inline=True)
    embed.add_field(name="⚙️ System Account",   value="Yes ✅" if target.system else "No ❌", inline=True)

    # Account Created
    embed.add_field(
        name="📅 Account Created",
        value=f"<t:{created_ts}:F>\n<t:{created_ts}:R> *(account is {age_str} old)*",
        inline=False,
    )

    # Nitro User id
    has_animated_av = target.display_avatar.is_animated()
    has_banner      = target.banner is not None
    nitro_hints = []
    if has_animated_av:
        nitro_hints.append("Animated avatar 🎞️")
    if has_banner:
        nitro_hints.append("Profile banner 🖼️")
    nitro_value = ", ".join(nitro_hints) if nitro_hints else "No indicators detected"
    embed.add_field(name="💎 Nitro Indicators", value=nitro_value, inline=False)

    # Banner
    if target.banner:
        embed.set_image(url=target.banner.url)
        embed.add_field(
            name="🎨 Banner",
            value=f"[PNG]({target.banner.replace(format='png', size=1024).url})"
                  + (f" • [GIF]({target.banner.replace(format='gif', size=1024).url})" if target.banner.is_animated() else ""),
            inline=True,
        )
    if target.accent_color:
        hex_color = f"#{target.accent_color.value:06X}"
        embed.add_field(name="🎨 Accent Color", value=f"`{hex_color}`", inline=True)

    # Avatar Urls
    av = target.display_avatar
    av_links = (
        f"[PNG]({av.replace(format='png', size=1024).url}) • "
        f"[WebP]({av.replace(format='webp', size=1024).url}) • "
        f"[GIF]({av.replace(format='gif', size=1024).url})"
        if av.is_animated()
        else f"[PNG]({av.replace(format='png', size=1024).url}) • "
             f"[WebP]({av.replace(format='webp', size=1024).url})"
    )
    embed.add_field(name="🖼️ Avatar Links", value=av_links, inline=False)

    # badges (might not work properly)
    flags = target.public_flags
    flag_map = {
        "staff":                  "👾 Discord Staff",
        "partner":                "🤝 Partnered Server Owner",
        "hypesquad":              "🏠 HypeSquad Events",
        "bug_hunter":             "🐛 Bug Hunter",
        "hypesquad_bravery":      "🦁 HypeSquad Bravery",
        "hypesquad_brilliance":   "🌟 HypeSquad Brilliance",
        "hypesquad_balance":      "⚖️ HypeSquad Balance",
        "early_supporter":        "🌅 Early Supporter",
        "bug_hunter_level_2":     "🐛🥇 Bug Hunter Level 2",
        "verified_bot_developer": "🔧 Verified Bot Developer",
        "active_developer":       "🛠️ Active Developer",
    }
    badges = [lbl for attr, lbl in flag_map.items() if getattr(flags, attr, False)]
    if badges:
        embed.add_field(name="🏅 Badges", value="\n".join(badges), inline=False)

    embed.set_footer(text="Made by Panda • [Portfolio](https://panda-404.netlify.app/)")
    await interaction.response.send_message(embed=embed, ephemeral=True)


# Get a user's avatar
@bot.tree.command(name="avatar", description="🖼️ Get a user's avatar")
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@app_commands.describe(user="The user whose avatar to fetch (leave blank for yours)")
async def avatar(interaction: discord.Interaction, user: discord.User = None):
    target = user or interaction.user
    av = target.display_avatar.replace(size=1024)
    embed = discord.Embed(title=f"{target.display_name}'s Avatar", color=0x5865F2)
    embed.set_image(url=av.url)
    links = f"[PNG]({av.replace(format='png').url})"
    if av.is_animated():
        links += f" • [GIF]({av.replace(format='gif').url})"
    else:
        links += f" • [WebP]({av.replace(format='webp').url})"
    embed.add_field(name="Download", value=links)
    embed.set_footer(text="Made by Panda • [Portfolio](https://panda-404.netlify.app/)")
    await interaction.response.send_message(embed=embed, ephemeral=True)


# Timestamp
@bot.tree.command(name="timestamp", description="⏱️ Convert a date to Discord timestamp format")
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@app_commands.describe(
    year="Year (e.g. 2025)",
    month="Month (1–12)",
    day="Day (1–31)",
    hour="Hour in 24h format (0–23, default 0)",
    minute="Minute (0–59, default 0)",
)
async def timestamp(
    interaction: discord.Interaction,
    year: int,
    month: int,
    day: int,
    hour: int = 0,
    minute: int = 0,
):
    try:
        dt = datetime.datetime(year, month, day, hour, minute, tzinfo=datetime.timezone.utc)
    except ValueError as e:
        await interaction.response.send_message(f"❌ Invalid date: `{e}`", ephemeral=True)
        return

    ts = int(dt.timestamp())
    styles = {
        "Short Time":       (f"<t:{ts}:t>",  f"`<t:{ts}:t>`"),
        "Long Time":        (f"<t:{ts}:T>",  f"`<t:{ts}:T>`"),
        "Short Date":       (f"<t:{ts}:d>",  f"`<t:{ts}:d>`"),
        "Long Date":        (f"<t:{ts}:D>",  f"`<t:{ts}:D>`"),
        "Short Date/Time":  (f"<t:{ts}:f>",  f"`<t:{ts}:f>`"),
        "Long Date/Time":   (f"<t:{ts}:F>",  f"`<t:{ts}:F>`"),
        "Relative":         (f"<t:{ts}:R>",  f"`<t:{ts}:R>`"),
    }

    embed = discord.Embed(title="Discord Timestamps", description=f"Unix: `{ts}`", color=0x5865F2)
    for label, (rendered, code) in styles.items():
        embed.add_field(name=label, value=f"{rendered}\n{code}", inline=True)

    embed.set_footer(text="Made by Panda • [Portfolio](https://panda-404.netlify.app/)")
    await interaction.response.send_message(embed=embed, ephemeral=True)


#Ping
@bot.tree.command(name="ping", description="🏓 Check the bot's response latency")
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def ping(interaction: discord.Interaction):
    latency = round(bot.latency * 1000)
    bar = "🟢" if latency < 100 else "🟡" if latency < 250 else "🔴"
    embed = discord.Embed(
        title="Pong! 🏓",
        description=f"{bar} **{latency}ms** WebSocket latency",
        color=0x57F287 if latency < 100 else 0xFEE75C if latency < 250 else 0xED4245,
    )
    embed.set_footer(text="Made by Panda • [Portfolio](https://panda-404.netlify.app/)")
    await interaction.response.send_message(embed=embed, ephemeral=True)


# Shortcuts
@bot.tree.command(name="shortcuts", description="⌨️ Useful Discord keyboard shortcuts & markdown tips")
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def shortcuts(interaction: discord.Interaction):
    embed = discord.Embed(
        title="⌨️ Discord Shortcuts & Tips",
        color=0x5865F2,
    )

    embed.add_field(
        name="🖥️ Desktop Keyboard Shortcuts",
        value=(
            "`Ctrl+K` — Quick switcher (jump to channel/DM)\n"
            "`Ctrl+/` — Show all shortcuts\n"
            "`Ctrl+Shift+M` — Toggle mute\n"
            "`Ctrl+Shift+D` — Toggle deafen\n"
            "`Alt+↑/↓` — Navigate channels\n"
            "`Ctrl+Shift+Alt+↑/↓` — Navigate unread channels\n"
            "`Esc` — Mark channel as read\n"
            "`Shift+Esc` — Mark all as read\n"
            "`Ctrl+E` — Open emoji picker\n"
            "`↑` (in chat) — Edit last message"
        ),
        inline=False,
    )

    embed.add_field(
        name="✍️ Text Markdown",
        value=(
            "`**bold**` → **bold**\n"
            "`*italic*` → *italic*\n"
            "`__underline__` → underline\n"
            "`~~strikethrough~~` → ~~strikethrough~~\n"
            "`||spoiler||` → spoiler tag\n"
            "`\`code\`` → inline code\n"
            "` ```lang ``` ` → code block\n"
            "`> text` → block quote\n"
            "`### heading` → large heading"
        ),
        inline=False,
    )

    embed.add_field(
        name="🔖 Timestamp Format",
        value=(
            "Use `/timestamp` to generate these.\n"
            "`<t:UNIX:t>` Short Time\n"
            "`<t:UNIX:F>` Full Date/Time\n"
            "`<t:UNIX:R>` Relative (e.g. '5 minutes ago')"
        ),
        inline=False,
    )

    embed.add_field(
        name="🔧 Handy Tricks",
        value=(
            "• `Shift+Enter` — New line without sending\n"
            "• Drag & drop a file to upload it\n"
            "• Click a reaction to add yours\n"
            "• Hold `Shift` when clicking ✉️ to reply ping-free\n"
            "• `@silent` at the start of a message = no notification\n"
            "• Star ⭐ a message to save it (right-click → Star)\n"
            "• Right-click your avatar → **Set Status** quickly"
        ),
        inline=False,
    )

    embed.set_footer(text="Made by Panda • [Portfolio](https://panda-404.netlify.app/)")
    await interaction.response.send_message(embed=embed, ephemeral=True)


# Help
@bot.tree.command(name="help", description="❓ List all available bot commands")
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def help_cmd(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🐼 Panda Bot — Commands",
        description="All responses are **ephemeral** (only you can see them).",
        color=0x5865F2,
    )
    commands_list = [
        ("/userid",     "📋", "Get a user's Discord ID (mention them or leave blank for yours)"),
        ("/userinfo",   "🪪", "Full account info for any user — badges, avatar, account age"),
        ("/avatar",     "🖼️", "Get anyone's full-res avatar with download links"),
        ("/timestamp",  "⏱️", "Convert any date to Discord's <t:> format"),
        ("/ping",       "🏓", "Check bot latency"),
        ("/shortcuts",  "⌨️", "Keyboard shortcuts & markdown cheatsheet"),
        ("/help",       "❓", "Show this menu"),
    ]
    for name, icon, desc in commands_list:
        embed.add_field(name=f"{icon} `{name}`", value=desc, inline=False)
    embed.set_footer(text="Made by Panda • [Portfolio](https://panda-404.netlify.app/)")
    await interaction.response.send_message(embed=embed, ephemeral=True)


#######


TOKEN = os.environ.get("DISCORD_TOKEN")
if not TOKEN:
    raise ValueError("❌ DISCORD_TOKEN environment variable not set!")

bot.run(TOKEN)
