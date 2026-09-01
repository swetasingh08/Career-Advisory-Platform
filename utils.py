import re


def estimate_score(text, default=75):
    match = re.search(r"(\d{1,3})\s*/\s*100", text or "")
    if match:
        return max(0, min(100, int(match.group(1))))
    match = re.search(r"score[:\s]+(\d{1,3})", text or "", re.IGNORECASE)
    if match:
        return max(0, min(100, int(match.group(1))))
    return default


def safe_text(value):
    return (value or "").strip()


def make_download_name(title):
    cleaned = re.sub(r"[^a-zA-Z0-9]+", "_", title).strip("_").lower()
    return f"{cleaned or 'ardhanarishwar'}_response.md"
