import asyncio
from functools import lru_cache

import boto3
from botocore.exceptions import ClientError
from fastapi import HTTPException, UploadFile, status

from app.core.config import settings

MAX_UPLOAD_BYTES = 20 * 1024 * 1024  # 20MB — generous ceiling for questionnaire files


@lru_cache
def _client():
    return boto3.client(
        "s3",
        endpoint_url=settings.s3_endpoint_url,
        aws_access_key_id=settings.aws_access_key_id,
        aws_secret_access_key=settings.aws_secret_access_key,
    )


async def ensure_bucket() -> None:
    """Idempotent — called once from app/main.py's lifespan handler on startup instead of
    adding a Docker Compose init container. Safe to call from multiple workers concurrently."""
    client = _client()
    try:
        await asyncio.to_thread(client.head_bucket, Bucket=settings.s3_bucket)
    except ClientError as exc:
        error_code = exc.response.get("Error", {}).get("Code")
        if error_code not in ("404", "NoSuchBucket"):
            raise
        try:
            await asyncio.to_thread(client.create_bucket, Bucket=settings.s3_bucket)
        except ClientError as create_exc:
            # Benign race: another worker created it between head_bucket and create_bucket.
            if create_exc.response.get("Error", {}).get("Code") != "BucketAlreadyOwnedByYou":
                raise


async def upload_bytes(key: str, data: bytes, content_type: str) -> None:
    await asyncio.to_thread(
        _client().put_object, Bucket=settings.s3_bucket, Key=key, Body=data, ContentType=content_type
    )


async def download_bytes(key: str) -> bytes:
    obj = await asyncio.to_thread(_client().get_object, Bucket=settings.s3_bucket, Key=key)
    # obj["Body"] is a blocking urllib3 stream — .read() must also go through to_thread.
    return await asyncio.to_thread(obj["Body"].read)


async def delete_object(key: str) -> None:
    await asyncio.to_thread(_client().delete_object, Bucket=settings.s3_bucket, Key=key)


async def presigned_get_url(key: str, expires_in: int = 3600) -> str:
    return await asyncio.to_thread(
        _client().generate_presigned_url,
        "get_object",
        Params={"Bucket": settings.s3_bucket, "Key": key},
        ExpiresIn=expires_in,
    )


async def read_upload_capped(file: UploadFile, max_bytes: int = MAX_UPLOAD_BYTES) -> bytes:
    """Starlette's UploadFile.read() is already async — no to_thread needed here, only for
    the boto3 calls above."""
    chunks: list[bytes] = []
    total = 0
    while chunk := await file.read(1024 * 1024):
        total += len(chunk)
        if total > max_bytes:
            raise HTTPException(status.HTTP_413_CONTENT_TOO_LARGE, "file too large")
        chunks.append(chunk)
    return b"".join(chunks)
