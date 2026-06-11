from __future__ import annotations

from app.models import EndpointCandidate


class RiskAnalyzer:
    def score(self, candidate: EndpointCandidate) -> EndpointCandidate:
        score = 0
        path = candidate.path.lower()
        source = candidate.source_file.lower()
        line_text = candidate.matched_text.lower()
        param_name = candidate.param_name.lower()

        if any(token in path for token in ("id", "user", "owner", "account", "tenant", "profile", "order", "product")):
            score += 3
        if any(token in param_name for token in ("id", "user", "owner", "account", "order", "product")):
            score += 3
        if any(token in path for token in ("admin", "manage", "delete", "update", "edit", "settings", "role", "permission")):
            score += 4
        if any(token in source for token in ("auth", "access", "permission", "role")):
            score += 2
        if candidate.method in {"POST", "PUT", "PATCH", "DELETE"}:
            score += 2
        if candidate.method == "GET" and any(token in path for token in ("detail", "view", "show", "item")):
            score += 1
        if candidate.line_number > 0:
            score += 1
        if line_text and any(token in line_text for token in ("$_get", "$_post", "req.body", "req.query")):
            score += 1

        candidate.risk_score = score
        candidate.category = self.category(candidate)
        candidate.reason = self.reason(candidate)
        candidate.notes = "Auto-scored for IDOR / Broken Access Control / Privilege Escalation"
        return candidate

    def category(self, candidate: EndpointCandidate) -> str:
        path = candidate.path.lower()
        source = candidate.source_file.lower()
        param = candidate.param_name.lower()

        if any(token in path for token in ("admin", "manage", "role", "permission")):
            return "Broken Access Control"
        if any(token in source for token in ("auth", "login", "session")) and candidate.method in {"POST", "PUT", "DELETE", "PATCH"}:
            return "Privilege Escalation"
        if any(token in path for token in ("id", "user", "owner", "account", "order", "product")) or any(token in param for token in ("id", "user", "owner", "account", "order", "product")):
            return "IDOR"
        if candidate.method in {"POST", "PUT", "PATCH", "DELETE"}:
            return "Broken Access Control"
        return "IDOR"

    def reason(self, candidate: EndpointCandidate) -> str:
        parts = []
        if candidate.line_number:
            parts.append(f"line {candidate.line_number}")
        if candidate.param_name:
            parts.append(f"param: {candidate.param_name}")
        if candidate.matched_text:
            parts.append(f"match: {candidate.matched_text}")
        if candidate.method in {"POST", "PUT", "PATCH", "DELETE"}:
            parts.append("state-changing method")
        if not parts:
            parts.append("auto-scored from route pattern")
        return "; ".join(parts)

    def rank(self, candidates: list[EndpointCandidate]) -> list[EndpointCandidate]:
        scored = [self.score(candidate) for candidate in candidates]
        return sorted(scored, key=lambda item: item.risk_score, reverse=True)
