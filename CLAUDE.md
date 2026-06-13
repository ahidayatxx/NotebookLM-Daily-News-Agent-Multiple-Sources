# CLAUDE.md

This file provides guidance to Claude Code when working with code in this repository.

## Overview

NotebookLM Knowledge Engine — a general-purpose pipeline that ingests multi-format sources, synthesizes knowledge via Google NotebookLM, and optionally generates artifacts (podcasts, slides, quizzes, etc.). Built on notebooklm-py.

## Commands

```bash
# Run the pipeline
python pipeline.py --project ./projects/<name> --template ./templates/<template>

# With artifacts
python pipeline.py --project ./projects/<name> --podcast --slides

# Verify notebooklm connectivity
notebooklm list --json

# Authenticate
notebooklm login
```

## Architecture

- `pipeline.py` — CLI orchestrator, parses args, calls stages in sequence
- `stages/source_loader.py` — reads `sources.md`, merges CLI sources, deduplicates
- `stages/synthesizer.py` — creates notebook, adds sources (parallel), polls readiness, asks prompt, saves markdown
- `stages/artifact_generator.py` — generates optional artifacts based on flags
- `templates/` — plain markdown prompt files
- `projects/` — one directory per topic, each with `sources.md` and `output/`

## Skill

`nblm-knowledge-engine.md` is the Claude Code skill. Install to `~/.claude/skills/` for conversational use.

## Key Patterns

- NotebookLM notebooks are **disposable by default** (create → use → delete). Use `--keep` to preserve.
- Always use full notebook IDs from `--json` output, never truncated.
- Language setting is global — the pipeline saves/restores it automatically.
- Source adding uses parallel ThreadPoolExecutor with retry logic.
- Artifacts are generated after synthesis, sequentially.
