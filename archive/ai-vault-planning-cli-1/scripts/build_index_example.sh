#!/bin/bash

# This script demonstrates how to build an index for a sample vault using the AI Vault Planning CLI.

# Set the path to your vault
VAULT_PATH="./examples/sample_vault"

# Initialize the vault (if not already initialized)
ai init "$VAULT_PATH"

# Build the index for the vault
ai index "$VAULT_PATH"

# Output the status
echo "Indexing completed for vault at: $VAULT_PATH"