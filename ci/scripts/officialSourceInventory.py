from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
import json
from pathlib import Path
import subprocess


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
VALIDATION_PREFIXES = ("tests/", "ci/", ".github/")
DOC_PREFIXES = ("projectDocs/", "user_docs/")
EXPERIMENTAL_PREFIXES = (
	"abandoned-",
	"revert-",
	"test-",
	"test_",
	"try-",
	"wip-",
)


@dataclass(frozen=True)
class BranchRecord:
	name: str
	sha: str
	commitDate: str
	subject: str
	aheadMaster: int
	behindMaster: int
	mergedToMaster: bool
	aheadBeta: int | None
	behindBeta: int | None
	mergedToBeta: bool | None
	ageDays: int
	classification: str
	priority: str
	changedPathCount: int | None
	touchesProtectedCore: bool | None
	validationOnly: bool | None
	documentationOnly: bool | None


@dataclass(frozen=True)
class TagRecord:
	name: str
	sha: str
	commitDate: str
	subject: str


def _git(repo: Path, *args: str, check: bool = True) -> str:
	result = subprocess.run(
		["git", "-C", str(repo), *args],
		check=check,
		capture_output=True,
		text=True,
		encoding="utf-8",
		errors="replace",
	)
	return result.stdout.strip()


def _ref_exists(repo: Path, ref: str) -> bool:
	return (
		subprocess.run(
			["git", "-C", str(repo), "rev-parse", "--verify", "--quiet", ref],
			check=False,
			stdout=subprocess.DEVNULL,
			stderr=subprocess.DEVNULL,
		).returncode
		== 0
	)


def _ahead_behind(repo: Path, base: str, head: str) -> tuple[int, int]:
	left, right = _git(repo, "rev-list", "--left-right", "--count", f"{base}...{head}").split()
	return int(right), int(left)


def _commit_info(repo: Path, ref: str) -> tuple[str, str, str]:
	output = _git(repo, "show", "-s", "--format=%H%n%cI%n%s", ref)
	sha, date, subject = output.split("\n", 2)
	return sha, date, subject


def _age_days(commitDate: str) -> int:
	committed = datetime.fromisoformat(commitDate)
	return max(0, (datetime.now(UTC) - committed.astimezone(UTC)).days)


def _changed_paths(repo: Path, base: str, head: str) -> list[str]:
	output = _git(repo, "diff", "--name-only", f"{base}...{head}")
	return [line for line in output.splitlines() if line]


def _path_scope(paths: list[str]) -> tuple[bool, bool, bool]:
	if not paths:
		return False, False, False
	protected = any(path.startswith(PROTECTED_PREFIXES) for path in paths)
	validationOnly = all(path.startswith(VALIDATION_PREFIXES) for path in paths)
	documentationOnly = all(path.startswith(DOC_PREFIXES) for path in paths)
	return protected, validationOnly, documentationOnly


def _classify(
	name: str,
	mergedMaster: bool,
	aheadMaster: int,
	behindMaster: int,
	ageDays: int,
	candidateWindowDays: int,
) -> tuple[str, str]:
	lower = name.lower()
	if name == "master":
		return "primary-master", "critical"
	if name == "beta":
		return "active-beta", "critical"
	if lower.startswith("l10n") or lower in {"mastertobeta", "betatomaster"}:
		return "release-workflow", "reference"
	if mergedMaster:
		return "merged-history", "reference"
	if lower.startswith(EXPERIMENTAL_PREFIXES):
		return "experimental-unmerged", "reference"
	if ageDays > candidateWindowDays:
		return "historical-unmerged", "reference"
	if aheadMaster > 0 and behindMaster == 0:
		return "current-ahead-candidate", "review"
	if aheadMaster > 0:
		return "current-diverged-candidate", "review"
	return "unclassified", "review"


def _remote_branches(repo: Path, remote: str) -> list[tuple[str, str]]:
	prefix = f"refs/remotes/{remote}/"
	output = _git(repo, "for-each-ref", "--format=%(refname)%09%(objectname)", prefix)
	result: list[tuple[str, str]] = []
	for line in output.splitlines():
		if not line:
			continue
		ref, sha = line.split("\t", 1)
		name = ref.removeprefix(prefix)
		if name == "HEAD":
			continue
		result.append((name, sha))
	return result


def _remote_tags(repo: Path, remote: str) -> list[str]:
	prefix = f"refs/tags/{remote}/"
	output = _git(repo, "for-each-ref", "--format=%(refname)", prefix)
	return [line.removeprefix(prefix) for line in output.splitlines() if line]


def build_inventory(
	repo: Path,
	remote: str,
	candidateWindowDays: int,
) -> tuple[list[BranchRecord], list[TagRecord]]:
	master = f"refs/remotes/{remote}/master"
	beta = f"refs/remotes/{remote}/beta"
	if not _ref_exists(repo, master):
		raise RuntimeError(f"Missing required official ref: {master}")
	betaExists = _ref_exists(repo, beta)

	branches: list[BranchRecord] = []
	for name, _ in _remote_branches(repo, remote):
		ref = f"refs/remotes/{remote}/{name}"
		sha, commitDate, subject = _commit_info(repo, ref)
		aheadMaster, behindMaster = _ahead_behind(repo, master, ref)
		mergedMaster = aheadMaster == 0
		ageDays = _age_days(commitDate)
		classification, priority = _classify(
			name,
			mergedMaster,
			aheadMaster,
			behindMaster,
			ageDays,
			candidateWindowDays,
		)

		aheadBeta: int | None = None
		behindBeta: int | None = None
		mergedBeta: bool | None = None
		if betaExists:
			aheadBeta, behindBeta = _ahead_behind(repo, beta, ref)
			mergedBeta = aheadBeta == 0

		changedPathCount: int | None = None
		touchesProtectedCore: bool | None = None
		validationOnly: bool | None = None
		documentationOnly: bool | None = None
		if name in {"master", "beta"} or priority == "review":
			paths = [] if name == "master" else _changed_paths(repo, master, ref)
			changedPathCount = len(paths)
			touchesProtectedCore, validationOnly, documentationOnly = _path_scope(paths)

		branches.append(
			BranchRecord(
				name=name,
				sha=sha,
				commitDate=commitDate,
				subject=subject,
				aheadMaster=aheadMaster,
				behindMaster=behindMaster,
				mergedToMaster=mergedMaster,
				aheadBeta=aheadBeta,
				behindBeta=behindBeta,
				mergedToBeta=mergedBeta,
				ageDays=ageDays,
				classification=classification,
				priority=priority,
				changedPathCount=changedPathCount,
				touchesProtectedCore=touchesProtectedCore,
				validationOnly=validationOnly,
				documentationOnly=documentationOnly,
			),
		)

	tags: list[TagRecord] = []
	for name in _remote_tags(repo, remote):
		ref = f"refs/tags/{remote}/{name}"
		sha, commitDate, subject = _commit_info(repo, f"{ref}^{{}}")
		tags.append(TagRecord(name=name, sha=sha, commitDate=commitDate, subject=subject))

	branches.sort(
		key=lambda item: (item.priority != "critical", item.priority != "review", item.name.lower()),
	)
	tags.sort(key=lambda item: item.commitDate, reverse=True)
	return branches, tags


def render_markdown(branches: list[BranchRecord], tags: list[TagRecord], remote: str) -> str:
	review = [branch for branch in branches if branch.priority == "review"]
	merged = sum(branch.mergedToMaster for branch in branches)
	historical = sum(branch.classification == "historical-unmerged" for branch in branches)
	experimental = sum(branch.classification == "experimental-unmerged" for branch in branches)
	lines = [
		"# NVDA official source inventory",
		"",
		f"Remote namespace: `{remote}`",
		"",
		f"- Official branches discovered: **{len(branches)}**",
		f"- Official tags discovered: **{len(tags)}**",
		f"- Branches already absorbed by master: **{merged}**",
		f"- Current unmerged branches requiring review: **{len(review)}**",
		f"- Historical unmerged branches: **{historical}**",
		f"- Experimental/test/revert unmerged branches: **{experimental}**",
		"",
		"## Branches requiring review",
		"",
		"| Branch | Class | Ahead | Behind | Age days | Paths | Core | Validation only | Docs only | Tip |",
		"| --- | --- | ---: | ---: | ---: | ---: | --- | --- | --- | --- |",
	]
	if review:
		for branch in review:
			lines.append(
				"| "
				+ f"`{branch.name}` | {branch.classification} | {branch.aheadMaster} | {branch.behindMaster} | "
				+ f"{branch.ageDays} | {branch.changedPathCount if branch.changedPathCount is not None else '-'} | "
				+ f"{branch.touchesProtectedCore if branch.touchesProtectedCore is not None else '-'} | "
				+ f"{branch.validationOnly if branch.validationOnly is not None else '-'} | "
				+ f"{branch.documentationOnly if branch.documentationOnly is not None else '-'} | `{branch.sha[:12]}` |",
			)
	else:
		lines.append("| _None_ | - | - | - | - | - | - | - | - | - |")

	lines.extend(("", "## Primary refs", ""))
	for branch in branches:
		if branch.priority == "critical":
			lines.append(
				f"- `{branch.name}`: `{branch.sha}` — {branch.subject} ({branch.commitDate})",
			)

	lines.extend(("", "## Newest official tags", ""))
	for tag in tags[:25]:
		lines.append(f"- `{tag.name}`: `{tag.sha[:12]}` — {tag.commitDate} — {tag.subject}")
	lines.append("")
	return "\n".join(lines)


def main() -> int:
	parser = argparse.ArgumentParser(
		description="Inventory every official NVDA branch and tag fetched locally.",
	)
	parser.add_argument("--repo", type=Path, default=Path("."))
	parser.add_argument("--remote", default="nvaccess")
	parser.add_argument("--candidate-window-days", type=int, default=730)
	parser.add_argument("--json", dest="jsonOutput", type=Path)
	parser.add_argument("--markdown", type=Path)
	args = parser.parse_args()

	repo = args.repo.resolve()
	branches, tags = build_inventory(repo, args.remote, args.candidate_window_days)
	payload = {
		"generatedAt": datetime.now(UTC).isoformat(),
		"remote": args.remote,
		"candidateWindowDays": args.candidate_window_days,
		"branches": [asdict(branch) for branch in branches],
		"tags": [asdict(tag) for tag in tags],
	}
	markdown = render_markdown(branches, tags, args.remote)
	print(markdown)

	if args.jsonOutput:
		args.jsonOutput.parent.mkdir(parents=True, exist_ok=True)
		args.jsonOutput.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
	if args.markdown:
		args.markdown.parent.mkdir(parents=True, exist_ok=True)
		args.markdown.write_text(markdown, encoding="utf-8")
	return 0


if __name__ == "__main__":
	raise SystemExit(main())
