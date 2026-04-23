"""
Activity Router — Proof of Activity & Trust (PoAT) engine.
"""
import uuid
from datetime import datetime
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Literal

router = APIRouter()

ActivityType = Literal[
    "rights_registration", "governance_vote", "resource_distribution",
    "identity_verification", "community_validation", "data_contribution"
]

TRUST_WEIGHTS: dict[str, float] = {
    "rights_registration": 10.0,
    "governance_vote": 5.0,
    "resource_distribution": 8.0,
    "identity_verification": 15.0,
    "community_validation": 6.0,
    "data_contribution": 4.0,
}


class LogActivityRequest(BaseModel):
    did: str
    activity_type: ActivityType
    description: str
    proof_hash: str | None = Field(None, description="IPFS CID or hash of proof document")
    metadata: dict = Field(default_factory=dict)


class ActivityRecord(BaseModel):
    id: str
    did: str
    activity_type: str
    description: str
    proof_hash: str | None
    trust_score_delta: float
    logged_at: str
    metadata: dict


class TrustProfile(BaseModel):
    did: str
    total_trust_score: float
    activity_count: int
    last_active: str


_activity_log: list[ActivityRecord] = []
_trust_profiles: dict[str, TrustProfile] = {}


@router.post("/log", response_model=ActivityRecord, status_code=201)
async def log_activity(req: LogActivityRequest):
    """Log a PoAT activity and update the actor's trust score."""
    delta = TRUST_WEIGHTS.get(req.activity_type, 1.0)
    record = ActivityRecord(
        id=f"drp-act-{uuid.uuid4().hex[:12]}",
        did=req.did,
        activity_type=req.activity_type,
        description=req.description,
        proof_hash=req.proof_hash,
        trust_score_delta=delta,
        logged_at=datetime.utcnow().isoformat() + "Z",
        metadata=req.metadata,
    )
    _activity_log.append(record)
    now = datetime.utcnow().isoformat() + "Z"
    if req.did not in _trust_profiles:
        _trust_profiles[req.did] = TrustProfile(
            did=req.did, total_trust_score=0.0, activity_count=0, last_active=now
        )
    profile = _trust_profiles[req.did]
    profile.total_trust_score += delta
    profile.activity_count += 1
    profile.last_active = now
    return record


@router.get("/trust/{did}", response_model=TrustProfile)
async def get_trust_profile(did: str):
    """Get the PoAT trust profile for a DID."""
    profile = _trust_profiles.get(did)
    if not profile:
        raise HTTPException(status_code=404, detail=f"No activity found for DID: {did}")
    return profile


@router.get("/log", response_model=list[ActivityRecord])
async def get_activity_log(did: str | None = None, limit: int = 50):
    """Retrieve PoAT activity log entries."""
    entries = _activity_log
    if did:
        entries = [a for a in entries if a.did == did]
    return entries[-limit:]


@router.get("/leaderboard", response_model=list[TrustProfile])
async def trust_leaderboard(limit: int = 20):
    """Get the top trust score holders."""
    sorted_profiles = sorted(
        _trust_profiles.values(), key=lambda p: p.total_trust_score, reverse=True
    )
    return sorted_profiles[:limit]
