# Python 3.15 critical dependency status

Last review: 2026-09-06

This file applies the repository-wide engineering policy to critical CPython 3.15 dependencies. It records only demonstrated or currently blocked states. A component is not considered integrated into NVDA merely because an isolated build succeeds.

## py2exe

Component: py2exe

Role: freezes the Python application into Windows executable artifacts used by the NVDA packaging chain.

State: `SOURCE_BUILD` for the isolated CPython 3.15 probe; `BLOCKED_EXTERNAL` for normal NVDA dependency resolution until the validated source artifact is wired into the project dependency path.

Upstream repository: https://github.com/py2exe/py2exe

Pinned source commit: `1be98bd71ac737f73aa146631ab902b2b1cc43f7`

License: MIT OR Mozilla Public License 2.0, as declared by upstream/PyPI.

Reason the upstream release artifact is insufficient:

- PyPI `py2exe==0.14.2.0` declares Python `<3.15`.
- That release publishes Windows wheels through CPython 3.14 but no source distribution.
- The NVDA CPython 3.15 resolver therefore cannot obtain a permitted source build from PyPI.
- Upstream `master` at the pinned revision also still carries the `<3.15` metadata bound.

Local source patch location: `.github/workflows/py2exe315Probe.yml` currently applies the minimum reviewed metadata change to the pinned source checkout. This metadata change is not considered compatibility proof by itself; the workflow must successfully compile the native wheel, import it, freeze a CPython 3.15 program containing native standard-library modules, and execute the resulting EXE.

Build environment: GitHub Actions `windows-2025-vs2026`, CPython `3.15.0-rc.2`.

Architectures: x64 and x86.

Produced artifacts: `py2exe` CP315 wheels uploaded by the isolated workflow after all probe steps pass.

Isolated tests:

- exact source SHA verification;
- source wheel build;
- installed-wheel import including `py2exe.runtime`;
- freeze of a program importing `_ssl`, `sqlite3`, `zlib` and other modules;
- execution of the frozen CPython 3.15 EXE and expected runtime marker.

Production packaging scope:

- NVDA `source/setup.py` uses py2exe with `bundle_files=3`.
- `runtime-builders/synthDriverHost32/setup-runtime.py` also uses `bundle_files=3`.
- The CP315 probe intentionally uses the same mode so its freeze/execution evidence matches the current NVDA packaging path.
- The py2exe memimporter path that references the removed private CPython symbol `_PyImport_FixupExtensionObject` is therefore not exercised by the current NVDA production packaging mode. It remains a real py2exe CP315 full-feature compatibility debt, and this probe does not claim compatibility for native-extension in-memory bundle modes.

NVDA integration tests: currently failing at deterministic `uv sync --dry-run --no-install-project` because the project still resolves `py2exe==0.14.2.0` from the release path rather than the source-built CP315 artifact.

Known limitation: source-build proof and NVDA dependency integration are separate stages. Do not mark py2exe CP315 as fully integrated until the deterministic NVDA dependency resolution, build and packaging gates consume the validated source-derived artifact.

Exit strategy: replace the project source-build path with an upstream release only when upstream publishes an equivalent or better CPython 3.15 artifact and the NVDA gates pass against it.

## BRLAPI

Component: BRLAPI Python binding / BRLTTY native API

Role: Python/native bridge used by NVDA braille support.

State: `SOURCE_BUILD` for the isolated CPython 3.15 x64 build; NVDA integration remains blocked by the currently pinned `miscDeps` submodule containing a CPython 3.13-tagged BRLAPI extension.

Upstream repository: https://github.com/nvaccess/brltty

Pinned source commit: `06e44da90784505fc5d2869f75f02160d6855d03`

License: GNU Lesser General Public License version 2.1 or any later version (`LGPL-2.1-or-later`). At the pinned source revision, BRLTTY's README states that this license applies to all files in the source tree, and the complete license text is provided as `LICENSE-LGPL`.

Release provenance/licensing requirements for source-derived BRLAPI artifacts:

- retain the applicable BRLTTY copyright, warranty and LGPL notices;
- include the `LICENSE-LGPL` license text with redistributed BRLAPI/BRLTTY artifacts;
- keep the exact source revision and local changes available in the provenance record;
- satisfy the LGPL 2.1 corresponding-source/relinkability requirements applicable to the exact binary composition that is distributed;
- verify those notices and source links as part of the final packaging/release audit rather than treating an isolated build artifact as release-ready.

Local source/build recipe: `.github/workflows/brlapi315Build.yml`.

Build environment: GitHub Actions `windows-2025`, MSYS2 UCRT64, CPython `3.15.0-rc.2` x64.

Produced artifacts:

- `brlapi.cp315-win_amd64.pyd`;
- BRLAPI runtime DLL;
- `libiconv-2.dll` runtime dependency;
- Python package files extracted from the generated BRLAPI distribution.

Isolated tests:

- pinned BRLTTY source checkout;
- native BRLAPI build;
- CPython 3.15 binding build;
- presence of the CP315-tagged extension;
- native DLL dependency inspection;
- CPython 3.15 import using the staged runtime DLL directory.

NVDA integration blocker:

- `miscDeps` is still the NV Access `nvda-misc-deps` submodule pinned at `67c2e36deb524eff89d202e807d00c8d98f2a5b3`.
- That submodule currently exposes `miscDeps/python/brlapi.cp313-win_amd64.pyd` to the Python 3.15 native-module audit.
- A source-built CP315 artifact must be integrated through a controlled `miscDeps` revision/fork or another reproducible project-owned staging mechanism before the old CP313 module can be removed from the validated NVDA dependency chain.

Known limitation: an isolated CP315 import does not prove braille functionality inside NVDA. Required next evidence includes NVDA import/integration, braille regression coverage, full native DLL closure, packaging and runtime tests.

Exit strategy: prefer a maintained upstream `nvda-misc-deps`/BRLTTY CP315 integration when available; otherwise maintain a project-controlled source revision with provenance, license notices and regression evidence.

## Current gate interpretation

At the reviewed project head, Python 3.15 x64/x86 runtime checks and MathCAT import have passed, while deterministic dependency resolution and rejection of old CPython-tagged native modules have failed for the exact blockers above.

These failures remain intentional release blockers. Do not weaken or suppress the gates to obtain a green status.