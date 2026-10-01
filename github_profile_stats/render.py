"""Jinja2 Markdown rendering."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, select_autoescape


def render_markdown(profile: dict[str, Any]) -> str:
    template_dir = Path(__file__).parent / "templates"
    environment = Environment(
        loader=FileSystemLoader(template_dir),
        autoescape=select_autoescape(enabled_extensions=("html", "xml")),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    return environment.get_template("profile.md.j2").render(profile=profile).strip() + "\n"
