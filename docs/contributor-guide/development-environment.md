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

### Secrets Management

To use our team's shared Discord bot token, you will need to retrieve it from the `.env.lock` file in the project
root directory. This section will guide you through the process of decrypting the file to access the token.

??? QUESTION "Can I use my own Discord bot token?"
    Yes, you can use your own Discord bot token.

    First, create a new bot account on the [Discord Developer Portal](https://discord.com/developers/applications).
    Generate a token for your bot account and create a `.env` file in the project root directory. Add the following
    line to the file:

    ```plaintext
    DISCORD_TOKEN=<YOUR DISCORD TOKEN>
    ```

    If you choose to use your own token, you can skip the steps below.

#### Install Tools

First, you will need to install [GnuPG](https://gnupg.org) and [SOPS](https://github.com/getsops/sops) on your
system. Follow the instructions for your operating system below.

=== "Windows"

    Open a PowerShell terminal and run the following commands:

    ```bash
    winget install -e --id Mozilla.SOPS
    winget install -e --id GnuPG.GnuPG
    ```

=== "macOS"

    Open a terminal and run the following command:

    ```bash
    brew install sops gnupg
    ```

=== "Linux"

    Download the [SOPS binary](https://github.com/getsops/sops/releases) for your platform.  For instance, if you are on an amd64 architecture:
    ```bash
    curl -LO https://github.com/getsops/sops/releases/download/v3.9.0/sops-v3.9.0.linux.amd64
    ```

    Move the binary into your PATH
    ```bash
    mv sops-v3.9.0.linux.amd64 /usr/local/bin/sops
    ```

    Make the binary executable
    ```bash
    chmod +x /usr/local/bin/sops
    ```
    Install GnuPG
    ```bash
    sudo apt-get install -y gnupg
    ```

=== "Development Container"

    If you are using the development container, the tools are already installed! 🎉

#### Install Keys

Next, you will need to import the required keys. Copy the files with the keys into your workspace and import them
using the following commands:

```bash
gpg --import courageous-comets.pub.asc
gpg --import courageous-comets.sec.asc
```

The keys will be imported into your keyring.

!!! DANGER "Security Warning"
    Do not share the keys with anyone!

??? QUESTION "Where can I find the keys?"
    You can download the keys from our private Discord server.

#### Decrypt `.env.lock`

Once you have installed the required keys, you can decrypt the `.env.lock` file using the following command:

```bash
sops -d --input-type dotenv --output-type dotenv .env.lock > .env
```

This will create a decrypted `.env` file at the project root directory. You can now view the contents of the file
and access the Discord bot token.

!!! DANGER "Security Warning"
    Do not commit your decrypted `.env` file to version control or share the token with anyone!

## Running the Documentation Locally

To view the documentation locally, you can use the following command:

```bash
poetry run mkdocs serve
```

Open your browser and navigate to [`http://localhost:8000`](http://localhost:8000) to view the documentation.
The changes you make to the documentation will be automatically reflected in the browser.
