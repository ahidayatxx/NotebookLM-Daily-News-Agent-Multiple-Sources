# CLAUDE.md

This file provides guidance to Claude Code when working with code in this repository.

## Overview

**nblm-knowledge-engine** is a scaffolding tool. It does NOT run NotebookLM synthesis itself. It generates standalone project repos (as siblings of itself) that each contain their own `pipeline.py`, `stages/`, template, and config — runnable independently.

## Commands

```bash
# Scaffold a new project (default: news-briefing template, English)
python3 pipeline.py --init my-topic

# Pick a template + language
python3 pipeline.py --init glp1-evidence --template pico-synthesis
python3 pipeline.py --init lecture-id --template lecture-summary --lang id

# Custom parent dir (default: sibling of engine repo)
python3 pipeline.py --init my-topic --path ~/repos
```

After scaffolding, the project runs on its own — users do not come back to this engine repo to run it.

## Architecture

- `pipeline.py` — scaffolding tool. Generates `pipeline.py` for new projects, copies `stages/`, copies selected template, creates `sources.md` / `README.md` / `CLAUDE.md` / `SKILL.md` / `.gitignore` / `run.sh` / `output/.gitkeep`.
- `stages/` — reusable pipeline stages. Copied verbatim into every scaffolded project:
  - `source_loader.py` — reads `sources.md`, merges CLI sources, deduplicates
  - `synthesizer.py` — creates notebook, configures chat (mode/length always, persona if provided) BEFORE source upload, adds sources in parallel, auto-cleans sources.md of failures, asks prompt, saves markdown
  - `artifact_generator.py` — generates optional artifacts (podcast, slides, quiz, etc.)
  - `source_validator.py` — removes URLs that failed in NotebookLM from sources.md
- `templates/` — reference prompt templates. One is selected per project via `--template`.
- `nblm-knowledge-engine/SKILL.md` — Claude Code skill.

## What a Scaffolded Project Looks Like

```
projects/<name>/
├── pipeline.py       # Generated with project-specific defaults baked in
├── stages/           # Copied from engine
├── templates/
│   └── <selected>.md # Copied from engine
├── sources.md        # Empty — user adds URLs
├── persona.md        # Optional — user creates to customize chat
├── output/
├── run.sh            # Convenience wrapper
├── README.md
├── CLAUDE.md
└── .gitignore
```

The scaffolded `pipeline.py` supports: `--template`, `--sources`, `--lang`, `--keep`, and artifact flags (`--podcast`, `--slides`, `--quiz`, `--flashcards`, `--infographic`, `--mindmap`, `--report`, `--video`, `--data-table`).

## Key Patterns

- The engine never runs synthesis — it only creates new project repos.
- Each scaffolded project is self-contained and standalone.
- Default scaffolding location is a sibling of the engine: `/Users/ahmadhidayat/claude-code/projects/<name>/`.
- The scaffolded project's `pipeline.py` auto-loads `persona.md` if present.
- Notebooks are disposable by default; use `--keep` to preserve.

## CLI Reference

Full `notebooklm` CLI documentation is at `docs/cli-reference/` (symlink to `../notebooklm-cli-commands-and-arguments/`):

- `notebooklm-cli-help.md` — complete command/option reference (CLI v0.7.1)
- `notebooklm-cli-beyond-web-ui.md` — 14 advanced features not available in the web UI

**Read these before adding or modifying any `notebooklm` CLI calls in `stages/`.**
