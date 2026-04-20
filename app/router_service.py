"""Intent routing using a tiny CPU-only embedding worker with heuristics fallback."""

from __future__ import annotations

from functools import lru_cache
import math
import re

from app.config import get_settings


class IntentRouterService:
    """Classify requests before they reach the main LLM."""

    PROTOTYPES = {
        "PROFILE": [
            "what is my name",
            "what is my cgpa",
            "what are my language levels",
            "remember my profile",
        ],
        "PROJECT_INFO": [
            "tell me about the smart hvac project",
            "project status for flood prediction",
            "who are the team members on this project",
        ],
        "TASK": ["show my tasks", "mark this task complete"],
        "SCHEDULE": ["what is on my schedule", "appointments on april 20"],
        "NOTE": ["summarize this note", "show my summaries", "summarize this file"],
        "GENERAL": ["capital of india", "explain recursion", "general question"],
    }

    def __init__(self) -> None:
        settings = get_settings()
        self.model_name = settings.embedding_model_name

    def classify(self, message: str) -> str:
        """Return the most likely intent label."""
        heuristic = self._heuristic_intent(message)
        if heuristic != "GENERAL":
            return heuristic
        embedding_intent = self._embedding_intent(message)
        return embedding_intent or heuristic

    def _heuristic_intent(self, message: str) -> str:
        lowered = message.lower().strip()
        if any(token in lowered for token in ["my name", "cgpa", "language level", "where do i live", "who am i", "remember my name"]):
            return "PROFILE"
        if "project" in lowered or "hvac" in lowered or "flood" in lowered:
            return "PROJECT_INFO"
        if any(token in lowered for token in ["task", "todo", "to-do"]):
            return "TASK"
        if any(token in lowered for token in ["schedule", "event", "calendar", "meeting", "appointment"]):
            return "SCHEDULE"
        if any(token in lowered for token in ["note", "summary", "summarize", "file", "document", "txt file"]):
            return "NOTE"
        return "GENERAL"

    def _embedding_intent(self, message: str) -> str | None:
        model = _load_embedding_model(self.model_name)
        if model is None:
            return None
        try:
            query_embedding = model.encode([message], device="cpu", normalize_embeddings=True)[0]
            best_label = None
            best_score = -1.0
            for label, prototypes in self.PROTOTYPES.items():
                prototype_embeddings = model.encode(prototypes, device="cpu", normalize_embeddings=True)
                for embedding in prototype_embeddings:
                    score = float(sum(a * b for a, b in zip(query_embedding, embedding)))
                    if score > best_score:
                        best_score = score
                        best_label = label
            if best_score >= 0.40:
                return best_label
        except Exception:
            return None
        return None


@lru_cache(maxsize=1)
def _load_embedding_model(model_name: str):
    try:
        from sentence_transformers import SentenceTransformer

        return SentenceTransformer(model_name, device="cpu")
    except Exception:
        return None
