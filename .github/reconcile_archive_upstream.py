from pathlib import Path

path = Path("source/NVDAObjects/UIA/__init__.py")
text = path.read_text(encoding="utf-8")
old = '''\tdef _get_shouldAllowUIAFocusEvent(self):
\t\ttry:
\t\t\t# Keep the cached event-sender property used by upstream NVDA. A live UIA
\t\t\t# property read here would add cross-process latency to every focus event and
\t\t\t# can block on a hung provider.
\t\t\treturn bool(self._getUIACacheablePropertyValue(UIAHandler.UIA_HasKeyboardFocusPropertyId))
\t\texcept COMError:
\t\t\treturn True
'''
new = '''\tdef _get_shouldAllowUIAFocusEvent(self):
\t\ttry:
\t\t\t# Focus may have moved since the event sender's cache was populated.
\t\t\t# Keep the upstream #20764 current-state check so stale intermediate UIA
\t\t\t# focus events (notably Qt/WeChat Page Up/Down) remain filtered.
\t\t\treturn bool(self.UIAElement.currentHasKeyboardFocus)
\t\texcept COMError:
\t\t\treturn True
'''
if text.count(old) != 1:
	raise RuntimeError(f"Expected exactly one V8 cached focus block, found {text.count(old)}")
path.write_text(text.replace(old, new, 1), encoding="utf-8", newline="")
