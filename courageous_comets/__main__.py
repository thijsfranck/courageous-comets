import asyncio
import logging

import discord

from courageous_comets import bot, exceptions, settings


async def main() -> None:
    """
    Start the appication.

    If a critical error occurs, attempt to shut down gracefully.

    Raises
    ------
    courageous_comets.exceptions.AuthenticationError
        If the Discord token is not valid.
    """
    logging.info("Starting the Courageous Comets application ☄️")
    try:
        await bot.start(settings.DISCORD_TOKEN)
    except discord.LoginFailure:
        logging.critical("Discord login failed. Check the DISCORD_TOKEN environment variable.")
    except (exceptions.CourageousCometsError, discord.DiscordException) as e:
        logging.critical(
            "A fatal error occurred while running the Courageous Comets application.",
            exc_info=e,
        )
    finally:
        await bot.close()


asyncio.run(main())
