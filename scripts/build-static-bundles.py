#!/usr/bin/env python3
"""Generate production CSS and JavaScript bundles for container images."""

from __future__ import annotations

import os
import sys

import bq.release  # noqa: F401 - imported for bq.release.__VERSION_HASH__ side effect.
import pylons
from bq.core.lib.js_includes import generate_css_files, generate_js_files


def main() -> int:
    app_dir = os.environ.get("BISQUE_APP_DIR", "/app")
    public_dir = os.environ.get("BISQUE_PUBLIC_DIR", os.path.join(app_dir, "public"))
    source_dir = os.path.join(app_dir, "source")

    pylons.config["cache_enabled"] = "False"

    generate_css_files(root=f"{source_dir}/", public=public_dir)
    generate_js_files(root=f"{source_dir}/", public=public_dir)

    missing = [
        path
        for path in (
            os.path.join(public_dir, "core/css/all_css.css"),
            os.path.join(public_dir, "core/js/all_js.js"),
        )
        if not os.path.isfile(path)
    ]
    if missing:
        for path in missing:
            print(f"missing generated static bundle: {path}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
