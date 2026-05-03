import re


def extract_act_metadata(text: str, source_url: str | None = None) -> dict:
    """Extract structured metadata from a statutory act text."""
    metadata = {
        "act_name": None,
        "section_number": None,
        "year": None,
        "category": None,
    }

    # Try to extract act name (e.g., "Indian Penal Code", "The Contract Act, 1872")
    act_patterns = [
        r"(?i)(?:the\s+)?(\w[\w\s]+(?:act|code|bill|ordinance))(?:,?\s*(\d{4}))?",
    ]
    for pat in act_patterns:
        m = re.search(pat, text[:500])
        if m:
            metadata["act_name"] = m.group(1).strip()
            if m.group(2):
                metadata["year"] = int(m.group(2))
            break

    # Extract section number
    sec_match = re.search(r"(?i)section\s+(\d+[a-zA-Z]?)", text[:500])
    if sec_match:
        metadata["section_number"] = sec_match.group(1)

    # Extract year if not found yet
    if not metadata["year"]:
        year_match = re.search(r"\b(1[89]\d{2}|20[0-2]\d)\b", text[:500])
        if year_match:
            metadata["year"] = int(year_match.group(1))

    # Categorize
    metadata["category"] = _categorize(metadata["act_name"] or text[:300])

    return metadata


def extract_case_metadata(text: str, source_url: str | None = None) -> dict:
    """Extract structured metadata from a case law text."""
    metadata = {
        "case_name": None,
        "court": None,
        "year": None,
        "citations": [],
    }

    # Case name: "X vs Y" or "X v. Y"
    case_match = re.search(r"([\w\s\.]+)\s+(?:vs?\.?|versus)\s+([\w\s\.]+)", text[:500], re.IGNORECASE)
    if case_match:
        metadata["case_name"] = f"{case_match.group(1).strip()} v. {case_match.group(2).strip()}"

    # Court
    court_patterns = [
        (r"(?i)supreme\s+court", "Supreme Court of India"),
        (r"(?i)high\s+court\s+of\s+([\w\s]+?)(?:\s+at|\s*,|\s*\n)", None),
        (r"(?i)([\w\s]+?)\s+high\s+court", None),
        (r"(?i)district\s+court", "District Court"),
        (r"(?i)sessions\s+court", "Sessions Court"),
        (r"(?i)tribunal", "Tribunal"),
    ]
    for pat, fixed in court_patterns:
        m = re.search(pat, text[:1000])
        if m:
            metadata["court"] = fixed or f"High Court of {m.group(1).strip()}"
            break

    # Year
    year_match = re.search(r"\b(19[5-9]\d|20[0-2]\d)\b", text[:500])
    if year_match:
        metadata["year"] = int(year_match.group(1))

    # Citations like (2019) 5 SCC 123 or AIR 2020 SC 456
    citation_patterns = [
        r"\(\d{4}\)\s+\d+\s+SCC\s+\d+",
        r"AIR\s+\d{4}\s+\w+\s+\d+",
        r"\d{4}\s+\(\d+\)\s+\w+\s+\d+",
    ]
    for pat in citation_patterns:
        metadata["citations"].extend(re.findall(pat, text[:2000]))

    return metadata


def _categorize(text: str) -> str:
    """Categorize legal text by domain."""
    text_lower = text.lower()
    categories = {
        "criminal": ["penal code", "ipc", "crpc", "criminal", "murder", "theft", "assault", "bail"],
        "civil": ["civil procedure", "cpc", "suit", "decree", "injunction"],
        "contract": ["contract act", "agreement", "breach", "consideration"],
        "consumer": ["consumer protection", "complaint", "deficiency", "unfair trade"],
        "family": ["marriage", "divorce", "maintenance", "custody", "hindu marriage", "muslim"],
        "property": ["property", "transfer", "rent", "rera", "lease", "mortgage"],
        "evidence": ["evidence act", "witness", "admissibility", "burden of proof"],
        "constitutional": ["constitution", "fundamental right", "article", "writ"],
        "labour": ["labour", "industrial dispute", "wage", "employment"],
    }
    for cat, keywords in categories.items():
        if any(kw in text_lower for kw in keywords):
            return cat
    return "general"
