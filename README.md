# DRP Backend — Decentralized Rights Protocol

> FastAPI backend powering the DRP testnet — post-quantum crypto, OrbitDB storage, PoAT engine, and AI-regulated governance.

## Architecture

```
drp-backend/
├── app/
│   ├── main.py           # FastAPI entrypoint
│   ├── config.py         # Environment config
│   ├── routers/
│   │   ├── identity.py   # DID / identity endpoints
│   │   ├── rights.py     # Rights registration & verification
│   │   ├── governance.py # $RIGHTS token voting
│   │   └── activity.py   # PoAT (Proof of Activity) engine
│   ├── models/
│   ├── services/
│   │   ├── orbitdb.py    # OrbitDB integration layer
│   │   ├── crypto.py     # Post-quantum crypto (Kyber/Dilithium)
│   │   └── ai_elder.py   # AI Elder governance module
│   └── middleware/
│       └── auth.py
├── tests/
│   └── test_api.py
├── requirements.txt
├── .env.example
├── render.yaml
└── Dockerfile
```

## Stack

| Layer | Tech |
|---|---|
| API | FastAPI + Uvicorn |
| Storage | OrbitDB (IPFS-backed) |
| Crypto | liboqs (Kyber-1024, Dilithium-3) |
| Auth | JWT + W3C DID |
| Consensus | PoAT (Proof of Activity & Trust) |
| Deployment | Render |

## Quick Start

```bash
git clone https://github.com/NeonTechno/drp-backend
cd drp-backend
cp .env.example .env
pip install -r requirements.txt
uvicorn app.main:app --reload
```

API docs: http://localhost:8000/docs

## Endpoints

| Method | Path | Description |
|---|---|---|
| POST | /identity/register | Create DRP identity (DID) |
| GET | /identity/{did} | Resolve DID document |
| POST | /rights/register | Register a rights claim |
| GET | /rights/{id} | Get rights record |
| POST | /activity/log | Log PoAT activity |
| GET | /governance/proposals | List active governance proposals |
| POST | /governance/vote | Cast governance vote |

## License

Apache 2.0 — Decentralized Rights Protocol
