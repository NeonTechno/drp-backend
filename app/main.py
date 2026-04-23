"""
DRP Backend — Main FastAPI Application
Decentralized Rights Protocol Testnet
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse

from app.config import settings
from app.routers import identity, rights, governance, activity

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "Backend API for the Decentralized Rights Protocol — "
        "post-quantum crypto, OrbitDB storage, PoAT consensus, and AI-regulated governance."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
    default_response_class=ORJSONResponse,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(identity.router, prefix="/identity", tags=["Identity"])
app.include_router(rights.router, prefix="/rights", tags=["Rights"])
app.include_router(governance.router, prefix="/governance", tags=["Governance"])
app.include_router(activity.router, prefix="/activity", tags=["Activity / PoAT"])


@app.get("/", tags=["Root"])
async def root():
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "chain": settings.chain_id,
        "status": "testnet",
        "docs": "/docs",
    }


@app.get("/health", tags=["Root"])
async def health():
    return {"status": "ok", "version": settings.app_version}
