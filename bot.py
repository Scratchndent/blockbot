# BlockBot Core — Railway-ready, with slow/lock controls
# Deps: discord.py  (pip install discord.py)

import os, time, platform
import discord
from discord.ext import commands

TOKEN = os.getenv("DISCORD_TOKEN")
BOOT = time.time()

# ---- Intents ----
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.presences = True

# ---- Prefix: longest-first so "bb " works ----
def get_prefix(bot, message):
    return ("bb! ", "bb ", "bb!", "bb")

bot = commands.Bot(
    command_prefix=get_prefix,
    case_insensitive=True,
    intents=intents,
    help_command=None,
)

# ===== Helpers =====
def fmt_uptime(secs: int) -> str:
    d, r = divmod(secs, 86400)
    h, r = divmod(r, 3600)
    m, s = divmod(r, 60)
    return f"{d}d {h}h {m}m {s}s"

def author_is_mod(ctx: commands.Context) -> bool:
    p = ctx.channel.permissions_for(ctx.author)
    return p.manage_messages or p.manage_guild or p.administrator

# ===== Events =====
@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game("bb help | Blockhouse"))
    print(f"✅ {bot.user} online • discord.py {discord.__version__} • Python {platform.python_version()}")

@bot.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return
    await bot.process_commands(message)

@bot.event
async def on_command_error(ctx: commands.Context, error: commands.CommandError):
    if isinstance(error, commands.CommandNotFound):
        return
    if isinstance(error, commands.MissingRequiredArgument):
        return await ctx.reply("Missing argument. Try `bb help`.")
    if isinstance(error, commands.BadArgument):
        return await ctx.reply("Bad argument. Try `bb help`.")
    if isinstance(error, commands.MissingPermissions):
        return await ctx.reply("You don’t have permission for that.")
    if isinstance(error, commands.BotMissingPermissions):
        return await ctx.reply("I’m missing permissions here (e.g., **Manage Messages** for `bb purge`).")
    try:
        await ctx.reply(f"Error: `{error.__class__.__name__}`")
    except Exception:
        pass

# ===== Help =====
@bot.command(name="help")
async def help_cmd(ctx: commands.Context):
    p = "bb"
    em = discord.Embed(title="BlockBot — Core Commands", color=discord.Color.dark_gold())
    em.description = (
        f"**Prefix:** `{p}` (also accepts `bb ` and `bb!`)\n"
        f"Examples: `{p} ping`, `{p} server`, `{p} uptime`, `{p} info`"
    )
    em.add_field(name=f"{p} ping", value="Latency check (pong).", inline=False)
    em.add_field(name=f"{p} uptime", value="How long the bot has been online.", inline=False)
    em.add_field(name=f"{p} info", value="Bot info + invite link.", inline=False)
    em.add_field(name=f"{p} server", value="Server stats (members, channels, roles).", inline=False)
    em.add_field(name=f"{p} user [@member]", value="User info (join date, roles).", inline=False)
    em.add_field(name=f"{p} say <text>", value="Echo a message (mods only).", inline=False)
    em.add_field(name=f"{p} purge <1-200>", value="Bulk delete messages (mods only).", inline=False)
    em.add_field(name=f"{p} slow <seconds>", value="Set slowmode for this channel (mods). `0` disables.", inline=False)
    em.add_field(name=f"{p} unslow", value="Disable slowmode in this channel (mods).", inline=False)
    em.add_field(name=f"{p} lockdown", value="Lock channel (@everyone cannot send) (mods).", inline=False)
    em.add_field(name=f"{p} unlock", value="Unlock channel (restore default perms) (mods).", inline=False)
    await ctx.reply(embed=em)

# ===== Basics =====
@bot.command()
async def ping(ctx: commands.Context):
    await ctx.reply(f"Pong. `{round(bot.latency*1000)}ms`")

@bot.command()
async def uptime(ctx: commands.Context):
    await ctx.reply(f"Uptime: **{fmt_uptime(int(time.time()-BOOT))}**")

@bot.command()
async def info(ctx: commands.Context):
    app = await bot.application_info()
    client_id = app.id
    invite = (
        "https://discord.com/api/oauth2/authorize"
        f"?client_id={client_id}&permissions=274877908992&scope=bot%20applications.commands"
    )
    em = discord.Embed(title="BlockBot Unsupervised", color=discord.Color.dark_teal())
    em.add_field(name="Prefix", value="`bb` (also `bb `, `bb!`)", inline=False)
    em.add_field(name="Invite", value=f"[Add me to a server]({invite})", inline=False)
    em.set_footer(text="Doing my best, no promises.")
    await ctx.reply(embed=em)

# ===== Server / User Info =====
@bot.command()
async def server(ctx: commands.Context):
    g: discord.Guild = ctx.guild
    if not g:
        return await ctx.reply("Run this in a server.")
    total = g.member_count or len(g.members)
    bots = sum(1 for m in g.members if m.bot)
    humans = total - bots
    text_ch = sum(1 for c in g.channels if isinstance(c, discord.TextChannel))
    voice_ch = sum(1 for c in g.channels if isinstance(c, discord.VoiceChannel))
    em = discord.Embed(title=f"{g.name}", color=discord.Color.blurple())
    em.add_field(name="Members", value=f"Total **{total}** • Humans **{humans}** • Bots **{bots}**", inline=False)
    em.add_field(name="Channels", value=f"Text **{text_ch}** • Voice **{voice_ch}**", inline=False)
    em.add_field(name="Roles", value=str(len(g.roles)))
    if g.icon:
        em.set_thumbnail(url=g.icon.url)
    await ctx.reply(embed=em)

@bot.command()
async def user(ctx: commands.Context, member: discord.Member | None = None):
    member = member or ctx.author
    roles = [r.mention for r in member.roles if r.name != "@everyone"]
    color = getattr(member, "color", discord.Color.greyple())
    em = discord.Embed(title=f"{member.display_name}", color=color)
    em.add_field(name="ID", value=member.id)
    if member.joined_at:
        em.add_field(name="Joined Server", value=discord.utils.format_dt(member.joined_at, style="R"))
    em.add_field(name="Account Created", value=discord.utils.format_dt(member.created_at, style="R"))
    if member.top_role:
        em.add_field(name="Top Role", value=member.top_role.mention)
    em.add_field(name="Roles", value=(" ".join(roles) if roles else "None"), inline=False)
    em.set_thumbnail(url=member.display_avatar.url)
    await ctx.reply(embed=em)

# ===== Mod tools =====
@bot.command()
@commands.check(author_is_mod)
async def say(ctx: commands.Context, *, text: str):
    try:
        await ctx.message.delete()
    except Exception:
        pass
    await ctx.send(text)

@bot.command()
@commands.check(author_is_mod)
async def purge(ctx: commands.Context, amount: int):
    amount = max(1, min(200, amount))
    deleted = await ctx.channel.purge(limit=amount+1)  # include the command
    note = await ctx.send(f"🧹 Deleted **{len(deleted)-1}** messages.")
    await note.delete(delay=3)

# ---- New: Slowmode controls ----
@bot.command()
@commands.check(author_is_mod)
async def slow(ctx: commands.Context, seconds: int):
    """Set slowmode delay for this channel (0–21600s)."""
    seconds = max(0, min(21600, seconds))
    try:
        await ctx.channel.edit(slowmode_delay=seconds)
        if seconds == 0:
            await ctx.reply("⏱️ Slowmode disabled.")
        else:
            await ctx.reply(f"⏱️ Slowmode set to **{seconds}s**.")
    except discord.Forbidden:
        await ctx.reply("I need **Manage Channels** to change slowmode.")
    except Exception as e:
        await ctx.reply(f"Could not set slowmode: `{e.__class__.__name__}`")

@bot.command(aliases=["unslow"])
@commands.check(author_is_mod)
async def unslow_cmd(ctx: commands.Context):
    """Disable slowmode (alias: unslow)."""
    try:
        await ctx.channel.edit(slowmode_delay=0)
        await ctx.reply("⏱️ Slowmode disabled.")
    except discord.Forbidden:
        await ctx.reply("I need **Manage Channels** to change slowmode.")
    except Exception as e:
        await ctx.reply(f"Could not disable slowmode: `{e.__class__.__name__}`")

# ---- New: Lockdown / Unlock ----
@bot.command()
@commands.check(author_is_mod)
async def lockdown(ctx: commands.Context):
    """
    Lock current channel: deny @everyone from sending messages.
    """
    ch = ctx.channel
    everyone = ctx.guild.default_role
    try:
        ow = ch.overwrites_for(everyone)
        if ow.send_messages is False:
            return await ctx.reply("🔒 Channel is already locked.")
        ow.send_messages = False
        await ch.set_permissions(everyone, overwrite=ow)
        await ctx.reply("🔒 Channel locked. `@everyone` cannot send messages.")
    except discord.Forbidden:
        await ctx.reply("I need **Manage Channels** to lock the channel.")
    except Exception as e:
        await ctx.reply(f"Could not lock: `{e.__class__.__name__}`")

@bot.command()
@commands.check(author_is_mod)
async def unlock(ctx: commands.Context):
    """
    Unlock current channel: clear explicit deny so defaults apply.
    """
    ch = ctx.channel
    everyone = ctx.guild.default_role
    try:
        ow = ch.overwrites_for(everyone)
        if ow.send_messages is None:
            return await ctx.reply("🔓 Channel is already unlocked.")
        ow.send_messages = None  # clear override to inherit default perms
        await ch.set_permissions(everyone, overwrite=ow)
        await ctx.reply("🔓 Channel unlocked. Defaults restored.")
    except discord.Forbidden:
        await ctx.reply("I need **Manage Channels** to unlock the channel.")
    except Exception as e:
        await ctx.reply(f"Could not unlock: `{e.__class__.__name__}`")

# ===== Run =====
if __name__ == "__main__":
    if not TOKEN:
        raise SystemExit("Set DISCORD_TOKEN as an environment variable (Railway Variables).")
    bot.run(TOKEN)
