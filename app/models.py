from dataclasses import dataclass, field
from typing import Any, Optional


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
    bearer_token: Optional[str] = None
    csrf_token: Optional[str] = None


@dataclass
class RequestSpec:
    method: str
    url: str
    headers: dict[str, str] = field(default_factory=dict)
    query: dict[str, str] = field(default_factory=dict)
    json_body: Optional[dict[str, Any]] = None
    data_body: Optional[dict[str, str]] = None
    raw_body: Optional[str] = None


@dataclass
class EndpointCandidate:
    method: str
    path: str
    source_file: str
    line_number: int = 0
    matched_text: str = ""
    param_name: str = ""
    risk_score: int = 0
    category: str = "IDOR"
    reason: str = ""
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
    category: str
    endpoint: str
    evidence: str
    notes: str = ""
