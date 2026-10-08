import asyncio
import io
import json
import os
import time
from pathlib import Path

import discord
from discord.ext import commands
from dotenv import load_dotenv

import render

load_dotenv()

# ── Configuration ──────────────────────────────────────────────────────────────
TOKEN = os.getenv("DISCORD_TOKEN")

COOLDOWN_SECONDS = 10         # per-user gap between pulls
MAX_CONCURRENT_RENDERS = 2    # keeps the Pi responsive if several people pull at once
GOLD = 0xC9A35A

STATE_FILE = Path(__file__).parent / "roulette_state.json"

# ── Persistent state ───────────────────────────────────────────────────────────
def load_state() -> dict:
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {"channel_id": None, "message_id": None}

def save_state(data: dict):
    STATE_FILE.write_text(json.dumps(data, indent=2))

state = load_state()

# ── Bot setup ──────────────────────────────────────────────────────────────────
intents = discord.Intents.default()
intents.message_content = True

class RouletteBot(commands.Bot):
    async def setup_hook(self):
        # Created here, not at import, so it binds to the running loop (Python 3.9 on the Pi).
        self.render_slots = asyncio.Semaphore(MAX_CONCURRENT_RENDERS)
        # Pre-rotate the wheel in the background so the first pulls are fast.
        asyncio.get_running_loop().create_task(asyncio.to_thread(render.warm_cache))

bot = RouletteBot(command_prefix="!", intents=intents)

last_pull = {}        # user id -> monotonic time of last pull
in_progress = set()   # user ids with a pull currently animating

def build_panel_embed() -> discord.Embed:
    return discord.Embed(
        title="🎰 Exile Roulette",
        description=(
            "Bored of your build? Pull the lever and let fate decide your next character.\n\n"
            "The wheel picks your **class and ascendancy**, and the reel picks your **main skill**.\n"
            "Your result is only visible to you."
        ),
        color=GOLD,
    )

def build_result_embed(user: discord.abc.User, segment: dict, skill: tuple) -> discord.Embed:
    name, category = skill
    embed = discord.Embed(
        title=f"{name} {segment['asc']}",
        description=f"Your next build, {user.mention}.",
        color=GOLD,
    )
    embed.add_field(name="Class", value=segment["cls"], inline=True)
    embed.add_field(name="Ascendancy", value=segment["asc"], inline=True)
    embed.add_field(name="Main Skill", value=f"{name} ({category})", inline=True)
    embed.set_image(url="attachment://result.png")
    return embed

# ── Lever view ─────────────────────────────────────────────────────────────────
class LeverView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Pull the Lever", emoji="🎰", custom_id="roulette_pull",
                       style=discord.ButtonStyle.danger)
    async def pull(self, interaction: discord.Interaction, _button: discord.ui.Button):
        user = interaction.user

        if user.id in in_progress:
            await interaction.response.send_message("Your reel is still spinning.", ephemeral=True)
            return
        wait = COOLDOWN_SECONDS - (time.monotonic() - last_pull.get(user.id, 0))
        if wait > 0:
            await interaction.response.send_message(
                f"The lever is resetting. Try again in {int(wait) + 1}s.", ephemeral=True
            )
            return

        last_pull[user.id] = time.monotonic()
        in_progress.add(user.id)
        try:
            await interaction.response.defer(ephemeral=True, thinking=True)

            segment, skill = render.pick()
            async with bot.render_slots:
                gif, png, seconds = await asyncio.to_thread(render.render_spin, segment, skill)

            msg = await interaction.followup.send(
                content=f"{user.mention} pulls the lever…",
                file=discord.File(io.BytesIO(gif), filename="spin.gif"),
                ephemeral=True,
                wait=True,
            )

            # Swap the GIF for a still result card once the animation has played.
            await asyncio.sleep(seconds + 1.5)
            await msg.edit(
                content=None,
                embed=build_result_embed(user, segment, skill),
                attachments=[discord.File(io.BytesIO(png), filename="result.png")],
            )
            print(f"[BOT] {user.display_name} → {skill[0]} {segment['asc']} ({segment['cls']})")
        except Exception as e:
            print(f"[ERROR] Pull failed for {user}: {e!r}")
            try:
                await interaction.followup.send("⚠️ The roulette jammed. Please try again.", ephemeral=True)
            except discord.HTTPException:
                pass
        finally:
            in_progress.discard(user.id)

# ── Commands ───────────────────────────────────────────────────────────────────
@bot.command(name="roulettesetup")
@commands.has_permissions(administrator=True)
async def roulette_setup(ctx: commands.Context):
    """Posts the Exile Roulette panel in this channel, replacing any previous panel."""
    if state["channel_id"] and state["message_id"]:
        old_channel = bot.get_channel(state["channel_id"])
        if old_channel is not None:
            try:
                old = await old_channel.fetch_message(state["message_id"])
                await old.delete()
            except discord.HTTPException:
                pass

    msg = await ctx.channel.send(embed=build_panel_embed(), view=LeverView())
    state["channel_id"] = ctx.channel.id
    state["message_id"] = msg.id
    save_state(state)

    try:
        await ctx.message.delete()
    except discord.HTTPException:
        pass
    print(f"[BOT] Panel posted. Channel: {ctx.channel.id} | Message: {msg.id}")

# ── Events ─────────────────────────────────────────────────────────────────────
@bot.event
async def on_ready():
    bot.add_view(LeverView())
    print(f"[BOT] Logged in as {bot.user} (ID: {bot.user.id})")
    if state["message_id"]:
        print(f"[BOT] Panel message: {state['message_id']} in channel {state['channel_id']}")
    else:
        print("[BOT] No panel posted yet. Run !roulettesetup in the target channel.")

@bot.event
async def on_command_error(ctx: commands.Context, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ You need Administrator permissions to use this command.")
    elif isinstance(error, commands.CommandNotFound):
        pass
    else:
        print(f"[ERROR] {error}")
        raise error

# ── Entry point ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    if not TOKEN:
        raise RuntimeError("DISCORD_TOKEN environment variable is not set.")
    bot.run(TOKEN)
