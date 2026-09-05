# NVDA 2026.2 Future RC validation

This document records reproducible validation for the experimental 2026.2 RC.
OCR is intentionally out of scope. Results must be updated from executed tests;
an unmeasured comparison must never be reported as a pass.

## Integrated reliability improvements

* Modal dialogs cache their parent state before `ShowModal`, preventing a deleted
  wx object from blocking restart after add-on installation.
* UIA focus validation reads the current provider focus state instead of a stale
  event cache value.
* Add-on module cleanup removes all modules owned by an add-on without retaining
  stale cache entries.
* Objects represented by tree interceptors are filtered correctly while Windows
  is locked.
* The remote Python console uses explicit UTF-8 byte transport and closes its
  server socket cleanly.
* Rectangle conversion accepts compatible rectangle representations without
  weakening coordinate validation.
* System tests allow slower Chrome startup on contended hosted runners and avoid
  masking application setup failures during teardown.
* CI allows fresh hosted runners enough time to compile both x64 components and
  bundled x86 helpers, and cache cleanup has a safe default expiration value.

## Reproducible comparison matrix (OCR excluded)

| Domain | Scenario | This RC evidence | JAWS evidence | Status |
| --- | --- | --- | --- | --- |
| Chrome / ARIA | NVDA `chrome_*` Robot suites | GitHub system-test matrix passed | Not measured locally | RC regression coverage verified |
| Firefox | Browse/focus navigation suites | GitHub system-test matrix passed | Not measured locally | RC regression coverage verified |
| UIA / WinUI | Reject stale intermediate focus events | Unit regression test | Not measured locally | RC improvement verified |
| Add-ons | Install/update followed by restart | Modal-dialog regression test | Not measured locally | RC improvement verified |
| Add-ons | Remove imported modules during unload | Add-on import cleanup tests | Not measured locally | RC improvement verified |
| Windows security | Filter intercepted objects below lock screen | Security regression tests | Not measured locally | RC improvement verified |
| Unicode console | UTF-8 output and invalid-surrogate replacement | Remote-console transport tests | Not measured locally | RC improvement verified |
| Win32 geometry | Compatible rectangle conversion | Location helper tests | Not measured locally | RC improvement verified |
| Startup / shutdown | Robot `startupShutdown` suite | GitHub system-test matrix passed | Not measured locally | RC regression coverage verified |
| Installer | Install-dialog smoke tests | GitHub installer suites passed | Not measured locally | RC regression coverage verified |
| Braille | Existing routing and handler unit suites | Full unit suite | Not measured locally | Regression coverage only |
| Speech | Existing speech-manager unit suites | Full unit suite | Not measured locally | Regression coverage only |
| Office / VS Code / Terminal | Existing app modules and available suites | Full unit/system suites | Not measured locally | No comparative claim |

## Required release evidence

Before promotion, record the exact Git HEAD, clean status, unit-test count, Ruff,
format, compileall, Pyright, source/dist/launcher results, GitHub Actions run,
installer path, PE metadata, size, SHA-256, architecture, and signature state.

## Latest validated RC candidate

* Source commit: `cb3cf76000663076a465f63164c5f20863fc7a43`
* Unit tests: 1213 passed, 0 failed.
* Ruff check and format check: passed.
* Python compileall and Pyright: passed with zero errors.
* Source, distribution, and launcher build: passed.
* GitHub Actions CI/CD run `33967037619`, attempt 2: passed. One Chrome
  annotations job failed on its first attempt due to transient browser exposure
  and passed unchanged when rerun.
* Product version: `2026.2rc1`.
* PE machine: `0x014C` (x86 launcher capable of installing the bundled
  multi-architecture distribution).
* Authenticode: not signed; no signing certificate was supplied.
* Candidate path: `output/nvda_2026.2rc1.exe`.
* Candidate size: 62,101,487 bytes.
* Candidate SHA-256: `95EFCE8B95410392DA11302060E65F9B6FDF00C40DC9992F9011988E0BE49862`.

This evidence describes the candidate built from the source commit above. The
documentation-only commit recording this evidence does not alter the executable.
