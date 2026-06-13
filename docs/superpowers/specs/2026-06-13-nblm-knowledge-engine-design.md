# NotebookLM Knowledge Engine — Design Spec

**Date:** 2026-06-13
**Status:** Approved
**Repo:** `projects/NotebookLM-Daily-News-Agent-Multiple-Sources/`

## Problem

notebooklm-py enables programmatic access to Google NotebookLM's full capability set — multi-source ingestion, AI synthesis, and artifact generation (audio, video, slides, quizzes, etc.). Currently only the news briefing use case is implemented. A general-purpose knowledge engine can serve healthcare evidence synthesis, education/training content, content creation, and research workflows from the same pipeline.

## Design Principle

**Skill-first, CLI-second.** Build the pipeline as a Claude Code skill first. When the workflow matures, extract the logic into standalone Python scripts that run without Claude Code. The skill becomes a thin wrapper — or gets dropped entirely in favor of the CLI.

## Architecture

```
projects/NotebookLM-Daily-News-Agent-Multiple-Sources/
├── nblm-knowledge-engine.md      # Claude Code skill definition
├── pipeline.py                   # CLI entry point (matures later)
├── stages/
│   ├── __init__.py
│   ├── source_loader.py          # Resolve sources (config file + CLI)
│   ├── synthesizer.py            # Create notebook, add sources, ask, save markdown
│   └── artifact_generator.py     # Generate optional artifacts (podcast, slides, etc.)
├── templates/                    # External prompt files
│   ├── news-briefing.md
│   ├── pico-synthesis.md
│   ├── lecture-summary.md
│   └── research-report.md
├── projects/                     # One directory per topic/domain
│   └── _example/
│       ├── sources.md
│       └── output/
├── requirements.txt
├── CLAUDE.md
├── README.md
└── .gitignore
```

## Claude Code Skill

**Skill name:** `nblm-knowledge-engine`
**Location:** `nblm-knowledge-engine.md` (checked into repo, installable to `~/.claude/skills/`)

### Skill behavior

When the user says things like "run the knowledge engine", "synthesize my sources", "generate a briefing from these URLs", or "create a podcast from these papers", the skill:

1. **Resolves the project** — from explicit `--project` arg, or by matching keywords to a project directory
2. **Loads sources** — reads `sources.md` from the project, merges with any ad-hoc URLs/files the user provides in the conversation
3. **Selects a template** — from explicit `--template` arg, or infers from the project name / user intent
4. **Runs the pipeline** — calls `pipeline.py` via Bash with the assembled arguments
5. **Reports results** — reads the output file and presents key findings
6. **Offers follow-ups** — suggests artifact generation (podcast, slides, quiz) if not already done

### Skill triggers

- "run knowledge engine", "nblm pipeline", "synthesize sources"
- "generate briefing", "run PICO synthesis", "create study guide"
- "make a podcast from these papers", "generate slides from report"
- Any request combining NotebookLM with knowledge management, evidence synthesis, or content generation

## Pipeline Stages

### `source_loader.py`

**Input:** project directory path + optional CLI sources
**Output:** list of dicts `[{url, type}, ...]`

- Reads `sources.md` from project directory
- Parses markdown links, bare URLs, and local file paths
- Merges with `--sources` CLI arguments
- Deduplicates by URL/path
- Validates URLs are reachable (optional, flag-controlled)

### `synthesizer.py`

**Input:** sources list + template path + language + project output dir
**Output:** path to saved markdown file

- Creates a disposable NotebookLM notebook with descriptive title
- Adds all sources in parallel (ThreadPoolExecutor, max 5 workers, retry x3)
- Polls source readiness (configurable timeout, default 180s)
- Reads the template prompt file
- Sends prompt via `notebooklm ask`
- Post-processes response: strip citation markers `[1]`, conversation artifacts, leading "Answer:"
- Saves to `output/<project-name>-<date>.md`

### `artifact_generator.py`

**Input:** notebook ID + artifact flags + output dir
**Output:** list of downloaded artifact paths

- Accepts flags: `--podcast`, `--slides`, `--quiz`, `--infographic`, `--mindmap`, `--flashcards`, `--report`
- Generates each requested artifact
- Waits for completion per artifact
- Downloads to output directory
- Supports format options: `--podcast-format deep-dive|brief|critique|debate`, `--slides-format pdf|pptx`, `--quiz-format json|markdown|html`

### `pipeline.py` (orchestrator)

- Parses all CLI arguments
- Calls source_loader → synthesizer → artifact_generator in sequence
- Handles `--keep` (skip notebook deletion, print notebook ID)
- Handles `--lang` (save/restore language setting)
- Handles `--project` (resolve project directory)
- Error handling with cleanup (delete notebook on failure unless `--keep`)

## CLI Interface

```bash
# Basic run
python pipeline.py --project ./projects/indonesia-news

# With artifacts
python pipeline.py --project ./projects/indonesia-news --podcast --slides

# Ad-hoc sources
python pipeline.py --project ./projects/indonesia-news --sources https://... ./paper.pdf

# Keep notebook
python pipeline.py --project ./projects/indonesia-news --keep

# Override template
python pipeline.py --project ./projects/indonesia-news --template ./templates/custom.md

# Language
python pipeline.py --project ./projects/indonesia-news --lang id
```

## Template Format

Plain markdown files in `templates/`. No YAML frontmatter, no placeholders. The entire file content is sent as the prompt to `notebooklm ask`.

Users create new templates by adding a `.md` file to `templates/`.

## Project Directory Format

Each topic/domain gets a directory under `projects/`:

```
projects/indonesia-news/
├── sources.md       # One URL/file path per line (markdown links or bare URLs)
└── output/          # Generated outputs land here
```

`sources.md` format:
```markdown
# Indonesia News Sources
https://www.kompas.com
https://www.thejakartapost.com
[BBC Indonesia](https://www.bbc.com/indonesia)
```

## Reuse from Existing News Pipeline

- Parallel source-add with retry (`add_source` pattern)
- Source readiness polling (`check_sources_ready` pattern)
- Citation cleanup regex
- Conversation artifact cleanup regex
- Language save/restore pattern
- Timezone-aware filename generation

## Evolution Path

1. **Phase 1 (now):** Claude Code skill + Python pipeline scripts
2. **Phase 2:** As templates and projects stabilize, extract common patterns into shared utilities
3. **Phase 3:** Mature CLI that runs independently; skill becomes optional wrapper

## Dependencies

- `notebooklm-py` (installed via pip/uv)
- `notebooklm` CLI available in PATH (for subprocess calls)
- Python 3.10+
