from __future__ import annotations

import builtins
import runpy
import sys
from pathlib import Path


if not getattr(builtins, "_seoul_monitor_modules_refreshed", False):
    for module_name in list(sys.modules):
        if module_name == "data_loader" or module_name == "components" or module_name.startswith("pages"):
            sys.modules.pop(module_name, None)
    builtins._seoul_monitor_modules_refreshed = True

runpy.run_path(str(Path(__file__).with_name("app.py")), run_name="__main__")
