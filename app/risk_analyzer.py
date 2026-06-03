from __future__ import annotations

from app.models import EndpointCandidate


class RiskAnalyzer:
    def score(self, candidate: EndpointCandidate) -> EndpointCandidate:
        score = 0
        path = candidate.path.lower()
        if "id" in path:
            score += 3
        if any(token in path for token in ("user", "owner", "account", "tenant")):
            score += 3
        if any(token in path for token in ("admin", "manage", "delete", "update", "edit")):
            score += 4
        if candidate.method in {"POST", "PUT", "PATCH", "DELETE"}:
            score += 2
        candidate.risk_score = score
        candidate.notes = "Auto-scored for authorization testing"
        return candidate

    def rank(self, candidates: list[EndpointCandidate]) -> list[EndpointCandidate]:
        scored = [self.score(candidate) for candidate in candidates]
        return sorted(scored, key=lambda item: item.risk_score, reverse=True)
