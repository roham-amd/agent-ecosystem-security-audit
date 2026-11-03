"""AESA command-line interface."""

from __future__ import annotations

from aesa.cli.dispatch import dispatch
from aesa.cli.parser import build_parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return dispatch(args)


__all__ = ["main"]
