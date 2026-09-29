"""set-up-project's scripts: the project's files, and the audit of its harness config.

They read set-up-machine's rule table through its `setupmachine` package, so a
rule means the same thing to the machine and to every project. `use_machine_skill`
puts that package on the import path; it sits in the sibling `set-up-machine`
skill folder, wherever the skills are installed.
"""
from __future__ import annotations

import sys
from pathlib import Path

DEFAULT_MACHINE_SKILL = Path(__file__).resolve().parents[3] / "set-up-machine"


def use_machine_skill(folder: Path = DEFAULT_MACHINE_SKILL) -> Path:
    """Make `import setupmachine` resolve to that skill's package. Returns its scripts folder."""
    scripts = Path(folder).resolve() / "scripts"
    if not (scripts / "setupmachine" / "rules.py").is_file():
        raise ImportError(
            f"set-up-machine isn't installed beside set-up-project (looked in {scripts}); "
            "install it, or pass --machine-skill <its folder>"
        )
    if str(scripts) not in sys.path:
        sys.path.insert(0, str(scripts))
    return scripts
