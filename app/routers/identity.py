"""
Identity Router — DID registration and resolution.
"""
import uuid
from datetime import datetime
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter()


class RegisterIdentityRequest(BaseModel):
    public_key: str = Field(..., description="Post-quantum public key (base64)")
    alias: str | None = Field(None, description="Optional human-readable alias")
    metadata: dict = Field(default_factory=dict, description="Extra identity metadata")


class IdentityResponse(BaseModel):
    did: str
    public_key: str
    alias: str | None
    created_at: str
    metadata: dict


# In-memory store for testnet (replace with OrbitDB)
_identity_store: dict[str, IdentityResponse] = {}


@router.post("/register", response_model=IdentityResponse, status_code=201)
async def register_identity(req: RegisterIdentityRequest):
    """Create a new DRP decentralized identity (DID)."""
    did = f"did:drp:{uuid.uuid4().hex}"
    identity = IdentityResponse(
        did=did,
        public_key=req.public_key,
        alias=req.alias,
        created_at=datetime.utcnow().isoformat() + "Z",
        metadata=req.metadata,
    )
    _identity_store[did] = identity
    return identity


@router.get("/{did}", response_model=IdentityResponse)
async def resolve_identity(did: str):
    """Resolve a DRP DID to its identity document."""
    identity = _identity_store.get(did)
    if not identity:
        raise HTTPException(status_code=404, detail=f"DID not found: {did}")
    return identity


@router.get("/", response_model=list[IdentityResponse])
async def list_identities():
    """List all registered identities (testnet only)."""
    return list(_identity_store.values())
