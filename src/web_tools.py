from __future__ import annotations

"""Utility helpers for lightweight web search used by Maya.

The goal is to take the free-form description (usually a concatenation of the
client interview notes) and turn it into a concise search query.  We then use
DuckDuckGo's free search endpoint (via the `duckduckgo_search` package if
available) to retrieve candidate sites, filtering out duplicates so we end up
with at most *n* distinct website URLs.

This is **best-effort** discovery – the orchestrator will pass the found links
as context and let Maya decide how to present them.  If the search package is
missing or the network fails, we simply return an empty list so the
conversation can proceed gracefully.
"""

from urllib.parse import urlparse, quote_plus
from typing import List
import logging
import threading, time
import base64
import openai

logger = logging.getLogger(__name__)

__all__ = [
    "find_similar_websites",
    "find_sites_jina",
]


def _deduplicate_urls(urls: List[str]) -> List[str]:
    """Return the list with duplicate *domains* removed, preserving order."""
    seen_domains = set()
    unique: List[str] = []
    for url in urls:
        domain = urlparse(url).netloc.lower()
        if domain and domain not in seen_domains:
            seen_domains.add(domain)
            unique.append(url)
    return unique


def _query_duckduckgo(query: str, max_results: int = 10) -> List[str]:
    """Query DuckDuckGo via `duckduckgo_search` (preferred) or fallback HTML scrape."""

    # Preferred: duckduckgo_search – pip install duckduckgo_search
    try:
        from duckduckgo_search import DDGS  # type: ignore

        with DDGS() as ddgs:
            results = ddgs.text(query, region="wt-wt", safesearch="Moderate", max_results=max_results)
            urls = [hit.get("href") or hit.get("url", "") for hit in results]
            return [u for u in urls if u]

    except Exception as e:  # noqa: BLE001
        logger.warning("duckduckgo_search failed or not installed – %s", e)

    # Fallback: very simple HTML scrape – last resort, may break anytime
    try:
        import requests
        from bs4 import BeautifulSoup  # type: ignore

        logger.info("Falling back to DuckDuckGo HTML scrape for query '%s'", query)
        resp = requests.get(
            f"https://duckduckgo.com/html/?q={quote_plus(query)}",
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=10,
        )
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        links = [a.get("href") for a in soup.select("a.result__a") if a.get("href")]
        return links[:max_results]

    except Exception as e:  # noqa: BLE001
        logger.error("Fallback HTML scrape failed: %s", e)
        return []


def build_search_query(raw_prefs: str) -> str:
    """Craft a reasonably specific query string from free-form preferences."""

    # Very naive – just join words + generic descriptors. You may refine later.
    key_phrase = raw_prefs.strip().replace("\n", " ")
    if not key_phrase:
        key_phrase = "inspiration website design"
    return f"{key_phrase} website inspiration"


def find_similar_websites(preferences: str, n: int = 4) -> List[str]:
    """Return up to *n* distinct website URLs matching the given preferences."""

    try:
        query = build_search_query(preferences)
        logger.info("🌐 Searching web for similar websites – query: '%s'", query)
        candidates = _query_duckduckgo(query, max_results=max(n * 3, 10))
        unique_sites = _deduplicate_urls(candidates)
        logger.info("🔎 Found %d unique sites", len(unique_sites))
        return unique_sites[:n]
    except Exception as e:  # noqa: BLE001
        logger.error("Web search failed: %s", e)
        return []


# ---------------------------------------------------------------------------
# Jina.ai powered search – returns structured results quickly
# ---------------------------------------------------------------------------

import os, re, httpx
from pathlib import Path
import json, requests

# Screenshot helper
_IMAGE_DIR = Path(__file__).resolve().parents[1] / "images"
_IMAGE_DIR.mkdir(exist_ok=True, parents=True)


# ---------- Claude design generation ----------

CLAUDE_API_URL = "https://api.anthropic.com/v1/messages"


def generate_initial_design(user_context: str, target_file: Path) -> Path:
    """Call Claude Sonnet to generate a single-file website and save it.

    Returns the path to the saved HTML file.
    """
    api_key = os.getenv("CLAUDE_API")
    if not api_key:
        logger.error("CLAUDE_API env var not set – cannot generate design")
        return target_file

    prompt = (
        "You are a senior full-stack engineer. Using the following requirements, "
        "produce a COMPLETE, runnable single-file HTML document (embed CSS & minimal JS inline). "
        "It must strictly comply with the description. Output NOTHING except the HTML code block.\n\n" + user_context
    )

    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }
    body = {
        "model": "claude-3-5-sonnet-20241022",
        "max_tokens": 1024,
        "messages": [{"role": "user", "content": prompt}],
    }

    try:
        resp = requests.post(CLAUDE_API_URL, headers=headers, data=json.dumps(body), timeout=60)
        resp.raise_for_status()
        html = resp.json()["content"] if isinstance(resp.json(), dict) else ""
        if not html.strip():
            logger.error("Claude returned empty content")
            return target_file
        target_file.write_text(html, encoding="utf-8")
        logger.info("💻 Saved generated design to %s", target_file)
    except Exception as ex:
        logger.error("Failed generating design: %s", ex)
    return target_file


# ---------- vibe code executor (stub) ----------

def vibe_code_executor(project_root: Path, terminal_cb=None, dev_cb=None) -> bool:
    """Run OpenManus workflow and build project, streaming stdout via callback.

    terminal_cb: callable that receives decoded stdout lines in real-time.
    """
    import subprocess, shlex, os, pty, select, sys, pathlib, time

    def emit(line: str):
        if terminal_cb:
            try:
                terminal_cb(line)
            except Exception:
                pass
        else:
            sys.stdout.write(line)

    # Check workspace first
    workspace_dir = pathlib.Path("/home/azureuser/OpenManus/workspace")
    workspace_empty = True
    project_dir = None
    
    if workspace_dir.exists():
        projects = [d for d in workspace_dir.iterdir() if d.is_dir()]
        if projects:
            workspace_empty = False
            # Pick most recently modified
            projects.sort(key=lambda p: p.stat().st_mtime, reverse=True)
            project_dir = str(projects[0])
            emit(f"[vibe] Found existing project: {project_dir}\n")

    if workspace_empty:
        # Run full OpenManus workflow
        emit("[vibe] Workspace empty - running full OpenManus workflow...\n")
        
        target_path = _IMAGE_DIR / "target.txt"
        if not target_path.exists():
            emit("ERROR: target.txt not found.\n")
            return False

        # Build the final prompt (template + spec)
        target_spec = target_path.read_text(encoding="utf-8")
        prompt = CODE_TEMPLATE.format(TARGET_SPEC=target_spec)
        
        # Debug: Show what we're sending to OpenManus
        emit(f"[vibe] Target spec: {target_spec[:200]}...\n")
        emit(f"[vibe] Prompt preview: {prompt[:300]}...\n")

        emit("[vibe] Launching OpenManus coding agent...\n")

        # Use --prompt flag to pass prompt directly as command line argument
        import shlex
        escaped_prompt = shlex.quote(prompt)
        shell_cmd = (
            f" cd /home/azureuser/OpenManus && source venv/bin/activate && "
            f"python3 main.py --prompt {escaped_prompt}"
        )

        emit(f"[vibe] Starting OpenManus with prompt ({len(prompt)} characters)...\n")

        # Use bash -c so we can source venv (no stdin needed with --prompt flag)
        p = subprocess.Popen(
            ["bash", "-c", shell_cmd],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True,
        )

        # Stream output from OpenManus
        try:
            for line in iter(p.stdout.readline, ""):
                emit(line)
        except Exception as e:
            emit(f"[vibe] Error reading output: {e}\n")
            p.terminate()
            return False

        p.wait()

        if p.returncode != 0:
            emit(f"OpenManus exited with code {p.returncode}\n")
            return False

        # Find the created project
        if not workspace_dir.exists():
            emit("Workspace directory not found after OpenManus run.\n")
            return False

        projects = [d for d in workspace_dir.iterdir() if d.is_dir()]
        if not projects:
            emit("No projects found in workspace after OpenManus run.\n")
            return False

        # Pick most recently modified
        projects.sort(key=lambda p: p.stat().st_mtime, reverse=True)
        project_dir = str(projects[0])
    else:
        emit(f"[vibe] Using existing project: {project_dir}\n")

    # Install and run dev server
    dev_cmd = (
        f"cd {shlex.quote(project_dir)} && npm install && "
        "npm run dev -- --host 0.0.0.0 --port 3001"
    )

    emit("[vibe] Installing dependencies and launching dev server...\n")

    p2 = subprocess.Popen(
        ["bash", "-c", dev_cmd],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        universal_newlines=True,
    )

    for line in iter(p2.stdout.readline, ""):
        emit(line)
        if "Local:" in line and "http" in line:
            url = line.strip().split()[-1]
            if dev_cb:
                try:
                    dev_cb(url)
                except Exception:
                    pass

    return True


def _capture_screenshots(urls, image_dir, user_context: str = ""):
    """Capture screenshots in a separate thread using sync Playwright."""
    try:
        # Define target file path
        target_file = image_dir / "target.txt"

        # Pre-seed target.txt with user context immediately
        if user_context:
            target_file.write_text(user_context, encoding="utf-8")
        else:
            target_file.write_text("(No user context)", encoding="utf-8")
        logger.info("📝 Pre-seeded target.txt with user context (%d chars)", len(user_context))

        from playwright.sync_api import sync_playwright

        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True)
            context = browser.new_context(viewport={"width": 1920, "height": 1080})
            page = context.new_page()

            descriptions = []

            for idx, url in enumerate(urls, 1):
                save_path = image_dir / f"landing_{idx}.png"
                try:
                    page.goto(url, timeout=4000, wait_until="networkidle")
                    page.screenshot(path=str(save_path), full_page=True)
                    logger.info("📸 Saved screenshot %s", save_path)

                    # Describe screenshot using GPT-4o vision
                    try:
                        openai.api_key = os.getenv("OPENAI_API_KEY")
                        if openai.api_key:
                            with open(save_path, "rb") as img_f:
                                b64 = base64.b64encode(img_f.read()).decode("utf-8")

                            response = openai.chat.completions.create(
                                model="gpt-4o",  # updated model name
                                messages=[
                                    {
                                        "role": "user",
                                        "content": [
                                            {
                                                "type": "text",
                                                "text": (
                                                    "Describe this website landing page in detail: layout, colour palette, typography, "
                                                    "images, calls-to-action, and notable UI patterns. Only describe what you see. "
                                                    "Limit to 200 words."
                                                ),
                                            },
                                            {
                                                "type": "image_url",
                                                "image_url": {
                                                    "url": f"data:image/png;base64,{b64}"
                                                },
                                            },
                                        ],
                                    }
                                ],
                                max_tokens=800,
                            )

                            desc = response.choices[0].message.content.strip()

                            # Skip if looks like a block / captcha page
                            if any(s in desc.lower() for s in [
                                "verify", "captcha", "blocked", "checking your browser"
                            ]):
                                logger.warning("Screenshot %s appears to be blocked page – skipping txt", save_path)
                            else:
                                txt_path = save_path.with_suffix(".txt")
                                txt_path.write_text(desc, encoding="utf-8")
                                descriptions.append(desc)
                                logger.info("📝 Wrote description %s", txt_path)
                    except Exception as gpt_ex:
                        logger.error("Vision description failed for %s: %s", save_path, gpt_ex)

                except Exception as shot_ex:
                    logger.warning("Failed screenshot for %s: %s", url, shot_ex)

            browser.close()

            # Collect any landing_*.txt files present (including previous runs)
            for txt_file in sorted(image_dir.glob("landing_*.txt")):
                content = txt_file.read_text(encoding="utf-8").strip()
                if content and content not in descriptions:
                    descriptions.append(content)

            # If we have user context and at least one description, generate overall plan
            if user_context and descriptions:
                try:
                    prompt_parts = [
                        {
                            "type": "text",
                            "text": (
                                "We have a client who said the following about their needs:\n" + user_context +
                                "\n\nWe analysed similar websites and observed these details:\n" + "\n---\n".join(descriptions) +
                                "\n\nProvide an extremely detailed website implementation brief that satisfies the client's needs while learning from the references. Cover structure, pages, colour palette, typography, imagery, interactions, accessibility, and performance."
                            ),
                        }
                    ]

                    openai.api_key = os.getenv("OPENAI_API_KEY")
                    if openai.api_key:
                        resp = openai.chat.completions.create(
                            model="gpt-4o",
                            messages=[{"role": "user", "content": prompt_parts}],
                            max_tokens=1200,
                        )
                        plan_text = resp.choices[0].message.content.strip()
                        if plan_text:
                            (image_dir / "target.txt").write_text(plan_text, encoding="utf-8")
                            logger.info("💻 Saved generated design to %s", image_dir / "target.txt")
                except Exception as plan_ex:
                    logger.error("Failed to create target.txt: %s", plan_ex)

            # Fallback: if no descriptions but user_context exists, still write target.txt
                target_file = image_dir / "target.txt"
            if not target_file.exists():
                default_text = user_context if user_context else "(No user context available)"
                target_file.write_text(default_text, encoding="utf-8")
                logger.info("📝 Wrote fallback target.txt")

    except Exception as pw_ex_outer:
        logger.error("Playwright thread outer error: %s", pw_ex_outer)


def _parse_jina_urls(text: str, max_urls: int) -> List[str]:
    pattern = re.compile(r"URL Source:\s*(\S+)")
    urls: List[str] = []
    for line in text.splitlines():
        m = pattern.search(line)
        if m:
            urls.append(m.group(1))
            if len(urls) >= max_urls:
                break
    return urls


def find_sites_jina(query: str, n: int = 4, user_context: str = "") -> List[str]:
    """Use Jina.ai search API to fetch up to *n* URLs (needs JINA_API_KEY)."""
    api_key = os.getenv("JINA_API_KEY")
    if not api_key:
        logger.warning("JINA_API_KEY env var not set – skipping Jina search")
        return []

    headers = {
        "Authorization": f"Bearer {api_key}",
        "X-Respond-With": "no-content",
    }
    params = {"q": query}

    try:
        r = httpx.get("https://s.jina.ai/", headers=headers, params=params, timeout=30)
        r.raise_for_status()
        urls = [u for u in _parse_jina_urls(r.text, n) if not "pdf" in u.lower()]

        if not urls:
            return urls

        # Capture screenshots synchronously with Playwright
        t = threading.Thread(target=_capture_screenshots, args=(urls, _IMAGE_DIR, user_context), daemon=True)
        t.start()
        t.join()

        return urls
    except Exception as e:  # noqa: BLE001
        logger.error("Jina search failed: %s", e)
        return [] 

CODE_TEMPLATE = """Role
You are a junior-friendly full-stack developer who writes clear, commented TypeScript and is allowed to execute shell commands to build and run the project.

Project
{TARGET_SPEC}

Tech stack (use NOTHING else)
• Vite + React + TypeScript (strict mode)  
• Plain CSS Modules (no Tailwind / UI libs)  
• ESLint + Prettier (defaults)

Pages / routes
1. Home – hero banner + three featured bouquets (each with image URL, name, price).  
2. Catalogue – grid of all bouquets loaded from `/public/bouquets.json`.  
3. About – short paragraph + florist photo (`/public/hero.jpg`).  
4. Contact – form (name, email, message) that logs data to console.

Required repo layout
/fleur-de-paris
  /public            hero.jpg, bouquets.json
  /src
    /components      Header.tsx, Footer.tsx, BouquetCard.tsx
    /pages           Home.tsx, Catalogue.tsx, About.tsx, Contact.tsx
    App.tsx
    main.tsx
  index.html
  vite.config.ts
  tsconfig.json
  README.md

Hard requirements
• Every import path resolves – **no missing files**.  
• **If you import a file, you MUST include that file in the deliverables.**  
• Use royalty-free flower images (e.g. Unsplash, Pexels) by URL OR download them into `/public` so the site shows real photos, not gray placeholders.  
• TypeScript strict mode passes.  
• Responsive layout with Flexbox / Grid.  
• Navigation bar + footer visible on every page.  
• Zero runtime errors **and** zero ESLint warnings after `npm run dev`.  
• Images/JSON must exist or be valid URLs so the build succeeds.

Runtime instructions (execute automatically)
1. If the project folder does NOT exist, create it:  
   `npm create vite@latest fleur-de-paris -- --template react-ts`
2. Replace the boilerplate with the source files you generate.  
3. Install dependencies:  
   `cd fleur-de-paris && npm install`
4. Launch the dev server on port **3001** (or the next free port if 3001 is busy):  
   `npm run dev -- --host 0.0.0.0 --port 3001`
5. Display the URL where the site is running.

Deliverables & output format
A. A short overview of what each file does.  
B. Every code file in its own fenced code block, ready to overwrite the boilerplate.  
C. Shell-command transcript showing that steps 1-5 ran successfully and the site compiled without errors.  
D. Finish with a “Further ideas” section listing three possible future improvements.

Quality gate
Agent must verify that:
• `npm run dev` starts successfully.  
• Visiting `/` renders the Home page without console errors and displays the real flower images.  
If any step fails, fix the code and rerun automatically until it passes.
""" 