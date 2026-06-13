#!/usr/bin/env python3
"""NotebookLM Knowledge Engine — pipeline orchestrator.

Usage:
    python pipeline.py --project ./projects/indonesia-news
    python pipeline.py --project ./projects/glp1-evidence --template ./templates/pico-synthesis.md --podcast
    python pipeline.py --project ./projects/indonesia-news --sources https://extra.com ./paper.pdf --keep --slides
"""

import argparse
import os
import subprocess
import sys

from stages.source_loader import load_sources
from stages.synthesizer import run as synthesize, log
from stages.artifact_generator import generate as generate_artifacts


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_TEMPLATE = os.path.join(SCRIPT_DIR, "templates", "news-briefing.md")


def parse_args():
    p = argparse.ArgumentParser(description="NotebookLM Knowledge Engine pipeline")
    p.add_argument("--project", required=True, help="Path to project directory")
    p.add_argument("--template", default=None, help="Path to prompt template .md file")
    p.add_argument("--sources", nargs="*", default=None, help="Additional URLs or file paths")
    p.add_argument("--lang", default="en", help="Output language code (default: en)")
    p.add_argument("--keep", action="store_true", help="Keep notebook after pipeline (prints ID)")

    # Artifact flags
    p.add_argument("--podcast", action="store_true", help="Generate audio podcast")
    p.add_argument("--podcast-format", default="deep-dive", choices=["deep-dive", "brief", "critique", "debate"])
    p.add_argument("--slides", action="store_true", help="Generate slide deck")
    p.add_argument("--slides-format", default="pdf", choices=["pdf", "pptx"])
    p.add_argument("--quiz", action="store_true", help="Generate quiz")
    p.add_argument("--quiz-format", default="json", choices=["json", "markdown", "html"])
    p.add_argument("--flashcards", action="store_true", help="Generate flashcards")
    p.add_argument("--infographic", action="store_true", help="Generate infographic")
    p.add_argument("--mindmap", action="store_true", help="Generate mind map")
    p.add_argument("--report", action="store_true", help="Generate report")

    return p.parse_args()


def build_artifact_flags(args):
    flags = {}
    if args.podcast:
        flags["podcast"] = {"format": args.podcast_format}
    if args.slides:
        flags["slides"] = {"format": args.slides_format}
    if args.quiz:
        flags["quiz"] = {"format": args.quiz_format}
    if args.flashcards:
        flags["flashcards"] = {}
    if args.infographic:
        flags["infographic"] = {}
    if args.mindmap:
        flags["mindmap"] = {}
    if args.report:
        flags["report"] = {}
    return flags


def main():
    args = parse_args()

    # Resolve project directory
    project_dir = args.project
    if not os.path.isabs(project_dir):
        project_dir = os.path.join(SCRIPT_DIR, project_dir)
    project_dir = os.path.abspath(project_dir)

    if not os.path.isdir(project_dir):
        log(f"Error: project directory not found: {project_dir}")
        sys.exit(1)

    project_name = os.path.basename(project_dir)
    output_dir = os.path.join(project_dir, "output")

    # Resolve template
    template = args.template or DEFAULT_TEMPLATE
    if not os.path.isabs(template):
        template = os.path.join(SCRIPT_DIR, template)
    if not os.path.isfile(template):
        log(f"Error: template not found: {template}")
        sys.exit(1)

    # Load sources
    log(f"Loading sources from project: {project_name}")
    sources = load_sources(project_dir, args.sources)
    if not sources:
        log("Error: no sources found. Add URLs to projects/<name>/sources.md or pass --sources")
        sys.exit(1)
    log(f"Sources loaded: {len(sources)}")

    # Run synthesis
    output_path, notebook_id = synthesize(
        sources=sources,
        template_path=template,
        output_dir=output_dir,
        project_name=project_name,
        lang=args.lang,
        keep=args.keep,
    )

    # Generate artifacts
    artifact_flags = build_artifact_flags(args)
    if artifact_flags and notebook_id:
        log(f"Generating artifacts: {', '.join(artifact_flags.keys())}")
        downloaded = generate_artifacts(notebook_id, output_dir, artifact_flags)
        for path in downloaded:
            log(f"Artifact saved: {path}")

    # Cleanup
    if args.keep:
        log(f"Notebook preserved. ID: {notebook_id}")
        log(f"Reuse with: python pipeline.py --project {args.project} --sources <existing notebook sources>")
        log(f"Or query directly: notebooklm ask 'your question' -n {notebook_id}")
    elif notebook_id:
        log("Deleting temporary notebook...")
        try:
            subprocess.run(
                ["notebooklm", "delete", "-n", notebook_id, "-y"],
                capture_output=True, text=True, check=True,
            )
            log("Notebook deleted.")
        except Exception as e:
            log(f"Warning: could not delete notebook: {e}")

    log(f"Done. Output: {output_path}")


if __name__ == "__main__":
    main()
