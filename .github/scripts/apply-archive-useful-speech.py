from __future__ import annotations

from pathlib import Path

SPEECH_PATH = Path("source/speech/speech.py")
TEST_PATH = Path("tests/unit/test_speechTypedCharacters_secure.py")
RUNTIME_SETUP_PATH = Path("runtime-builders/synthDriverHost32/setup-runtime.py")

NEW_FUNCTION = '''def speakTypedCharacters(ch: str) -> None:
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

TEST_CONTENT = '''# A part of NonVisual Desktop Access (NVDA)
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.
# Copyright (C) 2026 NVDA contributors

"""Tests for secure lazy protected-state handling in ``speakTypedCharacters``.

The implementation intentionally differs from the rejected PR #20694: when word
speech is disabled and protected state has not been queried, the word buffer uses
mask placeholders rather than retaining unchecked plaintext.
"""

import unittest
from unittest.mock import patch

import config
from config.configFlags import TypingEcho
from speech import speech as speechModule


class TestSecureLazyTypedCharacterProtection(unittest.TestCase):
\tdef setUp(self) -> None:
\t\tself._oldCharacterEcho = config.conf["keyboard"]["speakTypedCharacters"]
\t\tself._oldWordEcho = config.conf["keyboard"]["speakTypedWords"]
\t\tspeechModule.clearTypedWordBuffer()
\t\tspeechModule._speechState._suppressSpeakTypedCharactersNumber = 0
\t\tspeechModule._speechState._suppressSpeakTypedCharactersTime = None

\tdef tearDown(self) -> None:
\t\tconfig.conf["keyboard"]["speakTypedCharacters"] = self._oldCharacterEcho
\t\tconfig.conf["keyboard"]["speakTypedWords"] = self._oldWordEcho
\t\tspeechModule.clearTypedWordBuffer()

\tdef _setEcho(self, chars: TypingEcho, words: TypingEcho) -> None:
\t\tconfig.conf["keyboard"]["speakTypedCharacters"] = chars.value
\t\tconfig.conf["keyboard"]["speakTypedWords"] = words.value

\tdef test_bothEchoModesOffSkipsProtectedLookupAndPreservesBufferLength(self) -> None:
\t\tself._setEcho(TypingEcho.OFF, TypingEcho.OFF)
\t\twith patch.object(speechModule.api, "isTypingProtected") as isTypingProtected:
\t\t\tspeechModule.speakTypedCharacters("a")
\t\tisTypingProtected.assert_not_called()
\t\tself.assertEqual([speechModule.PROTECTED_CHAR], speechModule._curWordChars)

\tdef test_multipleLettersWithEchoOffKeepOnlyMaskedPlaceholders(self) -> None:
\t\tself._setEcho(TypingEcho.OFF, TypingEcho.OFF)
\t\twith patch.object(speechModule.api, "isTypingProtected") as isTypingProtected:
\t\t\tfor ch in "secret":
\t\t\t\tspeechModule.speakTypedCharacters(ch)
\t\tisTypingProtected.assert_not_called()
\t\tself.assertEqual(len("secret"), len(speechModule._curWordChars))
\t\tself.assertEqual(
\t\t\t[speechModule.PROTECTED_CHAR] * len("secret"),
\t\t\tspeechModule._curWordChars,
\t\t)

\tdef test_controlCharacterWithEmptyBufferSkipsProtectedLookup(self) -> None:
\t\tself._setEcho(TypingEcho.ALWAYS, TypingEcho.ALWAYS)
\t\twith patch.object(speechModule.api, "isTypingProtected") as isTypingProtected:
\t\t\tspeechModule.speakTypedCharacters("\\r")
\t\tisTypingProtected.assert_not_called()

\tdef test_wordEchoOffFlushesPlaceholderBufferWithoutLookup(self) -> None:
\t\tself._setEcho(TypingEcho.OFF, TypingEcho.OFF)
\t\tspeechModule._curWordChars.extend([speechModule.PROTECTED_CHAR] * 2)
\t\twith (
\t\t\tpatch.object(speechModule.api, "isTypingProtected") as isTypingProtected,
\t\t\tpatch.object(speechModule, "speakText") as speakText,
\t\t):
\t\t\tspeechModule.speakTypedCharacters(" ")
\t\tisTypingProtected.assert_not_called()
\t\tspeakText.assert_not_called()
\t\tself.assertEqual([], speechModule._curWordChars)

\tdef test_unprotectedCharacterEchoReplacesPlaceholderWithRealCharacter(self) -> None:
\t\tself._setEcho(TypingEcho.ALWAYS, TypingEcho.OFF)
\t\twith (
\t\t\tpatch.object(speechModule.api, "isTypingProtected", return_value=False) as isTypingProtected,
\t\t\tpatch.object(speechModule, "speakSpelling") as speakSpelling,
\t\t):
\t\t\tspeechModule.speakTypedCharacters("a")
\t\tisTypingProtected.assert_called_once_with()
\t\tspeakSpelling.assert_called_once_with("a")
\t\tself.assertEqual(["a"], speechModule._curWordChars)

\tdef test_protectedCharacterEchoKeepsMaskAndSpeaksMask(self) -> None:
\t\tself._setEcho(TypingEcho.ALWAYS, TypingEcho.OFF)
\t\twith (
\t\t\tpatch.object(speechModule.api, "isTypingProtected", return_value=True) as isTypingProtected,
\t\t\tpatch.object(speechModule, "speakSpelling") as speakSpelling,
\t\t):
\t\t\tspeechModule.speakTypedCharacters("a")
\t\tisTypingProtected.assert_called_once_with()
\t\tspeakSpelling.assert_called_once_with(speechModule.PROTECTED_CHAR)
\t\tself.assertEqual([speechModule.PROTECTED_CHAR], speechModule._curWordChars)

\tdef test_wordEchoEnabledBuffersProtectedInputMasked(self) -> None:
\t\tself._setEcho(TypingEcho.OFF, TypingEcho.ALWAYS)
\t\twith patch.object(speechModule.api, "isTypingProtected", return_value=True) as isTypingProtected:
\t\t\tspeechModule.speakTypedCharacters("a")
\t\tisTypingProtected.assert_called_once_with()
\t\tself.assertEqual([speechModule.PROTECTED_CHAR], speechModule._curWordChars)

\tdef test_protectedWordIsNeverSpoken(self) -> None:
\t\tself._setEcho(TypingEcho.OFF, TypingEcho.ALWAYS)
\t\twith patch.object(speechModule.api, "isTypingProtected", return_value=True):
\t\t\tspeechModule.speakTypedCharacters("a")
\t\twith (
\t\t\tpatch.object(speechModule.api, "isTypingProtected", return_value=True) as isTypingProtected,
\t\t\tpatch.object(speechModule, "speakText") as speakText,
\t\t):
\t\t\tspeechModule.speakTypedCharacters(" ")
\t\tisTypingProtected.assert_called_once_with()
\t\tspeakText.assert_not_called()

\tdef test_unprotectedWordIsSpokenNormally(self) -> None:
\t\tself._setEcho(TypingEcho.OFF, TypingEcho.ALWAYS)
\t\twith patch.object(speechModule.api, "isTypingProtected", return_value=False):
\t\t\tfor ch in "hi":
\t\t\t\tspeechModule.speakTypedCharacters(ch)
\t\twith (
\t\t\tpatch.object(speechModule.api, "isTypingProtected", return_value=False),
\t\t\tpatch.object(speechModule, "speakText") as speakText,
\t\t):
\t\t\tspeechModule.speakTypedCharacters(" ")
\t\tspeakText.assert_called_once_with("hi")

\tdef test_editControlCharacterEchoOutsideEditableControlSkipsProtectedLookup(self) -> None:
\t\tself._setEcho(TypingEcho.EDIT_CONTROLS, TypingEcho.OFF)
\t\twith (
\t\t\tpatch.object(speechModule, "isFocusEditable", return_value=False),
\t\t\tpatch.object(speechModule.api, "isTypingProtected") as isTypingProtected,
\t\t\tpatch.object(speechModule, "speakSpelling") as speakSpelling,
\t\t):
\t\t\tspeechModule.speakTypedCharacters("a")
\t\tisTypingProtected.assert_not_called()
\t\tspeakSpelling.assert_not_called()
\t\tself.assertEqual([speechModule.PROTECTED_CHAR], speechModule._curWordChars)


if __name__ == "__main__":
\tunittest.main()
'''


def replace_function() -> None:
\ttext = SPEECH_PATH.read_text(encoding="utf-8")
\tstart = text.index("def speakTypedCharacters")
\tend = text.index("\n\nclass SpeakTextInfoState", start)
\tcurrent = text[start:end]
\tif "bufferedWithoutProtectionCheck" in current:
\t\treturn
\tif "typingIsProtected = api.isTypingProtected()" not in current:
\t\traise RuntimeError("Unexpected speakTypedCharacters implementation; refusing blind replacement")
\tSPEECH_PATH.write_text(text[:start] + NEW_FUNCTION + text[end:], encoding="utf-8", newline="")


def add_tests() -> None:
\tif TEST_PATH.exists() and TEST_PATH.read_text(encoding="utf-8") != TEST_CONTENT:
\t\traise RuntimeError(f"{TEST_PATH} already exists with different content")
\tTEST_PATH.write_text(TEST_CONTENT, encoding="utf-8", newline="")


def align_python314_doc_reference() -> None:
\ttext = RUNTIME_SETUP_PATH.read_text(encoding="utf-8")
\ttext = text.replace(
\t\t"https://docs.python.org/3.13/tutorial/modules.html#compiled-python-files",
\t\t"https://docs.python.org/3.14/tutorial/modules.html#compiled-python-files",
\t)
\tRUNTIME_SETUP_PATH.write_text(text, encoding="utf-8", newline="")


if __name__ == "__main__":
\treplace_function()
\tadd_tests()
\talign_python314_doc_reference()
