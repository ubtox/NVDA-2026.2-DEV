# Evolution upstream audit

This project keeps the NV Access production tree aligned with upstream while preserving explicit Evolution-only validation and compatibility improvements.

## What is compared

`ci/scripts/upstreamAudit.py` compares tracked file content and submodule gitlinks when both inputs are Git checkouts. It can also compare against a GitHub source ZIP. ZIP archives do not encode submodule commit SHAs, so those refs are reported as unverifiable instead of being treated as failures.

Differences are classified as:

- `protected-core`: production source, build metadata, submodules and runtime/build infrastructure. Unexpected changes in this class fail the automated audit.
- `validation`: tests, CI scripts and workflow changes.
- `documentation`.
- `other`.

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

## Promotion rule

A new NV Access `master` revision should first be integrated on a `try-evolution/*` branch. Run the upstream audit, Autofix, CI/CD and Real Apps there. Promote to `evolution/2027.1-nextgen` and then `final/2027.1-nextgen` only after the same resulting tree is green. Durable branch pushes are automatically dispatched through the full CI/CD and Real Apps workflows.
