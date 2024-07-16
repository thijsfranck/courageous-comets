# Development Environment

Follow the steps below to set up your development environment.

!!! NOTE "Prerequisites"
    You need to have [Git](https://git-scm.com) installed on your system.

## Environment Setup

You can set up the development environment using either the [automated](#automated-setup) or [manual](#manual-setup)
setup process.

### Automated Setup

The project includes a [development container](https://containers.dev) to automatically set up your development
environment.

!!! NOTE "Prerequisites"
    [Docker](https://www.docker.com) must be installed on your system to use the development container.

??? TIP "GitHub Codespaces"
    If your system does not support Docker, you can use a [GitHub Codespace](https://docs.github.com/en/codespaces/getting-started/quickstart)
    to install a development container in the cloud.

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

## Secrets Management

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

### Install Tools

First, you will need to install [`age`](https://github.com/FiloSottile/age) and [`SOPS`](https://github.com/getsops/sops)
on your system. Follow the instructions for your operating system below.

=== "Windows"

    Open a PowerShell terminal and run the following command to install `SOPS`:

    ```bash
    winget install -e --id Mozilla.SOPS
    ```

    To install `age`, download the [latest binary for Windows](https://github.com/FiloSottile/age/releases) and
    move it into your `PATH`.

=== "macOS"

    Open a terminal and run the following command:

    ```bash
    brew install age sops
    ```

=== "Linux"

    Download the [`SOPS` binary](https://github.com/getsops/sops/releases) for your platform. For instance, if
    you are on an amd64 architecture:

    ```bash
    curl -LO https://github.com/getsops/sops/releases/download/v3.9.0/sops-v3.9.0.linux.amd64
    ```

    Move the binary into your `PATH`:

    ```bash
    mv sops-v3.9.0.linux.amd64 /usr/local/bin/sops
    ```

    Make the binary executable:

    ```bash
    chmod +x /usr/local/bin/sops
    ```

    Finally, install `age`:

    ```bash
    sudo apt-get install -y age
    ```

=== "Development Container"

    If you are using the development container, the tools are already installed! 🎉

### Generate Keys

Next, you will need to generate a new key pair using `age`. Run the following command from the root directory of
the project:

```bash
age-keygen -o > secrets/keys.txt
```

This will create a new key pair and save it to the `secrets/keys.txt` file. The public key will also be printed
to the terminal. Share this key with the team so it can be added to the `.env.lock` file.

!!! DANGER "Security Warning"
    Only your public key can be safely shared. Do not share the private key with anyone!

??? TIP "Development Container Automation"
    On initial setup, the key pair is generated automatically in the development container. You can find the
    public key in the devcontainer output.

??? QUESTION "Where can I find my public key?"
    You can find your public key in the `secrets/keys.txt` file or in the terminal output after generating the
    key pair.

### Registering a new Public Key

!!! NOTE "Prerequisite"
    This step needs to be performed by a team member who already has access to the `.env` file.

To register a new public key, first extend the `.sops.yaml` file in the project root directory.
Add the public key to the list of `age` keys. Each key is separated by a comma and a newline.

```yaml
creation_rules:
  - age: >-
      <KEY1>,
      <KEY2>,
      <KEY3>
```

Next, [encrypt](#encrypting-secrets) the `.env` file with the updated list of keys and push it to the repository.

### Decrypting Secrets

Once someone has added your public key to the `.env.lock` file, you can decrypt the file to access the Discord
bot token. First, pull the latest changes from the repository:

```bash
git pull
```

!!! NOTE "Prerequisite"
    `SOPS` requires the `SOPS_AGE_KEY_FILE` environment variable to be set to the path of your private key file.
    This is automatically set up in the development container.

Next, run the following command to decrypt the `.env.lock` file:

```bash
sops decrypt --input-type dotenv --output-type dotenv .env.lock > .env
```

This will decrypt the file and save the contents to a new `.env` file in the project root directory. You can now
access the Discord bot token.

!!! DANGER "Security Warning"
    Do not commit your decrypted `.env` file to version control or share the contents with anyone!

### Encrypting Secrets

To encrypt the `.env` file after making changes, run the following command:

```bash
sops encrypt .env > .env.lock
```

## Running the Documentation Locally

To view the documentation locally, you can use the following command:

```bash
poetry run mkdocs serve
```

Open your browser and navigate to [`http://localhost:8000`](http://localhost:8000) to view the documentation.
The changes you make to the documentation will be automatically reflected in the browser.
