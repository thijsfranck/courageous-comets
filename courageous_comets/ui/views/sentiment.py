import random
from typing import override

import discord

from courageous_comets import models

STICKERS = [
    751606065447305216,
    754109076933443614,
    772972089963577354,
    781324722394103808,
    809207198856904764,
]


class SentimentView(discord.ui.View):
    """
    A view for interacting with a user's sentiment analysis results.

    Attributes
    ----------
    user : discord.User | discord.Member
        The user whose sentiment is being analyzed.
    data : models.SentimentResult
        The sentiment analysis results.
    """

    def __init__(self, user: discord.User | discord.Member, data: models.SentimentResult) -> None:
        super().__init__()
        self.user = user
        self.data = data

        self.add_item(PraiseButton(user, data))


class PraiseButton(discord.ui.Button):
    """
    A button to praise a user.

    Attributes
    ----------
    user : discord.User | discord.Member
        The user to praise.
    """

    def __init__(self, user: discord.User | discord.Member, data: models.SentimentResult) -> None:
        super().__init__(
            style=discord.ButtonStyle.success,
            label="Send Praise",
            emoji="🎉",
            disabled=data.compound < 0,
        )
        self.user = user
        self.data = data

    @override
    async def callback(self, interaction: discord.Interaction) -> None:
        # Fetch a random sticker to send with the praise
        sticker = await interaction.client.fetch_sticker(random.choice(STICKERS))

        # Send the praise to the user
        await self.user.send(
            f"You've been praised by {interaction.user.mention}!",
            stickers=[sticker],  # type: ignore
        )

        # Send a confirmation message
        await interaction.response.send_message(
            f"Sent praise to {self.user.mention}!",
            ephemeral=True,
        )
