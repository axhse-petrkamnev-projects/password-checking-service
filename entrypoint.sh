#!/bin/bash

# Path to the storage
STORAGE_DIR="/data"

# Path to the .txt file with hashed passwords
PASSWORDS_TXT="/data/pwnedpasswords.txt"

# Check if storage needs to be initialized
if [ ! -d "$STORAGE_DIR" ] || [ ! "$(ls -A $STORAGE_DIR)" ]; then
    echo "Initializing the storage..."
    python -m devops_cli.update_storage "$STORAGE_DIR" -c 64 -f "$PASSWORDS_TXT"
else
    echo "Storage already initialized."
fi

# Start the Flask application
exec python app.py
