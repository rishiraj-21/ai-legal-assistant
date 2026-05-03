import json
import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)


def parse_legal_file(filepath: str) -> dict | None:
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        if "---" not in content:
            return None

        header_part, body = content.split("---", 1)
        metadata = {}
        for line in header_part.strip().splitlines():
            if ":" in line:
                key, value = line.split(":", 1)
                metadata[key.strip().lower()] = value.strip()

        body = body.strip()
        if not body:
            return None

        return {"text": body, "metadata": metadata, "source": os.path.basename(filepath)}
    except Exception as e:
        logger.warning("Failed to parse %s: %s", filepath, e)
        return None


def load_legal_dataset(dataset_path: str) -> list[dict]:
    docs = []
    dataset_dir = Path(dataset_path)

    if not dataset_dir.exists():
        logger.warning("Legal dataset directory not found: %s", dataset_path)
        return docs

    for txt_file in dataset_dir.rglob("*.txt"):
        doc = parse_legal_file(str(txt_file))
        if doc:
            docs.append(doc)

    logger.info("Loaded %d legal documents from %s", len(docs), dataset_path)
    return docs
