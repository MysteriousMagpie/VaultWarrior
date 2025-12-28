# AI Vault Planning CLI

This project is a command-line interface (CLI) tool designed for managing and interacting with Obsidian-style markdown vaults. It provides functionalities for initializing vaults, indexing markdown files, managing threads, and interacting with AI for planning and retrieval tasks.

## Features
- **Initialization**: Create a new vault with the necessary configuration and directory structure.
- **Indexing**: Build an index of markdown files using embeddings for efficient retrieval.
- **Thread Management**: Create and manage threads for organizing notes and discussions.
- **AI Interaction**: Ask questions and receive answers, chat with the AI, and capture quick notes.
- **Planning**: Generate plans based on threads and summarize information.

## Installation
To install the project, use the following command:

```bash
pip install -e .[dev]
```

## Usage Example
Here are some example commands to get started:

```bash
ai init /path/to/Vault
ai index /path/to/Vault
ai thread new demo --vault-path /path/to/Vault --seed "Kickoff notes"
ai chat demo "What is my next 2-hour task on project X?" --vault-path /path/to/Vault --write
```

Before using the chat or plan commands, set your OpenAI API key:

```bash
export OPENAI_API_KEY=sk-...
```

## Tests
To run the tests for the project, use:

```bash
pytest -q
```

## Roadmap
For a detailed roadmap and future features, refer to the `docs/roadmap.md` file. Future work includes implementing advanced filtering, citation enrichment, and improving the indexing process.