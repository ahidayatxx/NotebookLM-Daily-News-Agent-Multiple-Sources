---
description: Run the NotebookLM Knowledge Engine pipeline — synthesize sources, generate briefings, create artifacts. Use when user says "run knowledge engine", "synthesize sources", "generate briefing", "nblm pipeline", "make a podcast from", "PICO synthesis", "study guide from", or any request combining NotebookLM with knowledge management, evidence synthesis, or content generation.
---

# NotebookLM Knowledge Engine

A general-purpose knowledge management pipeline built on notebooklm-py. Creates a disposable NotebookLM notebook, ingests sources, synthesizes knowledge, optionally generates artifacts (podcast, slides, quiz, etc.), saves output, and cleans up.

## Pipeline Location

```
/Users/ahmadhidayat/claude-code/projects/NotebookLM-Daily-News-Agent-Multiple-Sources/
```

## How to Run

### Via Claude Code (skill mode — you are here)

1. Resolve what the user wants:
   - **Project**: look for a matching directory under `projects/`, or ask the user to specify `--project <path>`
   - **Template**: match user intent to a template in `templates/`, or use `--template <path>` if specified
   - **Extra sources**: if the user provides URLs or file paths in conversation, pass them via `--sources`
   - **Artifacts**: if user mentions podcast, slides, quiz, etc., add the corresponding flags

2. Build and run the CLI command:

```bash
cd /Users/ahmadhidayat/claude-code/projects/NotebookLM-Daily-News-Agent-Multiple-Sources
python pipeline.py --project ./projects/<project-name> [options]
```

### CLI Options

| Flag | Description |
|------|-------------|
| `--project <path>` | Project directory (required). Must contain `sources.md` |
| `--template <path>` | Prompt template file. Default: auto-detected or `templates/news-briefing.md` |
| `--sources <url\|file>...` | Additional sources merged with project's `sources.md` |
| `--lang <code>` | Output language (e.g., `en`, `id`). Default: `en` |
| `--keep` | Keep the notebook after pipeline (prints notebook ID) |
| `--podcast` | Generate audio podcast (MP3) |
| `--podcast-format <fmt>` | Podcast format: `deep-dive` (default), `brief`, `critique`, `debate` |
| `--slides` | Generate slide deck |
| `--slides-format <fmt>` | Slides format: `pdf` (default), `pptx` |
| `--quiz` | Generate quiz |
| `--quiz-format <fmt>` | Quiz format: `json` (default), `markdown`, `html` |
| `--flashcards` | Generate flashcards |
| `--infographic` | Generate infographic (PNG) |
| `--mindmap` | Generate mind map (JSON) |
| `--report` | Generate report (Markdown) |

### Examples

```bash
# Basic news briefing
python pipeline.py --project ./projects/indonesia-news

# PICO synthesis with podcast
python pipeline.py --project ./projects/glp1-evidence --template ./templates/pico-synthesis.md --podcast

# Ad-hoc sources, keep notebook, generate slides
python pipeline.py --project ./projects/clinical-guidelines --sources https://pubmed/123 ./paper.pdf --keep --slides

# Lecture study guide in Indonesian
python pipeline.py --project ./projects/lecture-week3 --template ./templates/lecture-summary.md --lang id --quiz
```

## Workflow

When this skill is triggered, follow these steps:

### Step 1 — Verify notebooklm connectivity

```bash
which notebooklm || uv tool install notebooklm-py
notebooklm list --json
```

If auth fails, run `notebooklm login --fresh` and re-check.

### Step 2 — Resolve parameters

- Match user request to a project directory under `projects/`
- Match user intent to a template in `templates/`
- Collect any extra sources from the conversation
- Note any artifact requests (podcast, slides, etc.)

### Step 3 — Run the pipeline

```bash
cd /Users/ahmadhidayat/claude-code/projects/NotebookLM-Daily-News-Agent-Multiple-Sources
python pipeline.py --project ./projects/<name> --template ./templates/<template>.md [artifact flags]
```

### Step 4 — Present results

- Read the output markdown file
- Summarize key findings for the user
- If artifacts were generated, list their file paths
- If `--keep` was used, remind user of the notebook ID for later reuse

### Step 5 — Offer follow-ups

- Suggest artifact generation if none were requested
- Offer to create a new template if the user has a recurring use case
- Offer to set up a new project directory for a new topic

## Templates

Templates are plain markdown files in `templates/`. The entire file content is the prompt sent to NotebookLM.

To create a new template, add a `.md` file to `templates/` with the synthesis prompt.

## Projects

Each project is a directory under `projects/` with a `sources.md` file listing source URLs (one per line, markdown links or bare URLs).

To create a new project:
```bash
mkdir -p projects/<name>/output
# Edit projects/<name>/sources.md with source URLs
```

## Important Notes

- Always use full notebook IDs from `--json` output, never truncated IDs
- The pipeline creates and deletes disposable notebooks by default — use `--keep` to preserve
- Source processing takes time (30s–3min depending on source count); the pipeline polls until ready
- Artifact generation is asynchronous; the pipeline waits for completion before downloading
- Language setting is global to the notebooklm account — the pipeline saves and restores it
