# NVDA official source inventory

This inventory complements `UPSTREAM_AUDIT.md`. The upstream audit answers whether the Evolution tree unexpectedly diverges from the authoritative NV Access development tree. This inventory answers a broader question: which official NVDA branches, tags, related NV Access repositories, and pinned third-party sources exist, and which of them deserve integration review?

## Authority order

1. `nvaccess/nvda:master` is authoritative for the next NVDA development cycle.
2. `nvaccess/nvda:beta` is the active maintenance/localization line after a release branch cut. Changes unique to beta are not copied into the next development cycle unless their intent is valid there as well.
3. Immutable `release-*` tags are reference snapshots for regression comparison and reproducibility.
4. Other branches in `nvaccess/nvda` are candidates or historical references. Their presence in the official repository does not mean they are supported, current, or suitable for merging.
5. Git submodules are integrated only through the gitlink selected by authoritative NVDA source, unless an explicit dependency-update project is independently validated.

## Complete branch and tag inventory

Run:

```powershell
$remote = "nvaccess"
git remote remove $remote 2>$null
git remote add $remote https://github.com/nvaccess/nvda.git
git fetch --prune --no-tags $remote "+refs/heads/*:refs/remotes/$remote/*"
git fetch --prune $remote "+refs/tags/*:refs/tags/$remote/*"
python ci/scripts/officialSourceInventory.py --repo . --remote $remote --json testOutput/official-source-inventory.json --markdown testOutput/official-source-inventory.md
```

The generated JSON contains every fetched official branch and tag. For every branch it records:

* exact tip SHA and commit date;
* commits ahead of and behind `master`;
* whether the branch has already been absorbed by `master` and `beta`;
* branch age and classification;
* for active unmerged candidates, changed-path count and whether the diff touches protected NVDA core, only validation infrastructure, or only documentation.

The generated Markdown promotes only current unmerged candidates to the review table. Historical, merged, test, revert, abandoned, and release-workflow branches remain in JSON so that the inventory is complete without encouraging unsafe integration.

## Current official lines at the 2027.1 baseline

At the recorded baseline:

* `master`: `4dd8aec18f27b4c583180fda235fd596cef74de0`, start of the compatibility-breaking 2027.1 cycle.
* `beta`: `0db3b245037a0bf2ac173e1de5297016f5cdadd6`, a diverged 2026.3 maintenance/localization line. It is four commits ahead of the common base and one commit behind current `master`; its unique commits include tracked translation updates and generated XLIFF updates.
* latest immutable final release: `release-2026.2`.

The beta-only localization commits are intentionally not cherry-picked into Evolution. NV Access controls when maintenance/localization work is merged back to the next development line, and bypassing that process can overwrite 2027.1 documentation state.

## Official NV Access repositories directly relevant to NVDA

The machine-readable source graph is `ci/official-source-policy.json`. It includes the active core, build dependencies, localization tooling, remote-service and add-on ecosystem repositories, and marks archived repositories as references only.

The authoritative `.gitmodules` graph currently pins NV Access-owned repositories for miscellaneous dependencies, Java Access Bridge 32-bit binaries, NSIS, CLDR data, VS Code workspace data and MathCAT. Third-party gitlinks include liblouis, eSpeak NG, Sonic, IAccessible2, WAI-ARIA practices, Microsoft Detours/WIL and cppjieba.

## Integration decision rules

A candidate may be integrated only when all of these are true:

1. it contains commits not already present in authoritative `master`;
2. its intent still applies to the current 2027.1 architecture;
3. it does not duplicate a newer implementation already in `master`;
4. protected-core changes receive source audit, lint/type/unit/system CI and Real Apps validation;
5. dependency changes preserve the exact upstream gitlink unless a separately justified dependency upgrade is being tested;
6. a branch named `try-*`, `test-*`, `revert-*`, `abandoned-*` or similarly experimental is treated as reference by default, regardless of repository ownership.

This prevents the common failure mode of treating every branch in an official repository as release-quality code.
