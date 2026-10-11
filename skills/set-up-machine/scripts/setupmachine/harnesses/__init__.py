"""Harness adapters for the plugins setup area that have not moved into a harness setup.

plugins.py dispatches through a lookup table. Pi and Codex expose validate, check and propose.
Claude Code keeps the install record and deny matching here, because Cursor's harness setup reads them.
"""
