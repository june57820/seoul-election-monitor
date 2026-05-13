from __future__ import annotations

import builtins
import runpy
import sys
from pathlib import Path


APP_BUILD_STAMP = "2026-05-13-keyword-timeseries-v5"


if getattr(builtins, "_seoul_monitor_build_stamp", None) != APP_BUILD_STAMP:
    for module_name in list(sys.modules):
        if module_name == "data_loader" or module_name == "components" or module_name.startswith("pages"):
            sys.modules.pop(module_name, None)
    builtins._seoul_monitor_build_stamp = APP_BUILD_STAMP

runpy.run_path(str(Path(__file__).with_name("app.py")), run_name="__main__")
