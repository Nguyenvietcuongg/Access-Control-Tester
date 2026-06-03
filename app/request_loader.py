from __future__ import annotations

from pathlib import Path

from app.models import RequestSpec


class RequestLoader:
    def load_from_file(self, path: str) -> RequestSpec:
        text = Path(path).read_text(encoding="utf-8")
        lines = text.splitlines()
        if not lines:
            raise ValueError("Request file is empty")

        first_line = lines[0].strip()
        method, url, *_ = first_line.split(maxsplit=2)

        headers: dict[str, str] = {}
        body_lines: list[str] = []
        in_body = False
        for line in lines[1:]:
            if not in_body:
                if line.strip() == "":
                    in_body = True
                    continue
                if ":" in line:
                    key, value = line.split(":", 1)
                    headers[key.strip()] = value.strip()
            else:
                body_lines.append(line)

        raw_body = "\n".join(body_lines).strip() or None
        return RequestSpec(method=method.upper(), url=url, headers=headers, raw_body=raw_body)
