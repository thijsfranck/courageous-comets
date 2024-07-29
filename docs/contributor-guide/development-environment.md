# Development Environment

Follow the steps below to set up your development environment.

!!! NOTE "Prerequisites"

    You need to have [Git](https://git-scm.com) installed on your system.

## Environment Setup

You can set up the development environment using either the [development container](#using-the-development-container)
or following the [manual](#manual-setup) setup process.

### Using the Development Container

The project includes a [development container](https://containers.dev) to automatically set up your development
environment, including the all tools and dependencies required to develop the application locally.

!!! NOTE "Prerequisites"

    [Docker](https://www.docker.com) must be installed on your system to use the development container.

#### Quick Start

See the video installation guide below for a step-by-step tutorial on installing the development container with
Visual Studio Code:

<video controls>
    <source src="https://github.com/user-attachments/assets/703aa245-9e33-44d9-9c79-7432afbeb445" type="video/mp4">
</video>

First, install the [Remote Development Extension Pack](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.vscode-remote-extensionpack).
Next, open Visual Studio Code and click on icon in the bottom left corner to open the command palette for remote
environments.

Select the `Clone Repository in Container Volume` command. This will prompt you to select the
repository to clone. Choose the `thijsfranck/courageous-comets` repository or paste the repository URL.

Once you confirm the selection, the development container will be set up automatically.

#### Detailed Setup Guide

For more details, refer to the setup guide for your IDE:

- [Visual Studio Code](https://code.visualstudio.com/docs/devcontainers/tutorial)
- [PyCharm](https://www.jetbrains.com/help/pycharm/connect-to-devcontainer.html)

#### Services

The development container includes the following services for local development:

| Service      | Description  | Address                                   |
| ------------ | ------------ | ----------------------------------------- |
| Redis        | Database     | [`localhost:6379`](http://localhost:6379) |
| RedisInsight | Database GUI | [`localhost:8001`](http://localhost:8001) |

### Manual Setup

If you prefer to set up the development environment manually, follow the steps below.

!!! NOTE "Prerequisites"

    Please ensure [Python 3.12](https://www.python.org) and [Poetry](https://python-poetry.org) are installed
    on your system.

#### Clone the Repository

To clone the repository, run the following command:

```bash
git clone https://github.com/thijsfranck/courageous-comets.git
```

Next, open the project in your preferred IDE or navigate to the project directory using the terminal.

#### Install Dependencies

Start by installing the project dependencies using Poetry:

```bash
poetry install
```

This will create a virtual environment and install the required dependencies.

#### Pre-commit Hooks

Next, install the pre-commit hooks to ensure that your code is formatted and linted before each commit:

```bash
poetry run pre-commit install
```

This will set up the pre-commit hooks to run automatically when you commit changes to the repository.

#### Redis Database

The application requires a Redis database to run. We recommend setting up a local Redis instance using Docker
for development purposes.

To start a Redis instance using Docker, run the following command:

```bash
docker run -d -p 6379:6379 -p 8001:8001 redis/redis-stack:latest
```

This will start a Redis server on port `6379` and a RedisInsight GUI on port `8001`.

## Configuring your Environment

To run the application, you will need to provide the following configurations in a `.env` file at the project
root directory.

### Discord Token

The application requires a Discord bot token to run. It should be stored in the `.env` file as follows:

```dotenv
DISCORD_TOKEN=<YOUR DISCORD_TOKEN>
```

The repository includes an encrypted `.env.lock` file with the shared Discord bot token for our team. Follow the
[Secrets Management](./secrets-management.md) guide to decrypt the file and start using the token.

??? QUESTION "Can I use my own Discord bot token?"

    Yes, you can use your own Discord bot token. If you do so, there's need to decrypt the `.env.lock` file.

### Redis Configuration

If you're not using the development container, you will need to configure the Redis connection in the `.env` file:

```dotenv
REDIS_HOST=localhost
REDIS_PORT=6379
```

This configuration assumes you are running a local Redis instance on the default port.

## Running the Application

With your development environment set up and configured, you can run the application using the following command:

```bash
poetry run python -m courageous_comets
```

The application should now be online and ready to respond to input from your Discord server.

## Building the Docker Image

!!! INFO "Production Builds"

    The release process is fully automated and does not require you to build the docker image locally. See the
    [GitHub Actions](./version-control.md#github-actions) section of the version control guide for more information.

Before building the Docker image, first build the Python package with Poetry:

```bash
poetry build -f wheel
```

This will create a `.whl` file in the `dist` directory. Next, build the Docker image as follows:

```bash
docker build -t ghcr.io/thijsfranck/courageous-comets:latest .
```

## Running the Docker Container

Once you have [built the Docker image](#building-the-docker-image), use the following command to run the production
container locally:

```bash
docker run -i --env-file .env ghcr.io/thijsfranck/courageous-comets:latest
```

This will run the application just as it would in production, using your local `.env` file and Redis instance.

## Running the Docker Compose Stack

To run the application in a production configuration including the Redis database, you can use the Docker Compose
stack.

First, build the Docker image as described in [the previous section](#building-the-docker-image). Then, run the
following command:

```bash
docker-compose up
```

This will start the application and the Redis database in separate containers using your local `.env` file.

## Running the Documentation

To view the documentation locally, you can use the following command:

```bash
poetry run mkdocs serve
```

Open your browser and navigate to [`http://localhost:8000`](http://localhost:8000) to view the documentation.
The changes you make to the documentation will be automatically reflected in the browser.
