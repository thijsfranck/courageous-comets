import logging

from discord.ext import commands


class Bot(commands.Bot):
    """Represents a Discord bot.

    This class is a subclass of :class:`discord.Client` and as a result
    anything that you can do with a :class:`discord.Client` you can do with
    this bot.

    This class also subclasses :class:`.GroupMixin` to provide the functionality
    to manage commands.

    Unlike :class:`discord.Client`, this class does not require manually setting
    a :class:`~discord.app_commands.CommandTree` and is automatically set upon
    instantiating the class.

    .. container:: operations

        .. describe:: async with x

            Asynchronously initialises the bot and automatically cleans up.

            .. versionadded:: 2.0

    Attributes
    ----------
    command_prefix
        The command prefix is what the message content must contain initially
        to have a command invoked. This prefix could either be a string to
        indicate what the prefix should be, or a callable that takes in the bot
        as its first parameter and :class:`discord.Message` as its second
        parameter and returns the prefix. This is to facilitate "dynamic"
        command prefixes. This callable can be either a regular function or
        a coroutine.

        An empty string as the prefix always matches, enabling prefix-less
        command invocation. While this may be useful in DMs it should be avoided
        in servers, as it's likely to cause performance issues and unintended
        command invocations.

        The command prefix could also be an iterable of strings indicating that
        multiple checks for the prefix should be used and the first one to
        match will be the invocation prefix. You can get this prefix via
        :attr:`.Context.prefix`.

        .. note::

            When passing multiple prefixes be careful to not pass a prefix
            that matches a longer prefix occurring later in the sequence.  For
            example, if the command prefix is ``('!', '!?')``  the ``'!?'``
            prefix will never be matched to any message as the previous one
            matches messages starting with ``!?``. This is especially important
            when passing an empty string, it should always be last as no prefix
            after it will be matched.
    case_insensitive: :class:`bool`
        Whether the commands should be case insensitive. Defaults to ``False``. This
        attribute does not carry over to groups. You must set it to every group if
        you require group commands to be case insensitive as well.
    description: :class:`str`
        The content prefixed into the default help message.
    help_command: Optional[:class:`.HelpCommand`]
        The help command implementation to use. This can be dynamically
        set at runtime. To remove the help command pass ``None``. For more
        information on implementing a help command, see :ref:`ext_commands_help_command`.
    owner_id: Optional[:class:`int`]
        The user ID that owns the bot. If this is not set and is then queried via
        :meth:`.is_owner` then it is fetched automatically using
        :meth:`~.Bot.application_info`.
    owner_ids: Optional[Collection[:class:`int`]]
        The user IDs that owns the bot. This is similar to :attr:`owner_id`.
        If this is not set and the application is team based, then it is
        fetched automatically using :meth:`~.Bot.application_info`.
        For performance reasons it is recommended to use a :class:`set`
        for the collection. You cannot set both ``owner_id`` and ``owner_ids``.

        .. versionadded:: 1.3
    strip_after_prefix: :class:`bool`
        Whether to strip whitespace characters after encountering the command
        prefix. This allows for ``!   hello`` and ``!hello`` to both work if
        the ``command_prefix`` is set to ``!``. Defaults to ``False``.

        .. versionadded:: 1.7
    tree_cls: Type[:class:`~discord.app_commands.CommandTree`]
        The type of application command tree to use. Defaults to :class:`~discord.app_commands.CommandTree`.

        .. versionadded:: 2.0
    allowed_contexts: :class:`~discord.app_commands.AppCommandContext`
        The default allowed contexts that applies to all application commands
        in the application command tree.

        Note that you can override this on a per command basis.

        .. versionadded:: 2.4
    allowed_installs: :class:`~discord.app_commands.AppInstallationType`
        The default allowed install locations that apply to all application commands
        in the application command tree.

        Note that you can override this on a per command basis.

        .. versionadded:: 2.4
    """  # noqa: E501

    config: dict
    logger: logging.Logger = logging.getLogger("discord.bot")

    async def on_ready(self) -> None:
        """Informs when the bot is ready."""
        self.logger.info("Logged in as %s (ID: %s)", self.user, self.user.id)  # type: ignore

    async def setup_hook(self) -> None:
        """Load all cogs in the config file."""
        logger = self.logger.getChild("cog")
        for cog in self.config["cogs"]:
            try:
                await self.load_extension(cog)
                logger.info("Loaded cog %s", cog)
            except (
                commands.ExtensionNotFound,
                commands.ExtensionAlreadyLoaded,
                commands.NoEntryPointError,
                commands.ExtensionFailed,
            ) as e:
                logger.exception("Failed to load cog %s", cog, exc_info=e)
