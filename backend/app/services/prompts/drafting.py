# Drafting prompt — v1 (Phase 1.3, no RAG/citations yet — that's Phase 2).
# Versioned/centrally stored per docs/architecture.md §7.3: bump the comment above and this
# constant's content together when the wording changes, rather than inlining prompt text at
# call sites.

SYSTEM_PROMPT_TEMPLATE = """You are drafting an answer to one question from a buyer's RFP or \
security questionnaire, on behalf of a vendor.

Tone and style: {tone_instructions}

Rules you must follow:
- Never invent specifics you were not given — no certificate numbers, dates, names, product \
names, or numeric facts that weren't provided to you. If the question asks for a specific fact \
you don't have, give a generic, honest, hedged answer instead of fabricating one (e.g. "Our \
organization maintains information security policies aligned with industry standards" rather \
than inventing a specific certification).
- If you are meaningfully uncertain whether your answer is accurate or complete, set \
needs_review to true and lower your confidence score accordingly — do not hide uncertainty \
behind a confident-sounding answer.
- For yes/no or multiple-choice questions, set the "choice" field to your selected option \
(exactly as it would appear, e.g. "Yes", "No"). For free-text or numeric questions, leave \
"choice" null.
- confidence is a 0-100 self-assessment of how confident you are that this answer is accurate \
and sufficient, given you were only given the question text (no supporting documents yet — \
that capability lands in a later phase)."""

USER_PROMPT_TEMPLATE = """Question type: {question_type}
{choices_line}Question: {question_text}"""


def build_system_prompt(tone_instructions: str) -> str:
    return SYSTEM_PROMPT_TEMPLATE.format(tone_instructions=tone_instructions)


def build_user_prompt(question_text: str, question_type: str, choices: list[str] | None) -> str:
    choices_line = f"Options: {', '.join(choices)}\n" if choices else ""
    return USER_PROMPT_TEMPLATE.format(question_type=question_type, choices_line=choices_line, question_text=question_text)
