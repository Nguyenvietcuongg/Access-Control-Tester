from __future__ import annotations

from pathlib import Path
import re

from app.models import EndpointCandidate


class SourceScanner:
    ROUTE_PATTERN = re.compile(r'@(?:app|router)\.(get|post|put|delete|patch)\(["\']([^"\']+)["\']\)', re.IGNORECASE)

    def scan(self, source_path: str) -> list[EndpointCandidate]:
        candidates: list[EndpointCandidate] = []
        base = Path(source_path)
        for file_path in base.rglob("*.py"):
            text = file_path.read_text(encoding="utf-8", errors="ignore")
            for match in self.ROUTE_PATTERN.finditer(text):
                method = match.group(1).upper()
                path = match.group(2)
                candidates.append(EndpointCandidate(method=method, path=path, source_file=str(file_path)))
        return candidates
