"""AESA command-line interface."""

from __future__ import annotations

from aesa.cli.dispatch import dispatch
from aesa.cli.parser import build_parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser(include_dev=False)
    args = parser.parse_args(argv)
    return dispatch(args)


def main_dev(argv: list[str] | None = None) -> int:
    """Maintainer entry point (`authdiff-dev`) with build/lint/corpus/…"""
    parser = build_parser(include_dev=True)
    args = parser.parse_args(argv)
    return dispatch(args)


__all__ = ["main", "main_dev"]
