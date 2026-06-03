from __future__ import annotations

import difflib

from app.models import ReplayResult, ResponseDiffResult


class ResponseDiff:
    def compare(self, left: ReplayResult, right: ReplayResult) -> ResponseDiffResult:
        body_diff = list(
            difflib.unified_diff(
                left.body.splitlines(),
                right.body.splitlines(),
                fromfile=left.account,
                tofile=right.account,
                lineterm="",
            )
        )
        status_delta = abs(left.status_code - right.status_code)
        elapsed_delta_ms = abs(left.elapsed_ms - right.elapsed_ms)
        suspicious = bool(status_delta or body_diff)
        return ResponseDiffResult(
            status_delta=status_delta,
            body_diff_lines=len(body_diff),
            elapsed_delta_ms=elapsed_delta_ms,
            suspicious=suspicious,
        )
