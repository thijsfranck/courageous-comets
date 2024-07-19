import os
import typing
from pathlib import Path

import discord
import yaml
from bot import Bot
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

# Get the path of the current working directory
wd = Path(__file__).parent


config_path = wd / "config.yaml"
with config_path.open() as config_file:
    CONFIG = yaml.safe_load(config_file)

discord.utils.setup_logging()

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = Bot(command_prefix=commands.when_mentioned, intents=intents)
bot.config = CONFIG


@bot.command()
@commands.guild_only()
@commands.is_owner()
async def sync(
    ctx: commands.Context,
    guilds: commands.Greedy[discord.Object],
    spec: typing.Literal["~", "*", "^"] | None = None,
) -> None:
    """
    Sync to the given scope.

    If no scope is provided and no guilds are given, sync the current tree to the global scope.
    `~` - Sync to the current guild.
    `*` - Sync to the global scope.
    `^` - Remove all non-global commands from the current guild.
    No spec - Sync the current tree to the current guild, used mostly for development.

    Parameters
    ----------
    guilds: commands.Greedy[discord.Object]
        The guilds to sync to.
    spec: typing.Literal["~", "*", "^"] | None
        The scope to sync to. Defaults to `~`.
    """
    async with ctx.typing():
        if not guilds:
            if spec == "~":
                synced = await ctx.bot.tree.sync(guild=ctx.guild)
            elif spec == "*":
                synced = await ctx.bot.tree.sync()
            elif spec == "^":
                ctx.bot.tree.clear_commands(guild=ctx.guild)
                await ctx.bot.tree.sync(guild=ctx.guild)
                synced = []
            else:
                ctx.bot.tree.copy_global_to(guild=ctx.guild)
                synced = await ctx.bot.tree.sync(guild=ctx.guild)

            scope = "globally" if spec == "*" else "to the current guild."
            await ctx.send(f"Synced {len(synced)} commands {scope}")

            return

        ret = 0
        for guild in guilds:
            try:
                await ctx.bot.tree.sync(guild=guild)
            except discord.HTTPException:
                pass
            else:
                ret += 1
        await ctx.send(f"Synced the tree to {ret}/{len(guilds)}.")


TOKEN = os.getenv("DISCORD_TOKEN")

if not TOKEN:
    msg = "No token provided. Please check the `DISCORD_TOKEN` environment variable."
    raise ValueError(msg)

bot.run(token=TOKEN, log_handler=None)
