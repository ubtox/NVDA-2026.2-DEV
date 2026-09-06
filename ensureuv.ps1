[CmdletBinding()]
param(
	[Parameter(ValueFromRemainingArguments = $true)]
	[string[]]$UvArgs
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
[Version]$RequiredUvVersion = '0.12.5'

function Get-InstalledUvVersion {
	if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
		return $null
	}
	try {
		$json = uv self version --output-format json | ConvertFrom-Json
		return [Version]$json.Version
	}
	catch {
		Write-Warning "Could not retrieve the installed uv version: $_"
		return $null
	}
}

function Invoke-Uv {
	& uv @UvArgs
	exit $LASTEXITCODE
}

function Install-PinnedUv {
	$versionText = $RequiredUvVersion.ToString()
	$installerUrl = "https://astral.sh/uv/$versionText/install.ps1"
	Write-Host "Installing project-pinned uv $versionText from $installerUrl"
	try {
		$installer = Invoke-RestMethod -Uri $installerUrl
		Invoke-Expression $installer
	}
	catch {
		throw "Failed to install project-pinned uv $versionText: $_"
	}

	# The official Windows installer normally uses the user executable directory.
	# Put the deterministic standalone install first for this process so a different
	# package-manager installation cannot shadow it.
	$localBin = Join-Path $env:USERPROFILE '.local\bin'
	$localUv = Join-Path $localBin 'uv.exe'
	if (Test-Path $localUv) {
		$env:PATH = "$localBin;$env:PATH"
	}
}

$installedVersion = Get-InstalledUvVersion
if ($installedVersion -ne $RequiredUvVersion) {
	if ($null -eq $installedVersion) {
		Write-Host "uv $RequiredUvVersion is required and is not currently available."
	}
	else {
		Write-Host "uv $installedVersion is installed, but this project requires exactly $RequiredUvVersion."
	}
	Install-PinnedUv
	$installedVersion = Get-InstalledUvVersion
}

if ($installedVersion -ne $RequiredUvVersion) {
	throw "Unable to activate project-pinned uv $RequiredUvVersion. Active version: $installedVersion"
}

Write-Host "Using project-pinned uv $installedVersion"
Invoke-Uv
