# NVDA Evolution project engineering policy

This policy applies to the whole repository and to every component required to build, test, package, run, maintain, and release the project.

It is intentionally broader than the Python 3.15 migration. Python 3.15 is a current target, not the boundary of the engineering policy.

## 1. Project objective

The project must preserve useful NVDA functionality while improving the fork in measurable areas such as compatibility, accessibility, robustness, performance, security, maintainability, build reproducibility, CI quality, and test coverage.

No improvement is considered valid if it silently removes or degrades an existing useful function without an explicit, reviewed justification and regression evidence.

Claims such as "compatible", "validated", "finished", "faster", "more robust", or "ahead of upstream" require reproducible evidence. A passing build or test proves only the scope exercised by that build or test.

## 2. Upstream-first, source-controlled fallback

For every external component, use the following order of preference:

1. Use the maintained upstream release when it satisfies the project's requirements.
2. Integrate an upstream fix when one exists but has not yet reached the selected release.
3. Build the component from its upstream source and carry the minimum reviewed compatibility patch when a release artifact is unavailable or incompatible.
4. Maintain a project fork when upstream cannot satisfy the requirement in the needed timeframe.
5. Replace the component with an in-project implementation only when repair or a maintained fork is not sufficient, not safe, or not sustainable.

A local fork or replacement is not automatically better than upstream. It must have a documented reason, ownership, tests, provenance, and an exit or maintenance strategy.

## 3. Dependency-pyramid rule

An incompatibility must be traced to its real source instead of hidden at the first failing layer.

If component A depends on B, and B depends on C, work continues down the dependency chain until the actual incompatible or unavailable component is identified. The repaired chain is then validated upward again:

source -> native libraries -> bindings -> Python packages/wheels -> NVDA integration -> packaging -> installer/portable artifacts -> runtime/system validation.

The same rule applies outside Python:

* C and C++ libraries;
* Windows APIs and SDKs;
* MSVC, clang, MinGW and build tools;
* SCons and other generators;
* Python packaging and freezing tools;
* Cython, pybind11 and native bindings;
* braille stacks and drivers;
* speech and audio components;
* UIA, IA2, Java Access Bridge and browser integration;
* add-on/runtime bridges;
* CI, signing, installer and distribution tooling;
* test frameworks and development utilities.

No external critical component should remain an uncontrolled blocker when a legally and technically maintainable source-based solution can be produced.

## 4. No fake compatibility

Do not declare compatibility by changing metadata alone.

In particular, do not treat any of the following as proof by themselves:

* widening `Requires-Python` without validating the code and native artifacts;
* suppressing dependency resolver errors;
* disabling a failing test or CI job without a documented replacement check;
* copying an older ABI-tagged native module into a newer runtime;
* ignoring missing DLL dependencies;
* swallowing a non-zero exit code;
* marking an external blocker as successful without a reproducible artifact.

Compatibility is demonstrated by execution under the target environment, not by metadata.

## 5. Source provenance and licensing

Every carried third-party source, fork, generated binary, patch, or replacement must retain enough information to reproduce and audit it:

* upstream project and repository;
* exact tag or commit when practical;
* license and required notices;
* local changes and their purpose;
* build toolchain and architecture;
* artifact version/hash where relevant;
* known limitations;
* upstream tracking or replacement status.

License compatibility is a release requirement, not a post-release cleanup task.

## 6. Component lifecycle states

A critical dependency should be classified using one of these states:

* `UPSTREAM_OK`: maintained upstream artifact is compatible and validated.
* `UPSTREAM_PATCH`: project consumes or carries a small upstream-compatible patch.
* `SOURCE_BUILD`: project reproducibly builds the upstream source itself.
* `PROJECT_FORK`: project maintains a fork because upstream is insufficient.
* `PROJECT_REPLACEMENT`: project owns a replacement implementation.
* `BLOCKED_EXTERNAL`: no safe solution is currently proven; exact blocker and evidence are recorded.
* `RETIRE`: component is being removed after a proven replacement path.

Transitions toward a local fork or replacement require stronger tests and maintenance documentation, not weaker validation.

## 7. Change workflow

Before beginning a substantial work block, record a baseline equivalent to:

```text
git status --short --branch
git rev-parse HEAD
git log -1 --oneline
git remote -v
git branch -vv
```

When upstream integration is relevant, also record the current upstream commit and branch divergence.

Then use this sequence:

1. Establish the exact failure or improvement target.
2. Reproduce it with the smallest useful test.
3. Identify the responsible layer in the dependency pyramid.
4. Check current upstream before inventing a local solution.
5. Apply the smallest correct source-level fix or controlled replacement.
6. Run targeted validation immediately.
7. Add or improve a regression test.
8. Run integration validation for affected subsystems.
9. Run expensive full-build/system/release gates only when the block is ready.
10. Commit a coherent unit of work with evidence in CI or logs.

Do not accumulate unrelated fixes into a single unreviewable change when they can be separated.

## 8. CI strategy

CI should minimize feedback time without lowering the final proof standard.

### Fast gate

Run on ordinary development pushes where applicable:

* diff/whitespace checks;
* deterministic dependency/lock checks;
* formatting and lint;
* compile/import smoke tests;
* targeted unit tests;
* dependency-pyramid policy checks relevant to changed files.

### Integration gate

Run for integration branches and pull requests:

* broader unit tests;
* Pyright and ty;
* source build;
* native import checks;
* affected subsystem tests;
* functional non-regression tests.

### Heavy/release gate

Run when a block is ready for release-level evidence:

* clean full build;
* launcher/installer/portable/distribution artifacts as applicable;
* system/browser/application tests;
* security and license checks;
* upstream delta audit;
* final dependency inventory;
* artifact provenance/hashes where relevant.

Expensive native dependencies should be built in dedicated workflows when their source or build recipe changes, then consumed as pinned, validated artifacts by normal CI where appropriate.

## 9. Python 3.15 application

Python 3.15 is a project target and must be treated as a real runtime/platform migration.

For an incompatible dependency such as a freezing tool or native binding:

1. inspect current upstream source and releases;
2. reproduce the CPython 3.15 failure independently from NVDA;
3. port or patch from source;
4. build a CPython 3.15 artifact with the required architecture;
5. prove import/startup and core behavior under CPython 3.15;
6. prove native DLL dependency closure;
7. integrate into NVDA only after the isolated component is proven;
8. run NVDA-level build and regression tests.

The Python 3.15 path must not force unrelated lint, documentation, translation, or test jobs to resolve an incompatible packaging-only dependency.

## 10. Functional preservation

Dependency modernization, architecture cleanup, Python migration, x64 work, CI optimization, or performance improvements must not erase useful behavior from official NVDA or from validated fork work.

For each major integration block, identify the affected functionality and provide one or more of:

* existing regression tests;
* new unit tests;
* system/application tests;
* deterministic manual validation instructions when automation is not currently possible.

A technical cleanup with an unmeasured functional regression is a failed change.

## 11. Upstream synchronization

Current official NVDA remains a reference source for useful fixes and architectural changes.

Before declaring a major project phase complete:

* fetch/inspect current official upstream;
* identify useful upstream changes not yet present;
* integrate or explicitly reject them with a technical reason;
* compare the fork against the current upstream state;
* avoid unsupported claims that the fork is ahead of official NVDA.

## 12. Definition of proven completion

A project phase is complete only for the scope actually demonstrated by evidence.

The final release candidate should have, as applicable:

* known branch/commit topology;
* clean working tree at release commit;
* current upstream audit;
* deterministic dependency resolution;
* supported Python runtime validation;
* native dependency validation;
* clean and incremental builds;
* packaging validation;
* unit, integration and system tests;
* lint, formatting and type checks;
* accessibility/functionality regressions covered;
* security/license/dependency checks;
* CI green for the required matrix;
* documented external blockers, if any, with exact logs and impact.

Anything not proven remains `UNKNOWN` or `BLOCKED`; it must not be reported as successful.

## 13. Working principle

The project owns the integration quality of the complete stack. When an upstream component is healthy, reuse it. When it is repairable, repair it from source. When it becomes an unavoidable critical limitation, fork or replace it with a controlled, licensed, reproducible and tested solution.

This rule continues through the complete dependency pyramid until the final NVDA artifact and its runtime behavior are proven.
