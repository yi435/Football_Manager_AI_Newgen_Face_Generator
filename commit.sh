#!/bin/bash
# Check if a commit message was passed as an argument
if [ -z "$1" ]; then
    read -p "Enter commit message: " message
else
    message="$1"
fi

# Add all changes
git add .

# Commit changes
git commit -m "$message"

# Push to GitHub
git push
echo "Successfully pushed to GitHub!"
