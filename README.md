# nblm-knowledge-engine

A scaffolding tool for standalone NotebookLM synthesis projects built on [notebooklm-py](https://github.com/teng-lin/notebooklm-py). The engine does **not** run synthesis itself — it generates a new self-contained project directory that you then run independently.

## How It Works

```bash
python3 pipeline.py --init my-topic
```

This creates a **sibling directory** at `../my-topic/` with everything needed to run:

```
projects/my-topic/
├── pipeline.py              # Generated with project-specific defaults
├── stages/                  # Copied from engine
├── templates/
│   └── news-briefing.md     # Copied from engine (selectable)
├── sources.md               # Empty — you add URLs
├── persona.md               # Optional — you create to customize chat
├── output/                  # Generated outputs land here
├── run.sh                   # Convenience wrapper
├── README.md, CLAUDE.md, .gitignore
```

Then:
```bash
cd ../my-topic
# Edit sources.md with your URLs
python3 pipeline.py
```

## Scaffolding Options

| Flag | Description |
|------|-------------|
| `--init <name>` | Name of the new project (required) |
| `--template <name>` | Template to copy (default: `news-briefing`) |
| `--lang <code>` | Default output language baked into the project (default: `en`) |
| `--path <path>` | Custom parent directory (default: sibling of engine) |

## Available Templates

| Template | Use Case |
|----------|----------|
| `news-briefing` | Daily news synthesis with top 10 + full briefing |
| `pico-synthesis` | Clinical evidence analysis using PICO framework |
| `lecture-summary` | Study guide with concepts, review questions, takeaways |
| `research-report` | Structured report with exec summary, findings, recommendations |

## Examples

```bash
# Default news briefing project in English
python3 pipeline.py --init indonesia-news

# Clinical evidence project in English
python3 pipeline.py --init glp1-evidence --template pico-synthesis

# Lecture study guide in Indonesian
python3 pipeline.py --init lecture-week3 --template lecture-summary --lang id

# Custom parent directory
python3 pipeline.py --init my-topic --path ~/repos
```

## Architecture

```
nblm-knowledge-engine/
├── pipeline.py              # Scaffolding tool (entry point)
├── stages/                  # Copied verbatim into each new project
│   ├── source_loader.py
│   ├── synthesizer.py
│   └── artifact_generator.py
├── templates/               # Reference templates (one copied per project)
│   ├── news-briefing.md
│   ├── pico-synthesis.md
│   ├── lecture-summary.md
│   └── research-report.md
└── nblm-knowledge-engine/
    └── SKILL.md             # Claude Code skill
```

## Why Scaffold Instead of Run?

Each project becomes independently runnable, version-controllable, and customizable without touching the engine. The engine stays a clean tool; projects own their configs, templates, and outputs. Pattern proven by [`health-mgmt-consultant-id`](https://github.com/ahidayatxx/health-mgmt-consultant-id).

## Claude Code Skill

Install the skill for conversational use:
```bash
cp -r nblm-knowledge-engine ~/.claude/skills/
```

Then in Claude Code: "scaffold a new NotebookLM project for X".

## Requirements

- Python 3.10+
- [notebooklm-py](https://pypi.org/project/notebooklm-py/) (needed by scaffolded projects at run time)

## License

MIT
