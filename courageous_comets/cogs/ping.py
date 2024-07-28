import discord
from discord import app_commands
from discord.ext import commands


class Ping(commands.Cog):
    """
    A cog containing a simple ping command.

    Attributes
    ----------
    bot : commands.Bot
        The bot instance.
    """

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="ping")
    async def ping(self, interaction: discord.Interaction) -> None:
        """Ping the bot."""
        await interaction.response.send_message("Pong!")


async def setup(bot: commands.Bot) -> None:
    """Load the cog."""
    await bot.add_cog(Ping(bot))
