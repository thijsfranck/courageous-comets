import logging

import discord
from discord import app_commands
from discord.ext import commands

from courageous_comets.client import CourageousCometsBot
from courageous_comets.enums import StatisticScope
from courageous_comets.redis.messages import get_average_sentiment
from courageous_comets.ui.charts import sentiment_bars
from courageous_comets.ui.embeds import user_sentiment
from courageous_comets.ui.views.sentiment import SentimentView
from courageous_comets.utils import contextmenu

logger = logging.getLogger(__name__)


class SentimentUserContextMenu(commands.Cog):
    """
    A cog that provides sentiment analysis for a user using a context menu.

    Attributes
    ----------
    bot : CourageousCometsBot
        The bot instance.
    """

    def __init__(self, bot: CourageousCometsBot) -> None:
        self.bot = bot

        menu = app_commands.ContextMenu(
            name="Show user sentiment",
            callback=self.show_user_sentiment,
        )
        self.bot.tree.add_command(menu)

    @contextmenu(name="Show user sentiment")
    async def show_user_sentiment(
        self,
        interaction: discord.Interaction,
        user: discord.User | discord.Member,
    ) -> None:
        """
        Allow users to view the sentiment analysis of a user using a context menu.

        Generates an embed with the sentiment analysis of a user and sends it to the user.
        The embed contains a line chart of the sentiment of a user over time.
        A view is attached to the message to allow users to interact with the sentiment analysis.

        Parameters
        ----------
        interaction : discord.Interaction
            The interaction that triggered the command.
        user : discord.User | discord.Member
            The user to analyze.
        """
        logger.info(
            "User %s requested sentiment analysis results %s for user %s.",
            interaction.user.id,
            interaction.id,
            user.id,
        )

        if self.bot.redis is None:
            logger.error(
                "Could not answer sentiment request %s due to Redis being unavailable.",
                interaction.id,
            )
            return await interaction.response.send_message(
                "This feature is currently unavailable. Please try again later.",
                ephemeral=True,
            )

        if interaction.guild is None:
            logger.debug(
                "Could not answer sentiment request %s due to user not being from a guild.",
                interaction.id,
            )
            return await interaction.response.send_message(
                "This feature is only available in guilds.",
                ephemeral=True,
            )

        await interaction.response.defer(ephemeral=True, thinking=True)

        sentiment_results = await get_average_sentiment(
            redis=self.bot.redis,
            guild_id=str(interaction.guild.id),
            ids=[str(user.id)],
            scope=StatisticScope.USER,
        )

        if not sentiment_results:
            logger.debug("No data found for sentiment request %s.", interaction.id)
            await interaction.followup.send(
                f"No sentiment data found for {user.mention}.",
                ephemeral=True,
            )

        average_sentiment = sentiment_results[0]

        embed = user_sentiment.render(user, average_sentiment)

        chart = sentiment_bars.for_user(average_sentiment)
        embed.set_image(url=f"attachment://{chart.filename}")

        view = SentimentView(user, average_sentiment)

        logger.debug("Sending sentiment analysis results for %s.", interaction.id)

        return await interaction.followup.send(
            embed=embed,
            file=chart,
            view=view,
            ephemeral=True,
        )


async def setup(bot: CourageousCometsBot) -> None:
    """Load the cog."""
    await bot.add_cog(SentimentUserContextMenu(bot))
