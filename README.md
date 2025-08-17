# BlockBot Core (Railway-ready)

Minimal, reliable Discord bot with `bb` / `bb!` prefixes (with or without a space).  
Commands: `bb ping`, `bb uptime`, `bb info`, `bb server`, `bb user [@tag]`, `bb say <text>` (mods), `bb purge <1-200>` (mods).

## 1) Discord Developer Portal
- Bot tab → **Privileged Gateway Intents**:
  - **MESSAGE CONTENT INTENT** → ON
  - (Optional) SERVER MEMBERS + PRESENCE → ON
- OAuth2 → Invite with permissions:
  - Scopes: `bot`, `applications.commands`
  - Perms: View Channels, Send Messages, Read Message History, Embed Links
  - (For purge) Manage Messages

## 2) Deploy on Railway
- Push this repo to GitHub.
- Railway → New Project → Deploy from GitHub → select repo.
- Service Type: **Worker**
- Start Command: `python bot.py`
- Variables: add `DISCORD_TOKEN = <your token>`
- Deploy → watch logs → should print “online”.

## 3) Test in Discord
- `bb ping`
- `bb uptime`
- `bb server`
- `bb user`
- `bb purge 10` (requires Manage Messages role)