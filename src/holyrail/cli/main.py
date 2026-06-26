from __future__ import annotations

import argparse
from pathlib import Path

from holyrail.config import HolyRailConfig
from holyrail.pipeline import workflows


def _config(args: argparse.Namespace) -> HolyRailConfig:
    return HolyRailConfig.load(args.config)


def _analyze(args: argparse.Namespace) -> int:
    project = workflows.analyze(args.source, args.project, _config(args))
    print(f"Analyzed {len(project.frames)} frames -> {args.project}")
    return 0


def _preview(args: argparse.Namespace) -> int:
    outputs = workflows.preview(args.project, args.output, _config(args))
    print(f"Wrote {len(outputs)} preview frames -> {args.output}")
    return 0


def _render(args: argparse.Namespace) -> int:
    outputs = workflows.render(
        args.project,
        args.output,
        _config(args),
        video_path=args.video,
        fps=args.fps,
    )
    print(f"Rendered {len(outputs)} frames -> {args.output}")
    if args.video:
        print(f"Assembled video -> {args.video}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="holyrail")
    parser.add_argument("--config", type=Path, help="Optional TOML configuration file.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    analyze_parser = subparsers.add_parser("analyze", help="Analyze an image sequence.")
    analyze_parser.add_argument(
        "source", type=Path, help="Directory containing RAW or bitmap frames."
    )
    analyze_parser.add_argument("--project", type=Path, default=Path("holyrail-project.json"))
    analyze_parser.set_defaults(func=_analyze)

    preview_parser = subparsers.add_parser("preview", help="Generate corrected preview frames.")
    preview_parser.add_argument("--project", type=Path, default=Path("holyrail-project.json"))
    preview_parser.add_argument("--output", type=Path, default=Path("previews"))
    preview_parser.set_defaults(func=_preview)

    render_parser = subparsers.add_parser("render", help="Render corrected frames.")
    render_parser.add_argument("--project", type=Path, default=Path("holyrail-project.json"))
    render_parser.add_argument("--output", type=Path, default=Path("rendered"))
    render_parser.add_argument("--video", type=Path, help="Optional assembled video path.")
    render_parser.add_argument("--fps", type=int, default=24)
    render_parser.set_defaults(func=_render)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
