"""CLI entry point."""

from __future__ import annotations

import argparse
from pathlib import Path

import requests

from .profile import build_stats
from .render import render_markdown


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description="Generate a GitHub profile stats Markdown card.")
    result.add_argument("username")
    result.add_argument("--output", type=Path, default=Path("profile-stats.md"))
    result.add_argument("--include-forks", action="store_true", help="Include forked repositories in totals")
    return result


def main() -> int:
    args = parser().parse_args()
    try:
        profile = build_stats(args.username, include_forks=args.include_forks)
        markdown = render_markdown(profile)
        output = args.output.expanduser().resolve()
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(markdown, encoding="utf-8")
    except (requests.RequestException, KeyError, ValueError) as exc:
        raise SystemExit(f"Could not generate profile card: {exc}") from exc
    print(f"Generated {output}")
    print(f"Profile: {profile['profile_url']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
