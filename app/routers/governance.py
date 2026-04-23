"""
Governance Router — $RIGHTS token governance proposals and voting.
"""
import uuid
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Literal

router = APIRouter()

ProposalStatus = Literal["active", "passed", "rejected", "pending"]


class CreateProposalRequest(BaseModel):
    proposer_did: str
    title: str
    description: str
    voting_period_hours: int = Field(72, ge=1, le=720)
    metadata: dict = Field(default_factory=dict)


class VoteRequest(BaseModel):
    proposal_id: str
    voter_did: str
    vote: Literal["yes", "no", "abstain"]
    rights_weight: float = Field(1.0, ge=0.001, description="$RIGHTS token voting weight")


class Proposal(BaseModel):
    id: str
    proposer_did: str
    title: str
    description: str
    status: ProposalStatus
    votes_yes: float
    votes_no: float
    votes_abstain: float
    total_votes: int
    created_at: str
    expires_at: str
    metadata: dict


_proposals: dict[str, Proposal] = {}
_votes: dict[str, dict] = {}


@router.post("/proposals", response_model=Proposal, status_code=201)
async def create_proposal(req: CreateProposalRequest):
    """Create a new governance proposal."""
    now = datetime.utcnow()
    proposal = Proposal(
        id=f"drp-prop-{uuid.uuid4().hex[:10]}",
        proposer_did=req.proposer_did,
        title=req.title,
        description=req.description,
        status="active",
        votes_yes=0.0,
        votes_no=0.0,
        votes_abstain=0.0,
        total_votes=0,
        created_at=now.isoformat() + "Z",
        expires_at=(now + timedelta(hours=req.voting_period_hours)).isoformat() + "Z",
        metadata=req.metadata,
    )
    _proposals[proposal.id] = proposal
    _votes[proposal.id] = {}
    return proposal


@router.get("/proposals", response_model=list[Proposal])
async def list_proposals(status: str | None = None):
    """List governance proposals."""
    proposals = list(_proposals.values())
    if status:
        proposals = [p for p in proposals if p.status == status]
    return proposals


@router.get("/proposals/{proposal_id}", response_model=Proposal)
async def get_proposal(proposal_id: str):
    """Get a specific governance proposal."""
    proposal = _proposals.get(proposal_id)
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")
    return proposal


@router.post("/vote", status_code=200)
async def cast_vote(req: VoteRequest):
    """Cast a vote on an active governance proposal."""
    proposal = _proposals.get(req.proposal_id)
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")
    if proposal.status != "active":
        raise HTTPException(status_code=400, detail="Proposal is not active")
    voter_record = _votes.get(req.proposal_id, {})
    if req.voter_did in voter_record:
        raise HTTPException(status_code=409, detail="Already voted on this proposal")
    voter_record[req.voter_did] = req.vote
    _votes[req.proposal_id] = voter_record
    if req.vote == "yes":
        proposal.votes_yes += req.rights_weight
    elif req.vote == "no":
        proposal.votes_no += req.rights_weight
    else:
        proposal.votes_abstain += req.rights_weight
    proposal.total_votes += 1
    return {
        "status": "vote_recorded",
        "proposal_id": req.proposal_id,
        "votes_yes": proposal.votes_yes,
        "votes_no": proposal.votes_no,
        "votes_abstain": proposal.votes_abstain,
        "total_votes": proposal.total_votes,
    }
