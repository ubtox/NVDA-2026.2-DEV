"""Regression tests for braille handling during desktop switches."""

import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import braille


class TestSecureDesktopStateChanged(unittest.TestCase):
	@patch.object(braille.easeOfAccess, "isRegistered", return_value=True)
	def test_ordinaryDesktopSwitchDoesNotRestoreCurrentDisplay(self, _isRegistered):
		displayName = "testDisplay"
		handler = SimpleNamespace(
			autoScroll=MagicMock(),
			mainBuffer=MagicMock(),
			display=SimpleNamespace(name=displayName),
			_lastRequestedDisplayName=displayName,
			_enableDetection=MagicMock(),
			setDisplayByName=MagicMock(),
		)

		braille.BrailleHandler._onSecureDesktopStateChanged(handler, isSecureDesktop=False)

		handler.autoScroll.assert_called_once_with(enable=False)
		handler.mainBuffer.clear.assert_called_once_with()
		handler._enableDetection.assert_not_called()
		handler.setDisplayByName.assert_not_called()
