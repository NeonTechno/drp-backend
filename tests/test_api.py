"""
DRP Backend — API Test Suite
"""
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root():
    r = client.get("/")
    assert r.status_code == 200
    assert r.json()["status"] == "testnet"


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_register_and_resolve_identity():
    reg = client.post("/identity/register", json={
        "public_key": "base64-kyber-pubkey==",
        "alias": "test-user",
        "metadata": {"country": "GH"}
    })
    assert reg.status_code == 201
    did = reg.json()["did"]
    assert did.startswith("did:drp:")

    res = client.get(f"/identity/{did}")
    assert res.status_code == 200
    assert res.json()["did"] == did


def test_register_rights():
    reg = client.post("/identity/register", json={"public_key": "pk==", "alias": "rights-user"})
    did = reg.json()["did"]
    r = client.post("/rights/register", json={
        "did": did,
        "category": "education",
        "description": "Right to free university education",
    })
    assert r.status_code == 201
    assert r.json()["status"] == "pending_verification"


def test_governance_flow():
    reg = client.post("/identity/register", json={"public_key": "pk-gov==", "alias": "voter"})
    did = reg.json()["did"]
    prop = client.post("/governance/proposals", json={
        "proposer_did": did,
        "title": "Enable cross-chain IBC rights",
        "description": "Extend DRP via Cosmos IBC.",
    })
    assert prop.status_code == 201
    prop_id = prop.json()["id"]
    vote = client.post("/governance/vote", json={
        "proposal_id": prop_id,
        "voter_did": did,
        "vote": "yes",
        "rights_weight": 100.0,
    })
    assert vote.status_code == 200
    assert vote.json()["votes_yes"] == 100.0


def test_poat_engine():
    reg = client.post("/identity/register", json={"public_key": "pk-act==", "alias": "activist"})
    did = reg.json()["did"]
    r = client.post("/activity/log", json={
        "did": did,
        "activity_type": "rights_registration",
        "description": "Registered land rights for 3 families in Accra",
    })
    assert r.status_code == 201
    assert r.json()["trust_score_delta"] == 10.0
    trust = client.get(f"/activity/trust/{did}")
    assert trust.status_code == 200
    assert trust.json()["total_trust_score"] == 10.0
