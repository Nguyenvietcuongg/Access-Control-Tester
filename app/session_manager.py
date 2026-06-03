from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
import json

import httpx

from app.models import Account, SessionInfo


class SessionManager:
    def __init__(self, db_path: str = "data/sessions.json") -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.sessions: dict[str, SessionInfo] = {}
        self._load()

    def _load(self) -> None:
        if not self.db_path.exists():
            return
        data = json.loads(self.db_path.read_text(encoding="utf-8"))
        for username, raw in data.items():
            self.sessions[username] = SessionInfo(**raw)

    def _save(self) -> None:
        payload = {username: asdict(session) for username, session in self.sessions.items()}
        self.db_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    def add_session(self, session: SessionInfo) -> None:
        self.sessions[session.username] = session
        self._save()

    def get_session(self, username: str) -> SessionInfo | None:
        return self.sessions.get(username)

    def build_client(self, account: Account) -> httpx.Client:
        session = self.get_session(account.username)
        headers: dict[str, str] = {}
        cookies: dict[str, str] = {}
        if session:
            cookies = session.cookies
            if session.bearer_token:
                headers["Authorization"] = f"Bearer {session.bearer_token}"
            if session.csrf_token:
                headers["X-CSRF-Token"] = session.csrf_token
        return httpx.Client(base_url=account.base_url, headers=headers, cookies=cookies, follow_redirects=True)
