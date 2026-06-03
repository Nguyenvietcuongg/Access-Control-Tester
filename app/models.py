from dataclasses import dataclass, field
from typing import Any


@dataclass
class Account:
    username: str
    password: str
    role: str = "user"
    tenant: str = "default"
    base_url: str = ""


@dataclass
class SessionInfo:
    username: str
    cookies: dict[str, str] = field(default_factory=dict)
    bearer_token: str | None = None
    csrf_token: str | None = None


@dataclass
class RequestSpec:
    method: str
    url: str
    headers: dict[str, str] = field(default_factory=dict)
    query: dict[str, str] = field(default_factory=dict)
    json_body: dict[str, Any] | None = None
    data_body: dict[str, str] | None = None
    raw_body: str | None = None


@dataclass
class EndpointCandidate:
    method: str
    path: str
    source_file: str
    risk_score: int = 0
    notes: str = ""


@dataclass
class ReplayResult:
    account: str
    status_code: int
    headers: dict[str, str]
    body: str
    elapsed_ms: float


@dataclass
class ResponseDiffResult:
    status_delta: int
    body_diff_lines: int
    elapsed_delta_ms: float
    suspicious: bool = False


@dataclass
class Finding:
    title: str
    severity: str
    endpoint: str
    evidence: str
    notes: str = ""
