from __future__ import annotations

from pathlib import Path


def read(path: str) -> str:
	with Path(path).open("r", encoding="utf-8", newline="") as f:
		return f.read()


def write(path: str, text: str) -> None:
	with Path(path).open("w", encoding="utf-8", newline="") as f:
		f.write(text)


def replace_once(path: str, old: str, new: str, label: str) -> None:
	text = read(path)
	count = text.count(old)
	if count != 1:
		raise RuntimeError(f"{label}: expected exactly one old block in {path}, found {count}")
	write(path, text.replace(old, new, 1))
	print(f"applied: {label}")


UIA = "source/NVDAObjects/UIA/__init__.py"
SPEECH = "source/speech/speech.py"
MAGNIFIER = "source/_magnifier/utils/focusManager.py"

replace_once(
	UIA,
	"\tUIAMixedAttributeError,\n\tUIATextRangeFromElement,\n\t_shouldUseWindowsTerminalNotifications,\n",
	"\tUIAMixedAttributeError,\n\tUIATextRangeFromElement,\n\tnormalizeUIAText,\n\t_shouldUseWindowsTerminalNotifications,\n",
	"UIA import normalizeUIAText",
)

replace_once(
	UIA,
	"""\t\telif position in (textInfos.POSITION_CARET, textInfos.POSITION_SELECTION):
\t\t\ttry:
\t\t\t\tsel = self.obj.UIATextPattern.GetSelection()
\t\t\texcept COMError:
\t\t\t\traise RuntimeError("No selection available")
\t\t\tif sel.length > 0:
\t\t\t\tself._rangeObj: IUIAutomationTextRangeT = sel.getElement(0).clone()
\t\t\telse:
\t\t\t\traise NotImplementedError("UIAutomationTextRangeArray is empty")
\t\t\tif position == textInfos.POSITION_CARET:
\t\t\t\tself.collapse()
""",
	"""\t\telif position in (textInfos.POSITION_CARET, textInfos.POSITION_SELECTION):
\t\t\t# Preserve NVDA's established TextPattern.GetSelection path first. This avoids
\t\t\t# adding an extra cross-process COM call for providers that already work well.
\t\t\tselectionError: COMError | None = None
\t\t\ttry:
\t\t\t\tsel = self.obj.UIATextPattern.GetSelection()
\t\t\texcept COMError as e:
\t\t\t\tselectionError = e
\t\t\t\tsel = None
\t\t\tif sel is not None and sel.length > 0:
\t\t\t\tself._rangeObj: IUIAutomationTextRangeT = sel.getElement(0).clone()
\t\t\t\tif position == textInfos.POSITION_CARET:
\t\t\t\t\tself.collapse()
\t\t\telse:
\t\t\t\t# TextPattern2 is a fallback only for caret retrieval. Some modern UIA
\t\t\t\t# providers expose a valid caret even when GetSelection fails or returns
\t\t\t\t# an empty array. Keeping it as a fallback protects the normal x64 path.
\t\t\t\tif position == textInfos.POSITION_CARET:
\t\t\t\t\ttextPattern2 = self.obj.UIATextPattern2
\t\t\t\t\tif textPattern2:
\t\t\t\t\t\ttry:
\t\t\t\t\t\t\tcaretResult = textPattern2.GetCaretRange()
\t\t\t\t\t\t\tif isinstance(caretResult, tuple):
\t\t\t\t\t\t\t\tisActive, caretRange = caretResult
\t\t\t\t\t\t\telse:
\t\t\t\t\t\t\t\tisActive, caretRange = True, caretResult
\t\t\t\t\t\t\tif isActive and caretRange:
\t\t\t\t\t\t\t\tself._rangeObj = caretRange.clone()
\t\t\t\t\t\t\t\treturn
\t\t\t\t\t\texcept (COMError, ValueError):
\t\t\t\t\t\t\tpass
\t\t\t\tif selectionError is not None:
\t\t\t\t\traise RuntimeError("No selection available") from selectionError
\t\t\t\traise NotImplementedError("UIAutomationTextRangeArray is empty")
""",
	"UIA TextPattern2 caret fallback",
)

replace_once(
	UIA,
	"""\t\telif isinstance(position, UIA) or isinstance(position, UIAHandler.IUIAutomationElement):  # noqa: SIM101
\t\t\tif isinstance(position, UIA):
\t\t\t\tposition = position.UIAElement
\t\t\ttry:
\t\t\t\tself._rangeObj: IUIAutomationTextRangeT | None = self.obj.UIATextPattern.rangeFromChild(
\t\t\t\t\tposition,
\t\t\t\t)
\t\t\texcept COMError:
\t\t\t\traise LookupError
\t\t\t# sometimes rangeFromChild can return a NULL range
\t\t\tif not self._rangeObj:
\t\t\t\traise LookupError
""",
	"""\t\telif isinstance(position, UIA) or isinstance(position, UIAHandler.IUIAutomationElement):  # noqa: SIM101
\t\t\tif isinstance(position, UIA):
\t\t\t\tposition = position.UIAElement
\t\t\tself._rangeObj: IUIAutomationTextRangeT | None = UIATextRangeFromElement(
\t\t\t\tself.obj.UIATextPattern,
\t\t\t\tposition,
\t\t\t)
\t\t\t# Sometimes both patterns can legitimately return a NULL range.
\t\t\tif not self._rangeObj:
\t\t\t\traise LookupError
""",
	"UIA TextChild range fallback",
)

replace_once(
	UIA,
	'''\tdef _getTextFromUIARange(self, textRange: IUIAutomationTextRangeT) -> str:
\t\t"""
\t\tFetches plain text from the given UI Automation text range.
\t\tJust calls getText(-1). This only exists to be overridden for filtering.
\t\t"""
\t\treturn textRange.getText(-1)
''',
	'''\tdef _getTextFromUIARange(self, textRange: IUIAutomationTextRangeT) -> str:
\t\t"""Fetch plain text from a UI Automation text range and normalize UTF-16 surrogates.

\t\tSome UIA providers expose text in UTF-16 code units and may return a surrogate pair
\t\tas two Python surrogate characters, or even return an isolated surrogate while moving
\t\tby character. Python cannot safely log or speak isolated surrogates as UTF-8.
\t\tRe-decode only strings which contain surrogate code points: valid pairs become their
\t\tUnicode scalar value and unmatched halves become the replacement character.
\t\t"""
\t\treturn normalizeUIAText(textRange.getText(-1))
''',
	"UIA text normalization",
)

replace_once(
	UIA,
	"""\tdef _get_shouldAllowUIAFocusEvent(self):
\t\ttry:
\t\t\t# Focus may have moved since the event sender's cache was populated.
\t\t\treturn bool(self.UIAElement.currentHasKeyboardFocus)
\t\texcept COMError:
\t\t\treturn True
""",
	"""\tdef _get_shouldAllowUIAFocusEvent(self):
\t\ttry:
\t\t\t# Keep the cached event-sender property used by upstream NVDA. A live UIA
\t\t\t# property read here would add cross-process latency to every focus event and
\t\t\t# can block on a hung provider.
\t\t\treturn bool(self._getUIACacheablePropertyValue(UIAHandler.UIA_HasKeyboardFocusPropertyId))
\t\texcept COMError:
\t\t\treturn True
""",
	"UIA cached keyboard focus state",
)

old_pattern = """\tdef _get_UIATextPattern(self):
\t\tself.UIATextPattern = self._getUIAPattern(
\t\t\tUIAHandler.UIA_TextPatternId,
\t\t\tUIAHandler.IUIAutomationTextPattern,
\t\t\tcache=False,
\t\t)
\t\treturn self.UIATextPattern
"""
new_pattern = (
	old_pattern
	+ '''
\tdef _get_UIATextPattern2(self):
\t\ttry:
\t\t\tself.UIATextPattern2 = self._getUIAPattern(
\t\t\t\tUIAHandler.UIA_TextPattern2Id,
\t\t\t\tUIAHandler.IUIAutomationTextPattern2,
\t\t\t\tcache=False,
\t\t\t)
\t\texcept (COMError, AttributeError):
\t\t\t# TextPattern2 is optional. Providers may expose only the original
\t\t\t# TextPattern and older UIAutomationClient type libraries may not define it.
\t\t\tself.UIATextPattern2 = None
\t\treturn self.UIATextPattern2

\tdef _get_UIAVirtualizedItemPattern(self):
\t\ttry:
\t\t\tself.UIAVirtualizedItemPattern = self._getUIAPattern(
\t\t\t\tUIAHandler.UIA_VirtualizedItemPatternId,
\t\t\t\tUIAHandler.IUIAutomationVirtualizedItemPattern,
\t\t\t)
\t\texcept (COMError, AttributeError):
\t\t\tself.UIAVirtualizedItemPattern = None
\t\treturn self.UIAVirtualizedItemPattern

\tdef _get_UIAScrollItemPattern(self):
\t\ttry:
\t\t\tself.UIAScrollItemPattern = self._getUIAPattern(
\t\t\t\tUIAHandler.UIA_ScrollItemPatternId,
\t\t\t\tUIAHandler.IUIAutomationScrollItemPattern,
\t\t\t)
\t\texcept (COMError, AttributeError):
\t\t\tself.UIAScrollItemPattern = None
\t\treturn self.UIAScrollItemPattern

\tdef realizeUIAVirtualizedItem(self) -> bool:
\t\t"""Ask a provider to materialize this element if it exposes VirtualizedItemPattern.

\t\tThis is intentionally explicit rather than automatic: realizing an item may scroll
\t\tor otherwise alter an application's visual state. Consumers can opt in when they
\t\tneed properties that a virtualized placeholder cannot provide.
\t\t"""
\t\tpattern = self.UIAVirtualizedItemPattern
\t\tif not pattern:
\t\t\treturn False
\t\ttry:
\t\t\tpattern.Realize()
\t\texcept COMError:
\t\t\treturn False
\t\treturn True
'''
)
replace_once(UIA, old_pattern, new_pattern, "UIA modern patterns and virtualization")

replace_once(
	UIA,
	"""\tdef setFocus(self):
\t\tself.UIAElement.setFocus()
""",
	"""\tdef setFocus(self):
\t\ttry:
\t\t\tself.UIAElement.setFocus()
\t\t\treturn
\t\texcept COMError:
\t\t\t# Virtualized WinUI/WPF items can reject SetFocus until they are realized.
\t\t\t# Realization is only attempted after the ordinary focus path fails, so
\t\t\t# providers that do not need it retain the existing behavior.
\t\t\tif not self.realizeUIAVirtualizedItem():
\t\t\t\traise
\t\tself.UIAElement.setFocus()
""",
	"UIA virtualized focus recovery",
)

replace_once(
	UIA,
	"""\tdef scrollIntoView(self):
\t\tpass
""",
	'''\tdef scrollIntoView(self):
\t\t"""Scroll this UIA object into view using ScrollItemPattern when available.

\t\tVirtualized items are realized only when necessary, then ScrollItemPattern is
\t\tqueried again because some providers expose it only after realization.
\t\t"""
\t\tpattern = self.UIAScrollItemPattern
\t\tif pattern:
\t\t\ttry:
\t\t\t\tpattern.ScrollIntoView()
\t\t\t\treturn
\t\t\texcept COMError:
\t\t\t\tpass
\t\tif not self.realizeUIAVirtualizedItem():
\t\t\treturn
\t\t# Drop a previously cached absence/failure and ask the provider again.
\t\ttry:
\t\t\tdel self.UIAScrollItemPattern
\t\texcept AttributeError:
\t\t\tpass
\t\tpattern = self.UIAScrollItemPattern
\t\tif not pattern:
\t\t\treturn
\t\ttry:
\t\t\tpattern.ScrollIntoView()
\t\texcept COMError:
\t\t\tlog.debugWarning("UIA ScrollItemPattern.ScrollIntoView failed", exc_info=True)
''',
	"UIA scroll/realize fallback",
)

old_speech = """def speakTypedCharacters(ch: str):
\ttypingIsProtected = api.isTypingProtected()
\tif typingIsProtected:
\t\trealChar = PROTECTED_CHAR
\telse:
\t\trealChar = ch
\tif unicodedata.category(ch)[0] in "LMN":
\t\t_curWordChars.append(realChar)
\telif ch == "\\b":
\t\t# Backspace, so remove the last character from our buffer.
\t\tdel _curWordChars[-1:]
\telif ch == "\\u007f":
\t\t# delete character produced in some apps with control+backspace
\t\treturn
\telif len(_curWordChars) > 0:
\t\ttypedWord = "".join(_curWordChars)
\t\tclearTypedWordBuffer()
\t\tif log.isEnabledFor(log.IO):
\t\t\tlog.io("typed word: %s" % typedWord)  # noqa: UP031
\t\ttypingEchoMode = config.conf["keyboard"]["speakTypedWords"]
\t\tif typingEchoMode != TypingEcho.OFF.value and not typingIsProtected:  # noqa: SIM102
\t\t\tif typingEchoMode == TypingEcho.ALWAYS.value or (
\t\t\t\ttypingEchoMode == TypingEcho.EDIT_CONTROLS.value and isFocusEditable()
\t\t\t):
\t\t\t\tspeakText(typedWord)
\tif _speechState._suppressSpeakTypedCharactersNumber > 0:
\t\t# We primarily suppress based on character count and still have characters to suppress.
\t\t# However, we time out after a short while just in case.
\t\tsuppress = time.time() - _speechState._suppressSpeakTypedCharactersTime <= 0.1
\t\tif suppress:
\t\t\t_speechState._suppressSpeakTypedCharactersNumber -= 1
\t\telse:
\t\t\t_speechState._suppressSpeakTypedCharactersNumber = 0
\t\t\t_speechState._suppressSpeakTypedCharactersTime = None
\telse:
\t\tsuppress = False

\ttypingEchoMode = config.conf["keyboard"]["speakTypedCharacters"]
\tif not suppress and typingEchoMode != TypingEcho.OFF.value and ch >= FIRST_NONCONTROL_CHAR:  # noqa: SIM102
\t\tif typingEchoMode == TypingEcho.ALWAYS.value or (
\t\t\ttypingEchoMode == TypingEcho.EDIT_CONTROLS.value and isFocusEditable()
\t\t):
\t\t\tspeakSpelling(realChar)
"""
new_speech = '''def speakTypedCharacters(ch: str) -> None:
\t# Resolving protected state can require a blocking cross-process accessibility call.
\t# Keep the result lazy, and avoid the call entirely when neither speech nor secure
\t# word buffering needs it. Unlike the rejected #20694 approach, never buffer plain
\t# text when protection has not been checked.
\tcachedTypingIsProtected: bool | None = None
\twordEchoMode = config.conf["keyboard"]["speakTypedWords"]
\tcharacterEchoMode = config.conf["keyboard"]["speakTypedCharacters"]

\tdef typingIsProtected() -> bool:
\t\t"""Whether the focus object hides its input, fetched at most once per call."""
\t\tnonlocal cachedTypingIsProtected
\t\tif cachedTypingIsProtected is None:
\t\t\tcachedTypingIsProtected = api.isTypingProtected()
\t\treturn cachedTypingIsProtected

\tdef getRealChar() -> str:
\t\t"""The character to expose to speech/buffering, masked when protected."""
\t\treturn PROTECTED_CHAR if typingIsProtected() else ch

\tbufferedWithoutProtectionCheck = False
\tif unicodedata.category(ch)[0] in "LMN":
\t\tif wordEchoMode == TypingEcho.OFF.value:
\t\t\t# Other NVDA code relies on the buffer length while filtering echoed terminal
\t\t\t# text. Preserve that length without storing unchecked plaintext passwords.
\t\t\t_curWordChars.append(PROTECTED_CHAR)
\t\t\tbufferedWithoutProtectionCheck = True
\t\telse:
\t\t\t_curWordChars.append(getRealChar())
\telif ch == "\\b":
\t\t# Backspace, so remove the last character from our buffer.
\t\tdel _curWordChars[-1:]
\telif ch == "\\u007f":
\t\t# delete character produced in some apps with control+backspace
\t\treturn
\telif len(_curWordChars) > 0:
\t\ttypedWord = "".join(_curWordChars)
\t\tclearTypedWordBuffer()
\t\tif log.isEnabledFor(log.IO):
\t\t\tlog.io("typed word: %s" % typedWord)  # noqa: UP031
\t\tif (
\t\t\twordEchoMode != TypingEcho.OFF.value
\t\t\tand (
\t\t\t\twordEchoMode == TypingEcho.ALWAYS.value
\t\t\t\tor (wordEchoMode == TypingEcho.EDIT_CONTROLS.value and isFocusEditable())
\t\t\t)
\t\t\tand not typingIsProtected()
\t\t):
\t\t\tspeakText(typedWord)
\tif _speechState._suppressSpeakTypedCharactersNumber > 0:
\t\t# We primarily suppress based on character count and still have characters to suppress.
\t\t# However, we time out after a short while just in case.
\t\tsuppress = time.time() - _speechState._suppressSpeakTypedCharactersTime <= 0.1
\t\tif suppress:
\t\t\t_speechState._suppressSpeakTypedCharactersNumber -= 1
\t\telse:
\t\t\t_speechState._suppressSpeakTypedCharactersNumber = 0
\t\t\t_speechState._suppressSpeakTypedCharactersTime = None
\telse:
\t\tsuppress = False

\tif not suppress and characterEchoMode != TypingEcho.OFF.value and ch >= FIRST_NONCONTROL_CHAR:  # noqa: SIM102
\t\tif characterEchoMode == TypingEcho.ALWAYS.value or (
\t\t\tcharacterEchoMode == TypingEcho.EDIT_CONTROLS.value and isFocusEditable()
\t\t):
\t\t\trealChar = getRealChar()
\t\t\t# If character echo already established that this field is not protected, keep
\t\t\t# the traditional real-character buffer semantics without an extra UIA call.
\t\t\tif bufferedWithoutProtectionCheck and realChar != PROTECTED_CHAR:
\t\t\t\t_curWordChars[-1] = ch
\t\t\tspeakSpelling(realChar)
'''
replace_once(SPEECH, old_speech, new_speech, "secure lazy typed-character protection")

replace_once(
	MAGNIFIER,
	'''\tdef _getNavigatorObjectLocation(self) -> Coordinates | None:
\t\t"""
\t\tGet the navigator object location from its bounding rectangle.

\t\t:return: The (x, y) coordinates of the navigator object center, or None if not available
\t\t"""
\t\tnavigatorObject = api.getNavigatorObject()
\t\tif navigatorObject:
\t\t\ttry:
\t\t\t\tleft, top, width, _height = navigatorObject.location
\t\t\t\tx = left + width if _isWindowRTL(navigatorObject) else left
\t\t\t\treturn Coordinates(x, top)
\t\t\texcept Exception:
\t\t\t\t# Navigator object may not have a valid location
\t\t\t\tif _isDebug():
\t\t\t\t\tlog.debug("Failed to get navigator object location", exc_info=True)
\t\treturn None
''',
	'''\tdef _getNavigatorObjectLocation(self) -> Coordinates | None:
\t\t"""
\t\tGet the navigator object location from its bounding rectangle.

\t\t:return: The (x, y) coordinates of the navigator object center, or None if not available
\t\t"""
\t\ttry:
\t\t\tnavigatorObject = api.getNavigatorObject()
\t\t\tif navigatorObject:
\t\t\t\tleft, top, width, _height = navigatorObject.location
\t\t\t\tx = left + width if _isWindowRTL(navigatorObject) else left
\t\t\t\treturn Coordinates(x, top)
\t\texcept Exception:
\t\t\t# #20488: UIA navigator creation itself can fail when a provider returns
\t\t\t# an invalid/stale text range. Treat this the same as an unavailable
\t\t\t# location so the magnifier keeps updating on subsequent cycles.
\t\t\tif _isDebug():
\t\t\t\tlog.debug("Failed to get navigator object location", exc_info=True)
\t\treturn None
''',
	"magnifier recovery when navigator creation fails",
)

print("V8 consolidation transformations completed")
