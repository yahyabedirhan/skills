#!/usr/bin/env python3
"""set-up-machine's pre-tool hook. A harness runs it before each tool call, with the call on stdin.

usage: pre_tool_hook.py [--harness claude-code] [--config FILE] [--rules FILE]

It refuses a call that any deny row of the rule table covers, naming each
refused part with the rule's instruction, and appends a line to the report
folder for a call an allow-and-report row covers. The report folder is
`report_dir` in the configuration file (default ~/.config/agents/hook.json).
set-up-machine wires it; see the skill's harness references. Python 3.9+,
standard library only.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from setupmachine.hook import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main())
