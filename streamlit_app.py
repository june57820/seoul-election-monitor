from __future__ import annotations

import runpy
import sys
from pathlib import Path


for module_name in list(sys.modules):
    if module_name == "data_loader" or module_name == "components" or module_name.startswith("pages"):
        sys.modules.pop(module_name, None)

runpy.run_path(str(Path(__file__).with_name("app.py")), run_name="__main__")
