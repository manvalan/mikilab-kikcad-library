#!/usr/bin/env python3
"""
add_component.py
=================

The simple, one-command way to add a component to the MIKILAB library.

    python3 scripts/add_component.py \\
        --name TPS7A2018PDBVR \\
        --symbol /path/to/TPS7A2018PDBVR.kicad_sym \\
        --footprint /path/to/SOT95P280X145-5N.kicad_mod \\
        --model /path/to/TPS7A2018PDBVR.step \\
        --category power

This does not reimplement anything: it is a thin, friendlier front-end
over import_component.py's core logic (same validation, same collision
handling, same lib-table regeneration). Use import_component.py directly
if you want the more explicit/verbose interface.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import import_component


def main() -> int:
    return import_component.main()


if __name__ == "__main__":
    sys.exit(main())
