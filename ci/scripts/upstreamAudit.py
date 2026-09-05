from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import subprocess
import tempfile
import zipfile
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class Entry:
	kind: str  # file | submodule
	digest: str | None
	mode: str | None = None


@dataclass(frozen=True)
class Difference:
	path: str
	status: str
	category: str
	allowed: bool
	current: Entry | None
	upstream: Entry | None


PROTECTED_PREFIXES = (
	"source/",
	"nvdaHelper/",
	"include/",
	"launcher/",
	"appx/",
	"runtime-builders/",
	"site_scons/",
	"uninstaller/",
	"typings/",
)
PROTECTED_ROOT_FILES = {
	".gitmodules",
	".python-versions",
	".vsconfig",
	"pyproject.toml",
	"uv.lock",
	"sconstruct",
	"scons.bat",
	"ensureuv.ps1",
}
VALIDATION_PREFIXES = ("tests/", "ci/", ".github/workflows/")
DOC_PREFIXES = ("projectDocs/", "user_docs/")
IGNORE_DIRS = {".git", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache"}


def _run_git(root: Path, *args: str) -> str:
	return subprocess.check_output(
		["git", "-C", str(root), *args],
		text=True,
		encoding="utf-8",
		errors="strict",
		stderr=subprocess.DEVNULL,
	).strip()


def _is_git_repo(root: Path) -> bool:
	try:
		return _run_git(root, "rev-parse", "--is-inside-work-tree") == "true"
	except (subprocess.CalledProcessError, FileNotFoundError):
		return False


def _sha256(path: Path) -> str:
	digest = hashlib.sha256()
	with path.open("rb") as stream:
		for chunk in iter(lambda: stream.read(1024 * 1024), b""):
			digest.update(chunk)
	return digest.hexdigest()


def _submodule_paths_from_git(root: Path) -> dict[str, str]:
	result: dict[str, str] = {}
	raw = subprocess.check_output(["git", "-C", str(root), "ls-files", "--stage", "-z"], text=False)
	for record in raw.split(b"\0"):
		if not record:
			continue
		metadata, pathBytes = record.split(b"\t", 1)
		mode, sha, stage = metadata.decode("ascii").split()
		if mode == "160000" and stage == "0":
			result[pathBytes.decode("utf-8")] = sha
	return result


def _tracked_files_from_git(root: Path) -> list[str]:
	raw = subprocess.check_output(["git", "-C", str(root), "ls-files", "-z"], text=False)
	return [item.decode("utf-8") for item in raw.split(b"\0") if item]


def _manifest_git(root: Path) -> tuple[dict[str, Entry], dict[str, str]]:
	submodules = _submodule_paths_from_git(root)
	manifest: dict[str, Entry] = {
		path: Entry(kind="submodule", digest=sha, mode="160000") for path, sha in submodules.items()
	}
	for rel in _tracked_files_from_git(root):
		if rel in submodules:
			continue
		path = root / rel
		if not path.is_file():
			continue
		stage = _run_git(root, "ls-files", "--stage", "--", rel)
		mode = stage.split(maxsplit=1)[0] if stage else None
		manifest[rel] = Entry(kind="file", digest=_sha256(path), mode=mode)
	return manifest, {"sourceType": "git", "commit": _run_git(root, "rev-parse", "HEAD")}


def _parse_gitmodules(root: Path) -> set[str]:
	path = root / ".gitmodules"
	if not path.is_file():
		return set()
	result: set[str] = set()
	for rawLine in path.read_text(encoding="utf-8", errors="replace").splitlines():
		line = rawLine.strip()
		if line.startswith("path") and "=" in line:
			result.add(line.split("=", 1)[1].strip().replace("\\", "/"))
	return result


def _manifest_filesystem(root: Path) -> tuple[dict[str, Entry], dict[str, str]]:
	submodules = _parse_gitmodules(root)
	manifest: dict[str, Entry] = {
		path: Entry(kind="submodule", digest=None, mode="160000") for path in submodules
	}
	for path in root.rglob("*"):
		if not path.is_file():
			continue
		rel = path.relative_to(root).as_posix()
		if any(part in IGNORE_DIRS for part in Path(rel).parts):
			continue
		if any(rel == submodule or rel.startswith(submodule + "/") for submodule in submodules):
			continue
		manifest[rel] = Entry(kind="file", digest=_sha256(path), mode=None)
	return manifest, {"sourceType": "filesystem", "commit": "unknown"}


def _safe_extract(zipPath: Path, destination: Path) -> Path:
	with zipfile.ZipFile(zipPath) as archive:
		seen: set[str] = set()
		for info in archive.infolist():
			normalized = Path(info.filename.replace("\\", "/"))
			if normalized.is_absolute() or ".." in normalized.parts:
				raise ValueError(f"Unsafe ZIP path: {info.filename}")
			if info.filename in seen:
				raise ValueError(f"Duplicate ZIP entry: {info.filename}")
			seen.add(info.filename)
		badMember = archive.testzip()
		if badMember:
			raise ValueError(f"Corrupt ZIP member: {badMember}")
		archive.extractall(destination)
	children = [path for path in destination.iterdir() if path.name != "__MACOSX"]
	if len(children) == 1 and children[0].is_dir():
		return children[0]
	return destination


def load_manifest(source: Path) -> tuple[dict[str, Entry], dict[str, str]]:
	if source.is_file() and source.suffix.lower() == ".zip":
		with tempfile.TemporaryDirectory(prefix="nvda-upstream-audit-") as tempDir:
			root = _safe_extract(source, Path(tempDir))
			manifest, meta = _manifest_filesystem(root)
			meta.update({"sourceType": "zip", "archive": str(source)})
			return manifest, meta
	if not source.is_dir():
		raise ValueError(f"Source does not exist or is unsupported: {source}")
	if _is_git_repo(source):
		return _manifest_git(source)
	return _manifest_filesystem(source)


def load_allowlist(path: Path | None) -> list[str]:
	if path is None:
		return []
	patterns: list[str] = []
	for rawLine in path.read_text(encoding="utf-8").splitlines():
		line = rawLine.strip()
		if line and not line.startswith("#"):
			patterns.append(line)
	return patterns


def category(path: str) -> str:
	if path in PROTECTED_ROOT_FILES or path.startswith(PROTECTED_PREFIXES):
		return "protected-core"
	if path.startswith(VALIDATION_PREFIXES):
		return "validation"
	if path.startswith(DOC_PREFIXES) or path.lower() in {"readme.md", "security.md", "copying.txt"}:
		return "documentation"
	return "other"


def is_allowed(path: str, patterns: Iterable[str]) -> bool:
	return any(fnmatch.fnmatchcase(path, pattern) for pattern in patterns)


def compare(
	current: dict[str, Entry],
	upstream: dict[str, Entry],
	allowPatterns: list[str],
) -> tuple[int, list[Difference]]:
	identical = 0
	differences: list[Difference] = []
	for path in sorted(set(current) | set(upstream)):
		cur = current.get(path)
		up = upstream.get(path)
		if cur is None:
			status = "upstream-only"
		elif up is None:
			status = "current-only"
		elif cur.kind != up.kind:
			status = "kind-changed"
		elif cur.kind == "submodule" and (cur.digest is None or up.digest is None):
			status = "submodule-ref-unverifiable"
		elif cur.digest != up.digest:
			status = "modified"
		elif cur.mode and up.mode and cur.mode != up.mode:
			status = "mode-changed"
		else:
			identical += 1
			continue
		differences.append(
			Difference(
				path=path,
				status=status,
				category=category(path),
				allowed=is_allowed(path, allowPatterns),
				current=cur,
				upstream=up,
			)
		)
	return identical, differences


def render_markdown(
	currentMeta: dict[str, str],
	upstreamMeta: dict[str, str],
	identical: int,
	differences: list[Difference],
) -> str:
	unexpected = [diff for diff in differences if not diff.allowed and diff.status != "submodule-ref-unverifiable"]
	protected = [diff for diff in unexpected if diff.category == "protected-core"]
	lines = [
		"# NVDA upstream audit",
		"",
		f"- Current source: `{currentMeta.get('sourceType')}` / `{currentMeta.get('commit')}`",
		f"- Upstream source: `{upstreamMeta.get('sourceType')}` / `{upstreamMeta.get('commit')}`",
		f"- Identical tracked entries: **{identical}**",
		f"- Differences: **{len(differences)}**",
		f"- Unexpected differences: **{len(unexpected)}**",
		f"- Unexpected protected-core differences: **{len(protected)}**",
		"",
	]
	if differences:
		lines.extend(("| Status | Category | Allowed | Path |", "| --- | --- | --- | --- |"))
		for diff in differences:
			lines.append(
				f"| {diff.status} | {diff.category} | {'yes' if diff.allowed else 'no'} | `{diff.path}` |"
			)
	else:
		lines.append("No differences detected.")
	lines.append("")
	return "\n".join(lines)


def main() -> int:
	parser = argparse.ArgumentParser(description="Compare an NVDA tree with an upstream checkout or source ZIP.")
	parser.add_argument("--current", type=Path, required=True)
	parser.add_argument("--upstream", type=Path, required=True)
	parser.add_argument("--allowlist", type=Path)
	parser.add_argument("--json", dest="jsonOutput", type=Path)
	parser.add_argument("--markdown", type=Path)
	parser.add_argument("--fail-on-protected", action="store_true")
	parser.add_argument("--fail-on-unexpected", action="store_true")
	args = parser.parse_args()

	current, currentMeta = load_manifest(args.current.resolve())
	upstream, upstreamMeta = load_manifest(args.upstream.resolve())
	patterns = load_allowlist(args.allowlist)
	identical, differences = compare(current, upstream, patterns)

	payload = {
		"current": currentMeta,
		"upstream": upstreamMeta,
		"identical": identical,
		"differences": [asdict(item) for item in differences],
	}
	markdown = render_markdown(currentMeta, upstreamMeta, identical, differences)
	print(markdown)

	if args.jsonOutput:
		args.jsonOutput.parent.mkdir(parents=True, exist_ok=True)
		args.jsonOutput.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
	if args.markdown:
		args.markdown.parent.mkdir(parents=True, exist_ok=True)
		args.markdown.write_text(markdown, encoding="utf-8")

	unexpected = [diff for diff in differences if not diff.allowed and diff.status != "submodule-ref-unverifiable"]
	unexpectedProtected = [diff for diff in unexpected if diff.category == "protected-core"]
	if args.fail_on_unexpected and unexpected:
		return 2
	if args.fail_on_protected and unexpectedProtected:
		return 3
	return 0


if __name__ == "__main__":
	raise SystemExit(main())
