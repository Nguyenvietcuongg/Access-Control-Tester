from dataclasses import dataclass


@dataclass
class AppConfig:
    base_url: str = ""
    source_path: str = ""
    output_dir: str = "data/reports"
    sessions_path: str = "data/sessions.json"
