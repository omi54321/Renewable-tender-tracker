from __future__ import annotations

import importlib
from typing import Any


def load_connector(module_name: str, config: dict[str, Any]):
    module = importlib.import_module(f"Python.connectors.{module_name}")
    return module.Connector(config)
