import logging

import discord
import discord.ext
import discord.ext.commands

from courageous_comets.client import CourageousCometsBot
from courageous_comets.enums import StatisticScope
from courageous_comets.redis.messages import get_tokens_count
from courageous_comets.ui.charts import keywords_bars
from courageous_comets.ui.embeds import user_keywords

logger = logging.getLogger(__name__)


class KeywordsUserContextMenu(discord.ext.commands.Cog):
    """
    A cog that provides keyword analysis for a user using a context menu.

    Attributes
    ----------
    bot : CourageousCometsBot
        The bot instance.
    """

    def __init__(self, bot: CourageousCometsBot) -> None:
        self.bot = bot

        menu = discord.app_commands.ContextMenu(
            name="Show user interests",
            callback=self.show_keywords,
        )
        self.bot.tree.add_command(menu)

    async def show_keywords(
        self,
        interaction: discord.Interaction,
        user: discord.User | discord.Member,
    ) -> None:
        """
        Allow users to view the most commonly used keywords of a user using a context menu.

        Generates an embed with the most commonly used keywords of a user and sends it to the user.
        The embed contains a bar chart of the keywords used by the user.

        Parameters
        ----------
        interaction : discord.Interaction
            The interaction that triggered the command.
        user : discord.User | discord.Member
            The user to analyze.
        """
        logger.info(
            "User %s requested keywords %s for user %s.",
            interaction.user.id,
            interaction.id,
            user.id,
        )

        if self.bot.redis is None:
            logger.error(
                "Could not answer search request %s due to Redis being unavailable.",
                interaction.id,
            )
            return await interaction.response.send_message(
                "This feature is currently unavailable. Please try again later.",
                ephemeral=True,
            )

        if not interaction.guild:
            logger.debug(
                "Could not answer search request %s due to it being used outside of a guild.",
                interaction.id,
            )
            return await interaction.response.send_message(
                "This command can only be used in a guild.",
                ephemeral=True,
            )

        await interaction.response.defer(ephemeral=True, thinking=True)

        tokens = await get_tokens_count(
            self.bot.redis,
            guild_id=str(interaction.guild.id),
            scope=StatisticScope.USER,
            ids=[str(user.id)],
        )

        embed = user_keywords.render(user, tokens)

        chart = keywords_bars.render(tokens)
        embed.set_image(url=f"attachment://{chart.filename}")

        return await interaction.followup.send(embed=embed, file=chart, ephemeral=True)


async def setup(bot: CourageousCometsBot) -> None:
    """Load the cog."""
    await bot.add_cog(KeywordsUserContextMenu(bot))
