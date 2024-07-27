import logging
import typing
from typing import override

import discord
import yaml
from discord import Intents
from discord.ext import commands
from redis.asyncio import Redis

from courageous_comets import settings
from courageous_comets.nltk import init_nltk
from courageous_comets.redis import init_redis
from courageous_comets.vectorizer import Vectorizer

DESCRIPTION = """
Thank you for using Courageous Comets! ☄️

This bot is designed to help you:

- 🚀 Connect with others who share your interests.
- 🤗 Find the friendliest communities.
- 🛡️ Moderate your server with ease.
"""

logger = logging.getLogger(__name__)


intents = Intents.default()
intents.members = True
intents.message_content = True

with settings.BOT_CONFIG_PATH.open("r") as config_file:
    CONFIG = yaml.safe_load(config_file)


class CourageousCometsBot(commands.Bot):
    """
    The Courageous Comets Discord bot.

    Attributes
    ----------
    redis : redis.asyncio.Redis | None
        The Redis connection instance for the bot, or `None` if not connected.
    """

    redis: Redis | None = None
    vectorizer = Vectorizer()

    def __init__(self) -> None:
        super().__init__(
            command_prefix=commands.when_mentioned,
            intents=intents,
            description=DESCRIPTION,
        )

    @override
    async def close(self) -> None:
        """
        Gracefully shut down the application.

        First closes the Discord client, then the Redis connection if it exists.

        Overrides the `close` method in `discord.ext.commands.Bot`.
        """
        logger.info("Gracefully shutting down the application...")

        await super().close()

        if self.redis is not None:
            await self.redis.aclose()
            logger.info("Closed the Redis connection")

        logger.info("Application shutdown complete. Goodbye! 👋")

    async def load_cogs(self, cogs: list[str]) -> None:
        """Load all given cogs."""
        for cog in cogs:
            try:
                await bot.load_extension(cog)
                logger.debug("Loaded cog %s", cog)
            except commands.ExtensionError as e:
                logger.exception("Failed to load cog %s", cog, exc_info=e)

    async def on_ready(self) -> None:
        """Log a message when the bot is ready."""
        logger.info("Logged in as %s", self.user)

    async def setup_hook(self) -> None:
        """
        On startup, initialize the bot.

        Performs the following setup actions:

        - Connect to Redis.
        - Load the NLTK resources.
        - Set up the vectorizer.
        - Load the cogs.
        """
        logger.info("Initializing the Discord client...")

        self.redis = await init_redis()

        nltk_resources = CONFIG.get("nltk", [])
        await init_nltk(nltk_resources)

        cogs = CONFIG.get("cogs", [])
        await self.load_cogs(cogs)

        if settings.IS_DEV:
            dev_cogs = CONFIG.get("dev-cogs", [])
            await self.load_cogs(dev_cogs)

        logger.info("Initialization complete 🚀")


bot = CourageousCometsBot()


@bot.command()
@commands.guild_only()
@commands.is_owner()
async def sync(
    ctx: commands.Context[commands.Bot],
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
    ctx : commands.Context[commands.Bot]
        The context of the command.
    guilds : commands.Greedy[discord.Object]
        The guilds to sync to.
    spec : typing.Literal["~", "*", "^"] | None
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
                ctx.bot.tree.copy_global_to(guild=ctx.guild)  # type: ignore (@commands.guild_only() ensures ctx has guild attribute)
                synced = await ctx.bot.tree.sync(guild=ctx.guild)

            scope = "globally." if spec == "*" else "to the current guild."
            await ctx.send(f"Synced {len(synced)} command(s) {scope}")

            return

        ret = 0

        for guild in guilds:
            try:
                await ctx.bot.tree.sync(guild=guild)
            except discord.HTTPException as e:
                logger.exception("Failed to sync to guild %s", guild, exc_info=e)
            else:
                ret += 1

        await ctx.send(f"Synced the tree to {ret}/{len(guilds)}.")
