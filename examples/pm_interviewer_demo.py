from __future__ import annotations

# Example: Project-Manager ↔ Interviewer demo using existing SimpleOrchestrator
# ---------------------------------------------------------------------------
# This script is the **first incremental slice** of the multi-agent workflow.
# It keeps everything inside the *current* Modcast pipeline (no library edits),
# but demonstrates our strict “finish-before-forward” rule with just two
# personas: Marcus (PM) and Sarah (Interviewer).
#
# ‑ Marcus greets the user and hands control to Sarah
# ‑ Sarah asks clarifying questions; when satisfied she returns control
#   back to Marcus.
#
# Requirements to run:
#   • Environment variable OPENAI_API_KEY must be set.
#   • Optionally set OPENAI_REALTIME_MODEL / OPENAI_VOICE env vars.
#
# Run with:
#   python -m modcast.examples.pm_interviewer_demo

import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
from pathlib import Path
from dotenv import load_dotenv
# Load .env before importing openai_config so OPENAI_REALTIME_CONFIG sees the key
env_path = Path(__file__).resolve().parent.parent / '.env'
if env_path.exists():
    load_dotenv(env_path)
import asyncio
from simple_orchestrator import SimpleOrchestrator, PersonaConfig
from openai_config import OPENAI_REALTIME_CONFIG

# ---------------------------------------------------------------------------
# Persona definitions (strict turn-taking prompts)
# ---------------------------------------------------------------------------

MARCUS_PROMPT = """You are Marcus, the Project Manager.
Your job is to greet the client, then delegate to Sarah (the interviewer) so she
can gather complete requirements.

RULES (must follow):
1. Keep each spoken turn to **max 2 sentences**.
2. After you finish speaking, **always** call the function `select_next_speaker`
   with `speaker_index=\"1\"` (Sarah) — **nothing else**.
3. Do **not** start any other tasks yet.  Wait for Sarah’s interview results
   before planning further.
"""

SARAH_PROMPT = """You are Sarah, the Interviewer.
Ask clear, concise questions to fully understand the client’s needs for their
flower-shop website (branding, colours, features, timeline, budget, success
metrics).

RULES (must follow):
1. Ask **one** focused question per turn (1-2 sentences).
2. Immediately after speaking, call `select_next_speaker` **with**
   `speaker_index=\"2\"` to hand the microphone to the **Human** so they can
   answer.
3. When you believe you have **all** necessary information, say a short closing
   acknowledgement (1 sentence) and then call
   `select_next_speaker` with `speaker_index=\"0\"` to give control back to
   Marcus.
4. If the human’s previous response was unclear, ask a follow-up question (still
   one sentence) and again `select_next_speaker=2`.
"""

# NOTE: SimpleOrchestrator automatically appends "Human" as the last speaker, so
# index mapping is: 0 = Marcus, 1 = Sarah, 2 = Human.

personas = [
    PersonaConfig(name="Marcus", voice=os.getenv("OPENAI_VOICE", "alloy"), instructions=MARCUS_PROMPT, temperature=0.7, max_response_tokens=200),
    PersonaConfig(name="Sarah",  voice="ballad", instructions=SARAH_PROMPT,  temperature=0.8, max_response_tokens=800),
]

# ---------------------------------------------------------------------------
# Simple helper callbacks to print progress to console
# ---------------------------------------------------------------------------

def on_persona_started(name: str):
    print(f"\n— {name} starts speaking —")

def on_persona_finished(name: str, text: str, _audio: bytes):
    print(f"{name}: {text.strip()}")

# ---------------------------------------------------------------------------
# Main entry
# ---------------------------------------------------------------------------

async def main():
    # Basic sanity check for API key
    if not OPENAI_REALTIME_CONFIG.api_key:
        raise RuntimeError("OPENAI_API_KEY env var is missing. Set it before running.")

    orchestrator = SimpleOrchestrator(personas, OPENAI_REALTIME_CONFIG)
    orchestrator.on_persona_started = on_persona_started
    orchestrator.on_persona_finished = on_persona_finished

    # Start conversation with the client request as initial topic
    client_request = (
        "Hey, I’d like to create an online flower shop called LeFleur based in Paris."
        " Can you help me?"
    )
    await orchestrator.start_conversation_async(client_request)

if __name__ == "__main__":
    asyncio.run(main()) 