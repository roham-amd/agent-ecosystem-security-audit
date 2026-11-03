"""Single source of product / package version resolution."""

from __future__ import annotations

import json
from functools import lru_cache

from aesa.paths import version_file_path, versions_path


@lru_cache(maxsize=1)
def load_versions() -> dict[str, str]:
    data = json.loads(versions_path().read_text(encoding="utf-8"))
    return {str(k): str(v) for k, v in data.items()}


def product_version() -> str:
    file_ver = version_file_path().read_text(encoding="utf-8").strip()
    canonical = load_versions().get("aesa_product", file_ver)
    return file_ver or canonical


def package_version() -> str:
    from aesa import __version__

    return __version__


def build_tool_tag() -> str:
    return load_versions().get("build_tool", f"aesa-tools-{package_version()}")
