#!/usr/bin/env python3
"""Generate and download optional NotebookLM artifacts."""

import os
import subprocess
import time


def log(msg):
    print(f"[*] {msg}", flush=True)


def _run_cmd(cmd):
    """Run a notebooklm CLI command, raise on failure."""
    subprocess.run(cmd, capture_output=True, text=True, check=True)


def _wait_and_download(notebook_id, artifact_type, download_path, timeout=300):
    """Wait for the latest artifact of a type to finish, then download."""
    poll_cmd = ["notebooklm", "artifact", "list", "--json", "-n", notebook_id]
    start = time.time()

    while time.time() - start < timeout:
        try:
            result = subprocess.run(poll_cmd, capture_output=True, text=True, check=True)
            import re, json
            json_match = re.search(r'\{.*\}', result.stdout, re.DOTALL)
            if not json_match:
                time.sleep(10)
                continue

            data = json.loads(json_match.group(0))
            artifacts = data.get("artifacts", [])
            # Find latest artifact of the matching type
            matching = [
                a for a in artifacts
                if artifact_type.lower() in a.get("type", "").lower()
                or artifact_type.lower() in a.get("title", "").lower()
            ]
            if not matching:
                time.sleep(10)
                continue

            latest = matching[-1]
            status = latest.get("status", "").lower()
            if status == "complete" or status == "ready":
                log(f"Artifact {artifact_type} is ready, downloading...")
                return True
            elif status == "failed":
                log(f"Artifact {artifact_type} generation failed")
                return False
            else:
                log(f"Artifact {artifact_type} status: {status}")

        except Exception as e:
            log(f"Warning checking artifact status: {e}")

        time.sleep(10)

    log(f"Timeout waiting for {artifact_type}")
    return False


def generate(notebook_id, output_dir, flags):
    """Generate artifacts based on flags dict. Returns list of downloaded file paths.

    flags is a dict like:
        {"podcast": {"format": "deep-dive"}, "slides": {"format": "pdf"}, "quiz": {"format": "json"}}
    """
    downloaded = []

    for artifact_type, options in flags.items():
        try:
            log(f"Generating {artifact_type}...")

            if artifact_type == "podcast":
                fmt = options.get("format", "deep-dive")
                _run_cmd([
                    "notebooklm", "generate", "audio",
                    f"make it {fmt}", "--wait", "-n", notebook_id,
                ])
                path = os.path.join(output_dir, "podcast.mp3")
                _run_cmd(["notebooklm", "download", "audio", path, "-n", notebook_id])
                downloaded.append(path)

            elif artifact_type == "slides":
                fmt = options.get("format", "pdf")
                _run_cmd([
                    "notebooklm", "generate", "slide-deck", "-n", notebook_id,
                ])
                ext = "pptx" if fmt == "pptx" else "pdf"
                path = os.path.join(output_dir, f"slides.{ext}")
                _run_cmd([
                    "notebooklm", "download", "slide-deck", path, "-n", notebook_id,
                ])
                downloaded.append(path)

            elif artifact_type == "quiz":
                fmt = options.get("format", "json")
                _run_cmd([
                    "notebooklm", "generate", "quiz", "-n", notebook_id,
                ])
                ext = fmt if fmt in ("json", "html") else "md"
                path = os.path.join(output_dir, f"quiz.{ext}")
                _run_cmd([
                    "notebooklm", "download", "quiz",
                    f"--format={fmt}", path, "-n", notebook_id,
                ])
                downloaded.append(path)

            elif artifact_type == "flashcards":
                _run_cmd([
                    "notebooklm", "generate", "flashcards", "-n", notebook_id,
                ])
                path = os.path.join(output_dir, "flashcards.json")
                _run_cmd([
                    "notebooklm", "download", "flashcards",
                    "--format=json", path, "-n", notebook_id,
                ])
                downloaded.append(path)

            elif artifact_type == "infographic":
                _run_cmd([
                    "notebooklm", "generate", "infographic", "-n", notebook_id,
                ])
                path = os.path.join(output_dir, "infographic.png")
                _run_cmd([
                    "notebooklm", "download", "infographic", path, "-n", notebook_id,
                ])
                downloaded.append(path)

            elif artifact_type == "mindmap":
                _run_cmd([
                    "notebooklm", "generate", "mind-map", "-n", notebook_id,
                ])
                path = os.path.join(output_dir, "mindmap.json")
                _run_cmd([
                    "notebooklm", "download", "mind-map", path, "-n", notebook_id,
                ])
                downloaded.append(path)

            elif artifact_type == "report":
                _run_cmd([
                    "notebooklm", "generate", "report",
                    "--format=briefing", "-n", notebook_id,
                ])
                path = os.path.join(output_dir, "report.md")
                _run_cmd([
                    "notebooklm", "download", "report", path, "-n", notebook_id,
                ])
                downloaded.append(path)

            elif artifact_type == "video":
                fmt = options.get("format", "explainer")
                _run_cmd([
                    "notebooklm", "generate", "video",
                    f"--format={fmt}", "--wait", "-n", notebook_id,
                ])
                path = os.path.join(output_dir, "video.mp4")
                _run_cmd(["notebooklm", "download", "video", path, "-n", notebook_id])
                downloaded.append(path)

            elif artifact_type == "data-table":
                _run_cmd([
                    "notebooklm", "generate", "data-table", "--wait", "-n", notebook_id,
                ])
                path = os.path.join(output_dir, "data-table.csv")
                _run_cmd(["notebooklm", "download", "data-table", path, "-n", notebook_id])
                downloaded.append(path)

            log(f"Downloaded: {path}")

        except subprocess.CalledProcessError as e:
            log(f"Failed to generate {artifact_type}: {e.stderr.strip() if e.stderr else e}")
        except Exception as e:
            log(f"Error with {artifact_type}: {e}")

    return downloaded
