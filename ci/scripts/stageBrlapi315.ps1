[CmdletBinding()]
param(
	[Parameter(Mandatory = $true)]
	[string] $ArtifactRoot,
	[string] $MiscDepsRoot = "miscDeps"
)

$ErrorActionPreference = "Stop"

$artifactRootPath = (Resolve-Path -Path $ArtifactRoot).Path
$miscDepsRootPath = (Resolve-Path -Path $MiscDepsRoot).Path
$pythonSource = Join-Path $artifactRootPath "python"
$binSource = Join-Path $artifactRootPath "bin"
$licenseSource = Join-Path $artifactRootPath "LICENSE-LGPL"
$provenanceSource = Join-Path $artifactRootPath "SOURCE-PROVENANCE.txt"
$pythonTarget = Join-Path $miscDepsRootPath "python"
$provenanceTarget = Join-Path $miscDepsRootPath "brlapi-cp315"

foreach ($requiredPath in @($pythonSource, $binSource, $licenseSource, $provenanceSource, $pythonTarget)) {
	if (-not (Test-Path -Path $requiredPath)) {
		throw "Required BRLAPI staging path is missing: $requiredPath"
	}
}

$cp315Extensions = @(Get-ChildItem -Path $pythonSource -Recurse -File -Filter "brlapi.cp315-win_amd64.pyd")
if ($cp315Extensions.Count -ne 1) {
	throw "Expected exactly one brlapi.cp315-win_amd64.pyd, found $($cp315Extensions.Count)."
}

$brlapiDlls = @(Get-ChildItem -Path $binSource -File -Filter "brlapi-*.dll")
if ($brlapiDlls.Count -lt 1) {
	throw "No BRLAPI native DLL was found in $binSource."
}
if (-not (Test-Path -Path (Join-Path $binSource "libiconv-2.dll"))) {
	throw "BRLAPI runtime dependency libiconv-2.dll is missing from $binSource."
}

Get-ChildItem -Path $pythonTarget -File -Filter "brlapi.cp31*-win_amd64.pyd" -ErrorAction SilentlyContinue |
	Remove-Item -Force
Copy-Item -Path (Join-Path $pythonSource "*") -Destination $pythonTarget -Recurse -Force
Get-ChildItem -Path $binSource -File -Filter "*.dll" | Copy-Item -Destination $pythonTarget -Force

New-Item -ItemType Directory -Path $provenanceTarget -Force | Out-Null
Copy-Item -Path $licenseSource -Destination (Join-Path $provenanceTarget "LICENSE-LGPL") -Force
Copy-Item -Path $provenanceSource -Destination (Join-Path $provenanceTarget "SOURCE-PROVENANCE.txt") -Force

$legacyExtensions = @(
	Get-ChildItem -Path $miscDepsRootPath -Recurse -File -Filter "*.pyd" |
		Where-Object { $_.Name -match "cp31[34]" }
)
if ($legacyExtensions) {
	throw "Legacy CPython native modules remain after BRLAPI CP315 staging: $($legacyExtensions.FullName -join ', ')"
}

$stagedExtension = Join-Path $pythonTarget "brlapi.cp315-win_amd64.pyd"
if (-not (Test-Path -Path $stagedExtension)) {
	throw "BRLAPI CP315 extension was not staged into $pythonTarget."
}

Write-Host "BRLAPI CP315 staged into: $pythonTarget"
Write-Host "BRLAPI source provenance staged into: $provenanceTarget"
