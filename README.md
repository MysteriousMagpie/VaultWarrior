# AI Vault Planning CLI (early scaffold)

This is an early scaffold implementing core building blocks for a vault-aware RAG assistant CLI `ai` for Obsidian-style markdown vaults.

## Features (implemented so far)
- `ai init <vault_path>` creates `_ai/config.yaml`, thread, and daily directories.
- `ai index <vault_path>` builds FAISS embeddings index (sentence-transformers) over markdown files.
- `ai thread new <slug>` creates a new thread file with frontmatter.
- `ai ask "question"` performs retrieval and prints citation list.
- `ai chat <slug> "message" --write` streams an OpenAI answer (requires API key) and appends to thread.
- `ai capture "text" --write` appends quick capture to the daily note.
- `ai plan <slug> --weekly --write` produces a checkpoint summary (placeholder prompt) and appends.
- `ai doctor` basic sanity checks (presence of config and index).

## Not Yet Implemented
- Watch / incremental indexing (`ai index --watch`, `ai daemon`).
- Advanced filters (frontmatter tags, globs) beyond placeholders.
- Robust error handling & rate limiting.
- Model backend abstraction beyond OpenAI placeholder.

## Install (dev)
```bash
pip install -e .[dev]
```

## Usage Example
```bash
ai init /path/to/Vault
ai index /path/to/Vault
ai thread new demo --vault-path /path/to/Vault --seed "Kickoff notes"
ai chat demo "What is my next 2-hour task on project X?" --vault-path /path/to/Vault --write
```

Set your environment variable for OpenAI before chat / plan:
```bash
export OPENAI_API_KEY=sk-...
```

## Tests
```bash
pytest -q
```

## Roadmap
See `Init.md` for full specification; remaining work includes daemon, advanced filtering, citation enrichment, thread summarization windowing, write policy enforcement, and git auto-commit improvements.
