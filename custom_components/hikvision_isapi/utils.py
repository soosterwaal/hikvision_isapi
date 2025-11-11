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
