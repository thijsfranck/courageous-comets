# Configuration

The following environment variables are available to configure the application:

| Variable        | Description            | Required | Default     |
| --------------- | -----------------------| -------- | ----------- |
| `DISCORD_TOKEN` | The Discord bot token. | Yes      | -           |
| `LOG_LEVEL`     | The minimum log level. | No       | `INFO`      |
| `REDIS_HOST`    | The Redis host.        | No       | `localhost` |
| `REDIS_PORT`    | The Redis port.        | No       | `6379`      |
| `REDIS_PASSWORD`| The Redis password.    | No       | -           |

## `DISCORD_TOKEN`

You can obtain a Discord bot token from the [Discord Developer Portal](https://discord.com/developers/applications).
Your token should have the following scopes:

- `bot`

!!! DANGER "Security Warning"
    Do not share your token with anyone!

## `LOG_LEVEL`

The minimum log level to display. The following levels are available:

- `DEBUG`
- `INFO`
- `WARNING`
- `ERROR`
- `CRITICAL`

## `REDIS_HOST`

The hostname of the Redis server. Defaults to `localhost`.

## `REDIS_PORT`

The port of the Redis server. Defaults to `6379`.

## `REDIS_PASSWORD`

The password of the Redis server. Set this variable if your Redis server requires authentication. No password
is set by default.

!!! DANGER "Security Warning"
    Do not share your Redis password with anyone!
