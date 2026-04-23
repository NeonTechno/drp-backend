from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    app_name: str = "DRP Backend"
    app_version: str = "0.1.0-testnet"
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8000

    # Security
    secret_key: str = "insecure-default-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440

    # OrbitDB
    ipfs_api_url: str = "http://localhost:5001"
    orbitdb_directory: str = "./orbitdb"

    # AI Elder
    ai_elder_enabled: bool = False
    anthropic_api_key: Optional[str] = None

    # Blockchain
    chain_id: str = "drp-testnet-1"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
