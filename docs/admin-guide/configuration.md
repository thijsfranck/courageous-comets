# Configuration

The following environment variables are available to configure the application:

| Variable                                                                          | Description                                                              | Required | Default            |
| --------------------------------------------------------------------------------- | ------------------------------------------------------------------------ | -------- | ------------------ |
| [`DISCORD_TOKEN`](#discord_token)                                                 | The Discord bot token.                                                   | Yes      | -                  |
| [`BOT_CONFIG_PATH`](#bot_config_path)                                             | The path to the bot's configuration file.                                | No       | `application.yaml` |
| [`DISCORD_API_CONCURRENCY`](#discord_api_concurrency)                             | The maximum number of concurrent Discord API requests.                   | No       | `3`                |
| [`ENVIRONMENT`](#environment)                                                     | The environment in which the application is running.                     | No       | `production`       |
| [`HF_DOWNLOAD_CONCURRENCY`](#hf_download_concurrency)                             | The maximum number of concurrent downloads when installing transformers. | No       | `3`                |
| [`HF_HOME`](#hf_home)                                                             | The directory containing Huggingface Transformers data files.            | No       | `hf_data`          |
| [`LOG_LEVEL`](#log_level)                                                         | The minimum log level.                                                   | No       | `INFO`             |
| [`MPLCONFIGDIR`](#mplconfigdir)                                                   | The directory containing Matplotlib configuration files.                 | No       | `/app/matplotlib`  |
| [`NLTK_DATA`](#nltk_data)                                                         | The directory containing NLTK data files.                                | No       | `nltk_data`        |
| [`NLTK_DOWNLOAD_CONCURRENCY`](#nltk_download_concurrency)                         | The maximum number of concurrent downloads when installing NLTK data.    | No       | `3`                |
| [`PREPROCESSING_MAX_WORD_LENGTH`](#preprocessing_max_word_length)                 | The maximum word length. Longer words are dropped.                       | No       | `35`               |
| [`PREPROCESSING_MESSAGE_TRUNCATE_LENGTH`](#preprocessing_message_truncate_length) | The maximum message length. Longer messages are truncated.               | No       | `256`              |
| [`REDIS_HOST`](#redis_host)                                                       | The Redis host.                                                          | No       | `localhost`        |
| [`REDIS_PORT`](#redis_port)                                                       | The Redis port.                                                          | No       | `6379`             |
| [`REDIS_PASSWORD`](#redis_password)                                               | The Redis password.                                                      | No       | -                  |

## Required Settings

The following settings are required to start the application:

### `DISCORD_TOKEN`

You can obtain a Discord bot token from the [Discord Developer Portal](https://discord.com/developers/applications).
Your token should have the following scopes:

- `bot`

!!! DANGER "Security Warning"

    Do not share your token with anyone!

## Optional Settings

The following settings are optional or have default values that can be overridden:

### `BOT_CONFIG_PATH`

This specifies the location of the bot's configuration file. By default, the application searches for a file named
`application.yaml` in the directory from which it is launched. In the Docker image, this file is located at `/app/application.yaml`.

[Read more](#applicationyaml) about the `application.yaml` file.

### `DISCORD_API_CONCURRENCY`

The maximum number of concurrent Discord API requests. By default, this is set to `3`.

### `ENVIRONMENT`

The environment in which the application is running. Set this to `development` to enable development features
such as loading development cogs. By default, this is set to `production`.

### `HF_DOWNLOAD_CONCURRENCY`

The maximum number of concurrent downloads when installing Huggingface Transformers models. By default, this
is set to `3`.

### `HF_HOME`

The directory containing Huggingface Transformers data files. By default, this is set to `hf_data` in the directory
from which the application is launched. In the Docker image, this directory is located at `/app/hf_data`.

### `LOG_LEVEL`

The minimum log level to display. The following levels are available:

- `DEBUG`
- `INFO`
- `WARNING`
- `ERROR`
- `CRITICAL`

The default log level is `INFO`.

### `MPLCONFIGDIR`

The directory containing `matplotlib` configuration files. Uses the default `matplotlib` configuration directory
unless otherwise configured. In the Docker image, the `matplotlib` configuration files are located at `/app/matplotlib`.

### `NLTK_DATA`

The directory containing NLTK data files. By default, this is set to `nltk_data` in the directory from which the
application is launched. In the Docker image, this directory is located at `/app/nltk_data`.

### `NLTK_DOWNLOAD_CONCURRENCY`

The application automatically downloads NLTK data files on startup. This setting controls the number of concurrent
downloads. By default, this is set to `3`.

### `PREPROCESSING_MAX_WORD_LENGTH`

The maximum word length. Words longer than this value are dropped. By default, this is set to `35`.

### `PREPROCESSING_MESSAGE_TRUNCATE_LENGTH`

The maximum message length. Messages longer than this value are truncated. By default, this is set to `256`.

### `REDIS_HOST`

The hostname of the Redis server. Defaults to `localhost`.

### `REDIS_PORT`

The port of the Redis server. Defaults to `6379`.

### `REDIS_PASSWORD`

The password of the Redis server. Set this variable if your Redis server requires authentication. No password
is set by default.

!!! DANGER "Security Warning"

    Do not share your Redis password with anyone!

## `application.yaml`

The `application.yaml` file is a configuration file that specifies the cogs to load, the NLTK datasets to download,
and the Huggingface Transformers models to install on startup. It has the following structure:

```yaml
# List of cogs to load when the bot starts, identified by their package name.
cogs:
  - <PACKAGE_NAME>
  - <PACKAGE_NAME>
# List of cogs to load in development mode only, identified by their package name.
dev-cogs:
  - <PACKAGE_NAME>
  - <PACKAGE_NAME>
# List of NLTK datasets to download on startup.
nltk:
  - <DATASET_NAME>
  - <DATASET_NAME>
# List of Huggingface Transformers models to download on startup.
transformers:
  - <MODEL_NAME>
  - <MODEL_NAME>
```

!!! WARNING "Advanced Users Only"

    For standard use, the `application.yaml` file does not need to be changed. We recommend against modifying this
    file unless you know what you're doing.

One possible use case is to add additional feature or disable existing features by modifying the list of cogs.
To add a new cog, add the package name to the `cogs` list. To disable a feature, remove the package name from
the list.

Below is a list of all cogs that are loaded by default:

| Package Name                                            | Description                                                                      |
| ------------------------------------------------------- | -------------------------------------------------------------------------------- |
| `courageous_comets.cogs.about`                          | Provides information about the bot.                                              |
| `courageous_comets.cogs.keywords.search_command`        | Searches for keywords using a slash command.                                     |
| `courageous_comets.cogs.keywords.search_context_menu`   | Searches for keywords using a context menu item.                                 |
| `courageous_comets.cogs.keywords.topics_command`        | Lists the most popular keywords for a given context using a slash command.       |
| `courageous_comets.cogs.keywords.user_context_menu`     | Lists the most popular keywords for a particular user using a context menu item. |
| `courageous_comets.cogs.messages`                       | Listens for messages and passes them on for internal processing.                 |
| `courageous_comets.cogs.ping`                           | Responds to ping requests.                                                       |
| `courageous_comets.cogs.sentiment.message_context_menu` | Analyzes the sentiment of a message using a context menu item.                   |
| `courageous_comets.cogs.sentiment.search_command`       | Searches for messages with similar sentiment using a slash command.              |
| `courageous_comets.cogs.sentiment.search_context_menu`  | Searches for messages with similar sentiment using a context menu item.          |
| `courageous_comets.cogs.sentiment.user_context_menu`    | Analyzes the sentiment of a user's messages using a context menu item.           |
| `courageous_comets.cogs.frequency`                      | Provides an overview of the amount of recent messages for a given timespan.      |
