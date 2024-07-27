import discord
from discord import app_commands
from discord.ext import commands


# Boilerplate cog code.
# To build a cog:
#   1. Copy this boilerplate to another file in the cogs directory
#   2. Rename the file and class
#   3. Add the file name to config.yaml
class Cog(commands.Cog):
    """A boilerplate cog."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    # Slash command handler
    # In order for these to be seen in the discord UI,
    # they must be synced (sunk?!) using the sync command
    @app_commands.command(name="COMMAND_NAME")
    async def _command_name(self, interaction: discord.Interaction) -> None:
        """Command description."""

    # Listen for events from discord
    # Event reference can be found here:
    # https://discordpy.readthedocs.io/en/stable/api.html#discord-api-events
    @commands.Cog.listener(name="EVENT_NAME")
    async def _event_name(self) -> None:
        """Event handler description."""


async def setup(bot: commands.Bot) -> None:
    """Load the cog."""
    await bot.add_cog(Cog(bot))
