"""Thin wrapper over the betting API so tests read as intent, not HTTP plumbing."""
from typing import Any, Optional
import requests
from core.config import settings

class ApiClient:

    def __init__(self, base_url: str = settings.base_url, user_id: Optional[str] = settings.user_id):
        self.base_url = base_url
        self.session = requests.Session()
        if user_id is not None:
            self.session.headers["x-user-id"] = user_id

    def _url(self, path: str) -> str:
        return f"{self.base_url}{path}"

    def get_matches(self) -> requests.Response:
        return self.session.get(self._url("/api/matches"), timeout=settings.timeout)

    def get_balance(self) -> requests.Response:
        return self.session.get(self._url("/api/balance"), timeout=settings.timeout)

    def reset_balance(self) -> requests.Response:
        return self.session.post(self._url("/api/reset-balance"), timeout=settings.timeout)

    def place_bet(self, match_id: Any, selection: Any, stake: Any) -> requests.Response:
        payload = {"matchId": match_id, "selection": selection, "stake": stake}
        return self.session.post(self._url("/api/place-bet"), json=payload, timeout=settings.timeout)


    def balance_value(self) -> float:
        response = self.get_balance()
        response.raise_for_status()
        return response.json()["balance"]

    def first_match(self) -> dict:
        response = self.get_matches()
        response.raise_for_status()
        return response.json()[0]
