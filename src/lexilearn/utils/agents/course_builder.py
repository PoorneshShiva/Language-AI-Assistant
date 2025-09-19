"""Utilities for producing adaptive lessons with Ollama Llama3.1."""
from __future__ import annotations

import json
import re
from textwrap import dedent
from typing import Any, Dict, List, Optional

from lexilearn.utils.agents.model import AgenticModels


_JSON_PATTERN = re.compile(r"\{(?:.|\n)*\}")


def _ensure_json(text: str) -> Dict[str, Any]:
    """Extract a JSON object from the LLM response."""
    text = text.strip()
    candidates: List[str] = []
    if text.startswith("{") and text.endswith("}"):
        candidates.append(text)
    candidates.extend(match.group(0) for match in _JSON_PATTERN.finditer(text))
    for candidate in candidates:
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            continue
    raise ValueError("Unable to parse JSON payload from LLM response")


class CourseBuilder:
    """Generate grammar-rich assignments and scenarios with Llama3.1."""

    def __init__(self, llm: Optional[Any] = None):
        self.llm = llm or AgenticModels(model="ollama", model_name="llama3.1").llm

    def _invoke(self, prompt: str) -> Dict[str, Any]:
        result = self.llm.invoke(prompt)
        if isinstance(result, str):
            payload = result
        elif hasattr(result, "content"):
            payload = result.content if isinstance(result.content, str) else "".join(getattr(result, "content", []))
        else:
            payload = str(result)
        return _ensure_json(payload)

    def generate_assignment(
        self,
        *,
        sentence: str,
        level: str,
        goals: List[str],
        analysis: Dict[str, Any],
    ) -> Dict[str, Any]:
        prompt = dedent(
            f"""
            You are a senior German language coach. Take the learner sentence below and craft a
            rapid iteration assignment plan that combines micro grammar explanations, targeted drills,
            and production tasks. Keep the tone supportive but concise.

            Sentence: {sentence}
            Level: {level}
            Learner goals: {', '.join(goals) if goals else 'general proficiency'}
            Extracted analysis (JSON): {json.dumps(analysis)}

            Respond with JSON using the schema:
            {{
              "focus": {{
                "grammar": ["..."],
                "vocabulary": ["..."],
                "strategies": ["..."]
              }},
              "activities": [
                {{
                  "title": "",
                  "summary": "",
                  "instructions": "",
                  "expected_output": "",
                  "tips": ["..."],
                  "iteration_prompt": "prompt to ask the student for another attempt"
                }}
              ],
              "reflection": ["prompt the learner to reflect"],
              "real_world_bridge": ["idea"],
              "language_bank": [{{"phrase": "", "usage": ""}}]
            }}

            Ensure every string is concise and in the target language (German) where appropriate.
            """
        ).strip()
        payload = self._invoke(prompt)
        return payload

    def generate_real_life_prompt(
        self,
        *,
        level: str,
        theme: str,
        recently_learned: List[str],
    ) -> Dict[str, Any]:
        prompt = dedent(
            f"""
            Design a real-world German scenario that helps learners transfer classroom practice
            to a practical context. Focus theme: {theme}. Learner level: {level}.
            Recently learned items: {', '.join(recently_learned) if recently_learned else 'n/a'}

            Return JSON with keys:
            {{
              "theme": "",
              "situation": "",  // short description in German
              "role_play": {{
                "you": "",  // learner role guidance
                "partner": ""  // counterpart behaviour cues
              }},
              "checklist": ["micro-tasks"],
              "language_bank": [{{"phrase": "", "context": ""}}]
            }}
            """
        ).strip()
        return self._invoke(prompt)


__all__ = ["CourseBuilder"]
