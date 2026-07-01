"""FastAPI runner for CPU-only Phi-3 GGUF chat and MiniLM embeddings."""

from __future__ import annotations

import logging
import os
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, HTTPException
from llama_cpp import Llama
from pydantic import BaseModel, Field
from sentence_transformers import SentenceTransformer


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("phi3_runner")

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(SCRIPT_DIR, "models")

PHI3_REPO = "hf.co/microsoft/Phi-3-mini-4k-instruct-gguf"
DEFAULT_THREADS = int(os.getenv("MODEL_THREADS", "4"))
DEFAULT_CONTEXT = int(os.getenv("MODEL_CONTEXT", "2048"))
DEFAULT_EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL_NAME",
    "sentence-transformers/all-MiniLM-L6-v2",
)

llm: Llama | None = None
embedding_model: SentenceTransformer | None = None
llm_startup_error: str | None = None
embedding_startup_error: str | None = None
loaded_model_path: str | None = None


class ChatRequest(BaseModel):
    prompt: str = Field(..., min_length=1)
    temperature: float = Field(default=0.2, ge=0.0, le=2.0)
    max_tokens: int = Field(default=256, ge=1, le=2048)


class EmbeddingRequest(BaseModel):
    text: str = Field(..., min_length=1)


def _build_phi3_prompt(prompt: str) -> str:
    return f"<|user|>\n{prompt}<|end|>\n<|assistant|>"


def _candidate_sort_key(path: str) -> tuple[int, str]:
    filename = os.path.basename(path).lower()
    preferred = 0 if "phi-3" in filename or "phi3" in filename else 1
    return (preferred, filename)


def _discover_model_file() -> str | None:
    configured = os.getenv("MODEL_FILE", "").strip()
    if configured:
        candidate = configured
        if not os.path.isabs(candidate):
            candidate = os.path.join(MODELS_DIR, candidate)
        candidate = os.path.abspath(candidate)
        return candidate if os.path.isfile(candidate) else None

    if not os.path.isdir(MODELS_DIR):
        return None

    gguf_files: list[str] = []
    for entry in os.listdir(MODELS_DIR):
        path = os.path.join(MODELS_DIR, entry)
        if os.path.isfile(path) and entry.lower().endswith(".gguf"):
            gguf_files.append(path)

    if not gguf_files:
        return None

    gguf_files.sort(key=_candidate_sort_key)
    return gguf_files[0]


def _missing_model_message() -> str:
    configured = os.getenv("MODEL_FILE", "").strip()
    if configured:
        expected_path = configured if os.path.isabs(configured) else os.path.join(MODELS_DIR, configured)
        return (
            "Phi-3 GGUF model file was not found. "
            f"Checked configured MODEL_FILE at '{expected_path}'. "
            f"Mount the '{PHI3_REPO}' GGUF file into '{MODELS_DIR}' and restart the container."
        )

    return (
        "Phi-3 GGUF model file was not found. "
        f"No .gguf files were discovered in '{MODELS_DIR}'. "
        f"Mount a GGUF file from '{PHI3_REPO}' into that directory and restart the container."
    )


def _load_llm() -> tuple[Llama | None, str | None, str | None]:
    model_path = _discover_model_file()
    if model_path is None:
        message = _missing_model_message()
        logger.error(message)
        return None, None, message

    logger.info("Loading Phi-3 model from %s", model_path)
    model = Llama(
        model_path=model_path,
        n_ctx=DEFAULT_CONTEXT,
        n_threads=DEFAULT_THREADS,
        n_gpu_layers=0,
        verbose=False,
    )
    return model, model_path, None


def _load_embedding_model() -> tuple[SentenceTransformer | None, str | None]:
    cache_dir = os.path.join(MODELS_DIR, "sentence-transformers-cache")
    os.makedirs(cache_dir, exist_ok=True)
    logger.info("Loading embedding model %s", DEFAULT_EMBEDDING_MODEL)
    try:
        model = SentenceTransformer(DEFAULT_EMBEDDING_MODEL, cache_folder=cache_dir, device="cpu")
    except Exception as exc:  # pragma: no cover - depends on runtime environment
        message = (
            "Embedding model failed to load. "
            f"Model '{DEFAULT_EMBEDDING_MODEL}' could not be initialized: {exc}"
        )
        logger.error(message)
        return None, message
    return model, None


def _require_llm() -> Llama:
    if llm_startup_error:
        raise HTTPException(status_code=503, detail=llm_startup_error)
    if llm is None:
        raise HTTPException(status_code=503, detail="Phi-3 model is not ready yet.")
    return llm


def _require_embedding_model() -> SentenceTransformer:
    if embedding_startup_error:
        raise HTTPException(status_code=503, detail=embedding_startup_error)
    if embedding_model is None:
        raise HTTPException(status_code=503, detail="Embedding model is not ready yet.")
    return embedding_model


@asynccontextmanager
async def lifespan(_: FastAPI):
    global llm
    global embedding_model
    global llm_startup_error
    global embedding_startup_error
    global loaded_model_path

    os.makedirs(MODELS_DIR, exist_ok=True)

    llm, loaded_model_path, llm_startup_error = _load_llm()
    embedding_model, embedding_startup_error = _load_embedding_model()

    if loaded_model_path:
        logger.info("Phi-3 runner ready with model: %s", loaded_model_path)

    yield


app = FastAPI(
    title="Phi-3 GGUF CPU Runner",
    description="Lightweight CPU-only inference service for Phi-3 chat and MiniLM embeddings.",
    lifespan=lifespan,
)


@app.get("/health")
def health() -> dict[str, Any]:
    return {
        "status": "ok" if llm is not None and embedding_model is not None else "degraded",
        "active_model": os.path.basename(loaded_model_path) if loaded_model_path else DEFAULT_EMBEDDING_MODEL,
        "llm_ready": llm is not None,
        "embeddings_ready": embedding_model is not None,
        "llm_error": llm_startup_error,
        "embedding_error": embedding_startup_error,
    }


@app.post("/v1/chat")
def chat(request: ChatRequest) -> dict[str, Any]:
    model = _require_llm()
    prompt = _build_phi3_prompt(request.prompt)
    response = model(
        prompt,
        max_tokens=request.max_tokens,
        temperature=request.temperature,
        stop=["<|end|>", "<|user|>"],
    )
    text = response["choices"][0]["text"].strip()
    return {
        "text": text,
        "model": os.path.basename(loaded_model_path) if loaded_model_path else "unknown",
    }


@app.post("/v1/embeddings")
def embeddings(request: EmbeddingRequest) -> dict[str, Any]:
    encoder = _require_embedding_model()
    vector = encoder.encode([request.text], convert_to_numpy=True)[0].tolist()
    return {
        "embedding": vector,
        "model": DEFAULT_EMBEDDING_MODEL,
    }
