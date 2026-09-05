from __future__ import annotations

from pathlib import Path
import subprocess

UPSTREAM = "acb904f88ebdbfb7415cddc2188a38f36a675243"
IA_PATH = Path("source/NVDAObjects/IAccessible/__init__.py")
CHANGES_PATH = Path("user_docs/en/changes.md")


def git_show(path: str) -> str:
	return subprocess.check_output(
		["git", "show", f"{UPSTREAM}:{path}"],
		text=True,
		encoding="utf-8",
	)


def replace_once(text: str, old: str, new: str, description: str) -> str:
	count = text.count(old)
	if count != 1:
		raise RuntimeError(f"Expected exactly one {description}; found {count}")
	return text.replace(old, new, 1)


def resolve_iaccessible() -> None:
	ours = IA_PATH.read_text(encoding="utf-8")
	upstream = git_show(IA_PATH.as_posix())

	if "import ctypes.wintypes\n" not in ours:
		ours = replace_once(ours, "import ctypes\n", "import ctypes\nimport ctypes.wintypes\n", "ctypes import anchor")
	if "import windowUtils\n" not in ours:
		ours = replace_once(ours, "import displayModel\n", "import displayModel\nimport windowUtils\n", "displayModel import anchor")
	if "import locationHelper\n" not in ours or "from locationHelper import RectLTRB, RectLTWH\n" not in ours:
		ours = replace_once(
			ours,
			"from locationHelper import RectLTWH\n",
			"import locationHelper\nfrom locationHelper import RectLTRB, RectLTWH\n",
			"locationHelper import anchor",
		)

	helper_start_marker = "#: Window message asking a popup menu window for the handle of the menu it displays,"
	class_marker = "class MenuItem(IAccessible):"
	helper_start = upstream.index(helper_start_marker)
	helper_end = upstream.index(class_marker, helper_start)
	helper_block = upstream[helper_start:helper_end].rstrip() + "\n\n\n"
	if helper_start_marker not in ours:
		ours = replace_once(ours, class_marker, helper_block + class_marker, "MenuItem class anchor")

	upstream_class = upstream.index(class_marker)
	upstream_description = upstream.index("\n\tdef _get_description", upstream_class)
	class_prefix = class_marker + "\n"
	location_method = upstream[upstream_class + len(class_prefix) : upstream_description].rstrip() + "\n\n"
	if "\tdef _get_location(self) -> RectLTWH | None:" not in ours:
		ours = replace_once(ours, class_prefix, class_prefix + location_method, "MenuItem method anchor")

	lines = ours.splitlines(keepends=True)
	for index, line in enumerate(lines[:10]):
		if line.startswith("# Copyright (C)"):
			if "Christopher Proß" not in line:
				ending = "\n" if line.endswith("\n") else ""
				lines[index] = line.rstrip("\r\n") + ", Christopher Proß" + ending
			break
	else:
		raise RuntimeError("Could not find IAccessible copyright line")
	ours = "".join(lines)

	for required in (
		"import ctypes.wintypes",
		"import windowUtils",
		"import locationHelper",
		"from locationHelper import RectLTRB, RectLTWH",
		helper_start_marker,
		"def _physicalLocationFromMenuLocation(",
		"def _get_location(self) -> RectLTWH | None:",
	):
		if required not in ours:
			raise RuntimeError(f"IAccessible port incomplete: missing {required!r}")

	IA_PATH.write_text(ours, encoding="utf-8", newline="\n")


def resolve_changes() -> None:
	ours = CHANGES_PATH.read_text(encoding="utf-8")
	upstream = git_show(CHANGES_PATH.as_posix())
	bullet = next(
		(
			line
			for line in upstream.splitlines()
			if line.startswith("* 64-bit NVDA now reports the correct location and label") and "#19225" in line
		),
		None,
	)
	if bullet is None:
		raise RuntimeError("Could not locate the upstream #20698 changelog bullet")
	if bullet not in ours:
		anchor = "## 2026.2 Future RC\n\n### Bug Fixes\n\n"
		ours = replace_once(ours, anchor, anchor + bullet + "\n", "2026.2 Future RC bug-fix anchor")
	CHANGES_PATH.write_text(ours, encoding="utf-8", newline="\n")


def main() -> None:
	resolve_iaccessible()
	resolve_changes()
	print("Resolved #20698 conflicts surgically against Evolution baseline.")


if __name__ == "__main__":
	main()
