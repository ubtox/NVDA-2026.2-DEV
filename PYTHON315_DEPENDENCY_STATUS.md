# Python 3.15 critical dependency status

Last review: 2026-09-06

This file applies the repository-wide engineering policy to critical CPython 3.15 dependencies. It records only demonstrated or currently blocked states. A component is not considered fully integrated into NVDA merely because an isolated build succeeds.

## py2exe

Component: py2exe

Role: freezes the Python application into Windows executable artifacts used by the NVDA packaging chain.

State: `SOURCE_INTEGRATED` for the CPython 3.15 project dependency paths; final NVDA build/packaging/runtime validation remains required.

Upstream repository: <https://github.com/py2exe/py2exe>

Pinned source commit: `1be98bd71ac737f73aa146631ab902b2b1cc43f7`

License: MIT OR Mozilla Public License 2.0, as declared by upstream/PyPI.

Reason the upstream release artifact is insufficient:

* PyPI `py2exe==0.14.2.0` declares Python `<3.15`.
* That release publishes Windows wheels through CPython 3.14 but no source distribution.
* The NVDA CPython 3.15 resolver therefore cannot obtain a permitted source build from PyPI.
* Upstream `master` at the pinned revision also still carries the `<3.15` metadata bound.

Project-owned integration:

* Root `[tool.uv.sources]` points `py2exe` directly at the immutable upstream Git revision above.
* Root `tool.uv.dependency-metadata` records the reviewed CPython 3.15 metadata override while preserving the upstream dependency set.
* Root `tool.uv.no-binary-package = ["py2exe"]` keeps the project on the source-build path.
* Root `uv.lock` is regenerated for `requires-python = "==3.15.*"` and records the exact Git source revision.
* GitHub Actions run `34044595281` passed source pinning, CPython 3.15 lock regeneration, lock provenance verification, source build/install and `py2exe.runtime` import.
* Generated root project state was committed as `8d41887770ce12aba5e47f6ebbdbec608187d2ad` (`build: consume pinned py2exe source on Python 3.15`).
* `runtime-builders/synthDriverHost32` now uses the same pinned py2exe source revision and a CPython 3.15 lock generated with the x86 interpreter.
* GitHub Actions run `34047789204` passed the CPython 3.15 x86 lock generation, root and synthDriverHost32 lock provenance checks, source build/install, and `py2exe.runtime` import under the 32-bit interpreter.
* Generated synthDriverHost32 project state was committed as `92007531a1964e3d99b56f93aec2831ca9144d46` (`build: align synthDriverHost32 with Python 3.15 source dependencies`).

Isolated compatibility proof: `.github/workflows/py2exe315Probe.yml` applies the minimum reviewed metadata change to the pinned source checkout and validates x64/x86 source wheel build, import, freeze and execution.

Build environment: GitHub Actions `windows-2025-vs2026`, CPython `3.15.0-rc.2`.

Architectures: x64 and x86 for the isolated compatibility probe; root project dependency integration is validated on x64; the synthDriverHost32 dependency environment is validated on x86.

Isolated tests:

* exact source SHA verification;
* source wheel build;
* installed-wheel import including `py2exe.runtime`;
* freeze of a program importing `_ssl`, `sqlite3`, `zlib` and other modules;
* execution of the frozen CPython 3.15 EXE and expected runtime marker.

Production packaging scope:

* NVDA `source/setup.py` uses py2exe with `bundle_files=3`.
* `runtime-builders/synthDriverHost32/setup-runtime.py` also uses `bundle_files=3`.
* The CP315 probe intentionally uses the same mode so its freeze/execution evidence matches the current NVDA packaging path.
* The py2exe memimporter path that references the removed private CPython symbol `_PyImport_FixupExtensionObject` is therefore not exercised by the current NVDA production packaging mode. It remains py2exe full-feature compatibility debt, but it is not a demonstrated blocker for NVDA's current `bundle_files=3` path.

Remaining validation: prove the real NVDA source build, synthDriverHost32 runtime build, packaging, launcher/installable artifacts and runtime path consume the CPython 3.15 dependency chain successfully.

Exit strategy: replace the project source-build path with an upstream release only when upstream publishes an equivalent or better CPython 3.15 artifact and the NVDA gates pass against it.

## BRLAPI

Component: BRLAPI Python binding / BRLTTY native API

Role: Python/native bridge used by NVDA braille support.

State: `SOURCE_STAGING_VALIDATED` for CPython 3.15 x64: source build, isolated import, project-owned staging into `miscDeps/python`, NVDA-path import and strict legacy-ABI audit pass in the Python 3.15 compatibility workflow. Full packaged NVDA braille/runtime validation remains required.

Upstream repository: <https://github.com/nvaccess/brltty>

Pinned source commit: `06e44da90784505fc5d2869f75f02160d6855d03`

License: GNU Lesser General Public License version 2.1 or any later version (`LGPL-2.1-or-later`). At the pinned source revision, BRLTTY's README states that this license applies to all files in the source tree, and the complete license text is provided as `LICENSE-LGPL`.

Release provenance/licensing requirements for source-derived BRLAPI artifacts:

* retain the applicable BRLTTY copyright, warranty and LGPL notices;
* include the `LICENSE-LGPL` license text with redistributed BRLAPI/BRLTTY artifacts;
* keep the exact source revision and local changes available in the provenance record;
* satisfy the LGPL 2.1 corresponding-source/relinkability requirements applicable to the exact binary composition that is distributed;
* verify those notices and source links as part of the final packaging/release audit rather than treating a source-build artifact as release-ready.

Local source/build recipe: `.github/workflows/brlapi315Build.yml`.

Build environment: GitHub Actions `windows-2025`, MSYS2 UCRT64, CPython `3.15.0-rc.2` x64.

Produced artifacts:

* `brlapi.cp315-win_amd64.pyd`;
* BRLAPI runtime DLL;
* `libiconv-2.dll` runtime dependency;
* Python package files extracted from the generated BRLAPI distribution;
* `LICENSE-LGPL` and source provenance record.

Validated source/staging tests:

* pinned BRLTTY source checkout and exact source revision verification;
* native BRLAPI build;
* CPython 3.15 binding build;
* presence of the CP315-tagged extension;
* native DLL dependency inspection;
* isolated CPython 3.15 import using an explicit staged runtime DLL directory;
* checkout of the NVDA integration branch and its pinned `miscDeps` submodule;
* project-owned replacement of the legacy BRLAPI module in the CI staging path;
* strict audit that no CPython 3.13/3.14-tagged `.pyd` remains after staging;
* import of BRLAPI from the staged NVDA `miscDeps/python` path;
* upload of the source-derived CP315 artifact set.

GitHub Actions run `34045495534` completed the original BRLAPI CP315 build/import/overlay job successfully after commit `490be609133dcba1c687903203a8730cbf5a1798` added the explicit Windows DLL search directory required by the source-derived runtime.

Python 3.15 compatibility run `34053420647` then consumed the source-derived BRLAPI artifact through the project staging path and passed the strict `Reject CPython 3.13/3.14 tagged native modules` gate without weakening it.

Persistent dependency context:

* `miscDeps` remains the NV Access `nvda-misc-deps` submodule pinned at `67c2e36deb524eff89d202e807d00c8d98f2a5b3`.
* That upstream submodule still contains `miscDeps/python/brlapi.cp313-win_amd64.pyd` before project staging.
* The project staging mechanism replaces that legacy module with the reproducibly built CP315 artifact before the compatibility audit/import path.
* No maintained upstream `nvda-misc-deps` CPython 3.15 BRLAPI integration has been identified as of this review.

Known limitation: the successful staged import does not prove braille functionality inside a built/packaged NVDA. Required next evidence includes full native DLL closure in packaging, braille regression coverage, launcher/installable validation and runtime tests.

Exit strategy: prefer a maintained upstream `nvda-misc-deps`/BRLTTY CP315 integration when available; otherwise retain the project-controlled source build/staging path with provenance, license notices and regression evidence.

## Python bootstrap / pip / uv

State: `VALIDATED_FOR_BOOTSTRAP` for CPython 3.15 x64 and x86; full application dependency/build completion remains a separate gate.

Validated evidence from Python 3.15 compatibility run `34053420647`:

* CPython 3.15 x64 and x86 interpreters install and execute;
* fresh virtual environments created with `--without-pip` can bootstrap pip using `ensurepip --upgrade` on both architectures;
* pip `26.2.1` is available on both architectures;
* `python -m pip check` reports no broken requirements in both bootstrap validation environments;
* `uv` is explicitly bound to the CPython 3.15 interpreter installed by `actions/setup-python`, rather than relying on a synthetic distribution identifier;
* implicit Python downloads are not used as a substitute for the required system CPython 3.15 interpreter.

Optimization policy: keep `uv` as the deterministic resolver/lock runner, keep pip/ensurepip as explicit runtime/bootstrap gates, avoid redundant package installation paths, and measure/cache expensive source builds only after correctness is preserved.

## Current gate interpretation

The py2exe source dependency is pinned and committed for the root CPython 3.15 environment and for the synthDriverHost32 CPython 3.15 x86 dependency environment. BRLAPI CP315 is reproducibly built from pinned source and the compatibility workflow stages it into the NVDA `miscDeps/python` path before import and legacy-ABI auditing. The strict CPython 3.13/3.14 native-module gate is green after that staging. Python 3.15 x64/x86 bootstrap, `ensurepip`, pip and `pip check` are also green.

The next release-level evidence is therefore completion of the real NVDA dependency synchronization/source build, synthDriverHost32 runtime build, packaging, launcher/installable, tests and runtime validation on the same CPython 3.15 chain. Failures remain release blockers. Do not weaken or suppress gates to obtain a green status.
