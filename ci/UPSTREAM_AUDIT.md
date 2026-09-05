# Evolution upstream audit

This project keeps the NV Access production tree aligned with upstream while preserving explicit Evolution-only validation and compatibility improvements.

## Integrated upstream baseline

`ci/upstream-baseline.json` records the exact NV Access commit/tree last audited and integrated, plus the SHA-256 of the source ZIP used for the corresponding archive audit when available. Update this file only as part of a fully validated upstream integration.

The scheduled `Upstream NVDA audit` workflow runs from the repository default branch and compares `final/2027.1-nextgen` with `nvaccess/nvda:master`. It also checks the live upstream commit against the integrated baseline, so a new NV Access revision is visible even when the changed files are outside the protected production core.

## What is compared

`ci/scripts/upstreamAudit.py` compares tracked file content and submodule gitlinks when both inputs are Git checkouts. It can also compare against a GitHub source ZIP. ZIP archives do not encode submodule commit SHAs, so those refs are reported as unverifiable instead of being treated as failures.

Differences are classified as:

* `protected-core`: production source, build metadata, submodules and runtime/build infrastructure. Unexpected changes in this class fail the automated audit.
* `validation`: tests, CI scripts and workflow changes.
* `documentation`.
* `other`.

`ci/upstream-audit-allowlist.txt` lists intentional Evolution differences. Allowlisted files are always included in reports; the allowlist only classifies them as expected.

## Local ZIP audit

```powershell
py -3.13 ci/scripts/upstreamAudit.py `
  --current . `
  --upstream C:\path\to\nvda-upstream.zip `
  --allowlist ci/upstream-audit-allowlist.txt `
  --json upstream-audit.json `
  --markdown upstream-audit.md `
  --fail-on-protected
```

## Git checkout audit

```powershell
py -3.13 ci/scripts/upstreamAudit.py `
  --current C:\work\NVDA-Evolution `
  --upstream C:\work\nvaccess-nvda `
  --allowlist ci/upstream-audit-allowlist.txt `
  --fail-on-protected
```

For release-gate work, add `--fail-on-unexpected` after reviewing and updating the allowlist deliberately.

## Upstream integration procedure

1. Read `ci/upstream-baseline.json` and fetch the current `nvaccess/nvda:master` SHA.
2. If upstream advanced, create or reuse a `try-evolution/*` integration branch from `evolution/2027.1-nextgen`.
3. Integrate the upstream delta while preserving intentional Evolution changes.
4. Update `ci/upstream-baseline.json` to the exact upstream commit/tree only in the same candidate that will be validated.
5. Run the upstream audit, Autofix, CI/CD and Real Apps. Every `try-evolution/**` push runs the Real Apps matrix automatically.
6. Review every unexpected difference; never add a path to the allowlist merely to make the gate green.
7. Promote the same validated tree to `evolution/2027.1-nextgen`, then to `final/2027.1-nextgen`.
8. Durable branch pushes dispatch CI/CD, Real Apps and the upstream audit again.

This procedure intentionally does not auto-merge a new upstream revision. A compatibility-breaking upstream change must be inspected before it can enter Evolution.
