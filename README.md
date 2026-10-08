# RouletteBot - Reference Guide

RouletteBot runs **Exile Roulette**: a panel with a single **Pull the Lever** button that randomly picks a Path of Exile 2 class/ascendancy and main skill for whoever clicks it. It is the Discord version of the Exile Roulette web app.

## How It Works

1. An admin runs `!roulettesetup` in the dedicated channel. The bot posts the panel embed with the 🎰 **Pull the Lever** button and stores the message ID in `roulette_state.json`.
2. When a member clicks the button, the bot defers with an ephemeral "thinking" response, picks an ascendancy and a skill at random, and renders an animated GIF (wheel on the left, slot reel on the right) in a worker thread.
3. The GIF is sent as an **ephemeral** follow-up that mentions the user ("@user pulls the lever…"). Only that user sees it.
4. About 5.7 seconds later (animation length + 1.5s), the bot edits that message: the GIF is replaced by a still PNG of the final frame and an embed showing Class, Ascendancy and Main Skill (with weapon/category).

The button is a persistent view (`custom_id="roulette_pull"`, `timeout=None`) re-registered in `on_ready`, so the panel keeps working across restarts.

Every ascendancy and every skill is equally likely. There are no filters.

## Limits

| Limit | Value | Where |
|---|---|---|
| Per-user cooldown | 10 seconds | `COOLDOWN_SECONDS` in `roulettebot.py` |
| One pull at a time per user | while their animation is playing | `in_progress` set |
| Concurrent renders | 2 | `MAX_CONCURRENT_RENDERS` (protects the Pi's CPU) |

Cooldowns are in memory and reset on restart.

## Commands

| Command | Permission | Description |
|---|---|---|
| `!roulettesetup` | Administrator | Posts the panel in the current channel. Deletes the previous panel (if the stored message still exists) and the command message itself. Re-run after changing panel text. |

## Pool Data

`data.py` holds the pool, mirrored from the web app:

- `CLASSES`: 8 classes, 22 ascendancies (patch 0.5), each class with its wheel colour.
- `SKILLS`: 140 main skills grouped by weapon/category (Mace, Shield, Spear, Bow, Crossbow, Quarterstaff, Elemental Spell, Chaos & Occult, Minion, Druid).
- Excluded: Kalguuran (Return of the Ancients) skills, ascendancy-only skills, unique-item skills, buffs/auras/marks/cries/movement skills.

To add or rename a skill, edit `data.py`, deploy it, and restart. No other file changes are needed. Keep the web app's list in step.

## Rendering

`render.py` uses Pillow only.

- The wheel is drawn once at import (2x supersampled, then downscaled). Rotating it is slow on the Pi (~80 ms/frame), so `warm_cache()` pre-renders every rotation in 2° steps (180 tiles, background baked in) in a background thread at startup (~16s on the Pi). Landing jitter keeps the pointer >3° inside a segment, so 2° rounding never changes the result.
- The reel is a pre-drawn strip of 36 cells cropped per frame.
- 760×380 px, 20 fps, wheel stops at 3.2s, reel at 4.2s. All frames use one fixed 255-colour palette built at startup.
- The GIF has no loop extension (plays once) and holds the last frame for 60s in case a client loops it anyway.
- Measured on the Pi: ~3s per render, ~2.8 MB GIF, ~140 MB process memory.
- Fonts are bundled in `fonts/` (IM Fell English SC, Alegreya Sans; SIL Open Font License, see `fonts/OFL.txt`).

## Configuration

| Variable | Location | Description |
|---|---|---|
| `DISCORD_TOKEN` | `.env` on Pi | Bot token |

The channel is not hard-coded; it is whichever channel `!roulettesetup` was run in (saved in `roulette_state.json`).

Privileged intents: **Message Content Intent** (needed for the `!roulettesetup` prefix command). Server Members Intent is not needed.

Bot permissions in the roulette channel: View Channel, Send Messages, Embed Links, Attach Files, Read Message History, Manage Messages (to delete the old panel and the setup command).

## Deployment

- **Bot Server:** Raspberry Pi 5 (`pi-bots`)
- **Service:** `roulettebot` (unit file in repo: `roulettebot.service`)
- **Location:** `/home/admin/GD-roulette-bot/`
- **State file:** `roulette_state.json`
- **Logs:** `sudo journalctl -u roulettebot -f`
- **Restart:** `sudo systemctl restart roulettebot`

Files to deploy: `roulettebot.py`, `render.py`, `data.py`, `requirements.txt`, and the `fonts/` folder.

## Integrations

None. RouletteBot does not read or write the Roster and does not interact with other bots.
