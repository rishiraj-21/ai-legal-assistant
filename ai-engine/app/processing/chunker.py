import re

import tiktoken

from config import settings

_encoder = tiktoken.get_encoding("cl100k_base")


def count_tokens(text: str) -> int:
    return len(_encoder.encode(text))


def _split_into_paragraphs(text: str) -> list[str]:
    """Split text on double newlines (paragraphs)."""
    parts = re.split(r"\n\s*\n", text)
    return [p.strip() for p in parts if p.strip()]


def _split_into_sentences(text: str) -> list[str]:
    """Simple sentence splitting on period/question mark/exclamation followed by space."""
    sentences = re.split(r"(?<=[.!?])\s+", text)
    return [s.strip() for s in sentences if s.strip()]


def chunk_text(
    text: str,
    max_tokens: int | None = None,
    overlap_tokens: int | None = None,
) -> list[dict]:
    """
    Chunk text into segments of max_tokens with overlap_tokens overlap.
    Strategy: paragraph-first, then sentence split for oversized paragraphs.
    Returns list of {"text": str, "token_count": int, "chunk_index": int}.
    """
    max_tokens = max_tokens or settings.chunk_size_tokens
    overlap_tokens = overlap_tokens or settings.chunk_overlap_tokens

    paragraphs = _split_into_paragraphs(text)

    # Expand oversized paragraphs into sentences
    units: list[str] = []
    for para in paragraphs:
        if count_tokens(para) <= max_tokens:
            units.append(para)
        else:
            sentences = _split_into_sentences(para)
            units.extend(sentences)

    chunks: list[dict] = []
    current_tokens: list[int] = []
    current_texts: list[str] = []

    for unit in units:
        unit_tokens = count_tokens(unit)

        # If single unit exceeds max, force it as its own chunk
        if unit_tokens > max_tokens:
            if current_texts:
                chunks.append({
                    "text": "\n\n".join(current_texts),
                    "token_count": sum(current_tokens),
                    "chunk_index": len(chunks),
                })
                current_texts = []
                current_tokens = []
            chunks.append({
                "text": unit,
                "token_count": unit_tokens,
                "chunk_index": len(chunks),
            })
            continue

        projected = sum(current_tokens) + unit_tokens
        if projected > max_tokens and current_texts:
            chunks.append({
                "text": "\n\n".join(current_texts),
                "token_count": sum(current_tokens),
                "chunk_index": len(chunks),
            })
            # Overlap: keep trailing units that fit within overlap budget
            overlap_budget = overlap_tokens
            overlap_texts = []
            overlap_tok = []
            for t, tc in reversed(list(zip(current_texts, current_tokens))):
                if sum(overlap_tok) + tc > overlap_budget:
                    break
                overlap_texts.insert(0, t)
                overlap_tok.insert(0, tc)
            current_texts = overlap_texts
            current_tokens = overlap_tok

        current_texts.append(unit)
        current_tokens.append(unit_tokens)

    if current_texts:
        chunks.append({
            "text": "\n\n".join(current_texts),
            "token_count": sum(current_tokens),
            "chunk_index": len(chunks),
        })

    return chunks
