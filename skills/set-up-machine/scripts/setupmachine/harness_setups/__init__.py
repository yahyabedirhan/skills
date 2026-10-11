"""Discovered harness setups. One module here is one harness.

The verifier, the hook, and the plugin checker load every module in this folder.
They do not keep a list of harness names. A harness setup exposes the operations it needs:

- `id` and `label`
- `present(home)` — whether that harness is on the machine
- `audit(home)` — `(channel, status, text)` lines for the checks it owns
- `read(payload)` and `write(denials, asks)` — one hook call, when the harness runs the hook
- `validate`, `check`, and `propose` — one plugin entry, when the harness takes plugins

A harness with no plugins omits the plugin operations. Cursor is the first harness setup.
A later harness copies these operations.
"""
from __future__ import annotations

import importlib
import pkgutil


def load() -> list:
    """Every harness setup in this folder, in module order."""
    found = []
    for info in pkgutil.iter_modules(__path__):
        if info.name.startswith("_"):
            continue
        module = importlib.import_module(f"{__name__}.{info.name}")
        if getattr(module, "id", None):
            found.append(module)
    return found
