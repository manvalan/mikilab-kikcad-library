# MIKILAB KiCad Library

Personal, self-contained KiCad library for MIKILAB hardware projects.

This directory is fully autonomous: it does **not** depend on
`kicad-personal-library` or any other external directory. Every path used
inside `sym-lib-table`, `fp-lib-table` and the footprint 3D model
references is relative to this library (via `${KIPRJMOD}`), so the whole
folder can be moved, renamed, zipped, or synced to another machine without
breaking anything.

## Architecture

Every `.kicad_sym` file under `symbols/` is an **independent** KiCad
symbol library (there is deliberately no single monolithic
`MIKILAB.kicad_sym`). Every `.pretty` directory under `footprints/` is
likewise an independent KiCad footprint library. This mirrors how the
official KiCad libraries are structured and keeps components easy to find,
diff, and maintain individually.

```
mikylab_kikad_library/
├── sym-lib-table         # registers every symbols/**/*.kicad_sym
├── fp-lib-table          # registers every footprints/**/*.pretty
├── symbols/<category>/<Name>.kicad_sym
├── footprints/<category>/<Name>.pretty/<Name>.kicad_mod
├── 3dmodels/<category>/<Name>.step
├── docs/                 # reference documentation (incl. upstream KiCad docs)
├── legacy/                # legacy .lib/.dcm sources kept for reference
├── scripts/               # import & check tooling (this README's §5, §6)
├── MANIFEST.csv           # full provenance/status log, one row per file
└── README.md
```

Categories in use: `analog`, `audio`, `display`, `fpga_cpld`, `interface`,
`logic`, `mechanical`, `memory`, `microcontrollers`, `other`, `power`,
`rf`.

Every symbol/footprint library is registered under a `MIKILAB_<name>`
nickname, e.g. `MIKILAB_TPS7A2012PDBVR`, `MIKILAB_TPS7A2018PDBVR`,
`MIKILAB_Amplifier_Operational`, `MIKILAB_altera`. Nicknames are derived
automatically from the file/directory name and are guaranteed unique.

## 1. Installing the library

There are two ways to make this library available in KiCad. Which one you
want depends on whether you use it in one project or in every project.

### Option A -- one project only (no KiCad config changes)

`sym-lib-table` / `fp-lib-table` at the root of this repo use
`${KIPRJMOD}`, which KiCad automatically resolves to *the currently open
project's directory*. So if a `.kicad_pro` project lives directly inside
`mikylab_kikad_library/` (or you copy these two table files into your
project's directory), KiCad picks them up automatically -- no extra
configuration needed. This is the setup `check_library.py` and the
`scripts/` tooling assume.

### Option B -- available in every project (recommended for a personal library)

This is the practical setup for a library you want in every schematic you
open, not just one project. Tested against the KiCad 10.0 install on this
machine (`/Applications/KiCad/KiCad.app`, config at
`~/Library/Preferences/kicad/10.0/`).

1. **Define an environment variable pointing at this library.**
   KiCad → Preferences → Configure Paths... → add a new entry:
   - Name: `MIKILAB`
   - Path: `/Users/michelebigi/Development/mikylab_kikad_library`

2. **Generate the "global" table variant** (uses `${MIKILAB}` instead of
   `${KIPRJMOD}`; regenerate any time after adding components):
   ```
   python3 scripts/generate_global_tables.py
   ```
   This writes `sym-lib-table.global` and `fp-lib-table.global` at the
   library root.

3. **Merge those into KiCad's global tables.** The simplest way is to
   append their `(lib ...)` lines into your existing global tables (back
   them up first):
   ```
   cp ~/Library/Preferences/kicad/10.0/sym-lib-table ~/Library/Preferences/kicad/10.0/sym-lib-table.bak
   cp ~/Library/Preferences/kicad/10.0/fp-lib-table  ~/Library/Preferences/kicad/10.0/fp-lib-table.bak

   python3 - <<'EOF'
   import re
   from pathlib import Path

   kicad_dir = Path.home() / "Library/Preferences/kicad/10.0"
   lib_root = Path("/Users/michelebigi/Development/mikylab_kikad_library")

   for kind, global_file, generated in (
       ("sym_lib_table", "sym-lib-table", "sym-lib-table.global"),
       ("fp_lib_table", "fp-lib-table", "fp-lib-table.global"),
   ):
       target = kicad_dir / global_file
       new_libs = (lib_root / generated).read_text().splitlines()
       new_libs = [l for l in new_libs if l.strip().startswith("(lib")]

       text = target.read_text()
       # insert the new (lib ...) lines just before the final closing paren
       idx = text.rstrip().rfind(")")
       text = text.rstrip()[:idx] + "\n" + "\n".join(new_libs) + "\n" + text.rstrip()[idx:] + "\n"
       target.write_text(text)
       print(f"Merged {len(new_libs)} libraries into {target}")
   EOF
   ```
   (Or do it by hand: open both `.global` files and copy each `(lib
   ...)` line into the corresponding file under
   `~/Library/Preferences/kicad/10.0/`, just before the final closing
   `)`.)

4. Restart KiCad. Every `MIKILAB_*` symbol and footprint library is now
   available in any project, resolved via `${MIKILAB}`.

**Known issue on this machine, to clean up before deleting
`kicad-personal-library`:** the current global `sym-lib-table` already
has a handful of entries pointing directly at
`/Users/michelebigi/Development/kicad-personal-library/...` with absolute
paths (added before this library existed, e.g. libraries named `ti`,
`TPS63020DSJT`). Once the `MIKILAB_*` libraries above are installed and
working, remove those old absolute-path entries from
`~/Library/Preferences/kicad/10.0/sym-lib-table` -- otherwise you'll have
duplicate/stale libraries, and deleting `kicad-personal-library` will
leave KiCad with broken references. This library's own tables never
contain absolute paths (verified by `check_library.py` and by `grep -R
"/Users/michelebigi"`), so this cleanup is only about your existing
global KiCad config, not about anything in this repo.

## 2. Using the symbols

In the schematic editor, symbols are available as
`MIKILAB_<LibraryName>:<SymbolName>`, e.g.
`MIKILAB_TPS7A2012PDBVR:TPS7A2012PDBVR` or
`MIKILAB_Amplifier_Operational:LM358`.

## 3. Using the footprints

In the footprint assignment tool / PCB editor, footprints are available as
`MIKILAB_<LibraryName>:<FootprintName>`, e.g.
`MIKILAB_SOT95P280X145_5N:SOT95P280X145-5N`.

## 4. How 3D models are resolved

Footprints reference 3D models with `${KIPRJMOD}/3dmodels/<category>/<Name>.step`,
resolved relative to this library — portable by construction, no
absolute paths anywhere.

**Known gap (pre-existing, not introduced by this cleanup):** a set of
vendor-imported footprints (`footprints/other/*.pretty` and a few others —
see `check_library.py` warnings) reference 3D models via
`${KISBLIB}/...`, an environment variable that is not defined by this
library or by a stock KiCad install, and the corresponding 3D files were
never present locally to begin with. These footprints are fully usable
for schematic/PCB work (pads, courtyard, silkscreen are all correct and
complete) — they simply won't show a 3D body until you either supply the
matching STEP/WRL file and update the reference, or define `KISBLIB` in
KiCad pointing at wherever you keep those vendor 3D models. `run
scripts/check_library.py` lists every affected file.

Some IPC-generated footprints reference the *standard* KiCad 3D model
library via `${KISYS3DMOD}`, which is defined automatically by every
KiCad installation — those resolve normally and need no action.

**Special case — shared footprint, distinct 3D bodies:** `SOT95P280X145-5N`
is used by both `MIKILAB_TPS7A2012PDBVR` and `MIKILAB_TPS7A2018PDBVR`.
The footprint itself was verified byte-identical between the two parts
(SHA256 comparison showed the only difference was KiCad's internal
`tedit` timestamp), so a single shared footprint library is used. Their
3D bodies are genuinely different STEP files, though
(`3dmodels/power/TPS7A2012PDBVR.step` vs. `.../TPS7A2018PDBVR.step`), and
a `.kicad_mod` can only carry one embedded `(model ...)` reference — so
neither is embedded by default. If you want a 3D render for one of these
parts, assign the STEP file manually per footprint instance (PCB editor →
right-click footprint → Properties → 3D Models).

## 5. Adding a component

Simplest path — one command:

```
python3 scripts/add_component.py \
    --name TPS7A2018PDBVR \
    --symbol /path/to/TPS7A2018PDBVR.kicad_sym \
    --footprint /path/to/SOT95P280X145-5N.kicad_mod \
    --model /path/to/TPS7A2018PDBVR.step \
    --category power
```

`--footprint` and `--model` are optional — you can import a symbol-only
component, or symbol+footprint without a 3D model. `--category` is
optional too; it's auto-detected from `--name` using the same rules used
throughout this library (falls back to `other`).

The importer:
- refuses to overwrite a component that already exists (by name), with a
  clear error and no changes made;
- deduplicates footprints by content (SHA256), not filename — if the
  footprint you're importing is byte-identical to one already in the
  library, the existing one is reused instead of creating a duplicate;
- if a *different* footprint happens to share a filename with an existing
  one, it is imported under a distinct, semantically-derived name and the
  collision is recorded in `MANIFEST.csv`;
- rewrites the symbol's `Footprint` property to point at the correct new
  `MIKILAB_<lib>:<name>` reference;
- links the 3D model into the footprint (unless the footprint was reused
  from an existing shared library — see §4's shared-footprint case);
- regenerates `sym-lib-table` and `fp-lib-table` from scratch by scanning
  the directory tree, so there is never more than one `(version 7)` entry
  and every library on disk is registered exactly once;
- appends a row per file to `MANIFEST.csv` (columns: `type`, `source`,
  `destination`, `status`, `hash`, `notes`; status is one of `NEW`,
  `DUPLICATE`, `RENAMED_COLLISION`, `ERROR`, `UNCHANGED`).

`import_component.py` is the same tool with a more explicit/verbose CLI —
`add_component.py` just calls into it. For importing many components at
once, lay them out one subdirectory per component and run:

```
python3 scripts/import_batch.py --source /path/to/batch_dir [--category power]
```

(subdirectory name = component `--name`; exactly one `.kicad_sym` per
subdirectory required, footprint/model optional — same collision and
lib-table rules as a single import, applied per component).

## 6. Running the check

```
python3 scripts/check_library.py
```

Verifies: directory structure; symbol/footprint syntax and duplicates;
real filename collisions (by content hash, not just name); 3D model
reference validity and portability; `sym-lib-table`/`fp-lib-table`
syntax, single `(version 7)`, no missing/duplicate/unregistered entries;
and symbol → footprint cross-references for every MIKILAB-owned library.
Exits 0 (`RESULT: OK`) iff there are no errors. Warnings are pre-existing,
documented, non-fatal gaps (see §4).

Note: many symbols mirrored from the official KiCad symbol libraries
reference *standard* KiCad footprint libraries (e.g. `Package_SO`,
`RF_Module`) by their upstream nickname — those are outside MIKILAB's
scope (they ship with every KiCad install) and are not checked or
reported as errors.

## Provenance

`MANIFEST.csv` has one row per file in the library (`type`, `source`,
`destination`, `status`, `hash`, `notes`). Rows from the initial bulk
import are marked `UNCHANGED`/baseline; rows added by
`import_component.py` / `add_component.py` / `import_batch.py` record
exactly what happened during that import (new file, deduplicated,
renamed due to a real collision, or error).

### Components imported from FreeDSP

The following `audio`/`analog` category chips were imported from
[FreeDSP_ki-CAD_Libraries](https://github.com/freeDSP/FreeDSP_ki-CAD_Libraries)
(legacy KiCad `.lib`/`.dcm` format, converted to modern `.kicad_sym` via
`kicad-cli sym upgrade`): `ADAU1467WBCPZ300RL`, `PCM1808QPWRQ1`,
`PCM9211PTR`, `Combo384`, `MW-1466CORE` (FreeDSP's ADAU1466 core module),
`LME49720MA`, `CS8421-CZZ`, `PCM1861DBT`, `FDC608PZ`, `IMN10T108`,
`AK5384`. `PCM1681-Q1` was skipped (it's a KiCad `extends` variant of
`PCM1681` and can't be split into a standalone file without duplicating
`PCM1681`'s graphics -- import `PCM1681` if you need the automotive
variant, base symbol is identical for schematic purposes).

Notable fixes applied during that import (see `MANIFEST.csv` notes for
the affected files): `PCM1808QPWRQ1`'s footprint had an absolute 3D model
path pointing at the upstream maintainer's own machine
(`/Users/HILO/...`); `ADAU1467WBCPZ300RL` and `PCM9211PTR`'s footprints
had two dead 3D model references each (`${KICAD_USER_TEMPLATE_DIR}` and a
bare filename). All three were corrected to `${KIPRJMOD}`-relative
references pointing at the STEP files now under `3dmodels/audio/`.
`LME49720MA` was imported symbol-only, with its `Footprint` property
repointed at this library's existing `MIKILAB_ipc_soic:IPC_SOIC127P600X175-8N`
(an exact IPC-standard match already present) instead of duplicating a
generic SOIC-8 footprint. Several FreeDSP parts already covered by the
official mirrored libraries (`PCM5102A`, `INA194`, `AZ1117-3.3`,
`ADAU1452`) were intentionally *not* re-imported.

### Espressif modules

19 module symbols (each with footprint + 3D model) were imported from
the official [espressif/kicad-libraries](https://github.com/espressif/kicad-libraries)
repository: `ESP32-C3-MINI-1`, `ESP32-C3-WROOM-02`, `ESP32-C5-WROOM-1`,
`ESP32-C5-WROOM-1U`, `ESP32-C6-MINI-1/U`, `ESP32-C6-WROOM-1`,
`ESP32-H2-MINI-1`, `ESP32-MINI-1`, `ESP32-S2-MINI-1`, `ESP32-S2-SOLO`,
`ESP32-S2-WROOM`, `ESP32-S2-WROVER`, `ESP32-S3-MINI-1`,
`ESP32-S3-WROOM-1`, `ESP32-S3-WROOM-2`, `ESP32-S31-WROOM-3`,
`ESP32-WROOM-E`, `ESP32-WROVER-E`, `ESP8684-WROOM-02C/U`. Bare SoC/die
symbols (`ESP32`, `ESP32-C3`, `ESP32-S3`, `ESP8266`, ...) and DevKit
board symbols were skipped -- they have no footprint of their own (dies)
or aren't components you'd place on your own board (dev boards).
`ESP32-S31-WROOM-3` **replaces** an earlier `easyeda2kicad.py`-exported
version that had a fatal unquoted-URL syntax error in `(generator ...)`
(see the earlier commit fixing that bug) -- the official symbol/footprint
is used now instead.

All 19 footprints originally referenced their 3D model via
`${KICAD8_3RD_PARTY}` / `${KICAD9_3RD_PARTY}` (the path KiCad's Plugin
and Content Manager uses when a library is installed through it). Since
this library is not PCM-installed, that variable is never defined here;
the references were repointed to `${KIPRJMOD}/3dmodels/microcontrollers/`
using the STEP files copied in alongside each part, so every model
resolves without needing PCM or any extra KiCad configuration.

## Source safety

This library was built by copying (never moving) from external source
repositories; none of those repositories are modified by anything in
`scripts/`, and nothing in this library references them. In particular,
this directory does not depend on `kicad-personal-library` in any way —
verify at any time with:

```
grep -R "kicad-personal-library" .
```

which is expected to return no matches outside of historical mentions in
this README/docs.
