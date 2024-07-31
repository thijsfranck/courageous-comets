<!-- markdownlint-disable MD013 - All syntax for button has to be on the same line -->

# Deployment

This section provides instructions on how to deploy the Courageous Comets application in a production environment.
Follow the steps below to set up the application.

The application is deployed using [Docker](https://www.docker.com/) and [Docker Compose](https://docs.docker.com/compose/).
It consists of the following services:

- [**courageous-comets**](https://github.com/thijsfranck/courageous-comets/pkgs/container/courageous-comets):
  The Courageous Comets application.
- [**redis-stack**](https://hub.docker.com/r/redis/redis-stack-server): The Redis instance used to store data.

By the end of this guide, all services will be running as Docker containers on your system.

## Checklist

- [ ] Set up Docker and Docker Compose on your system.
- [ ] Get the Docker Compose file.
- [ ] Set up a `.env` file.
- [ ] Configure your `DISCORD_TOKEN` in the `.env` file.
- [ ] Select the image versions (optional).
- [ ] Configure additional options (optional).
- [ ] Start the application using Docker Compose.

## Get the Docker Compose File

The application can be deployed using Docker Compose. You can use the `docker-compose.yaml` file provided in the
GitHub repository to start the application.

[Get the Docker Compose :fontawesome-brands-docker:](https://github.com/thijsfranck/courageous-comets/blob/<APP_VERSION>/docker-compose.yaml){ .md-button .md-button--primary }

Download the file and save it in any directory on your system.

## Configuration

Before starting the application, you need to configure the application settings. Create a `.env` file in the same
directory as the `docker-compose.yaml` file.

The sections below will guide you through setting up a minimal configuration to start the application.

??? QUESTION "What other configuration options are available?"

    Refer to the [configuration](configuration.md) section for a complete list of the available options.

### Discord Token

The application requires a valid Discord bot token to connect to Discord. Add the following line to the `.env`
file:

```dotenv
DISCORD_TOKEN=<YOUR_TOKEN>
```

Replace `<YOUR_TOKEN>` with your Discord bot token.

!!! DANGER "Security Warning"

    Keep your Discord bot token secure and do not share it with anyone!

??? QUESTION "Where do I find my Discord bot token?"

    See the configuration section for instructions on [how to obtain a Discord bot token](./configuration.md#discord_token).

### Image Versions

By default, the application uses the latest version of each Docker image. To specify a particular version, you
can add the following variables to the `.env` file:

```dotenv
COURAGEOUS_COMETS_VERSION=<APP_VERSION>
REDIS_STACK_VERSION=latest
```

Replace `latest` with the tag corresponding to the version you want to use.

??? QUESTION "Where can I find previous versions of the image?"

    Previous versions of the Courageous Comets image are available on the [GitHub Container Registry](https://github.com/thijsfranck/courageous-comets/pkgs/container/courageous-comets).

## Start the Application

!!! NOTE "Prerequisites"

    Please ensure that [Docker](https://www.docker.com/) and [Docker Compose](https://docs.docker.com/compose/)
    are installed on your system, and that the Docker daemon is running.

Once you have set up the configuration, you can start the application using Docker Compose. Open a terminal and
navigate to the directory where you saved the `docker-compose.yaml` file. Run the following command:

```bash
docker-compose up -d
```

Docker Compose will start the application in the background. You can check the logs to verify that the application
has started successfully:

```bash
docker-compose logs -f
```

You can now interact with the application in any Discord server where it has been installed.
