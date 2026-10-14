"""Central configuration, read from environment variables (or a local .env file)."""
import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    base_url: str = os.getenv("QA_BASE_URL").rstrip("/")
    user_id: str = os.getenv("QA_USER_ID")
    if user_id in {"", None, "<user-id>"}:
            raise RuntimeError(
                "USER_ID is not set. Copy .env.example to .env and put your user id"
            )
    headless: bool = os.getenv("QA_HEADLESS","true").lower() == "true"
    timeout: int = int(os.getenv("QA_TIMEOUT", "10"))

    @property
    def ui_url(self) -> str:
        return f"{self.base_url}/?user-id={self.user_id}"


settings = Settings()

