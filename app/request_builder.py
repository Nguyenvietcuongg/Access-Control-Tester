from __future__ import annotations

from app.models import EndpointCandidate, RequestSpec


class RequestBuilder:
    def build(self, candidate: EndpointCandidate, base_url: str) -> RequestSpec:
        url = base_url.rstrip("/") + candidate.path
        return RequestSpec(method=candidate.method, url=url, headers={"Accept": "application/json"})
