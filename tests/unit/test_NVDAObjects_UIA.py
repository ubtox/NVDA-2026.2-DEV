# A part of NonVisual Desktop Access (NVDA)
# Copyright (C) 2026 NV Access Limited
# This file may be used under the terms of the GNU General Public License, version 2 or later.
# For more details see: https://www.gnu.org/licenses/gpl-2.0.html

"""Unit tests for NVDAObjects.UIA."""

import unittest
from unittest.mock import Mock, patch

from NVDAObjects.UIA import UIA


class TestUIAFocusEvent(unittest.TestCase):
	def test_shouldAllowUIAFocusEventIgnoresStaleCache(self):
		obj = object.__new__(UIA)
		obj.UIAElement = Mock(currentHasKeyboardFocus=False)

		with patch.object(UIA, "_getUIACacheablePropertyValue", return_value=True) as getCachedValue:
			self.assertFalse(obj._get_shouldAllowUIAFocusEvent())
			getCachedValue.assert_not_called()
