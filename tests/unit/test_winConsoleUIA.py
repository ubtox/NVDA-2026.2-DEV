"""Regression tests for console-specific UIA behavior."""

import unittest

from NVDAObjects.UIA import winConsoleUIA


class TestWindowsTerminalCaretTimeout(unittest.TestCase):
	def test_bothStrategiesAllowDelayedCaretUpdates(self):
		self.assertEqual(3.0, winConsoleUIA._DiffBasedWinTerminalUIA._caretMovementTimeoutMultiplier)
		self.assertEqual(3.0, winConsoleUIA._NotificationsBasedWinTerminalUIA._caretMovementTimeoutMultiplier)
