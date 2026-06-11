"""
spotify_client.py
Autentica com a Spotify Web API via OAuth 2.0 (refresh_token flow)
"""
from __future__ import annotations
import base64, logging, os
from typing import Optional
import requests

log = logging.getLogger(__name__)
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_API_BASE  = "https://api.spotify.com/v1"

class SpotifyClient:
    def __init__(self, client_id: str, client_secret: str, refresh_token: str) -> None:
        self.client_id     = client_id
        self.client_secret = client_secret
        self.refresh_token = refresh_token
        self._access_token: Optional[str] = None

    def _get_access_token(self) -> str:
        credentials = base64.b64encode(f"{self.client_id}:{self.client_secret}".encode()).decode()
        resp = requests.post(
            SPOTIFY_TOKEN_URL,
            headers={"Authorization": f"Basic {credentials}", "Content-Type": "application/x-www-form-urlencoded"},
            data={"grant_type": "refresh_token", "refresh_token": self.refresh_token},
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()["access_token"]

    def _headers(self) -> dict:
        if not self._access_token:
            self._access_token = self._get_access_token()
        return {"Authorization": f"Bearer {self._access_token}"}

    def _get(self, endpoint: str, params: dict | None = None) -> dict:
        resp = requests.get(f"{SPOTIFY_API_BASE}{endpoint}", headers=self._headers(), params=params or {}, timeout=10)
        resp.raise_for_status()
        return resp.json()

    def get_current_user(self) -> dict:
        return self._get("/me")

    def get_now_playing(self) -> dict | None:
        resp = requests.get(f"{SPOTIFY_API_BASE}/me/player/currently-playing", headers=self._headers(), timeout=10)
        if resp.status_code == 204 or not resp.content:
            return None
        return resp.json()

    def get_recently_played(self, limit: int = 50) -> dict:
        return self._get("/me/player/recently-played", params={"limit": limit})

    def get_top_tracks(self, time_range: str = "short_term", limit: int = 5) -> dict:
        return self._get("/me/top/tracks", params={"time_range": time_range, "limit": limit})

    def get_top_artists(self, time_range: str = "short_term", limit: int = 5) -> dict:
        return self._get("/me/top/artists", params={"time_range": time_range, "limit": limit})

    def get_album_art_b64(self, image_url: str) -> str:
        resp = requests.get(image_url, timeout=10)
        resp.raise_for_status()
        return base64.b64encode(resp.content).decode()

    def get_estimated_listening_time(self) -> str:
        """Estima tempo ouvido com base nas ultimas 50 musicas."""
        try:
            data = self.get_recently_played(limit=50)
            items = data.get("items", [])
            total_ms = sum(item["track"]["duration_ms"] for item in items)
            total_min = total_ms // 60000
            hours = total_min // 60
            mins  = total_min % 60
            if hours > 0:
                return f"{hours}h {mins}min"
            return f"{mins}min"
        except Exception:
            return "—"

def from_env() -> SpotifyClient:
    return SpotifyClient(
        os.environ["SPOTIFY_CLIENT_ID"],
        os.environ["SPOTIFY_CLIENT_SECRET"],
        os.environ["SPOTIFY_REFRESH_TOKEN"],
    )