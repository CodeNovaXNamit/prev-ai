"""Optional Chroma-backed semantic memory for notes and distilled personal facts."""

from __future__ import annotations

from functools import lru_cache
from typing import Any

import requests

from app.config import get_settings


class SemanticMemoryService:
    """Index and query semantic documents with metadata filters."""

    COLLECTION_NAME = "semantic_memory"

    def __init__(self) -> None:
        settings = get_settings()
        self.chroma_path = settings.chroma_path
        self.model_name = settings.embedding_model_name
        self.model_runner_url = settings.model_runner_url.rstrip("/")

    def index_user_prompt(self, item_id: str, content: str) -> None:
        """Legacy entry point kept intentionally inert to avoid indexing raw chat noise."""
        return None

    def index_personal_fact(
        self,
        item_id: str,
        fact_text: str,
        *,
        key: str,
        importance: int,
        source: str = "user_input",
    ) -> None:
        """Index one cleaned personal fact for semantic retrieval."""
        if not fact_text.strip():
            return
        collection = _get_collection(self.chroma_path, self.COLLECTION_NAME)
        embedding = _embed_text(self.model_runner_url, self.model_name, fact_text)
        if collection is None or embedding is None:
            return
        collection.upsert(
            ids=[f"fact:{item_id}"],
            documents=[fact_text],
            embeddings=[embedding],
            metadatas=[{"kind": "personal_fact", "key": key, "importance": int(importance), "source": source}],
        )

    def query_personal_facts(self, query_text: str, limit: int = 4, source: str = "user_input") -> list[dict[str, Any]]:
        """Retrieve semantically related personal facts."""
        collection = _get_collection(self.chroma_path, self.COLLECTION_NAME)
        embedding = _embed_text(self.model_runner_url, self.model_name, query_text)
        if collection is None or embedding is None or not query_text.strip():
            return []
        result = collection.query(
            query_embeddings=[embedding],
            n_results=limit,
            where={"$and": [{"kind": "personal_fact"}, {"source": source}]},
        )
        documents = result.get("documents") or [[]]
        metadatas = result.get("metadatas") or [[]]
        facts: list[dict[str, Any]] = []
        for document, metadata in zip(documents[0], metadatas[0], strict=False):
            if not isinstance(document, str):
                continue
            facts.append(
                {
                    "text": document,
                    "key": (metadata or {}).get("key", ""),
                    "importance": int((metadata or {}).get("importance", 3)),
                    "source": (metadata or {}).get("source", source),
                }
            )
        return facts

    def index_note(
        self,
        note_id: str,
        note_text: str,
        summary: str | None,
        project_id: str | None = None,
    ) -> None:
        """Index uploaded or summarized notes with an optional project firewall."""
        collection = _get_collection(self.chroma_path, self.COLLECTION_NAME)
        document = summary or note_text
        if not document.strip():
            return
        embedding = _embed_text(self.model_runner_url, self.model_name, document)
        if collection is None or embedding is None:
            return
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
        embedding = _embed_text(self.model_runner_url, self.model_name, query_text)
        if collection is None or embedding is None or not query_text.strip():
            return []
        where = _build_note_query_filter(project_id)
        result = collection.query(query_embeddings=[embedding], n_results=limit, where=where)
        documents = result.get("documents") or []
        if not documents:
            return []
        return [doc for doc in documents[0] if isinstance(doc, str)]


def _build_note_query_filter(project_id: str | None) -> dict[str, Any]:
    """Build a Chroma-compatible metadata filter for note queries."""
    if project_id:
        return {
            "$and": [
                {"kind": "note"},
                {"project_id": project_id},
            ]
        }
    return {"kind": "note"}


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


def _embed_text(model_runner_url: str, model_name: str, text: str) -> list[float] | None:
    """Get one embedding from the runner, with an optional local fallback."""
    if not text.strip():
        return None
    try:
        response = requests.post(
            f"{model_runner_url}/v1/embeddings",
            json={"text": text},
            timeout=10,
        )
        response.raise_for_status()
        payload = response.json()
        embedding = payload.get("embedding")
        if isinstance(embedding, list) and embedding:
            return [float(value) for value in embedding]
    except requests.RequestException:
        pass
    except (TypeError, ValueError):
        pass

    model = _load_embedding_model(model_name)
    if model is None:
        return None
    return model.encode([text], device="cpu", normalize_embeddings=True)[0].tolist()
