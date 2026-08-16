#!/usr/bin/env python3
"""
generate_global_tables.py
==========================

sym-lib-table / fp-lib-table at the library root use ${KIPRJMOD}, which
KiCad only resolves when this directory *is* (or is symlinked as) the
currently open project's directory. To use this library globally, across
every KiCad project, you instead need a custom environment variable (this
script defaults to MIKILAB) defined once in KiCad's Configure Paths, plus
a copy of the two tables that reference that variable instead of
${KIPRJMOD}.

This script writes:
    sym-lib-table.global
    fp-lib-table.global

at the library root, identical in content to sym-lib-table/fp-lib-table
except for the environment variable used in each URI. See README.md
section 1 for the full install steps.

Usage:
    python3 scripts/generate_global_tables.py [--env-var MIKILAB]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import lib_common as lc

ROOT = lc.LIBRARY_ROOT


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--env-var", default="MIKILAB", help="KiCad environment variable name to use (default: MIKILAB)")
    args = parser.parse_args()

    sym_entries = lc.build_sym_table_entries(ROOT, env_var=args.env_var)
    fp_entries = lc.build_fp_table_entries(ROOT, env_var=args.env_var)

    (ROOT / "sym-lib-table.global").write_text(
        lc.render_lib_table("sym_lib_table", sym_entries), encoding="utf-8"
    )
    (ROOT / "fp-lib-table.global").write_text(
        lc.render_lib_table("fp_lib_table", fp_entries), encoding="utf-8"
    )

    print(f"Wrote sym-lib-table.global ({len(sym_entries)} libraries, using \\${{{args.env_var}}})")
    print(f"Wrote fp-lib-table.global ({len(fp_entries)} libraries, using \\${{{args.env_var}}})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
