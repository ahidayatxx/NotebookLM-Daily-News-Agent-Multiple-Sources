---
name: nblm-knowledge-engine
description: Scaffold standalone NotebookLM synthesis project repos. Creates a new self-contained project directory (with its own pipeline.py, stages, template, sources.md) as a sibling of the engine. Use when user says "scaffold a new NotebookLM project", "create a knowledge engine project", "nblm-knowledge-engine", "new nblm project", "set up a synthesis project", or any request to create a new NotebookLM-based synthesis pipeline for a topic.
---

# nblm-knowledge-engine

A scaffolding tool for standalone NotebookLM synthesis projects. The engine does **not** run synthesis — it generates a new self-contained project directory that the user then runs independently.

## Engine Location

```
/Users/ahmadhidayat/claude-code/projects/nblm-knowledge-engine/
```

## How to Use

### Scaffold a new project

```bash
cd /Users/ahmadhidayat/claude-code/projects/nblm-knowledge-engine
python3 pipeline.py --init <project-name> [--template <name>] [--lang <code>] [--path <path>]
```

### Available Templates

- `news-briefing` — daily news synthesis with top 10 + full briefing (default)
- `pico-synthesis` — clinical evidence analysis using PICO framework
- `lecture-summary` — study guide with concepts, review questions, takeaways
- `research-report` — structured report with exec summary, findings, recommendations

### Examples

```bash
# Default news briefing
python3 pipeline.py --init indonesia-news

# Clinical evidence in English
python3 pipeline.py --init glp1-evidence --template pico-synthesis

# Lecture study guide in Indonesian
python3 pipeline.py --init lecture-week3 --template lecture-summary --lang id
```

## What Gets Created

Scaffolding creates a sibling directory at `/Users/ahmadhidayat/claude-code/projects/<name>/`:

```
<project-name>/
├── pipeline.py              # Generated with project-specific defaults
├── stages/                  # Copied from engine (source_loader, synthesizer, artifact_generator)
├── templates/
│   └── <selected>.md        # Copied from engine
├── sources.md               # Empty — user adds URLs
├── persona.md               # Optional — user creates to customize chat
├── output/                  # Outputs land here
├── run.sh                   # Convenience wrapper
├── README.md, CLAUDE.md, .gitignore
```

## Workflow

When this skill is triggered:

### Step 1 — Resolve parameters with the user

- **Project name**: required, kebab-case (e.g. `indonesia-news`, `glp1-evidence`)
- **Template**: match user intent — `news-briefing` (default), `pico-synthesis` (clinical), `lecture-summary` (study guide), `research-report` (general research)
- **Language**: `en` (default), `id`, or other notebooklm-supported codes
- **Path**: usually default (sibling of engine), override only if user specifies

### Step 2 — Run the scaffolding

```bash
cd /Users/ahmadhidayat/claude-code/projects/nblm-knowledge-engine
python3 pipeline.py --init <name> --template <template> --lang <lang>
```

### Step 3 — Guide next steps

After scaffolding succeeds, tell the user:

1. Edit `<project>/sources.md` to add source URLs
2. (Optional) Create `<project>/persona.md` to customize chat behavior
3. Run: `cd <project> && python3 pipeline.py`
4. (Optional) `git init && git add -A && git commit -m 'initial'` then push to GitHub

### Step 4 — Offer follow-ups

- Offer to pre-fill `sources.md` if the user mentioned specific URLs
- Offer to create `persona.md` if the user described a desired voice/perspective
- Offer to run the project for them right after they confirm sources

## Important Notes

- The engine repo at `/Users/ahmadhidayat/claude-code/projects/nblm-knowledge-engine/` only scaffolds. It does not run synthesis.
- Each scaffolded project is fully standalone — its `pipeline.py` does not import from the engine.
- Default scaffolding location: `/Users/ahmadhidayat/claude-code/projects/<name>/` (sibling of engine).
- To run an existing project, `cd` into it and run its `pipeline.py` directly — do not involve the engine.
