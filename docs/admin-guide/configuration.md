# Configuration

The following environment variables are available to configure the application:

| Variable                              | Description                               | Required | Default            |
| ------------------------------------- | ------------------------------------------| -------- | ------------------ |
| [`DISCORD_TOKEN`](#discord_token)     | The Discord bot token.                    | Yes      | -                  |
| [`BOT_CONFIG_PATH`](#bot_config_path) | The path to the bot's configuration file. | No       | `application.yaml` |
| [`LOG_LEVEL`](#log_level)             | The minimum log level.                    | No       | `INFO`             |
| [`NLTK_DATA`](#nltk_data)             | The directory containing NLTK data files. | No       | `/nltk_data`       |
| [`REDIS_HOST`](#redis_host)           | The Redis host.                           | No       | `localhost`        |
| [`REDIS_PORT`](#redis_port)           | The Redis port.                           | No       | `6379`             |
| [`REDIS_PASSWORD`](#redis_password)   | The Redis password.                       | No       | -                  |

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

This specifies the location of the bot's configuration file, which is a YAML file containing the following information:

```yaml
# List of cogs to load when the bot starts, identified by their package name.
cogs:
  - <PACKAGE_NAME>
  - <PACKAGE_NAME>
```

By default, the application searches for a file named `application.yaml` in the directory from which it is launched.
In the Docker image, this file is located at `/app/application.yaml`.

### `LOG_LEVEL`

The minimum log level to display. The following levels are available:

- `DEBUG`
- `INFO`
- `WARNING`
- `ERROR`
- `CRITICAL`

The default log level is `INFO`.

### `NLTK_DATA`

The directory containing NLTK data files. By default, this is set to `nltk_data` in the directory from which the
application is launched. In the Docker image, this directory is located at `/app/nltk_data`.

### `REDIS_HOST`

The hostname of the Redis server. Defaults to `localhost`.

### `REDIS_PORT`

The port of the Redis server. Defaults to `6379`.

### `REDIS_PASSWORD`

The password of the Redis server. Set this variable if your Redis server requires authentication. No password
is set by default.

!!! DANGER "Security Warning"
    Do not share your Redis password with anyone!
