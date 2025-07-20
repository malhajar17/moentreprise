#!/usr/bin/env python3
"""Capture screenshots of the first four search results from Jina.ai.

Usage:
    python capture_top_sites.py "website for flowers in paris france"

The script:
1. Queries Jina.ai's search endpoint (requires the Jina bearer token to be
   available in the JINA_API_KEY env variable).
2. Parses the plaintext response to extract the first four `URL Source:` lines.
3. Uses Playwright (Chromium) to navigate and capture a full-page PNG
   screenshot for each URL, saving them under ../../images/landing_N.png.

This is intended to run inside the dev container / VM where Playwright Chromium
binaries are already installed (`python -m playwright install chromium`).
"""
from __future__ import annotations

import asyncio
import os
import re
import sys
from pathlib import Path
from typing import List

import httpx  # lightweight async HTTP client
from playwright.async_api import async_playwright
from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
API_ENDPOINT = "https://s.jina.ai/"
DEFAULT_SAVE_DIR = Path(__file__).resolve().parents[1] / "images"
DEFAULT_SAVE_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def parse_urls(text: str, max_urls: int = 4) -> List[str]:
    """Extract up to *max_urls* `URL Source:` links from the Jina response."""
    urls: List[str] = []
    pattern = re.compile(r"URL Source:\s*(\S+)")
    for line in text.splitlines():
        m = pattern.search(line)
        if m:
            urls.append(m.group(1))
            if len(urls) >= max_urls:
                break
    return urls


async def query_jina(query: str, api_key: str, max_urls: int = 4) -> List[str]:
    headers = {
        "Authorization": f"Bearer {api_key}",
        "X-Respond-With": "no-content",
    }
    params = {"q": query}
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.get(API_ENDPOINT, headers=headers, params=params)
        r.raise_for_status()
        return parse_urls(r.text, max_urls=max_urls)


async def capture_screenshot(page, url: str, save_path: Path):
    try:
        await page.goto(url, timeout=20000, wait_until="networkidle")
        await page.screenshot(path=str(save_path), full_page=True)
        print(f"✅ Saved screenshot {save_path.name} ({url})")
    except Exception as e:
        print(f"⚠️  Failed to capture {url}: {e}")


async def main(query: str):
    # Load environment variables from ../.env (project root)
    load_dotenv(Path(__file__).resolve().parents[1] / ".env")

    api_key = os.environ.get("JINA_API_KEY")
    if not api_key:
        print("❌ Set JINA_API_KEY environment variable with your token.")
        sys.exit(1)

    urls = await query_jina(query, api_key)
    if not urls:
        print("❌ No URLs found in Jina response.")
        sys.exit(1)

    print("🔗 URLs to capture:")
    for i, u in enumerate(urls, 1):
        print(f"  {i}) {u}")

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1920, "height": 1080})
        page = await context.new_page()

        for idx, url in enumerate(urls, 1):
            save_file = DEFAULT_SAVE_DIR / f"landing_{idx}.png"
            await capture_screenshot(page, url, save_file)

        await browser.close()

    print(f"🎉 Screenshots saved under {DEFAULT_SAVE_DIR}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: capture_top_sites.py <search query>")
        sys.exit(1)
    asyncio.run(main(" ".join(sys.argv[1:]))) 