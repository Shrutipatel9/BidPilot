from google import genai
from google.genai import types
from openai import AsyncOpenAI

from app.core.config import settings

EMBEDDING_DIMENSIONS = 768


class EmbeddingError(Exception):
    """Raised after both the primary attempt and one retry fail to produce an embedding."""


_openai_client = AsyncOpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None
_gemini_client = genai.Client(api_key=settings.gemini_api_key) if settings.gemini_api_key else None


async def _embed_openai(text: str) -> list[float]:
    response = await _openai_client.embeddings.create(
        model=settings.openai_embedding_model, input=text, dimensions=EMBEDDING_DIMENSIONS
    )
    return response.data[0].embedding


async def _embed_gemini(text: str) -> list[float]:
    response = await _gemini_client.aio.models.embed_content(
        model=settings.gemini_embedding_model,
        contents=text,
        config=types.EmbedContentConfig(output_dimensionality=EMBEDDING_DIMENSIONS),
    )
    return response.embeddings[0].values


async def generate_embedding(text: str) -> list[float]:
    if _openai_client is not None:
        provider = _embed_openai
    elif _gemini_client is not None:
        provider = _embed_gemini
    else:
        raise EmbeddingError("no embedding provider configured — set OPENAI_API_KEY or GEMINI_API_KEY")

    # One retry on any failure, same policy as llm_provider.generate_draft_answer.
    try:
        return await provider(text)
    except Exception as first_exc:
        try:
            return await provider(text)
        except Exception as retry_exc:
            raise EmbeddingError(f"embedding failed after retry: {retry_exc}") from first_exc
