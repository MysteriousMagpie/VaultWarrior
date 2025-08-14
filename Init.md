Build a production-ready, vault-aware Python CLI called ai for iterative planning with Retrieval-Augmented Generation (RAG). It must integrate with an Obsidian vault, keep long-running “threads,” retrieve context from markdown notes, and write updates back to the vault. Ship a complete repo.

Stack
Python 3.11+

CLI: typer, output: rich

Embeddings: sentence-transformers (local), index: faiss

LLM: OpenAI (configurable model); clean abstraction so I can swap backends later

Config: pyyaml

Optional: watchfiles for live reindex; gitpython for history snapshots

Core Features (Must Have)
Indexing

Scan vault_path for *.md (exclude /.obsidian/, /_ai/).

Chunk size ~1200 chars, 200 overlap. Persist FAISS + metadata (file, chunk_id, start/end offsets, headings).

Command: ai index (full) and ai index --watch (incremental via file watcher).

RAG Retrieval

Embed queries locally; cosine sim; return top-k (configurable).

Map results to precise file paths and char ranges so responses can cite like [file.md §H2 lines 120–210].

Provide a --filters option (by path glob, tag inferred from frontmatter, or folder).

Threads (Continuity)

Store conversations in vault/_ai/threads/<slug>.md with YAML frontmatter:

yaml
Copy
Edit
thread_id: <slug>
status: active
context_links: [ "[[projects/evoagentX/README]]", "#tag" ]
review_cadence: weekly
Append timestamped entries:

**YYYY-MM-DD HH:MM — user**

**YYYY-MM-DD HH:MM — assistant**

Commands:

ai thread new <slug> [--seed "text"]

ai chat <slug> "message" → RAG + prior thread summary + streaming response; append both sides.

ai plan <slug> --weekly → generate a compact weekly checkpoint (wins, blockers, next 3 tasks), append.

One-off Q&A

ai ask "question" → RAG answer with inline numbered citations; no writeback unless --write.

Capture

ai capture "thought" → appends to daily/YYYY-MM-DD.md under a “⚡ Captures” heading; reindex touched files.

Privacy & Safety
Local embeddings only (no remote vector DB).

Redaction pass before LLM: configurable regex list (API keys, IDs, etc.).

Write policies:

Default read-only; require --write to modify anything outside _ai/threads and daily/.

Denylist/allowlist from config.

Streaming + UX
Stream assistant tokens to terminal (no color styles hardcoded in output text; use rich for live rendering).

On finish, print a compact Sources section listing cited files with ranges.

Git Integration (Nice to Have, but include)
If the vault is a git repo, on --write operations:

Stage changed files.

Create commit: ai:<command> <target> (#chunks=<n>).

Optional flag --no-commit to skip.

Cron-style Auto Indexing
Provide a lightweight ai daemon command that:

Watches the vault for file changes and incrementally updates the FAISS index.

Logs to vault/_ai/logs/daemon.log.

Config (vault/_ai/config.yaml)
yaml
Copy
Edit
vault_path: "/abs/path/to/Vault"
provider:
  type: openai
  model: "gpt-4.1-mini"
  api_key_env: "OPENAI_API_KEY"
rag:
  embed_model: "sentence-transformers/all-MiniLM-L6-v2"
  chunk_chars: 1200
  chunk_overlap: 200
  top_k: 8
  exclude_globs: ["_ai/**", ".obsidian/**"]
writeback:
  thread_dir: "_ai/threads"
  default_target: "daily"
  allow_globs: ["daily/**", "_ai/threads/**", "projects/**"]
privacy:
  redact:
    - "(?i)passport\\s*\\d+"
    - "(?i)api[_-]?key\\s*[:=]\\s*\\S+"
git:
  auto_commit: true
  message_template: "ai:{command} {target} (k={k})"
CLI Commands (exact)
ai init

ai index [--watch]

ai thread new <slug> [--seed "text"]

ai chat <slug> "message" [--write] [--filters path_glob...]

ai ask "question" [--filters path_glob...]

ai capture "text" [--write]

ai plan <slug> --weekly [--write]

ai daemon (watch & incrementally index)

ai doctor (sanity checks: config present, index present, API key, git status)

Implementation Notes
Modularize: core/config.py, core/index.py, core/retrieve.py, core/llm.py, core/threads.py, core/writeback.py, core/gitwrap.py, cli.py.

Precise citations: store (file, chunk_id, start, end, heading); render citations like [1] path/to/file.md §Heading (chars 12,340–13,100).

Summarize prior thread content to ~2–3k chars before each LLM call (sliding window); keep full history in file.

Add tests for chunking, retrieval order, citation formatting, and redaction.

Output
Full repo with:

pyproject.toml (or requirements.txt)

cli.py (entry via python -m ai or console script)

core/*.py modules

Example _ai/config.yaml

README.md with setup, env vars, commands, and examples

Basic tests in tests/

Success Criteria: ai init → ai index → ai thread new demo → ai chat demo "What’s my next 2-hour task on project X?" --write should:

Retrieve relevant chunks with citations,

stream a grounded answer,

append both sides to _ai/threads/demo.md,

auto-commit if git is enabled.