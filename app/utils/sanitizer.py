"""Input sanitization helpers for noisy logs and shell-like text."""

from __future__ import annotations

from dataclasses import dataclass
import re


BLACKLISTED_PATTERNS: tuple[re.Pattern[str], ...] = tuple(
    re.compile(pattern, flags=re.IGNORECASE)
    for pattern in (
        r"\bpytest\b",
        r"\btraceback\b",
        r"\blsof\b",
        r"\bgit pull\b",
        r"\brm\s+-rf\b",
        r"\bpermission denied\b",
    )
)
SHELL_COMMAND_PATTERN = re.compile(
    r"^(?:\$|#)?\s*(?:pytest|python|pip|npm|npx|node|git|docker|docker-compose|docker compose|"
    r"rm|cp|mv|chmod|chown|kill|ps|cat|ls|cd|export|set|echo|grep|find|alembic|uvicorn)\b",
    flags=re.IGNORECASE,
)
ENV_VAR_PATTERN = re.compile(r"\b[A-Z][A-Z0-9_]{2,}\s*=\s*[^\s]+")


@dataclass(frozen=True)
class SanitizedText:
    """Sanitized text plus noise metadata."""

    original_text: str
    cleaned_text: str
    noise_ratio: float
    matched_lines: int
    total_lines: int

    @property
    def is_system_log(self) -> bool:
        return self.noise_ratio > 0.30


def sanitize_text(text: str) -> SanitizedText:
    """Strip obvious shell/log noise and compute a noise ratio."""
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = [line for line in normalized.split("\n") if line.strip()]
    if not lines:
        return SanitizedText(original_text=text, cleaned_text=text.strip(), noise_ratio=0.0, matched_lines=0, total_lines=0)

    cleaned_lines: list[str] = []
    matched_lines = 0
    for line in lines:
        stripped = line.strip()
        if _looks_like_noise(stripped):
            matched_lines += 1
            continue
        cleaned_lines.append(stripped)

    cleaned_text = "\n".join(cleaned_lines).strip()
    if not cleaned_text:
        cleaned_text = " ".join(line.strip() for line in lines[:2]).strip()

    return SanitizedText(
        original_text=text,
        cleaned_text=cleaned_text,
        noise_ratio=matched_lines / max(1, len(lines)),
        matched_lines=matched_lines,
        total_lines=len(lines),
    )


def count_environment_variables(text: str) -> int:
    """Count env-var assignments in a text block."""
    return len(ENV_VAR_PATTERN.findall(text))


def count_shell_commands(text: str) -> int:
    """Count shell-like command lines in a text block."""
    return sum(1 for line in text.splitlines() if SHELL_COMMAND_PATTERN.search(line.strip()))


def _looks_like_noise(line: str) -> bool:
    if any(pattern.search(line) for pattern in BLACKLISTED_PATTERNS):
        return True
    if SHELL_COMMAND_PATTERN.search(line):
        return True
    if ENV_VAR_PATTERN.search(line):
        return True
    return False
