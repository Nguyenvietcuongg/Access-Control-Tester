from __future__ import annotations

import time
from urllib.parse import urlparse

from app.models import Account, RequestSpec, ReplayResult
from app.session_manager import SessionManager


class ReplayEngine:
    def __init__(self, session_manager: SessionManager) -> None:
        self.session_manager = session_manager

    def replay(self, account: Account, request: RequestSpec) -> ReplayResult:
        client = self.session_manager.build_client(account)
        parsed = urlparse(request.url)
        target_path = parsed.path or "/"
        if parsed.query:
            target_path = f"{target_path}?{parsed.query}"

        start = time.perf_counter()
        response = client.request(
            method=request.method,
            url=target_path,
            headers=request.headers,
            content=request.raw_body,
        )
        elapsed_ms = (time.perf_counter() - start) * 1000
        return ReplayResult(
            account=account.username,
            status_code=response.status_code,
            headers=dict(response.headers),
            body=response.text,
            elapsed_ms=elapsed_ms,
        )
