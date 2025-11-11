# utils.py
from __future__ import annotations
import hashlib

def normalize_path_key(path: str) -> str:
    """Remove [n] indices, trim slashes, collapse spaces; keep case."""
    if not path:
        return ""
    parts = []
    for seg in path.strip().split("/"):
        if not seg:
            continue
        if "[" in seg:
            seg = seg.split("[", 1)[0]
        parts.append(seg)
    return "/".join(parts)

def stable_uid(entry_id: str, path_key: str) -> str:
    """Deterministic unique_id from entry_id + normalized path."""
    norm = normalize_path_key(path_key)
    raw = f"{entry_id}::{norm}"
    # Short, deterministic uid
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()[:20]

def path_to_xpath(path: str) -> str:
    """Convert '/ImageChannel/BLC/enabled' -> '//BLC/enabled' safely.
    - Strip [n] indices
    - Remove 'ImageChannel' root
    - Ensure exactly '//' prefix
    """
    if not path:
        return "//"
    parts = []
    for part in path.split('/'):
        if not part:
            continue
        if '[' in part:
            part = part.split('[', 1)[0]
        parts.append(part)
    if parts and parts[0] == "ImageChannel":
        parts = parts[1:]
    rel = "/".join(parts)
    return f"//{rel}"
