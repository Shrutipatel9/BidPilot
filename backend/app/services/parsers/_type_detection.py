import re

_YES_NO_PATTERN = re.compile(r"\(?\s*(yes\s*/\s*no|y\s*/\s*n)\s*\)?", re.IGNORECASE)
_NUMERIC_PATTERN = re.compile(r"\bhow (many|much)\b|\bnumber of\b", re.IGNORECASE)
_ATTACHMENT_PATTERN = re.compile(r"\battach(ed|ment)?\b.*\b(document|evidence|policy|certificate|report)\b", re.IGNORECASE)


def detect_question_type(text: str) -> str:
    """First-pass heuristic guess — good enough since the mapping-confirmation step (1.2's own
    exit criteria) lets a human correct it, not meant to be exhaustive/ML-based."""
    if _YES_NO_PATTERN.search(text):
        return "yes_no"
    if _ATTACHMENT_PATTERN.search(text):
        return "attachment_requested"
    if _NUMERIC_PATTERN.search(text):
        return "numeric"
    return "free_text"
