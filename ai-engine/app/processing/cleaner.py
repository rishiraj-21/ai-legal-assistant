import re

import bleach


def html_to_text(html: str) -> str:
    """Convert HTML to clean text, stripping all tags and normalizing whitespace."""
    # Strip HTML tags
    text = bleach.clean(html, tags=[], strip=True)
    # Decode common HTML entities
    text = text.replace("&nbsp;", " ").replace("&amp;", "&")
    text = text.replace("&lt;", "<").replace("&gt;", ">")
    return normalize_whitespace(text)


def normalize_whitespace(text: str) -> str:
    """Collapse multiple whitespace/newlines into single spaces, strip edges."""
    text = re.sub(r"\r\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    lines = [line.strip() for line in text.splitlines()]
    return "\n".join(lines).strip()


def strip_boilerplate(text: str) -> str:
    """Remove common boilerplate patterns from Indian legal websites."""
    patterns = [
        r"(?i)disclaimer\s*:.*?(?=\n\n|\Z)",
        r"(?i)copyright\s*©.*?(?=\n\n|\Z)",
        r"(?i)all rights reserved.*?(?=\n\n|\Z)",
        r"(?i)website\s*:?\s*https?://\S+",
        r"(?i)last\s+updated\s*:.*?(?=\n|\Z)",
        r"(?i)source\s*:?\s*https?://\S+",
    ]
    for pat in patterns:
        text = re.sub(pat, "", text)
    return normalize_whitespace(text)


def clean_legal_text(raw: str, is_html: bool = False) -> str:
    """Full cleaning pipeline."""
    if is_html:
        text = html_to_text(raw)
    else:
        text = raw
    text = strip_boilerplate(text)
    return normalize_whitespace(text)
