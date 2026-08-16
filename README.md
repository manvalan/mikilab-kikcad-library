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

Point KiCad at this directory's two lib-tables so its symbols and
footprints show up in the schematic/PCB editors:

- **Symbols**: KiCad → Preferences → Manage Symbol Libraries → Global (or
  Project) Libraries → add all entries from `sym-lib-table`, or simply
  copy/merge this repo's `sym-lib-table` into your KiCad configuration
  directory (or your project directory, if you set `KIPRJMOD` per
  project).
- **Footprints**: same, using `fp-lib-table` under Manage Footprint
  Libraries.
- Easiest in practice: open a KiCad project whose project directory *is*
  (or contains a symlink/copy of) this library, so `${KIPRJMOD}` resolves
  to `mikylab_kikad_library` automatically. Alternatively, define your own
  KiCad environment variable (e.g. `MIKILAB`) pointing at this directory
  and rewrite the two table files to use it instead of `${KIPRJMOD}` if
  you want the library available across every project without copying
  files.

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
