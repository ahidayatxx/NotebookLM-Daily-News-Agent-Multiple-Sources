#!/usr/bin/env python3
"""Create notebook, add sources, ask synthesis prompt, save markdown output."""

import os
import re
import json
import time
import subprocess
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed


def log(msg):
    print(f"[*] {msg}", flush=True)


def create_notebook(title):
    """Create a new NotebookLM notebook. Returns notebook ID."""
    result = subprocess.run(
        ["notebooklm", "create", title],
        capture_output=True, text=True, check=True,
    )
    uuid_match = re.search(
        r'([a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})',
        result.stdout,
    )
    if not uuid_match:
        raise RuntimeError(f"Could not parse notebook UUID from output: {result.stdout}")
    return uuid_match.group(0)


def configure_response_settings(mode="detailed", response_length="longer"):
    """Set chat response mode and length on the active notebook.

    Always called before source upload so synthesis uses detailed + longer
    responses by default.
    """
    log(f"Configuring response settings: mode={mode}, length={response_length}...")
    try:
        subprocess.run(
            ["notebooklm", "configure", "--mode", mode, "--response-length", response_length],
            capture_output=True, text=True, check=True,
        )
        log("Response settings applied.")
    except subprocess.CalledProcessError as e:
        log(f"Warning: failed to set response settings: {e.stderr.strip()}")


def configure_persona(persona):
    """Set a custom chat persona on the active notebook.

    Called before source upload so NotebookLM grounds synthesis in the
    requested perspective (e.g. chemistry tutor, senior consultant, etc.).
    """
    log("Configuring chat persona...")
    try:
        subprocess.run(
            ["notebooklm", "configure", "--persona", persona],
            capture_output=True, text=True, check=True,
        )
        log("Persona applied.")
    except subprocess.CalledProcessError as e:
        log(f"Warning: failed to set persona: {e.stderr.strip()}")


def add_source(url, notebook_id, retries=3):
    """Add a single source to a notebook. Returns (success, url)."""
    cmd = ["notebooklm", "source", "add", url, "--json", "-n", notebook_id]
    for attempt in range(1, retries + 1):
        try:
            log(f"Adding source: {url} (attempt {attempt}/{retries})")
            subprocess.run(cmd, capture_output=True, text=True, check=True)
            log(f"Added: {url}")
            return True, url
        except subprocess.CalledProcessError as e:
            log(f"Failed to add {url} (attempt {attempt}): {e.stderr.strip()}")
            if attempt < retries:
                time.sleep(2)
    log(f"All {retries} attempts failed for: {url}")
    return False, url


def wait_for_sources(notebook_id, timeout=180, poll_interval=10):
    """Poll until all sources are ready. Returns list of ready source URLs."""
    cmd = ["notebooklm", "source", "list", "--json", "-n", notebook_id]
    start = time.time()

    while time.time() - start < timeout:
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            json_match = re.search(r'\{.*\}', result.stdout, re.DOTALL)
            if not json_match:
                time.sleep(poll_interval)
                continue

            data = json.loads(json_match.group(0))
            sources = data.get("sources", [])
            if not sources:
                time.sleep(poll_interval)
                continue

            all_ready = all(
                src.get("status", "").lower() == "ready" for src in sources
            )
            if all_ready:
                return [s.get("url") for s in sources if s.get("status") == "ready"]

            for src in sources:
                if src.get("status", "").lower() != "ready":
                    log(f"Source '{src.get('url')}' status: {src.get('status')}")

        except Exception as e:
            log(f"Warning checking source status: {e}")

        time.sleep(poll_interval)

    log("Timeout waiting for sources. Proceeding with what's ready.")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        json_match = re.search(r'\{.*\}', result.stdout, re.DOTALL)
        if json_match:
            data = json.loads(json_match.group(0))
            return [s.get("url") for s in data.get("sources", []) if s.get("status") == "ready"]
    except Exception:
        pass
    return []


def ask_notebook(notebook_id, prompt):
    """Ask NotebookLM a question. Returns the answer text."""
    result = subprocess.run(
        ["notebooklm", "ask", prompt, "-n", notebook_id],
        capture_output=True, text=True, check=True,
    )
    return result.stdout.strip()


def clean_response(text):
    """Strip citation markers and conversation artifacts from NotebookLM output."""
    text = re.sub(r'\s*\[\d+[\d,\s\-]*\]', '', text)
    text = re.sub(r'(?i)Continuing conversation [a-f0-9]+\.{3,}\n?', '', text)
    text = re.sub(r'(?i)Resumed conversation: [a-f0-9\-]+\n?', '', text)
    text = re.sub(r'(?i)^Answer:\n?', '', text)
    return text.strip()


def set_language(lang):
    """Set notebooklm output language. Returns original language for restore."""
    original = None
    try:
        res = subprocess.run(
            ["notebooklm", "language", "get"],
            capture_output=True, text=True, check=True,
        )
        match = re.search(r'Language:\s*([a-zA-Z_]+)', res.stdout)
        if match:
            original = match.group(1)
    except Exception:
        pass

    try:
        subprocess.run(["notebooklm", "language", "set", lang], check=True)
    except Exception as e:
        log(f"Warning: failed to set language to {lang}: {e}")

    return original


def restore_language(lang):
    """Restore notebooklm language setting."""
    if lang:
        try:
            subprocess.run(["notebooklm", "language", "set", lang], check=True)
        except Exception as e:
            log(f"Warning: failed to restore language: {e}")


def run(sources, template_path, output_dir, project_name, lang="en", keep=False,
        persona=None, mode="detailed", response_length="longer"):
    """Full synthesis pipeline. Returns (output_path, notebook_id)."""
    original_lang = set_language(lang)

    notebook_id = None
    try:
        # Create notebook
        date_str = datetime.now().strftime("%Y-%m-%d")
        title = f"{project_name} {date_str} ({lang.upper()})"
        log(f"Creating notebook: {title}")
        notebook_id = create_notebook(title)
        subprocess.run(["notebooklm", "use", notebook_id], check=True)
        log(f"Notebook ID: {notebook_id}")

        # Configure BEFORE source upload so all synthesis uses these settings
        configure_response_settings(mode=mode, response_length=response_length)
        if persona:
            configure_persona(persona)

        # Add sources in parallel
        log(f"Adding {len(sources)} sources...")
        success_count = 0
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(add_source, s["url"], notebook_id) for s in sources]
            for future in as_completed(futures):
                success, _ = future.result()
                if success:
                    success_count += 1
        log(f"Sources added: {success_count}/{len(sources)}")

        if success_count == 0:
            raise RuntimeError("No sources were successfully added")

        # Wait for readiness
        log("Waiting for sources to be ready...")
        ready = wait_for_sources(notebook_id)
        log(f"Ready sources: {len(ready)}")

        if not ready:
            raise RuntimeError("No sources became ready in time")

        # Read template
        with open(template_path, "r") as f:
            prompt = f.read().strip()

        # Ask
        log("Requesting synthesis from NotebookLM...")
        raw_answer = ask_notebook(notebook_id, prompt)
        cleaned = clean_response(raw_answer)

        # Build output
        wib_time = ""
        try:
            res = subprocess.run(
                ["date", "+%Y-%m-%d %H:%M"],
                env={**os.environ, "TZ": "Asia/Jakarta"},
                capture_output=True, text=True, check=True,
            )
            wib_time = f"{res.stdout.strip()} WIB"
        except Exception:
            wib_time = datetime.now().strftime("%Y-%m-%d %H:%M")

        header = f"# {project_name} — {wib_time}\n\n"
        url_sources = [s for s in ready if s and s.startswith(('http://', 'https://'))]
        footer = f"\n\n---\n\n*Sources: {', '.join(url_sources)}*"
        final = header + cleaned + footer

        # Save
        os.makedirs(output_dir, exist_ok=True)
        date_file = datetime.now().strftime("%Y-%m-%d")
        filename = f"{project_name.lower().replace(' ', '-')}-{date_file}-{lang}.md"
        filepath = os.path.join(output_dir, filename)

        counter = 2
        while os.path.exists(filepath):
            filename = f"{project_name.lower().replace(' ', '-')}-{date_file}-{lang}-{counter}.md"
            filepath = os.path.join(output_dir, filename)
            counter += 1

        with open(filepath, "w") as f:
            f.write(final)

        log(f"Output saved: {filepath}")
        return filepath, notebook_id

    except Exception:
        if notebook_id and not keep:
            log("Cleaning up notebook due to error...")
            try:
                subprocess.run(
                    ["notebooklm", "delete", "-n", notebook_id, "-y"], check=True
                )
            except Exception:
                pass
        raise

    finally:
        restore_language(original_lang)
