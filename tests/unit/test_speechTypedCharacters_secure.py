# A part of NonVisual Desktop Access (NVDA)
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.
# Copyright (C) 2026 NVDA contributors

"""Regression tests for secure lazy protected-state handling in typed-character speech."""

import unittest
from unittest.mock import patch

import config
from config.configFlags import TypingEcho
from speech import speech as speechModule


class TestSecureLazyTypedCharacterProtection(unittest.TestCase):
	def setUp(self) -> None:
		self._oldCharacterEcho = config.conf["keyboard"]["speakTypedCharacters"]
		self._oldWordEcho = config.conf["keyboard"]["speakTypedWords"]
		speechModule.clearTypedWordBuffer()
		speechModule._speechState._suppressSpeakTypedCharactersNumber = 0
		speechModule._speechState._suppressSpeakTypedCharactersTime = None

	def tearDown(self) -> None:
		config.conf["keyboard"]["speakTypedCharacters"] = self._oldCharacterEcho
		config.conf["keyboard"]["speakTypedWords"] = self._oldWordEcho
		speechModule.clearTypedWordBuffer()

	def _setEcho(self, chars: TypingEcho, words: TypingEcho) -> None:
		config.conf["keyboard"]["speakTypedCharacters"] = chars.value
		config.conf["keyboard"]["speakTypedWords"] = words.value

	def test_bothEchoModesOffSkipsProtectedLookupAndPreservesBufferLength(self) -> None:
		self._setEcho(TypingEcho.OFF, TypingEcho.OFF)
		with patch.object(speechModule.api, "isTypingProtected") as isTypingProtected:
			speechModule.speakTypedCharacters("a")
		isTypingProtected.assert_not_called()
		self.assertEqual([speechModule.PROTECTED_CHAR], speechModule._curWordChars)

	def test_multipleLettersWithEchoOffKeepOnlyMaskedPlaceholders(self) -> None:
		self._setEcho(TypingEcho.OFF, TypingEcho.OFF)
		with patch.object(speechModule.api, "isTypingProtected") as isTypingProtected:
			for ch in "secret":
				speechModule.speakTypedCharacters(ch)
		isTypingProtected.assert_not_called()
		self.assertEqual(len("secret"), len(speechModule._curWordChars))
		self.assertEqual([speechModule.PROTECTED_CHAR] * len("secret"), speechModule._curWordChars)

	def test_controlCharacterWithEmptyBufferSkipsProtectedLookup(self) -> None:
		self._setEcho(TypingEcho.ALWAYS, TypingEcho.ALWAYS)
		with patch.object(speechModule.api, "isTypingProtected") as isTypingProtected:
			speechModule.speakTypedCharacters("\r")
		isTypingProtected.assert_not_called()

	def test_wordEchoOffFlushesPlaceholderBufferWithoutLookup(self) -> None:
		self._setEcho(TypingEcho.OFF, TypingEcho.OFF)
		speechModule._curWordChars.extend([speechModule.PROTECTED_CHAR] * 2)
		with (
			patch.object(speechModule.api, "isTypingProtected") as isTypingProtected,
			patch.object(speechModule, "speakText") as speakText,
		):
			speechModule.speakTypedCharacters(" ")
		isTypingProtected.assert_not_called()
		speakText.assert_not_called()
		self.assertEqual([], speechModule._curWordChars)

	def test_unprotectedCharacterEchoReplacesPlaceholderWithRealCharacter(self) -> None:
		self._setEcho(TypingEcho.ALWAYS, TypingEcho.OFF)
		with (
			patch.object(speechModule.api, "isTypingProtected", return_value=False) as isTypingProtected,
			patch.object(speechModule, "speakSpelling") as speakSpelling,
		):
			speechModule.speakTypedCharacters("a")
		isTypingProtected.assert_called_once_with()
		speakSpelling.assert_called_once_with("a")
		self.assertEqual(["a"], speechModule._curWordChars)

	def test_protectedCharacterEchoKeepsMaskAndSpeaksMask(self) -> None:
		self._setEcho(TypingEcho.ALWAYS, TypingEcho.OFF)
		with (
			patch.object(speechModule.api, "isTypingProtected", return_value=True) as isTypingProtected,
			patch.object(speechModule, "speakSpelling") as speakSpelling,
		):
			speechModule.speakTypedCharacters("a")
		isTypingProtected.assert_called_once_with()
		speakSpelling.assert_called_once_with(speechModule.PROTECTED_CHAR)
		self.assertEqual([speechModule.PROTECTED_CHAR], speechModule._curWordChars)

	def test_wordEchoEnabledBuffersProtectedInputMasked(self) -> None:
		self._setEcho(TypingEcho.OFF, TypingEcho.ALWAYS)
		with patch.object(speechModule.api, "isTypingProtected", return_value=True) as isTypingProtected:
			speechModule.speakTypedCharacters("a")
		isTypingProtected.assert_called_once_with()
		self.assertEqual([speechModule.PROTECTED_CHAR], speechModule._curWordChars)

	def test_protectedWordIsNeverSpoken(self) -> None:
		self._setEcho(TypingEcho.OFF, TypingEcho.ALWAYS)
		with patch.object(speechModule.api, "isTypingProtected", return_value=True):
			speechModule.speakTypedCharacters("a")
		with (
			patch.object(speechModule.api, "isTypingProtected", return_value=True) as isTypingProtected,
			patch.object(speechModule, "speakText") as speakText,
		):
			speechModule.speakTypedCharacters(" ")
		isTypingProtected.assert_called_once_with()
		speakText.assert_not_called()

	def test_unprotectedWordIsSpokenNormally(self) -> None:
		self._setEcho(TypingEcho.OFF, TypingEcho.ALWAYS)
		with patch.object(speechModule.api, "isTypingProtected", return_value=False):
			for ch in "hi":
				speechModule.speakTypedCharacters(ch)
		with (
			patch.object(speechModule.api, "isTypingProtected", return_value=False),
			patch.object(speechModule, "speakText") as speakText,
		):
			speechModule.speakTypedCharacters(" ")
		speakText.assert_called_once_with("hi")

	def test_editControlCharacterEchoOutsideEditableControlSkipsProtectedLookup(self) -> None:
		self._setEcho(TypingEcho.EDIT_CONTROLS, TypingEcho.OFF)
		with (
			patch.object(speechModule, "isFocusEditable", return_value=False),
			patch.object(speechModule.api, "isTypingProtected") as isTypingProtected,
			patch.object(speechModule, "speakSpelling") as speakSpelling,
		):
			speechModule.speakTypedCharacters("a")
		isTypingProtected.assert_not_called()
		speakSpelling.assert_not_called()
		self.assertEqual([speechModule.PROTECTED_CHAR], speechModule._curWordChars)


if __name__ == "__main__":
	unittest.main()
