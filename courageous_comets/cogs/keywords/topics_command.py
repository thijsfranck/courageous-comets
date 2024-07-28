import logging

import discord
import discord.ext
import discord.ext.commands

from courageous_comets.client import CourageousCometsBot
from courageous_comets.enums import StatisticScope
from courageous_comets.redis.messages import get_tokens_count
from courageous_comets.ui.charts import keywords_bars
from courageous_comets.ui.embeds import popular_topics

logger = logging.getLogger(__name__)


class TopicsCommand(discord.ext.commands.Cog):
    """
    A cog that provides keyword analysis for a guild,  channel or user using a slash command.

    Attributes
    ----------
    bot : CourageousCometsBot
        The bot instance.
    """

    def __init__(self, bot: CourageousCometsBot) -> None:
        self.bot = bot

    @discord.app_commands.command(
        name="topics",
        description="Show the most commonly used keywords.",
    )
    async def show_keywords(
        self,
        interaction: discord.Interaction,
        scope: StatisticScope = StatisticScope.GUILD,
    ) -> None:
        """
        Allow users to view the most commonly used keywords in the server.

        Replies with an embed with the most commonly used keywords in the given scope.
        The embed contains a bar chart of the keywords used in the server.

        Parameters
        ----------
        interaction: discord.Interaction
            The interaction that triggered the command.
        scope : StatisticScope
            The scope of the keywords to show.
        """
        logger.info(
            "User %s requested the most commonly used keywords %s in %s using the /topics command.",
            interaction.user.id,
            interaction.id,
            scope.name,
        )

        if self.bot.redis is None:
            logger.error(
                "Could not answer topics request %s due to Redis being unavailable.",
                interaction.id,
            )
            return await interaction.response.send_message(
                "This feature is currently unavailable. Please try again later.",
                ephemeral=True,
            )

        if not interaction.guild:
            logger.debug(
                "Could not answer topics request %s due to it being used outside of a guild.",
                interaction.id,
            )
            return await interaction.response.send_message(
                "This command can only be used in a guild.",
                ephemeral=True,
            )

        if scope == StatisticScope.CHANNEL and not interaction.channel:
            logger.debug(
                "Could not answer topics request %s due to it being used outside of a channel.",
                interaction.id,
            )
            return await interaction.response.send_message(
                "This command can only be used in a channel.",
                ephemeral=True,
            )

        await interaction.response.defer(ephemeral=True, thinking=True)

        ids = (
            [str(interaction.channel.id)]  # type: ignore
            if scope == StatisticScope.CHANNEL
            else [str(interaction.user.id)]
            if scope == StatisticScope.USER
            else None
        )

        keywords = await get_tokens_count(
            self.bot.redis,
            guild_id=str(interaction.guild.id),
            scope=scope,
            ids=ids,
        )

        if not keywords:
            logger.debug(
                "Could not find any keywords for scope %s.",
                scope.name,
            )
            return await interaction.followup.send(
                f"No keywords found for scope {scope.name}.",
                ephemeral=True,
            )

        embed = popular_topics.render(scope, keywords)

        chart = keywords_bars.render(keywords)
        embed.set_image(url=f"attachment://{chart.filename}")

        return await interaction.followup.send(embed=embed, file=chart, ephemeral=True)


async def setup(bot: CourageousCometsBot) -> None:
    """Load the cog."""
    await bot.add_cog(TopicsCommand(bot))
