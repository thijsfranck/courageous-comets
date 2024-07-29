# Secrets Management

To use our team's shared Discord bot token, you will need to retrieve it from the `.env.lock` file in the project
root directory. This section will guide you through the process of decrypting the file to access the token.

## Install Tools

First, you will need to install [`age`](https://github.com/FiloSottile/age) and [`SOPS`](https://github.com/getsops/sops)
on your system. Follow the instructions for your operating system below.

=== "Windows"

    Open a PowerShell terminal and run the following command to install `SOPS`:

    ```bash
    winget install -e --id Mozilla.SOPS
    ```

    To install `age`, download the [latest binary for Windows](https://github.com/FiloSottile/age/releases) and
    add your `age` binary to the system `PATH`.

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

## Generate Keys

??? TIP "Using the development container"

    The development container automatically generates a key pair for you on initial setup. You public key will
    be shown in the terminal output. You can also find it later in the `secrets/keys.txt` file.

Next, you will need to generate a new key pair using `age`. Run the following command from the root directory of
the project:

```bash
age-keygen -o > secrets/keys.txt
```

This will create a new key pair and save it to the `secrets/keys.txt` file. Share your public key with the team
so it can be registered.

!!! DANGER "Security Warning"

    Only your public key can be safely shared. Do not share the private key with anyone!

??? QUESTION "Where can I find my public key?"

    You can find your public key in the `secrets/keys.txt` file or in the terminal output after generating the
    key pair.

## Registering a new Public Key

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

## Decrypting Secrets

Once your public key is added to the `.env.lock` file, you can decrypt the file to access the Discord bot token.
First, pull the latest changes from the repository:

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

## Encrypting Secrets

To encrypt the `.env` file after making changes, run the following command:

```bash
sops encrypt .env > .env.lock
```

This will encrypt the file and save it to the `.env.lock` file. You can now commit the changes to version control.
