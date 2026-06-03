from __future__ import annotations

from pathlib import Path

import typer

from app.finding_reporter import FindingReporter
from app.models import Account, EndpointCandidate, Finding
from app.risk_analyzer import RiskAnalyzer
from app.request_builder import RequestBuilder
from app.request_loader import RequestLoader
from app.replay_engine import ReplayEngine
from app.response_diff import ResponseDiff
from app.session_manager import SessionManager
from app.source_scanner import SourceScanner
from app.storage import Storage

app = typer.Typer(help="Authorization security MVP tool")

session_manager = SessionManager()
request_loader = RequestLoader()
replay_engine = ReplayEngine(session_manager)
response_diff = ResponseDiff()
reporter = FindingReporter()
source_scanner = SourceScanner()
risk_analyzer = RiskAnalyzer()
request_builder = RequestBuilder()
storage = Storage()


@app.command()
def scan(source_path: str = typer.Argument(..., help="Path to source code folder")) -> None:
    candidates = source_scanner.scan(source_path)
    ranked = risk_analyzer.rank(candidates)
    storage.save_endpoints(ranked)
    for item in ranked:
        print(f"[{item.risk_score}] {item.method} {item.path} -> {item.source_file}")


@app.command()
def replay(
    request_file: str = typer.Argument(..., help="Path to raw HTTP request file"),
    base_url: str = typer.Option(..., help="Target base URL, e.g. http://localhost:8000"),
    user_a: str = typer.Option(..., help="Username of first account"),
    user_b: str = typer.Option(..., help="Username of second account"),
) -> None:
    request = request_loader.load_from_file(request_file)
    request.url = base_url.rstrip("/") + request.url

    account_a = Account(username=user_a, password="", base_url=base_url)
    account_b = Account(username=user_b, password="", base_url=base_url)

    result_a = replay_engine.replay(account_a, request)
    result_b = replay_engine.replay(account_b, request)

    diff = response_diff.compare(result_a, result_b)
    findings: list[Finding] = []
    if diff.suspicious:
        findings.append(
            Finding(
                title="Possible authorization inconsistency",
                severity="medium",
                endpoint=request.url,
                evidence=f"status_delta={diff.status_delta}, body_diff_lines={diff.body_diff_lines}, elapsed_delta_ms={diff.elapsed_delta_ms:.2f}",
                notes="Compare responses from two accounts to confirm whether access is intended.",
            )
        )

    reporter.print_summary(findings)
    report_path = reporter.save_json(findings)
    reporter.print_saved_path(report_path)


@app.command()
def run(
    source_path: str = typer.Option(..., help="Path to source code folder"),
    base_url: str = typer.Option(..., help="Target base URL"),
    request_path: str | None = typer.Option(None, help="Optional raw request file"),
    user_a: str = typer.Option(..., help="Username of first account"),
    user_b: str = typer.Option(..., help="Username of second account"),
) -> None:
    candidates = source_scanner.scan(source_path)
    ranked = risk_analyzer.rank(candidates)
    storage.save_endpoints(ranked)

    findings: list[Finding] = []
    top_candidates = ranked[:5]
    for candidate in top_candidates:
        request = request_builder.build(candidate, base_url)
        account_a = Account(username=user_a, password="", base_url=base_url)
        account_b = Account(username=user_b, password="", base_url=base_url)
        result_a = replay_engine.replay(account_a, request)
        result_b = replay_engine.replay(account_b, request)
        diff = response_diff.compare(result_a, result_b)
        if diff.suspicious:
            findings.append(
                Finding(
                    title="Possible authorization inconsistency",
                    severity="medium",
                    endpoint=request.url,
                    evidence=f"status_delta={diff.status_delta}, body_diff_lines={diff.body_diff_lines}",
                    notes=f"Auto-generated from scanned route {candidate.source_file}",
                )
            )

    if request_path:
        request = request_loader.load_from_file(request_path)
        request.url = base_url.rstrip("/") + request.url
        account_a = Account(username=user_a, password="", base_url=base_url)
        account_b = Account(username=user_b, password="", base_url=base_url)
        result_a = replay_engine.replay(account_a, request)
        result_b = replay_engine.replay(account_b, request)
        diff = response_diff.compare(result_a, result_b)
        if diff.suspicious:
            findings.append(
                Finding(
                    title="Possible authorization inconsistency",
                    severity="medium",
                    endpoint=request.url,
                    evidence=f"status_delta={diff.status_delta}, body_diff_lines={diff.body_diff_lines}",
                    notes="Detected from supplied raw request file.",
                )
            )

    reporter.print_summary(findings)
    report_path = reporter.save_json(findings)
    reporter.print_saved_path(report_path)


@app.command()
def health() -> None:
    print("Authorization security MVP is ready.")
