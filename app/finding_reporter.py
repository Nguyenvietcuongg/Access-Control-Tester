from __future__ import annotations

from pathlib import Path
import json

from app.models import Finding


class FindingReporter:
    def __init__(self, output_dir: str = "data/reports") -> None:
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def save_json(self, findings: list[Finding], filename: str = "findings.json") -> Path:
        path = self.output_dir / filename
        payload = [finding.__dict__ for finding in findings]
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        return path

    def print_summary(self, findings: list[Finding]) -> None:
        if not findings:
            print("No findings detected.")
            return
        for item in findings:
            print(f"[{item.severity}] {item.title} -> {item.endpoint}")

    def print_saved_path(self, path: Path) -> None:
        print(f"Report saved to: {path}")
