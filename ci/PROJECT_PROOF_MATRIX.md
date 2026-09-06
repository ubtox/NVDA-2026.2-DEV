# Project proof matrix

Use this matrix to report project status without unsupported certainty.

Allowed status values:

- `PASS`: current reproducible evidence demonstrates the check.
- `FAIL`: current evidence demonstrates a failure.
- `BLOCKED`: the check cannot currently complete; blocker and evidence are known.
- `UNKNOWN`: no current evidence is available.
- `N/A`: check is not applicable to the reviewed scope.

Do not convert `UNKNOWN` or `BLOCKED` into `PASS` because adjacent checks succeed.

| Area | Minimum evidence | Status |
| --- | --- | --- |
| Repository topology | branch, HEAD, merge base/divergence, current upstream ref | UNKNOWN |
| Working tree | `git status --short --branch` at validated commit/worktree | UNKNOWN |
| Upstream audit | current official NVDA comparison and disposition | UNKNOWN |
| Functional preservation | regression mapping for affected features | UNKNOWN |
| Dependency inventory | direct + critical transitive/native dependency classification | UNKNOWN |
| Source provenance | source refs, licenses, local patches, artifact provenance | UNKNOWN |
| Python runtime | interpreter versions/architectures execute required gates | UNKNOWN |
| Native Python modules | correct ABI tags/import/runtime tests | UNKNOWN |
| Native DLL closure | dependent DLLs resolved from controlled artifact/runtime paths | UNKNOWN |
| Dependency resolution | deterministic resolver/lock succeeds for intended groups | UNKNOWN |
| Lint/format | required Ruff/format gates | UNKNOWN |
| Static typing | Pyright + ty required gates | UNKNOWN |
| Unit tests | required unit suite and targeted regressions | UNKNOWN |
| Source build | SCons source target | UNKNOWN |
| Incremental build | repeated build without clean | UNKNOWN |
| Clean build | clean x64 build from declared environment | UNKNOWN |
| Packaging | launcher/installer/portable/AppX as applicable | UNKNOWN |
| Braille | supported driver/binding smoke and regressions | UNKNOWN |
| Speech/audio | supported synthesizer/audio smoke and regressions | UNKNOWN |
| UIA/IA2/JAB | subsystem regressions and representative application tests | UNKNOWN |
| Browsers/apps | representative Chrome/Firefox/Office/console/system tests | UNKNOWN |
| Accessibility | user-facing accessibility regression coverage | UNKNOWN |
| Security | required security/static/dependency checks | UNKNOWN |
| Licensing | dependency/source license checks and notices | UNKNOWN |
| CI matrix | required workflows green at release commit | UNKNOWN |
| Release artifacts | expected files, versions, hashes/provenance | UNKNOWN |

## Dependency component record

For each critical component that is not simply `UPSTREAM_OK`, record:

```text
Component:
Role:
State: UPSTREAM_PATCH | SOURCE_BUILD | PROJECT_FORK | PROJECT_REPLACEMENT | BLOCKED_EXTERNAL | RETIRE
Upstream repository:
Pinned source/tag/commit:
License:
Reason upstream artifact is insufficient:
Local source/patch location:
Build environment:
Architectures:
Produced artifacts:
Artifact hashes:
Isolated tests:
NVDA integration tests:
Known limitations:
Upstream tracking issue/PR:
Replacement/exit strategy:
Last validated commit/date:
Evidence links/logs:
```

## Current Python 3.15 rule

A component is not CPython 3.15 compatible merely because metadata permits 3.15. Required evidence is component-specific, but native components normally require successful CP315 build/import, native dependency closure, core behavior tests, and NVDA integration evidence.

The same proof principle applies to non-Python components and future platform/toolchain migrations.