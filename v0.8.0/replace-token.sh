#!/bin/bash

# Check if the correct number of arguments is provided
if [ "$#" -ne 2 ]; then
  echo "Usage: $0 <token> <replacement>"
  exit 1
fi

# Assign arguments to variables
token=$1
replacement=$2

# Get the directory where the script is located
docs_dir=$(dirname "$0")

# Find and iterate over all .md files in the docs directory and its subdirectories
find "$docs_dir" -name "*.md" | while read -r file;
do
  # Replace the token with the replacement in each file
  sed -i.bak "s/$token/$replacement/g" "$file"
  # Remove the backup file
  rm "$file.bak"
done

echo "Token '$token' replaced with '$replacement' in all .md files in the '$docs_dir' directory."
