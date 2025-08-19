# AI Vault Planning CLI Commands Documentation

## Overview
This document provides an overview of the commands available in the AI Vault Planning CLI. Each command is designed to facilitate interaction with your markdown vault, enabling various functionalities such as initialization, indexing, and querying.

## Commands

### `ai init <vault_path>`
- **Description**: Initializes a new vault at the specified path.
- **Usage**: 
  ```bash
  ai init /path/to/vault
  ```

### `ai index <vault_path>`
- **Description**: Builds a FAISS embeddings index over the markdown files in the specified vault.
- **Usage**: 
  ```bash
  ai index /path/to/vault
  ```

### `ai thread new <slug>`
- **Description**: Creates a new thread file with frontmatter in the vault.
- **Usage**: 
  ```bash
  ai thread new demo --vault-path /path/to/vault --seed "Kickoff notes"
  ```

### `ai ask "question"`
- **Description**: Performs a retrieval operation based on the provided question and prints a citation list.
- **Usage**: 
  ```bash
  ai ask "What is the status of project X?"
  ```

### `ai chat <slug> "message" --write`
- **Description**: Streams an OpenAI answer to the specified thread and appends the message.
- **Usage**: 
  ```bash
  ai chat demo "What is my next 2-hour task on project X?" --vault-path /path/to/vault --write
  ```

### `ai capture "text" --write`
- **Description**: Appends a quick capture note to the daily note.
- **Usage**: 
  ```bash
  ai capture "Meeting notes from today" --write
  ```

### `ai plan <slug> --weekly --write`
- **Description**: Produces a checkpoint summary and appends it to the specified thread.
- **Usage**: 
  ```bash
  ai plan demo --weekly --write
  ```

### `ai doctor`
- **Description**: Performs basic sanity checks to ensure the presence of necessary configuration and index files.
- **Usage**: 
  ```bash
  ai doctor
  ```

## Conclusion
This document serves as a quick reference for the commands available in the AI Vault Planning CLI. For further details on each command, please refer to the respective implementation files in the `src/ai_vault_cli/commands` directory.