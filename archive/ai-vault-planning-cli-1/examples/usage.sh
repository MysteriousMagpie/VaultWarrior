#!/bin/bash

# AI Vault Planning CLI Usage Example

# Initialize a new vault
ai init /path/to/Vault

# Index markdown files in the vault
ai index /path/to/Vault

# Create a new thread with a seed note
ai thread new demo --vault-path /path/to/Vault --seed "Kickoff notes"

# Ask a question related to the project
ai chat demo "What is my next 2-hour task on project X?" --vault-path /path/to/Vault --write

# Capture a quick note in the daily log
ai capture "Remember to follow up with the team on project X." --write

# Plan the next steps for the project
ai plan demo --weekly --write