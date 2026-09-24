from google import genai
from google.genai import types
from openai import AsyncOpenAI
from pydantic import BaseModel, Field

from app.core.config import settings
from app.services.prompts.drafting import build_grounded_user_prompt, build_system_prompt


class DraftAnswer(BaseModel):
    answer_text: str
    confidence: int = Field(ge=0, le=100)
    choice: str | None = None
    needs_review: bool


class LLMDraftError(Exception):
    """Raised after both the primary attempt and one retry fail to produce a valid DraftAnswer."""


_openai_client = AsyncOpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None
_gemini_client = genai.Client(api_key=settings.gemini_api_key) if settings.gemini_api_key else None


async def _draft_openai(question_text, question_type, choices, tone_instructions, retrieved_chunks) -> DraftAnswer:
    response = await _openai_client.chat.completions.parse(
        model=settings.openai_model,
        messages=[
            {"role": "system", "content": build_system_prompt(tone_instructions)},
            {
                "role": "user",
                "content": build_grounded_user_prompt(question_text, question_type, choices, retrieved_chunks),
            },
        ],
        response_format=DraftAnswer,
    )
    parsed = response.choices[0].message.parsed
    if parsed is None:
        raise LLMDraftError("OpenAI returned no parsed structured output")
    return parsed


async def _draft_gemini(question_text, question_type, choices, tone_instructions, retrieved_chunks) -> DraftAnswer:
    response = await _gemini_client.aio.models.generate_content(
        model=settings.gemini_model,
        contents=build_grounded_user_prompt(question_text, question_type, choices, retrieved_chunks),
        config=types.GenerateContentConfig(
            system_instruction=build_system_prompt(tone_instructions),
            response_mime_type="application/json",
            response_schema=DraftAnswer,
        ),
    )
    if response.parsed is None:
        raise LLMDraftError("Gemini returned no parsed structured output")
    return response.parsed if isinstance(response.parsed, DraftAnswer) else DraftAnswer.model_validate(response.parsed)


async def generate_draft_answer(
    question_text: str,
    question_type: str,
    choices: list[str] | None,
    tone_instructions: str,
    retrieved_chunks: list,
) -> DraftAnswer:
    if _openai_client is not None:
        provider = _draft_openai
    elif _gemini_client is not None:
        provider = _draft_gemini
    else:
        raise LLMDraftError("no LLM provider configured — set OPENAI_API_KEY or GEMINI_API_KEY")

    # One retry on any failure — malformed/invalid structured output, a transient provider
    # error (rate limit, 5xx, network), all treated the same way. If the retry also fails,
    # the caller (drafting_service, per-question) writes a needs_review placeholder rather
    # than aborting the whole batch.
    try:
        return await provider(question_text, question_type, choices, tone_instructions, retrieved_chunks)
    except Exception as first_exc:
        try:
            return await provider(question_text, question_type, choices, tone_instructions, retrieved_chunks)
        except Exception as retry_exc:
            raise LLMDraftError(f"drafting failed after retry: {retry_exc}") from first_exc
