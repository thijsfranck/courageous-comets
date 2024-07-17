#!/bin/bash

# Mark the git repository as safe
git config --global --add safe.directory $PWD

# Install pre-commit hooks
poetry run pre-commit install

# Generate a new secret key if one doesn't exist
if [ ! -f secrets/keys.txt ]; then
  echo
  echo "Generating a new secret key. Share the following public key with the team:"
  age-keygen -o secrets/keys.txt
  echo
fi
