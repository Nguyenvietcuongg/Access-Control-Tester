from __future__ import annotations

from pathlib import Path
import json

from app.models import EndpointCandidate, Finding


class Storage:
    def __init__(self, root: str = "data") -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def save_endpoints(self, endpoints: list[EndpointCandidate], filename: str = "endpoints.json") -> Path:
        path = self.root / filename
        payload = [endpoint.__dict__ for endpoint in endpoints]
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        return path

    def save_findings(self, findings: list[Finding], filename: str = "findings.json") -> Path:
        path = self.root / filename
        payload = [finding.__dict__ for finding in findings]
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        return path
