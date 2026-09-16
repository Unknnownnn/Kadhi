from __future__ import annotations

import os
import sys

import pytest


def _windows_ci() -> bool:
    return sys.platform == "win32" and os.environ.get("CI") == "true"


skip_on_windows_ci = pytest.mark.skipif(
    _windows_ci(),
    reason=(
        "#382: a real trainer.train() hits an illegal instruction on part "
        "of GitHub's windows-latest fleet and kills the interpreter, which "
        "censors every other test in the cell. NOT a statement about this "
        "code path on Windows: still covered on ubuntu + macos, and still "
        "live on a local Windows box."
    ),
)
