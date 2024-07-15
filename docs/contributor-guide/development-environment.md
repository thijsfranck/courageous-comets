# Development Environment

Follow the steps below to set up your development environment.

!!! NOTE "Prerequisites"
    You need to have [Git](https://git-scm.com) installed on your system.

## Cloning the Repository

To clone the repository, run the following command:

```bash
git clone https://github.com/thijsfranck/courageous-comets.git
```

Next, open the project in your preferred IDE or navigate to the project directory using the terminal.

## Environment Setup

You can set up the development environment using either the [automated](#automated-setup) or [manual](#manual-setup)
setup process.

### Automated Setup

The project includes a [development container](https://containers.dev) to automatically set up your development
environment.

To get started, refer to the setup guide for your IDE:

- [Visual Studio Code (recommended)](https://code.visualstudio.com/docs/devcontainers/tutorial)
- [PyCharm](https://www.jetbrains.com/help/pycharm/connect-to-devcontainer.html)

??? TIP "Cloud Development Environment"
    Alternatively, you can use a [GitHub Codespace](https://docs.github.com/en/codespaces/getting-started/quickstart)
    to set up your development environment in the cloud.

### Manual Setup

If you prefer to set up the development environment manually, follow the steps below.

!!! NOTE "Prerequisites"
    Please ensure [Python 3.12](https://www.python.org) and [Poetry](https://python-poetry.org) are installed
    on your system.

Start by installing the project dependencies using Poetry:

```bash
poetry install
```

Finally, install the pre-commit hooks:

```bash
poetry run pre-commit install
```

## Configuration

To configure your development environment, create a `.env` file in the project root directory with the following
content:

```env
DISCORD_TOKEN=<YOUR_TOKEN>
```

Replace `<YOUR_TOKEN>` with your Discord bot token.

!!! DANGER "Security Warning"
    Do not commit your `.env` file to version control or share your token with anyone!

??? QUESTION "Where do I find my Discord bot token?"
    You can obtain a Discord bot token from the [Discord Developer Portal](https://discord.com/developers/applications).

## Running the Documentation Locally

To view the documentation locally, you can use the following command:

```bash
poetry run mkdocs serve
```

Open your browser and navigate to [`http://localhost:8000`](http://localhost:8000) to view the documentation.
The changes you make to the documentation will be automatically reflected in the browser.
