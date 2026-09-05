# Official NVDA source comparison

Target Evolution commit: `9b9cfa090b96cc34df9629be911742670d7a6045`

The official 2026.2 beta/RC/final Git trees and current `nvaccess/master` were fetched directly from NV Access for this audit. NV Access does not publish separate Git tags named `alpha`; the current development/alpha source is represented by `master`.

| Reference | Official commit | Files official | Identical paths | Modified | Only Evolution | Only official | +lines | -lines |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| 2026.2 beta1 | `5d9090d2632b` | 1400 | 1183 | 216 | 18 | 1 | 609739 | 454906 |
| 2026.2 beta2 | `08c0b11ff545` | 1401 | 1187 | 213 | 17 | 1 | 478091 | 406160 |
| 2026.2 beta3 | `405b5f8535fe` | 1402 | 1189 | 212 | 16 | 1 | 477070 | 405026 |
| 2026.2 beta4 | `73ceb35a44c5` | 1402 | 1194 | 207 | 16 | 1 | 436019 | 359595 |
| 2026.2 beta5 | `31cb389ba2cf` | 1406 | 1198 | 207 | 12 | 1 | 432127 | 356039 |
| 2026.2 beta6 | `e2acb638741a` | 1406 | 1199 | 206 | 12 | 1 | 430101 | 354356 |
| 2026.2 beta7 | `4cd7e513df01` | 1406 | 1202 | 203 | 12 | 1 | 425148 | 349690 |
| 2026.2 beta8 | `e898d0af9b94` | 1410 | 1214 | 194 | 9 | 2 | 422634 | 347722 |
| 2026.2 beta9 | `6104135f1403` | 1411 | 1221 | 188 | 8 | 2 | 418637 | 347076 |
| 2026.2 beta10 | `80a106a22ccc` | 1410 | 1236 | 173 | 8 | 1 | 371800 | 313703 |
| 2026.2 beta11 | `0fc393b94c3f` | 1411 | 1274 | 137 | 6 | 0 | 9480 | 7932 |
| 2026.2 rc1 | `1931a34275cc` | 1411 | 1305 | 106 | 6 | 0 | 2140 | 608 |
| 2026.2 rc2 | `f62c980589d1` | 1411 | 1369 | 42 | 6 | 0 | 1662 | 130 |
| 2026.2 final | `f62c980589d1` | 1411 | 1369 | 42 | 6 | 0 | 1662 | 130 |
| master (alpha/development 2027.1) | `4dd8aec18f27` | 1485 | 735 | 675 | 7 | 75 | 13226 | 24868 |

## 2026.2 beta1

- Commit: `5d9090d2632bc4d139cb21650fb3e98196fddd3b`
- Date: `2026-06-01T13:43:43+10:00`
- Subject: Update tracked translations from Crowdin (#20257)
- Changed paths versus Evolution: **235**
- Top-level concentration: `source` 129, `user_docs` 65, `tests` 21, `.github` 5, `ci` 3, `projectDocs` 3, `runtime-builders` 2, `.pre-commit-config.yaml` 1, `.python-versions` 1, `ensureuv.ps1` 1, `include` 1, `nvdaHelper` 1

## 2026.2 beta2

- Commit: `08c0b11ff5457fb951f0b8c2d347b5364a8829bc`
- Date: `2026-06-09T02:16:11Z`
- Subject: Update user_docs/en/userGuide.xliff
- Changed paths versus Evolution: **231**
- Top-level concentration: `source` 125, `user_docs` 65, `tests` 21, `.github` 5, `ci` 3, `projectDocs` 3, `runtime-builders` 2, `.pre-commit-config.yaml` 1, `.python-versions` 1, `ensureuv.ps1` 1, `include` 1, `nvdaHelper` 1

## 2026.2 beta3

- Commit: `405b5f8535fef3e58af2fa243ad806a6c2998f3d`
- Date: `2026-06-12T03:29:21Z`
- Subject: Update user_docs/en/userGuide.xliff
- Changed paths versus Evolution: **229**
- Top-level concentration: `source` 123, `user_docs` 65, `tests` 21, `.github` 5, `ci` 3, `projectDocs` 3, `runtime-builders` 2, `.pre-commit-config.yaml` 1, `.python-versions` 1, `ensureuv.ps1` 1, `include` 1, `nvdaHelper` 1

## 2026.2 beta4

- Commit: `73ceb35a44c5e4bafd02ed27216e3cc10f870bcc`
- Date: `2026-06-22T14:20:47+10:00`
- Subject: Fix saving comments in speech dictionaries (#20352)
- Changed paths versus Evolution: **224**
- Top-level concentration: `source` 120, `user_docs` 65, `tests` 20, `.github` 5, `ci` 3, `projectDocs` 3, `runtime-builders` 2, `.pre-commit-config.yaml` 1, `.python-versions` 1, `ensureuv.ps1` 1, `include` 1, `pyproject.toml` 1

## 2026.2 beta5

- Commit: `31cb389ba2cf78e0a8f185e5aeec8efebd0563b1`
- Date: `2026-06-29T13:45:21+10:00`
- Subject: Update tracked translations from Crowdin (#20417)
- Changed paths versus Evolution: **220**
- Top-level concentration: `source` 116, `user_docs` 65, `tests` 20, `.github` 5, `ci` 3, `projectDocs` 3, `runtime-builders` 2, `.pre-commit-config.yaml` 1, `.python-versions` 1, `ensureuv.ps1` 1, `include` 1, `pyproject.toml` 1

## 2026.2 beta6

- Commit: `e2acb638741a07b698dea0ef93656e0e1c7b10f2`
- Date: `2026-07-08T12:20:12+10:00`
- Subject: Show the restart dialog after updating from within NVDA, and make sure restarting offers the user the ability to save work in progress" (#20441)
- Changed paths versus Evolution: **219**
- Top-level concentration: `source` 115, `user_docs` 65, `tests` 20, `.github` 5, `ci` 3, `projectDocs` 3, `runtime-builders` 2, `.pre-commit-config.yaml` 1, `.python-versions` 1, `ensureuv.ps1` 1, `include` 1, `pyproject.toml` 1

## 2026.2 beta7

- Commit: `4cd7e513df0190e9f18910b55f9523f5f066e578`
- Date: `2026-07-14T14:17:20+10:00`
- Subject: Update tracked translations from Crowdin (#20489)
- Changed paths versus Evolution: **216**
- Top-level concentration: `source` 112, `user_docs` 65, `tests` 20, `.github` 5, `ci` 3, `projectDocs` 3, `runtime-builders` 2, `.pre-commit-config.yaml` 1, `.python-versions` 1, `ensureuv.ps1` 1, `include` 1, `pyproject.toml` 1

## 2026.2 beta8

- Commit: `e898d0af9b943a2b8afbf9988083899aaee5e96c`
- Date: `2026-07-21T01:29:48Z`
- Subject: Update user_docs/en/changes.xliff
- Changed paths versus Evolution: **205**
- Top-level concentration: `source` 107, `user_docs` 65, `tests` 18, `.github` 5, `ci` 3, `projectDocs` 3, `runtime-builders` 2, `.python-versions` 1, `include` 1

## 2026.2 beta9

- Commit: `6104135f1403041bd9b451530ffc15399a6ae6f1`
- Date: `2026-07-27T17:05:16+10:00`
- Subject: Update monitor-localisation-file-changes.yml in line with fetch-crowdin-translations.yml (#20563)
- Changed paths versus Evolution: **198**
- Top-level concentration: `source` 104, `user_docs` 65, `tests` 17, `.github` 4, `projectDocs` 3, `runtime-builders` 2, `.python-versions` 1, `ci` 1, `include` 1

## 2026.2 beta10

- Commit: `80a106a22ccc1c492d12688d7e6df88978e90187`
- Date: `2026-08-03T23:16:10Z`
- Subject: Update user_docs/en/userGuide.xliff
- Changed paths versus Evolution: **182**
- Top-level concentration: `source` 92, `user_docs` 63, `tests` 15, `.github` 4, `projectDocs` 3, `runtime-builders` 2, `.python-versions` 1, `ci` 1, `include` 1

## 2026.2 beta11

- Commit: `0fc393b94c3fea60b79e846ee10a6a6601acf970`
- Date: `2026-08-17T11:05:51+10:00`
- Subject: Update valid tracked translations from Crowdin (#20684)
- Changed paths versus Evolution: **143**
- Top-level concentration: `source` 81, `user_docs` 35, `tests` 15, `.github` 4, `projectDocs` 3, `runtime-builders` 2, `.python-versions` 1, `ci` 1, `include` 1

## 2026.2 rc1

- Commit: `1931a34275cc7be776d73131c978765cd11a6c13`
- Date: `2026-08-24T10:40:49+10:00`
- Subject: Update valid tracked translations from Crowdin (#20723)
- Changed paths versus Evolution: **112**
- Top-level concentration: `source` 80, `tests` 15, `user_docs` 5, `.github` 4, `projectDocs` 3, `runtime-builders` 2, `.python-versions` 1, `ci` 1, `include` 1

## 2026.2 rc2

- Commit: `f62c980589d1ac30babf68ad48177e9ad29a2e84`
- Date: `2026-08-26T11:38:19+10:00`
- Subject: beta to rc (#20740)
- Changed paths versus Evolution: **48**
- Top-level concentration: `source` 20, `tests` 15, `.github` 4, `projectDocs` 3, `runtime-builders` 2, `.python-versions` 1, `ci` 1, `include` 1, `user_docs` 1

## 2026.2 final

- Commit: `f62c980589d1ac30babf68ad48177e9ad29a2e84`
- Date: `2026-08-26T11:38:19+10:00`
- Subject: beta to rc (#20740)
- Changed paths versus Evolution: **48**
- Top-level concentration: `source` 20, `tests` 15, `.github` 4, `projectDocs` 3, `runtime-builders` 2, `.python-versions` 1, `ci` 1, `include` 1, `user_docs` 1

## master (alpha/development 2027.1)

- Commit: `4dd8aec18f27b4c583180fda235fd596cef74de0`
- Date: `2026-09-04T18:20:41+10:00`
- Subject: Start dev cycle for 2027.1 (#20787)
- Changed paths versus Evolution: **757**
- Top-level concentration: `source` 529, `tests` 137, `nvdaHelper` 28, `.github` 12, `projectDocs` 12, `ci` 9, `include` 6, `runtime-builders` 4, `site_scons` 4, `user_docs` 2, `.gitattributes` 1, `.gitignore` 1

## Raw path-level data

See `upstream-comparison-files.tsv` on this audit branch for every modified/added/removed path across every official reference.
