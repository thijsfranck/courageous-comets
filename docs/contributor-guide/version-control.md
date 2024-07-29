# Version Control

When making changes to the project, follow these guidelines.

## Branching

Always create a new branch for your changes. This makes it easier to handle multiple contributions simultaneously.

First, pull the latest changes from the `main` branch:

```bash
git pull main
```

Next, create a new branch with the following command:

```bash
git checkout -b "<YOUR_BRANCH_NAME>"
```

Replace `<YOUR_BRANCH_NAME>` with a short, descriptive name for your branch. For example, `add-uptime-command`.

## Commits

Commits should follow the [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) specification.
This helps maintain a clean and structured commit history.

Try to keep your commits focused on a single task. If you need to make multiple changes, create separate commits
for each change.

??? EXAMPLE "Conventional Commit Format"

    Here's an example of a good commit message:

    ```plaintext
    feat: add uptime command

    Add a new command to display the bot's uptime.
    ```

??? TIP "Use Commitizen"

    The workspace includes [Commitizen](https://commitizen-tools.github.io/commitizen/) to help you write conventional
    commit messages. Run the following command to create a commit message interactively:

    ```bash
    poetry run cz commit
    ```

### Automated Checks

The project includes pre-commit hooks to ensure your code meets the quality standards. These hooks run automatically
before each commit.

The pre-commit hooks include:

- Linting and formatting with [Ruff](https://docs.astral.sh/ruff/)
- Commit message validation with [Commitizen](https://commitizen-tools.github.io/commitizen/)

??? QUESTION "What if the pre-commit hooks fail?"

    If the pre-commit hooks fail, you will need to address the issues before committing your changes. Follow the
    instructions provided by the pre-commit hooks to identify and fix the issues.

??? QUESTION "How do I run the pre-commit hooks manually?"

    Pre-commit hooks can also be run manually using the following command:

    ```bash
    poetry run pre-commit
    ```

The pre-commit hooks are intended to help us keep the codebase maintainable. If there are rules that you believe
are too strict, please discuss them with the team.

## Pull Requests

Once you have completed your changes, it's time to create a pull request. A pull request allows your changes to
be reviewed and merged into the `main` branch.

Before creating a pull request, ensure your branch is up to date with the latest changes from the `main` branch:

```bash
git pull main
```

Next, push your changes to the repository:

```bash
git push
```

Finally, [create a pull request on GitHub](https://github.com/thijsfranck/courageous-comets/compare). Select
your branch as the source and the `main` branch as the base.

In the pull request description, provide a brief overview of the changes and any relevant information for reviewers.

??? EXAMPLE "Pull Request Description"

    Here's an example of a good pull request description:

    ```plaintext
    # feat: add uptime command

    This pull request adds a new uptime command to display the bot's uptime.

    ## Changes

    - Added a new command to display the bot's uptime
    - Updated the help command to include information about the new command

    ## Notes

    - The new command is implemented in a separate file for better organization
    - The command has been tested locally and works as expected
    ```

### Automated Checks

The project includes automated checks to ensure the code meets the quality standards. These checks include:

- All [pre-commit hooks](#automated-checks) must pass
- Type checking with [Pyright](https://github.com/microsoft/pyright)
- Running all tests with [pytest](https://docs.pytest.org/en/stable/)

??? QUESTION "What if the automated checks fail?"

    If any of the automated checks fail, please address the issues before requesting a review. Feedback from the
    automated checks should be available in the pull request checks tab.

### Code Review

All pull requests should be reviewed by at least one other team member before merging. The reviewer will provide
feedback and suggestions for improvement.

Once the reviewer approves the pull request, you can merge it into the `main` branch.

??? QUESTION "How do I request a review?"

    Request a review from a team member by [assigning them as a reviewer](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/requesting-a-pull-request-review)
    to your pull request.

#### Giving Feedback

When providing feedback on a pull request, be constructive and specific. Point out areas for improvement and suggest
possible solutions. If you have any questions or concerns, don't hesitate to ask the author for clarification.

A code review should focus on the following aspects:

- Correctness and functionality
- Code quality and readability
- Adherence to the project guidelines

??? EXAMPLE "Good Code Review Feedback"

    Here are some examples of good code review feedback:

    ```plaintext
    - Great work on the new command! The implementation looks good overall.
    - I noticed a small typo in the docstring. Could you update it to fix the typo?
    - The logic in the new command is a bit complex. Consider breaking it down into smaller functions for clarity.
    - The tests cover most of the functionality, but we are missing a test case for edge case X. Could you add a test for that?
    ```

Always be respectful and considerate when giving feedback. Remember that the goal is to improve the code and help
the author grow as a developer.

!!! SUCCESS "Be Positive"

    Don't forget to acknowledge the positive aspects of the contribution as well!

## Release

Releases are managed through [Commitizen](https://commitizen-tools.github.io/commitizen/). To generate a
new release, run the following command:

```bash
poetry run cz bump
```

This command will automatically determine the next version number based on the commit history and generate a
new tag. It will also update the changelog with the latest changes. To push the changes to the repository, run:

```bash
git push && git push --tags
```

The release will trigger a [GitHub actions workflow](#github-actions) to build and publish a new version of the
Docker image and update the documentation.

??? TIP "Dry Run"

    You can perform a dry run to see the changes that will be made without actually committing them:

    ```bash
    poetry run cz bump --dry-run
    ```

??? TIP "Commitizen and Conventional Commits"

    Commitizen uses the commit messages to determine the type of changes and generate the release notes.
    Make sure to follow the [commit message guidelines](#commits) to ensure accurate release notes.

### Semantic Versioning

Tags should be unique and follow the [Semantic Versioning](https://semver.org/) format.
Semantic version numbers consist of three parts: `major.minor.patch`. For example, `1.0.0`.

To calculate the next version number, follow these guidelines:

- For _bug fixes_ or _minor improvements_, increment the patch version.
- For _new features_ or _significant improvements_, increment the minor version.
- For **breaking changes**, increment the major version.

??? QUESTION "What is a breaking change?"

    A breaking change requires users to change the way they use the software. Examples include removal of features
    or backwards-incompatible API changes.

??? EXAMPLE "Semantic Versioning"

    Here are some examples of version increments:

    - Bug fixes: `1.0.0` -> `1.0.1`
    - New features: `1.0.1` -> `1.1.0`
    - Breaking changes: `1.1.0` -> `2.0.0`

### GitHub Actions

A GitHub actions workflow will automatically build and publish a new version of the Docker image when a new tag
is pushed to the repository.

The updated image will be available on the [GitHub Container Registry](https://github.com/thijsfranck/courageous-comets/pkgs/container/courageous-comets)
with both the release tag and the `latest` tag.

The GitHub actions workflow also updates the documentation to reflect the new release.
