# A part of NonVisual Desktop Access (NVDA)
# Copyright (C) 2026 NV Access Limited, Leonard de Ruijter, Tobias Heath
# This file may be used under the terms of the GNU General Public License, version 2 or later, as modified by the NVDA license.
# For full terms and any additional permissions, see the NVDA license file:
# https://github.com/nvaccess/nvda/blob/master/copying.txt


"""Unit tests for the UIAHandler hung-window guard.

These cover the mechanism that drops UIA events from a not-responding
application so it cannot freeze NVDA or flood the log.
"""

from unittest import TestCase  # noqa: I001
from unittest.mock import Mock, patch

from comtypes import COMError

import textInfos
import UIAHandler
from UIAHandler import getUIAUnitFromNVDAUnit, NVDAUnitsToUIAUnits, utils
import winUser


def _makeCOMError() -> COMError:
	# Mirrors the error seen when an unresponsive application's element is accessed:
	# (-2147220991, 'An event was unable to invoke any of the subscribers', ...)
	return COMError(
		-2147220991,
		"An event was unable to invoke any of the subscribers",
		(None, None, None, 0, None),
	)


class _FakeElement:
	"""Stand-in for an IUIAutomationElement event sender."""

	def __init__(self, cachedHandle: int = 0, raiseOnCached: bool = False) -> None:
		self._cachedHandle = cachedHandle
		self._raiseOnCached = raiseOnCached

	@property
	def cachedNativeWindowHandle(self) -> int:
		if self._raiseOnCached:
			raise _makeCOMError()
		return self._cachedHandle

	@property
	def currentNativeWindowHandle(self):
		raise AssertionError(
			"The hung-window guard must never read a live (current) property, "
			"as that is exactly the call that hangs on an unresponsive application.",
		)


class Test_getUIAUnitFromNVDAUnit(TestCase):
	def test_mappedUnitReturnsUIAUnit(self):
		self.assertEqual(
			getUIAUnitFromNVDAUnit(textInfos.UNIT_WORD),
			NVDAUnitsToUIAUnits[textInfos.UNIT_WORD],
		)

	def test_unmappedUnitRaisesNotImplementedError(self):
		with self.assertRaises(NotImplementedError):
			getUIAUnitFromNVDAUnit(textInfos.UNIT_SENTENCE)


class Test_getCachedWindowHandleFromEvent(TestCase):
	def test_returnsHandle(self):
		self.assertEqual(
			utils._getCachedWindowHandleFromEvent(_FakeElement(cachedHandle=1234)),
			1234,
		)

	def test_noHandleReturnsNone(self):
		self.assertIsNone(utils._getCachedWindowHandleFromEvent(_FakeElement(cachedHandle=0)))

	def test_comErrorReturnsNone(self):
		# Must swallow the COMError rather than propagate, and must not fall back
		# to the live property (which _FakeElement asserts against).
		self.assertIsNone(utils._getCachedWindowHandleFromEvent(_FakeElement(raiseOnCached=True)))


class TestNormalizeUIAText(TestCase):
	def test_plainTextReturnedUnchanged(self):
		text = "NVDA WinUI 3"
		self.assertIs(utils.normalizeUIAText(text), text)

	def test_validSurrogatePairBecomesUnicodeScalar(self):
		self.assertEqual(utils.normalizeUIAText("\ud83d\ude00"), "😀")

	def test_isolatedHighSurrogateIsReplaced(self):
		self.assertEqual(utils.normalizeUIAText("A\ud83dB"), "A\ufffdB")

	def test_isolatedLowSurrogateIsReplaced(self):
		self.assertEqual(utils.normalizeUIAText("A\ude00B"), "A\ufffdB")


class TestUIATextRangeFromElement(TestCase):
	def test_standardRangeFromChildHasPriority(self):
		textPattern = Mock()
		standardRange = Mock()
		textPattern.rangeFromChild.return_value = standardRange
		element = Mock()

		self.assertIs(utils.UIATextRangeFromElement(textPattern, element), standardRange)
		element.GetCurrentPattern.assert_not_called()

	def test_textChildPatternFallbackAfterCOMError(self):
		textPattern = Mock()
		textPattern.rangeFromChild.side_effect = COMError(-1, "failure", None)
		documentRange = Mock()
		textPattern.documentRange = documentRange
		element = Mock()
		textChildRange = Mock()
		textChildPattern = Mock(TextRange=textChildRange)
		punk = Mock()
		punk.QueryInterface.return_value = textChildPattern
		element.GetCurrentPattern.return_value = punk

		self.assertIs(utils.UIATextRangeFromElement(textPattern, element), textChildRange)
		element.GetCurrentPattern.assert_called_once_with(UIAHandler.UIA_TextChildPatternId)
		textChildRange.CompareEndpoints.assert_called_once_with(
			UIAHandler.TextPatternRangeEndpoint_Start,
			documentRange,
			UIAHandler.TextPatternRangeEndpoint_Start,
		)

	def test_textChildPatternFallbackAfterNullRange(self):
		textPattern = Mock()
		textPattern.rangeFromChild.return_value = None
		textPattern.documentRange = Mock()
		element = Mock()
		textChildRange = Mock()
		textChildPattern = Mock(TextRange=textChildRange)
		punk = Mock()
		punk.QueryInterface.return_value = textChildPattern
		element.GetCurrentPattern.return_value = punk

		self.assertIs(utils.UIATextRangeFromElement(textPattern, element), textChildRange)

	def test_textChildPatternFallbackRejectsRangeFromDifferentTextProvider(self):
		textPattern = Mock()
		textPattern.rangeFromChild.return_value = None
		textPattern.documentRange = Mock()
		element = Mock()
		textChildRange = Mock()
		textChildRange.CompareEndpoints.side_effect = COMError(-1, "different provider", None)
		textChildPattern = Mock(TextRange=textChildRange)
		punk = Mock()
		punk.QueryInterface.return_value = textChildPattern
		element.GetCurrentPattern.return_value = punk

		self.assertIsNone(utils.UIATextRangeFromElement(textPattern, element))


class Test_shouldSkipEventForHungWindow(TestCase):
	def test_noWindowHandleIsNotSkipped(self):
		with patch.object(winUser, "isHungAppWindow", side_effect=AssertionError("must not be called")):
			self.assertFalse(utils._shouldSkipEventForHungWindow(_FakeElement(cachedHandle=0)))

	def test_hungWindowIsSkipped(self):
		with patch.object(winUser, "isHungAppWindow", return_value=True):
			self.assertTrue(utils._shouldSkipEventForHungWindow(_FakeElement(cachedHandle=1)))

	def test_respondingWindowIsNotSkipped(self):
		with patch.object(winUser, "isHungAppWindow", return_value=False):
			self.assertFalse(utils._shouldSkipEventForHungWindow(_FakeElement(cachedHandle=1)))

	def test_guardNeverRaises(self):
		with patch.object(winUser, "isHungAppWindow", side_effect=RuntimeError("boom")):
			# A failure inside the guard itself must never escape into the COM handler.
			self.assertFalse(utils._shouldSkipEventForHungWindow(_FakeElement(cachedHandle=1)))


class _FakeCachedClassElement:
	CachedClassName = "_WwG"
	CachedAutomationID = ""

	@property
	def currentClassName(self):
		raise AssertionError("Local UIA event registration must not read currentClassName")


class Test_addLocalEventHandlerGroupToElement(TestCase):
	def test_usesCachedClassName(self) -> None:
		handler = object.__new__(UIAHandler.UIAHandler)
		handler.localEventHandlerGroup = object()
		handler.localEventHandlerGroupWithTextChanges = object()
		handler._localEventHandlerGroupElements = set()
		handler.MTAThreadQueue = Mock()
		handler.addEventHandlerGroup = Mock()
		element = _FakeCachedClassElement()

		handler.addLocalEventHandlerGroupToElement(element)
		handler.MTAThreadQueue.put_nowait.assert_called_once()
		queuedFunction = handler.MTAThreadQueue.put_nowait.call_args.args[0]
		queuedFunction()

		handler.addEventHandlerGroup.assert_called_once_with(
			element,
			handler.localEventHandlerGroupWithTextChanges,
		)
		self.assertIn(element, handler._localEventHandlerGroupElements)
