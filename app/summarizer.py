"""Offline note summarization."""

from __future__ import annotations

from collections import Counter
import re
from typing import Any

from sqlalchemy.orm import Session

from app.encryption import EncryptionManager
from app.llm_engine import LocalLLMEngine
from app.models import NoteRecord
from app.semantic_memory import SemanticMemoryService
from app.utils import generate_id


class NotesSummarizer:
    """Summarize notes locally and persist both note and summary."""

    TABLE_NAME = "notes"
    SUSPICIOUS_TERMS = (
        ".pytest_tmp",
        "lsof",
        "kill command",
        "rm -rf",
        "git pull",
        "chown",
        "chmod",
        "terminate the process",
    )

    def __init__(
        self,
        session: Session,
        llm_engine: LocalLLMEngine | None = None,
        encryption_manager: EncryptionManager | None = None,
        semantic_memory: SemanticMemoryService | None = None,
    ) -> None:
        self.session = session
        self.llm_engine = llm_engine or LocalLLMEngine()
        self.encryption_manager = encryption_manager or EncryptionManager()
        self.semantic_memory = semantic_memory or SemanticMemoryService()

    def create_note(self, title: str, note_text: str, project_id: str | None = None) -> dict[str, Any]:
        """Store a note without generating a summary."""
        note = NoteRecord(
            id=generate_id(),
            title_encrypted=self.encryption_manager.encrypt(title.strip()),
            note_text_encrypted=self.encryption_manager.encrypt(note_text.strip()),
            summary_encrypted=None,
            project_id=project_id,
        )
        self.session.add(note)
        self.session.commit()
        self.session.refresh(note)
        self.semantic_memory.index_note(note.id, note_text, None, project_id=project_id)
        return self._serialize(note)

    def summarize(self, title: str, note_text: str, project_id: str | None = None) -> dict[str, Any]:
        """Summarize note text using Ollama or a deterministic local fallback."""
        summary = self._generate_summary(note_text)
        note = NoteRecord(
            id=generate_id(),
            title_encrypted=self.encryption_manager.encrypt((title.strip() or "Untitled note")),
            note_text_encrypted=self.encryption_manager.encrypt(note_text.strip()),
            summary_encrypted=self.encryption_manager.encrypt(summary),
            project_id=project_id,
        )
        self.session.add(note)
        self.session.commit()
        self.session.refresh(note)
        self.semantic_memory.index_note(note.id, note_text, summary, project_id=project_id)
        return self._serialize(note)

    def list_notes(self) -> list[dict[str, Any]]:
        """Return saved note summaries."""
        notes = self.session.query(NoteRecord).order_by(NoteRecord.updated_at.desc()).all()
        return [self._serialize(note) for note in notes]

    def delete_note(self, note_id: str) -> bool:
        """Delete a stored note."""
        note = self.session.get(NoteRecord, note_id)
        if not note:
            return False
        self.session.delete(note)
        self.session.commit()
        return True

    def _generate_summary(self, note_text: str) -> str:
        """Generate a concise summary locally."""
        prompt = (
            "Summarize the following note in exactly 3 short bullet points. "
            "Use only information present in the note. "
            "Do not include shell commands, troubleshooting steps, unrelated prior conversation, or invented details. "
            "Keep the output readable for a student or teammate.\n\n"
            f"{note_text}"
        )
        candidate = self.llm_engine.generate(
            prompt,
            system_prompt=(
                "You write compact note summaries. "
                "Return only 3 bullet points. "
                "Never mention prior chat context, commands, filesystem operations, Git, or debugging instructions "
                "unless they appear in the note itself."
            ),
            options={
                "temperature": 0.0,
                "top_p": 0.75,
                "num_predict": 120,
                "repeat_penalty": 1.15,
            },
        )
        if (
            "Local summary fallback" in candidate
            or "Ollama is not running" in candidate
            or self._looks_corrupted_summary(note_text, candidate)
        ):
            return self._extractive_summary(note_text)
        return self._normalize_summary(candidate)

    def _extractive_summary(self, note_text: str) -> str:
        """Create a simple extractive summary without a model."""
        sentences = [segment.strip() for segment in note_text.replace("\n", " ").split(".") if segment.strip()]
        if not sentences:
            return "No note content provided."

        stopwords = {
            "the",
            "a",
            "an",
            "and",
            "or",
            "to",
            "of",
            "in",
            "for",
            "on",
            "with",
            "is",
            "are",
            "be",
            "this",
            "that",
        }
        words = [
            word.strip(" ,:;!?").lower()
            for word in note_text.split()
            if word.strip(" ,:;!?").lower() not in stopwords and len(word.strip(" ,:;!?")) > 2
        ]
        scores = Counter(words)
        ranked = sorted(
            sentences,
            key=lambda sentence: sum(scores.get(word.strip(" ,:;!?").lower(), 0) for word in sentence.split()),
            reverse=True,
        )
        selected = ranked[: min(3, len(ranked))]
        return self._normalize_summary("\n".join(f"- {sentence.strip()}." for sentence in selected))

    def _normalize_summary(self, candidate: str) -> str:
        """Normalize model output into at most three readable bullet points."""
        lines = [
            line.strip(" -*\t")
            for line in candidate.replace("\r", "\n").split("\n")
            if line.strip()
        ]
        if not lines:
            return "No readable summary could be generated."

        bullets: list[str] = []
        for line in lines:
            if len(line) < 3:
                continue
            cleaned = re.sub(r"\s+", " ", line).strip(" .")
            if cleaned:
                bullets.append(cleaned)
            if len(bullets) == 3:
                break

        if not bullets:
            return "No readable summary could be generated."

        return "\n".join(f"- {bullet}." for bullet in bullets)

    def _looks_corrupted_summary(self, note_text: str, candidate: str) -> bool:
        """Reject outputs that look unrelated, tool-like, or excessively noisy."""
        lowered_note = note_text.lower()
        lowered_candidate = candidate.lower()

        if len(candidate) > 900 or "```" in candidate:
            return True

        if any(term in lowered_candidate and term not in lowered_note for term in self.SUSPICIOUS_TERMS):
            return True

        note_tokens = {
            token
            for token in re.findall(r"[a-z0-9]{4,}", lowered_note)
            if token not in {"this", "that", "with", "from", "have", "will", "your"}
        }
        candidate_tokens = {
            token
            for token in re.findall(r"[a-z0-9]{4,}", lowered_candidate)
            if token not in {"this", "that", "with", "from", "have", "will", "your"}
        }

        if candidate_tokens and note_tokens:
            overlap = len(candidate_tokens & note_tokens) / max(1, len(candidate_tokens))
            if overlap < 0.18:
                return True

        return False

    def _serialize(self, note: NoteRecord) -> dict[str, Any]:
        """Convert an ORM row into an API payload."""
        return {
            "id": note.id,
            "title": self.encryption_manager.decrypt(note.title_encrypted),
            "note_text": self.encryption_manager.decrypt(note.note_text_encrypted),
            "project_id": note.project_id,
            "summary": (
                self.encryption_manager.decrypt(note.summary_encrypted)
                if note.summary_encrypted
                else None
            ),
            "created_at": note.created_at.isoformat(),
            "updated_at": note.updated_at.isoformat(),
        }
