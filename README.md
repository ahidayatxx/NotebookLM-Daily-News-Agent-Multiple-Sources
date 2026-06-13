# NotebookLM Knowledge Engine

A general-purpose knowledge management pipeline built on [notebooklm-py](https://github.com/teng-lin/notebooklm-py). Ingests multi-format sources, synthesizes knowledge via Google NotebookLM, and optionally generates artifacts (podcasts, slides, quizzes, infographics, mind maps, flashcards, reports).

## How It Works

1. **Load sources** from a project's `sources.md` + optional CLI arguments
2. **Create a disposable NotebookLM notebook**, bulk-add all sources
3. **Synthesize** using a prompt template (news briefing, PICO analysis, study guide, etc.)
4. **Optionally generate artifacts** — podcast, slides, quiz, infographic, etc.
5. **Save markdown + artifacts** to the project's `output/` directory
6. **Clean up** (or keep the notebook with `--keep`)

## Quick Start

```bash
# Install notebooklm-py
pip install notebooklm-py

# Authenticate
notebooklm login

# Run with the example project
python pipeline.py --project ./projects/_example --template ./templates/news-briefing

# Generate a podcast too
python pipeline.py --project ./projects/_example --template ./templates/news-briefing --podcast

# Keep the notebook for later queries
python pipeline.py --project ./projects/_example --keep
```

## CLI Reference

| Flag | Description |
|------|-------------|
| `--project <path>` | Project directory (required). Must contain `sources.md` |
| `--template <path>` | Prompt template file |
| `--sources <url\|file>...` | Additional sources merged with `sources.md` |
| `--lang <code>` | Output language (default: `en`) |
| `--keep` | Keep notebook after pipeline (prints ID for reuse) |
| `--podcast` | Generate audio podcast (MP3) |
| `--podcast-format` | `deep-dive` (default), `brief`, `critique`, `debate` |
| `--slides` | Generate slide deck (PDF or PPTX) |
| `--slides-format` | `pdf` (default) or `pptx` |
| `--quiz` | Generate quiz |
| `--quiz-format` | `json` (default), `markdown`, `html` |
| `--flashcards` | Generate flashcards |
| `--infographic` | Generate infographic (PNG) |
| `--mindmap` | Generate mind map (JSON) |
| `--report` | Generate report (Markdown) |

## Creating a New Project

```bash
mkdir -p projects/my-topic/output
cat > projects/my-topic/sources.md << 'EOF'
# My Topic Sources
https://example.com/article1
https://example.com/article2
./local-paper.pdf
EOF
```

Then run:
```bash
python pipeline.py --project ./projects/my-topic --template ./templates/research-report
```

## Creating a New Template

Add a `.md` file to `templates/`. The entire file content is sent as the prompt to NotebookLM.

Example `templates/my-template.md`:
```markdown
Analyze all sources and:
1. Identify the top 3 key findings
2. Explain their significance
3. Recommend next steps
```

## Built-in Templates

| Template | Use Case |
|----------|----------|
| `news-briefing` | Daily news synthesis with top 10 + full briefing |
| `pico-synthesis` | Clinical evidence analysis using PICO framework |
| `lecture-summary` | Study guide with concepts, review questions, takeaways |
| `research-report` | Structured report with exec summary, findings, recommendations |

## Claude Code Skill

This repo includes a Claude Code skill (`nblm-knowledge-engine.md`) that lets you run the pipeline conversationally. To install:

```bash
cp nblm-knowledge-engine.md ~/.claude/skills/
```

Then in Claude Code:
- "run the knowledge engine for indonesia news"
- "synthesize these sources using PICO template"
- "generate a podcast from the clinical guidelines project"

## Architecture

```
pipeline.py              # CLI orchestrator
stages/
├── source_loader.py     # Resolve sources from config + CLI
├── synthesizer.py       # Notebook CRUD, source ingestion, synthesis
└── artifact_generator.py # Optional artifact generation
templates/               # Prompt files (plain markdown)
projects/                # One directory per topic
```

## Requirements

- Python 3.10+
- [notebooklm-py](https://pypi.org/project/notebooklm-py/)
- Authenticated Google account (`notebooklm login`)

## License

MIT
