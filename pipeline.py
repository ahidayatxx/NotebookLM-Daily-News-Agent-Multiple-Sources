#!/usr/bin/env python3
"""nblm-knowledge-engine — scaffolds standalone NotebookLM project repos.

The engine does NOT run synthesis itself. It creates a new self-contained
project directory (with its own pipeline.py + stages/ + template + sources.md)
as a sibling of this repo. You then cd into the new project and run it directly.

Usage:
    python3 pipeline.py --init <project-name>
    python3 pipeline.py --init <project-name> --template pico-synthesis
    python3 pipeline.py --init <project-name> --lang id
    python3 pipeline.py --init <project-name> --path /custom/parent/dir
"""

import argparse
import os
import shutil
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECTS_PARENT = os.path.dirname(SCRIPT_DIR)

TEMPLATES_DIR = os.path.join(SCRIPT_DIR, "templates")
AVAILABLE_TEMPLATES = sorted(
    f[:-3] for f in os.listdir(TEMPLATES_DIR) if f.endswith(".md")
)


def log(msg):
    print(f"[*] {msg}", flush=True)


def parse_args():
    p = argparse.ArgumentParser(
        description="Scaffold a standalone NotebookLM project repo",
    )
    p.add_argument(
        "--init",
        required=True,
        metavar="PROJECT_NAME",
        help="Name of the new project (creates a sibling directory under projects/)",
    )
    p.add_argument(
        "--template",
        default="news-briefing",
        choices=AVAILABLE_TEMPLATES,
        help="Template to copy into the new project (default: news-briefing)",
    )
    p.add_argument(
        "--path",
        default=None,
        help="Custom parent directory (default: sibling of this engine repo)",
    )
    p.add_argument(
        "--lang",
        default="en",
        help="Default output language baked into the scaffolded project (default: en)",
    )
    return p.parse_args()


def generate_pipeline_py(project_name, template_name, lang):
    return f'''#!/usr/bin/env python3
"""{project_name} — NotebookLM synthesis pipeline.

Standalone project scaffolded from nblm-knowledge-engine.
Default template: {template_name}
Default language: {lang}
"""

import argparse
import os
import subprocess
import sys

from stages.source_loader import load_sources
from stages.synthesizer import run as synthesize, log
from stages.artifact_generator import generate as generate_artifacts


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_TEMPLATE = os.path.join(SCRIPT_DIR, "templates", "{template_name}.md")
DEFAULT_PERSONA_FILE = os.path.join(SCRIPT_DIR, "persona.md")
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "output")
PROJECT_NAME = "{project_name}"


def parse_args():
    p = argparse.ArgumentParser(description="{project_name} pipeline")
    p.add_argument("--template", default=DEFAULT_TEMPLATE, help="Prompt template .md file")
    p.add_argument("--sources", nargs="*", default=None, help="Additional sources")
    p.add_argument("--lang", default="{lang}", help="Output language")
    p.add_argument("--keep", action="store_true", help="Keep notebook after pipeline")

    p.add_argument("--podcast", action="store_true")
    p.add_argument("--podcast-format", default="deep-dive", choices=["deep-dive", "brief", "critique", "debate"])
    p.add_argument("--slides", action="store_true")
    p.add_argument("--slides-format", default="pdf", choices=["pdf", "pptx"])
    p.add_argument("--quiz", action="store_true")
    p.add_argument("--quiz-format", default="json", choices=["json", "markdown", "html"])
    p.add_argument("--flashcards", action="store_true")
    p.add_argument("--infographic", action="store_true")
    p.add_argument("--mindmap", action="store_true")
    p.add_argument("--report", action="store_true")

    return p.parse_args()


def build_artifact_flags(args):
    flags = {{}}
    if args.podcast:
        flags["podcast"] = {{"format": args.podcast_format}}
    if args.slides:
        flags["slides"] = {{"format": args.slides_format}}
    if args.quiz:
        flags["quiz"] = {{"format": args.quiz_format}}
    if args.flashcards:
        flags["flashcards"] = {{}}
    if args.infographic:
        flags["infographic"] = {{}}
    if args.mindmap:
        flags["mindmap"] = {{}}
    if args.report:
        flags["report"] = {{}}
    return flags


def main():
    args = parse_args()

    template = args.template
    if not os.path.isabs(template):
        template = os.path.join(SCRIPT_DIR, template)
    if not os.path.isfile(template):
        log(f"Error: template not found: {{template}}")
        sys.exit(1)

    sources = load_sources(SCRIPT_DIR, args.sources)
    if not sources:
        log("Error: no sources found. Edit sources.md to add URLs.")
        sys.exit(1)
    log(f"Sources loaded: {{len(sources)}}")

    persona = None
    if os.path.isfile(DEFAULT_PERSONA_FILE):
        with open(DEFAULT_PERSONA_FILE, "r") as f:
            persona = f.read().strip()
        log(f"Loaded persona from {{DEFAULT_PERSONA_FILE}}")

    output_path, notebook_id = synthesize(
        sources=sources,
        template_path=template,
        output_dir=OUTPUT_DIR,
        project_name=PROJECT_NAME,
        lang=args.lang,
        keep=args.keep,
        persona=persona,
    )

    artifact_flags = build_artifact_flags(args)
    if artifact_flags and notebook_id:
        log(f"Generating artifacts: {{', '.join(artifact_flags.keys())}}")
        downloaded = generate_artifacts(notebook_id, OUTPUT_DIR, artifact_flags)
        for path in downloaded:
            log(f"Artifact saved: {{path}}")

    if args.keep:
        log(f"Notebook preserved. ID: {{notebook_id}}")
        log(f"Query directly: notebooklm ask 'your question' -n {{notebook_id}}")
    elif notebook_id:
        log("Deleting temporary notebook...")
        try:
            subprocess.run(
                ["notebooklm", "delete", "-n", notebook_id, "-y"],
                capture_output=True, text=True, check=True,
            )
            log("Notebook deleted.")
        except Exception as e:
            log(f"Warning: could not delete notebook: {{e}}")

    log(f"Done. Output: {{output_path}}")


if __name__ == "__main__":
    main()
'''


def generate_readme(project_name, template_name, lang):
    return f'''# {project_name}

NotebookLM synthesis project scaffolded from [nblm-knowledge-engine](https://github.com/ahidayatxx/nblm-knowledge-engine).

## Quick Start

```bash
pip install notebooklm-py
notebooklm login

# Edit sources.md with your URLs, then:
python3 pipeline.py

# With artifacts + keep notebook
python3 pipeline.py --podcast --keep
```

## Configuration

- **Sources**: edit `sources.md`
- **Template**: `templates/{template_name}.md`
- **Persona** (optional): create `persona.md`
- **Language**: `{lang}` (override with `--lang`)

## CLI Options

| Flag | Description |
|------|-------------|
| `--lang <code>` | Output language (default: `{lang}`) |
| `--sources <url\\|file>...` | Extra sources on top of `sources.md` |
| `--keep` | Keep notebook after pipeline (prints ID) |
| `--podcast` | Generate audio podcast |
| `--slides` | Generate slide deck |
| `--quiz` | Generate quiz |
| `--flashcards` | Generate flashcards |
| `--infographic` | Generate infographic (PNG) |
| `--mindmap` | Generate mind map (JSON) |
| `--report` | Generate report (Markdown) |
'''


def generate_claude_md(project_name, template_name, lang):
    return f'''# CLAUDE.md

## Overview

`{project_name}` — NotebookLM synthesis project. Standalone, scaffolded from nblm-knowledge-engine.

## Commands

```bash
python3 pipeline.py                  # Run synthesis
python3 pipeline.py --podcast --keep # With artifacts, keep notebook
./run.sh                             # Convenience wrapper
```

## Architecture

- `pipeline.py` — orchestrator with project-specific defaults
- `stages/` — reused engine stages (source_loader, synthesizer, artifact_generator)
- `templates/{template_name}.md` — synthesis prompt
- `sources.md` — source URLs
- `persona.md` (optional) — chat persona

## Defaults

- Template: `templates/{template_name}.md`
- Language: `{lang}`
- Output dir: `./output/`
'''


def scaffold(project_name, template_name, parent_path, lang):
    parent = parent_path or PROJECTS_PARENT
    project_dir = os.path.join(parent, project_name)

    if os.path.exists(project_dir):
        log(f"Error: directory already exists: {project_dir}")
        sys.exit(1)

    log(f"Scaffolding project: {project_dir}")
    os.makedirs(project_dir)

    # stages/
    log("Copying stages/...")
    shutil.copytree(
        os.path.join(SCRIPT_DIR, "stages"),
        os.path.join(project_dir, "stages"),
    )

    # templates/<selected>.md
    log(f"Copying template: {template_name}.md")
    os.makedirs(os.path.join(project_dir, "templates"))
    shutil.copy(
        os.path.join(TEMPLATES_DIR, f"{template_name}.md"),
        os.path.join(project_dir, "templates", f"{template_name}.md"),
    )

    # pipeline.py (generated)
    log("Generating pipeline.py...")
    with open(os.path.join(project_dir, "pipeline.py"), "w") as f:
        f.write(generate_pipeline_py(project_name, template_name, lang))

    # sources.md (empty template)
    log("Creating sources.md...")
    with open(os.path.join(project_dir, "sources.md"), "w") as f:
        f.write(
            f"# {project_name} Sources\n\n"
            "<!-- Add URLs below, one per line. Markdown links or bare URLs. -->\n"
        )

    # run.sh wrapper
    log("Creating run.sh...")
    with open(os.path.join(project_dir, "run.sh"), "w") as f:
        f.write(
            "#!/bin/bash\n"
            'cd "$(dirname "$0")"\n'
            'python3 pipeline.py "$@"\n'
        )
    os.chmod(os.path.join(project_dir, "run.sh"), 0o755)

    # README.md
    log("Creating README.md...")
    with open(os.path.join(project_dir, "README.md"), "w") as f:
        f.write(generate_readme(project_name, template_name, lang))

    # CLAUDE.md
    log("Creating CLAUDE.md...")
    with open(os.path.join(project_dir, "CLAUDE.md"), "w") as f:
        f.write(generate_claude_md(project_name, template_name, lang))

    # .gitignore
    log("Creating .gitignore...")
    with open(os.path.join(project_dir, ".gitignore"), "w") as f:
        f.write(
            "__pycache__/\n"
            "*.pyc\n"
            ".venv/\n"
            "*.egg-info/\n"
            "dist/\n"
            ".DS_Store\n"
            "output/*\n"
            "!output/.gitkeep\n"
        )

    # output/.gitkeep
    os.makedirs(os.path.join(project_dir, "output"))
    open(os.path.join(project_dir, "output", ".gitkeep"), "w").close()

    log("")
    log(f"SUCCESS: Project scaffolded at {project_dir}")
    log("")
    log("Next steps:")
    log(f"  1. Edit {project_dir}/sources.md to add your source URLs")
    log(f"  2. (Optional) Create {project_dir}/persona.md to customize chat behavior")
    log(f"  3. Run: cd {project_dir} && python3 pipeline.py")
    log(f"  4. (Optional) git init && git add -A && git commit -m 'initial'")


def main():
    args = parse_args()
    scaffold(args.init, args.template, args.path, args.lang)


if __name__ == "__main__":
    main()
