"""Optional Chroma-backed semantic memory for uploaded notes and user prompts."""

from __future__ import annotations

from functools import lru_cache
from typing import Any

from app.config import get_settings


class SemanticMemoryService:
    """Index and query semantic documents with project metadata filters."""

    COLLECTION_NAME = "semantic_memory"

    def __init__(self) -> None:
        settings = get_settings()
        self.model_name = settings.embedding_model_name
        self.chroma_path = settings.chroma_path

    def index_user_prompt(self, item_id: str, content: str) -> None:
        """Index only user-authored prompts for future semantic lookup."""
        if not content.strip():
            return
        collection = _get_collection(self.chroma_path, self.COLLECTION_NAME)
        model = _load_embedding_model(self.model_name)
        if collection is None or model is None:
            return
        embedding = model.encode([content], device="cpu", normalize_embeddings=True)[0].tolist()
        collection.upsert(
            ids=[f"user:{item_id}"],
            documents=[content],
            embeddings=[embedding],
            metadatas=[{"kind": "user_prompt"}],
        )

    def index_note(
        self,
        note_id: str,
        note_text: str,
        summary: str | None,
        project_id: str | None = None,
    ) -> None:
        """Index uploaded or summarized notes with an optional project firewall."""
        collection = _get_collection(self.chroma_path, self.COLLECTION_NAME)
        model = _load_embedding_model(self.model_name)
        if collection is None or model is None:
            return
        document = summary or note_text
        if not document.strip():
            return
        embedding = model.encode([document], device="cpu", normalize_embeddings=True)[0].tolist()
        metadata: dict[str, Any] = {"kind": "note"}
        if project_id:
            metadata["project_id"] = project_id
        collection.upsert(
            ids=[f"note:{note_id}"],
            documents=[document],
            embeddings=[embedding],
            metadatas=[metadata],
        )

    def query_notes(self, query_text: str, project_id: str | None = None, limit: int = 3) -> list[str]:
        """Retrieve semantically related notes, optionally restricted to one project."""
        collection = _get_collection(self.chroma_path, self.COLLECTION_NAME)
        model = _load_embedding_model(self.model_name)
        if collection is None or model is None or not query_text.strip():
            return []
        embedding = model.encode([query_text], device="cpu", normalize_embeddings=True)[0].tolist()
        where: dict[str, Any] = {"kind": "note"}
        if project_id:
            where["project_id"] = project_id
        result = collection.query(query_embeddings=[embedding], n_results=limit, where=where)
        documents = result.get("documents") or []
        if not documents:
            return []
        return [doc for doc in documents[0] if isinstance(doc, str)]


@lru_cache(maxsize=8)
def _get_collection(path: str, collection_name: str):
    try:
        import chromadb

        client = chromadb.PersistentClient(path=path)
        return client.get_or_create_collection(name=collection_name)
    except Exception:
        return None


@lru_cache(maxsize=1)
def _load_embedding_model(model_name: str):
    try:
        from sentence_transformers import SentenceTransformer

        return SentenceTransformer(model_name, device="cpu")
    except Exception:
        return None
