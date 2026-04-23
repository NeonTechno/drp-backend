"""
Rights Router — Register and query human rights claims.
"""
import uuid
from datetime import datetime
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Literal

router = APIRouter()

RightsCategory = Literal[
    "education", "healthcare", "shelter", "food", "water",
    "identity", "expression", "privacy", "economic", "governance"
]


class RegisterRightsRequest(BaseModel):
    did: str = Field(..., description="DID of the rights holder")
    category: RightsCategory
    description: str
    evidence_hash: str | None = Field(None, description="IPFS CID of supporting evidence")
    beneficiaries: list[str] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)


class RightsRecord(BaseModel):
    id: str
    did: str
    category: str
    description: str
    evidence_hash: str | None
    beneficiaries: list[str]
    status: str
    registered_at: str
    metadata: dict


_rights_store: dict[str, RightsRecord] = {}


@router.post("/register", response_model=RightsRecord, status_code=201)
async def register_rights(req: RegisterRightsRequest):
    """Register a new human rights claim on the DRP."""
    record = RightsRecord(
        id=f"drp-rights-{uuid.uuid4().hex[:12]}",
        did=req.did,
        category=req.category,
        description=req.description,
        evidence_hash=req.evidence_hash,
        beneficiaries=req.beneficiaries,
        status="pending_verification",
        registered_at=datetime.utcnow().isoformat() + "Z",
        metadata=req.metadata,
    )
    _rights_store[record.id] = record
    return record


@router.get("/{rights_id}", response_model=RightsRecord)
async def get_rights(rights_id: str):
    """Retrieve a rights record by ID."""
    record = _rights_store.get(rights_id)
    if not record:
        raise HTTPException(status_code=404, detail=f"Rights record not found: {rights_id}")
    return record


@router.get("/", response_model=list[RightsRecord])
async def list_rights(category: str | None = None, did: str | None = None):
    """List rights records, optionally filtered."""
    records = list(_rights_store.values())
    if category:
        records = [r for r in records if r.category == category]
    if did:
        records = [r for r in records if r.did == did]
    return records
