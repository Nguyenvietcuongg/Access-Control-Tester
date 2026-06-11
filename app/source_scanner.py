from __future__ import annotations

from pathlib import Path
import re

from app.models import EndpointCandidate


class SourceScanner:
    EXTENSIONS = {".py", ".js", ".jsx", ".ts", ".tsx", ".java", ".php"}

    PY_PATTERN = re.compile(r'@(?:app|router|bp)\.(get|post|put|delete|patch)\(["\']([^"\']+)["\']\)', re.IGNORECASE)
    JS_PATTERN = re.compile(r'\b(?:app|router)\.(get|post|put|delete|patch)\(["\']([^"\']+)["\']', re.IGNORECASE)
    JAVA_PATTERN = re.compile(r'@(GetMapping|PostMapping|PutMapping|DeleteMapping|PatchMapping|RequestMapping)\s*\(\s*["\']([^"\']+)["\']', re.IGNORECASE)
    PHP_PARAM_PATTERN = re.compile(r'\$_(GET|POST|REQUEST)\s*\[\s*["\']([^"\']+)["\']\s*\]', re.IGNORECASE)

    def scan(self, source_path: str) -> list[EndpointCandidate]:
        raw_candidates: list[EndpointCandidate] = []
        base = Path(source_path)
        print(f"[scan] starting in: {base}")
        for file_path in base.rglob("*"):
            if file_path.suffix.lower() not in self.EXTENSIONS:
                continue
            if not file_path.is_file():
                continue
            print(f"[scan] checking file: {file_path}")
            text = file_path.read_text(encoding="utf-8", errors="ignore")
            found_in_file = 0
            found_in_file += self._scan_python(text, file_path, raw_candidates)
            found_in_file += self._scan_js(text, file_path, raw_candidates)
            found_in_file += self._scan_java(text, file_path, raw_candidates)
            found_in_file += self._scan_php(text, file_path, raw_candidates)
            if found_in_file == 0:
                print(f"[scan] no routes in: {file_path}")

        candidates = self._dedupe(raw_candidates)
        print(f"[scan] done. raw routes found: {len(raw_candidates)}")
        print(f"[scan] done. unique routes found: {len(candidates)}")
        return candidates

    def _line_number(self, text: str, index: int) -> int:
        return text.count("\n", 0, index) + 1

    def _add_candidate(
        self,
        candidates: list[EndpointCandidate],
        method: str,
        path: str,
        file_path: Path,
        line_number: int,
        matched_text: str,
        param_name: str = "",
    ) -> None:
        candidates.append(
            EndpointCandidate(
                method=method,
                path=path,
                source_file=str(file_path),
                line_number=line_number,
                matched_text=matched_text,
                param_name=param_name,
            )
        )

    def _scan_python(self, text: str, file_path: Path, candidates: list[EndpointCandidate]) -> int:
        found = 0
        for match in self.PY_PATTERN.finditer(text):
            method = match.group(1).upper()
            path = match.group(2)
            self._add_candidate(candidates, method, path, file_path, self._line_number(text, match.start()), match.group(0))
            found += 1
            print(f"[scan] found python route: {method} {path}")
        return found

    def _scan_js(self, text: str, file_path: Path, candidates: list[EndpointCandidate]) -> int:
        found = 0
        for match in self.JS_PATTERN.finditer(text):
            method = match.group(1).upper()
            path = match.group(2)
            self._add_candidate(candidates, method, path, file_path, self._line_number(text, match.start()), match.group(0))
            found += 1
            print(f"[scan] found js route: {method} {path}")
        return found

    def _scan_java(self, text: str, file_path: Path, candidates: list[EndpointCandidate]) -> int:
        found = 0
        for match in self.JAVA_PATTERN.finditer(text):
            annotation = match.group(1).lower()
            path = match.group(2)
            method = self._java_method(annotation)
            self._add_candidate(candidates, method, path, file_path, self._line_number(text, match.start()), match.group(0))
            found += 1
            print(f"[scan] found java route: {method} {path}")
        return found

    def _scan_php(self, text: str, file_path: Path, candidates: list[EndpointCandidate]) -> int:
        found = 0
        file_name = file_path.name
        route_path = f"/{file_name}"
        seen_params = set()

        for match in self.PHP_PARAM_PATTERN.finditer(text):
            param_type = match.group(1).upper()
            param_name = match.group(2)
            key = (route_path, param_type, param_name)
            if key in seen_params:
                continue
            seen_params.add(key)
            line_number = self._line_number(text, match.start())
            method = "GET" if param_type == "GET" else "POST"
            self._add_candidate(
                candidates,
                method,
                route_path,
                file_path,
                line_number,
                match.group(0),
                param_name=param_name,
            )
            found += 1
            print(f"[scan] found php param: {param_type} {param_name}")

        if found == 0 and file_name.lower().endswith(".php"):
            self._add_candidate(candidates, "GET", route_path, file_path, 1, file_name)
            found += 1
            print(f"[scan] found php file endpoint: GET {route_path}")

        return found

    def _dedupe(self, candidates: list[EndpointCandidate]) -> list[EndpointCandidate]:
        grouped = {}
        for item in candidates:
            key = (item.method, item.path, item.source_file, item.param_name)
            if key not in grouped:
                grouped[key] = item
                continue

            current = grouped[key]
            if item.line_number and (current.line_number == 0 or item.line_number < current.line_number):
                current.line_number = item.line_number
            if item.matched_text and len(item.matched_text) > len(current.matched_text):
                current.matched_text = item.matched_text
        return list(grouped.values())

    def _java_method(self, annotation: str) -> str:
        if annotation == "getmapping":
            return "GET"
        if annotation == "postmapping":
            return "POST"
        if annotation == "putmapping":
            return "PUT"
        if annotation == "deletemapping":
            return "DELETE"
        if annotation == "patchmapping":
            return "PATCH"
        return "GET"
