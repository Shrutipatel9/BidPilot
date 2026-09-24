import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.auth import router as auth_router
from app.api.invitations import router as invitations_router
from app.api.orgs import router as orgs_router
from app.api.projects import router as projects_router
from app.core.config import settings
from app.core.storage import ensure_bucket

logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await ensure_bucket()
    yield


app = FastAPI(title="BidPilot API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    # Bearer-token auth (Authorization header), not cookies — no credentials mode needed.
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
    # Browsers hide response headers from JS on cross-origin requests unless explicitly exposed —
    # the project export download reads the server-set filename out of this header.
    expose_headers=["Content-Disposition"],
)

app.include_router(auth_router)
app.include_router(orgs_router)
app.include_router(invitations_router)
app.include_router(projects_router)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/")
def root():
    return {"message": "BidPilot API"}
