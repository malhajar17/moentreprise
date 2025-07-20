from __future__ import annotations

import asyncio
from typing import List
from simple_orchestrator import SimpleOrchestrator, PersonaConfig
from datetime import datetime

# ---------------------------------------------------------------------------
# Patch: prevent SimpleOrchestrator from looping Human turns
# After the human finishes speaking we want control to return to the persona
# set in `selected_next_speaker`, not start another human turn.
# We apply this patch once at import time.
# ---------------------------------------------------------------------------

if not hasattr(SimpleOrchestrator, "_patched_no_human_loop"):
    _orig_start_human_turn = SimpleOrchestrator._start_human_turn

    async def _start_human_turn_once(self):  # type: ignore[override]
        """Wrapped start_human_turn that clears current_speaker afterwards."""
        await _orig_start_human_turn(self)

        # Capture human answer during interview phase
        if getattr(self, "phase", "") == "interview" and self.pending_human_response:
            self.interview_notes.append(self.pending_human_response)

        # Force next speaker to Sarah if still interviewing
        if getattr(self, "phase", "") == "interview" and getattr(self, "questions_left", 0) > 0:
            self.selected_next_speaker = "Sarah"
            self.selection_reason = "Return to interviewer after human response"

        # Debug state after human response
        print("DEBUG >> phase:", getattr(self, "phase", "?"),
              "selected_next_speaker:", getattr(self, "selected_next_speaker", None),
              "current_persona_index:", getattr(self, "current_persona_index", None),
              "current_speaker:", self.current_speaker,
              "questions_left:", getattr(self, "questions_left", None))
        # NOTE: do NOT clear current_speaker here; we need it set to 'Human'
        # so that _move_to_next_persona can detect the human turn once.

    SimpleOrchestrator._start_human_turn = _start_human_turn_once  # type: ignore[assignment]
    SimpleOrchestrator._patched_no_human_loop = True

# ---------------------------------------------------------------------------
# Patch 2: replace the verbose conspiracy prompt builder in _start_persona_turn
# with a minimal business-oriented prompt: persona.instructions + recent context.
# ---------------------------------------------------------------------------

if not hasattr(SimpleOrchestrator, "_patched_clean_prompt"):

    async def _start_persona_turn_clean(self, prompt: str = None):  # type: ignore
        """Simplified start_persona_turn that uses clean, task-specific prompts."""
        if not self.is_running:
            return

        if self.current_turn >= self.max_turns:
            await self._end_conversation(); return

        persona = self.personas[self.current_persona_index]
        self.current_speaker = persona.name
        self.is_speaking = True
        self.current_turn += 1

        self.logger.info(f"🎤 Turn {self.current_turn}: {persona.name} speaking…")
        if self.on_persona_started:
            self.on_persona_started(persona.name)

        # Build a *clean* prompt
        context = self._build_conversation_context()

        # If Marcus is about to start ideation, include summary of interview notes
        if persona.name == "Marcus" and getattr(self, "phase", "") == "ideation_prep":
            summary_lines = "\n".join(f"- {line}" for line in getattr(self, "interview_notes", [])) or "(no notes)"
            context += f"\n\nSUMMARY OF CLIENT PREFERENCES:\n{summary_lines}\n\nPlease thank Sarah for collecting the info, then instruct Maya to fetch 5 similar websites with screenshots. After your two-sentence message, call the function with speaker_index='4'."

        # NEW: For Maya, run a live web search to find similar websites based on the interview notes
        if persona.name == "Maya" and getattr(self, "phase", "") == "ideation":
            try:
                from web_tools import find_sites_jina

                prefs_text = " ".join(getattr(self, "interview_notes", [])) or "website inspiration"
                search_query = prefs_text

                summary_lines = "\n".join(f"- {line}" for line in getattr(self, "interview_notes", [])) or "(no notes)"
                context += f"\n\nCLIENT PREFERENCES SUMMARY:\n{summary_lines}"

                user_context_text = "\n".join(getattr(self, "interview_notes", []))
                sites = find_sites_jina(search_query, n=4, user_context=user_context_text)
                if sites:
                    sites_list = "\n".join(f"- {url}" for url in sites)
                    context += (
                        f"\n\nAUTO-FETCHED TOP SITES (Jina.ai):\n{sites_list}\n\n"
                        "Screenshots of these pages have been captured and saved. "
                        "Simply respond with 'Screenshots updated' - nothing more."
                    )
            except Exception as search_ex:
                self.logger.error(f"🌐 Jina search for Maya failed: {search_ex}")

        # Dynamically change Marcus's instructions after Maya completes screenshots
        if persona.name == "Marcus" and getattr(self, "phase", "") == "ideation" and not getattr(self, "awaiting_maya_followup", False):
            # Check if Maya just finished (last speaker was Maya)
            if self.conversation_history and self.conversation_history[-1]['speaker'] == 'Maya':
                # Change Marcus's instructions for this specific turn
                persona.instructions = (
                    "You are Marcus, the Project Manager. Maya has just completed the screenshot research task. "
                    "Thank Maya briefly in one sentence. "
                    "Then immediately tell Alex to start coding: 'Alex, please start coding the website based on our requirements.' "
                    "Keep it direct and simple. End by calling select_next_speaker with speaker_index='2'."
            )

        # Append detailed plan if target.txt exists
        if persona.name == "Marcus" and getattr(self, "phase", "") == "ideation":
            from pathlib import Path
            plan_file = Path(__file__).resolve().parents[1] / "images" / "target.txt"
            if plan_file.exists():
                plan_text = plan_file.read_text(encoding="utf-8")[:1500]  # cap length
                context += f"\n\nDETAILED IMPLEMENTATION BRIEF (for your reference):\n{plan_text}"

        if prompt:
            full_prompt = f"{persona.instructions}\n\n{context}\n\nHUMAN JUST SAID: {prompt}\nRespond appropriately."
        else:
            full_prompt = f"{persona.instructions}\n\n{context}"

        try:
            # SPECIAL: for Sarah ensure non-repeating questions
            if persona.name == "Sarah" and self.phase == "interview":
                remaining = [q for q in self.question_list if q not in self.asked_questions]
                if remaining:
                    next_q = remaining[0]
                    self.asked_questions.append(next_q)
                    # Prepend acknowledgement placeholder
                    full_prompt = (
                        f"{persona.instructions}\n\nRECENT CONTEXT:\n{context}\n\n"
                        f"Acknowledge the last human answer in ONE short sentence.\n"
                        f"Then ask exactly this question: '{next_q}'.\n"
                        f"After the question call the function."
                    )
                else:
                    # No questions left
                    self.questions_left = 0

            elif persona.name == "Sarah" and self.phase == "farewell":
                full_prompt = (
                    "Please thank the user for the information in one friendly sentence and say you will report to the project manager, then call the function with speaker_index='0'."
                )

            text, audio = await self._get_persona_response(persona, full_prompt)

            # Fallback if Sarah (or any persona) produced empty text
            if not text.strip():
                text = "(repeats question clearly)"

            self.conversation_history.append({
                'speaker': persona.name,
                'text': text,
                'timestamp': datetime.now(),
                'audio_length': len(audio)
            })

            if self.on_persona_finished:
                self.on_persona_finished(persona.name, text, audio)

            await self._wait_for_audio_completion_async(persona.name)
            await self._move_to_next_persona()
        except Exception as ex:
            self.logger.error(f"Error in persona turn: {ex}")
            await self._handle_persona_error(persona.name)

    # Replace original method
    SimpleOrchestrator._start_persona_turn = _start_persona_turn_clean  # type: ignore[assignment]
    SimpleOrchestrator._patched_clean_prompt = True

class PhasedOrchestrator(SimpleOrchestrator):
    """Custom orchestrator with a fixed multi-phase flow.

    Phase A – Greeting + Interview
        Marcus greets once then Sarah ↔ Human Q&A for N questions.
    Phase B – Ideation chain (Alex → Jordan → Maya → Casey → Sam)
        Each persona contributes exactly one turn.
    After Sam, control returns to Marcus who can close / delegate implementation.
    """

    def __init__(self,
                 personas: List[PersonaConfig],
                 openai_config,
                 interview_questions: int = 6,
                 logger=None):
        super().__init__(personas, openai_config, logger=logger)

        # Ensure the conversation doesn’t stop halfway – allow up to 30 turns
        self.max_turns = 30

        self.phase = "greeting"   # greeting -> interview -> ideation -> complete
        self.questions_left = interview_questions
        self.ideation_order = ["Maya", "Alex"]  # Simplified: Maya research → Alex implementation
        # Interview checklist and tracking
        self.question_list = [
            "Who is the target audience?",
            "Which pages do you need?",
            "Preferred colour palette?",
            "Example websites you like?",
            "Timeline and budget?",
            "How will you measure success?"
        ]
        self.asked_questions: List[str] = []
        # Store human answers for later agents
        self.interview_notes: List[str] = []
        # Track if Maya requested a follow-up answer from Marcus
        self.awaiting_maya_followup: bool = False

    # Helper
    def _idx(self, name: str) -> int:
        return next(i for i, p in enumerate(self.personas) if p.name == name)

    async def _move_to_next_persona(self):  # type: ignore[override]
        """Override default speaker selection with deterministic phase logic."""

        # Figure out who just finished speaking – needed in several branches.
        if self.conversation_history:
            speaker = self.conversation_history[-1]['speaker']
        else:
            speaker = self.current_speaker or self.personas[self.current_persona_index].name

        # --- Phase-based routing ---
        if self.phase == "greeting":
            # Marcus has just spoken, now force Sarah
            self.current_persona_index = self._idx("Sarah")
            self.phase = "interview"
        elif self.phase == "interview":
            # `speaker` already determined above
            if speaker == "Sarah":
                # Sarah asks a question. Pre-set the next speaker so after the human
                # response control automatically returns to Sarah.
                self.selected_next_speaker = "Sarah"
                self.selection_reason = "Interview next question"
                # Now start human turn
                await self._start_human_turn()
                return
            elif speaker == "Human":
                # Human just answered
                self.questions_left -= 1
                if self.questions_left > 0:
                    self.current_persona_index = self._idx("Sarah")
                    await self._start_persona_turn()
                else:
                    # Human answered last required question – schedule Sarah farewell
                    self.phase = "farewell"
                    self.current_persona_index = self._idx("Sarah")
                    await self._start_persona_turn()
            else:
                # Fallback sequential
                await super()._move_to_next_persona()
                return
        elif self.phase == "ideation_prep":
            # Marcus summarised; start ideation
            self.current_persona_index = self._idx(self.ideation_order[0])
            self.phase = "ideation"
        elif self.phase == "ideation":
            speaker = self.personas[self.current_persona_index].name

            # HARD RULE: After Maya, ALWAYS go to Marcus - no exceptions
            if speaker == "Maya":
                self.current_persona_index = self._idx("Marcus")
                self.selected_next_speaker = None  # clear any pending selections
                # small delay
                if self.turn_delay_seconds > 0:
                    await asyncio.sleep(self.turn_delay_seconds)
                await self._start_persona_turn()
                return

            # First check if ANY explicit speaker selection was made (not just Marcus)
            if self.selected_next_speaker:
                next_speaker = self.selected_next_speaker
                self.selected_next_speaker = None  # clear so it isn't reused
                self.current_persona_index = self._idx(next_speaker)
                # small delay
                if self.turn_delay_seconds > 0:
                    await asyncio.sleep(self.turn_delay_seconds)
                await self._start_persona_turn()
                return

            elif speaker in self.ideation_order:
                idx = self.ideation_order.index(speaker)
                if idx < len(self.ideation_order) - 1:
                    # Move to next persona in ideation order
                    self.current_persona_index = self._idx(self.ideation_order[idx + 1])
                else:
                    # After Alex executes vibe_code, mark conversation complete
                    self.phase = "complete"
                    self.logger.info("🎯 Alex has executed vibe_code - implementation pipeline started!")
                    await self._end_conversation()
                    return

            elif speaker == "Marcus":
                # After Marcus reflection, move to Alex for implementation
                self.current_persona_index = self._idx("Alex")

            else:
                # Fallback to default behavior
                await super()._move_to_next_persona()
                return
        elif self.phase == "farewell":
            if speaker == "Sarah":
                # After farewell hand to Marcus for summary
                self.phase = "ideation_prep"
                self.current_persona_index = self._idx("Marcus")
            else:
                await super()._move_to_next_persona(); return
        elif self.phase == "showcase":
            # Handle showcase phase: Alex showcases -> Marcus responds -> Sophie creates LinkedIn post
            if speaker == "Alex":
                # Alex showcased the website, now hand to Marcus for his response
                self.current_persona_index = self._idx("Marcus")
                # Update Marcus's instructions for showcase response
                marcus_persona = next((p for p in self.personas if p.name == "Marcus"), None)
                if marcus_persona:
                    marcus_persona.instructions = (
                        "You are Marcus, the Project Manager. Alex has just showcased the completed website and you're very impressed! "
                        "Praise Alex's excellent work in 2-3 enthusiastic sentences. Then mention that Sophie will now handle the marketing announcement on LinkedIn. "
                        "End by calling select_next_speaker with speaker_index='7' to hand control to Sophie."
                    )
            elif speaker == "Marcus":
                # Marcus responded to Alex's showcase, now hand to Sophie for LinkedIn marketing
                self.current_persona_index = self._idx("Sophie")
                self.phase = "marketing"  # Switch to marketing phase
            else:
                await super()._move_to_next_persona(); return
        elif self.phase == "marketing":
            # Sophie creates LinkedIn post, then hand back to Marcus for closing
            if speaker == "Sophie":
                # Sophie finished marketing, now Marcus closes the session
                self.current_persona_index = self._idx("Marcus")
                self.phase = "closing"  # Switch to closing phase
                
                # Update Marcus instructions for closing
                marcus_persona = next((p for p in self.personas if p.name == "Marcus"), None)
                if marcus_persona:
                    marcus_persona.instructions = (
                        "You are Marcus, the Project Manager. Sophie has just completed an excellent LinkedIn marketing campaign for our website launch. "
                        "Thank Sophie warmly for her outstanding marketing work in 2-3 sentences. "
                        "Then provide a brief project wrap-up: acknowledge the entire team's great work (Maya for research, Alex for development, Sophie for marketing). "
                        "Conclude by saying the project is successfully completed and the session is now closed. "
                        "Keep it professional, positive, and conclusive. Do not call any functions - just provide the closing statement."
                    )
            else:
                await super()._move_to_next_persona(); return
        elif self.phase == "closing":
            # Marcus provides final thanks and closes the session
            if speaker == "Marcus":
                self.phase = "complete"
                self.logger.info("🎯 Marcus has closed the session - project completed!")
                await self._end_conversation()
                return
            else:
                await super()._move_to_next_persona(); return
        else:  # complete – fall back to default sequencing
            await super()._move_to_next_persona()
            return

        # Delay small buffer to keep experience natural
        if self.turn_delay_seconds > 0:
            await asyncio.sleep(self.turn_delay_seconds)

        # Kick off next turn
        await self._start_persona_turn() 