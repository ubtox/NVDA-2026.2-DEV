# A part of NonVisual Desktop Access (NVDA)
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.
# Copyright (C) 2022 NV Access Limited, Leonard de Ruijter

"""Unit tests for the hwIo module."""

import unittest  # noqa: I001
from unittest.mock import MagicMock, patch
import hwIo
import hwIo.base
import threading
from serial.win32 import INVALID_HANDLE_VALUE


class TestIoBaseClose(unittest.TestCase):
	"""Tests for IoBase.close() without requiring real Win32 I/O handles."""

	def _makeIoBase(self, file=1, writeFile=2):
		obj = hwIo.base.IoBase.__new__(hwIo.base.IoBase)
		obj._onReceive = MagicMock()
		obj._onReadError = MagicMock()
		obj._file = file
		obj._writeFile = writeFile
		obj._readOl = hwIo.base.OVERLAPPED()
		obj._writeOl = hwIo.base.OVERLAPPED()
		obj._recvEvt = "RECV_EVT"
		return obj

	def test_close_cancelsWriteWithWriteOverlapped(self):
		"""close() must use the matching OVERLAPPED structure for each handle."""
		obj = self._makeIoBase(file=1, writeFile=2)
		with (
			patch("hwIo.base.winBindings.kernel32.CancelIoEx") as mockCancel,
			patch("hwIo.base.winKernel.closeHandle") as mockCloseHandle,
		):
			obj.close()
		self.assertEqual(mockCancel.call_count, 2)
		readCall = mockCancel.call_args_list[0]
		writeCall = mockCancel.call_args_list[1]
		self.assertEqual(readCall.args[0], 1)
		self.assertEqual(writeCall.args[0], 2)
		self.assertIs(readCall.args[1]._obj, obj._readOl)
		self.assertIs(writeCall.args[1]._obj, obj._writeOl)
		mockCloseHandle.assert_called_once_with("RECV_EVT")

	def test_close_isIdempotent(self):
		"""A repeated close must not cancel or close the same handles again."""
		obj = self._makeIoBase(file=1, writeFile=2)
		with (
			patch("hwIo.base.winBindings.kernel32.CancelIoEx") as mockCancel,
			patch("hwIo.base.winKernel.closeHandle") as mockCloseHandle,
		):
			obj.close()
			obj.close()
		self.assertEqual(mockCloseHandle.call_count, 1)
		self.assertEqual(mockCancel.call_count, 2)

	def test_close_skipsWriteCancelWhenSameHandleAsRead(self):
		obj = self._makeIoBase(file=1, writeFile=1)
		with (
			patch("hwIo.base.winBindings.kernel32.CancelIoEx") as mockCancel,
			patch("hwIo.base.winKernel.closeHandle"),
		):
			obj.close()
		self.assertEqual(mockCancel.call_count, 1)

	def test_close_skipsWriteCancelWhenInvalidHandle(self):
		obj = self._makeIoBase(file=1, writeFile=INVALID_HANDLE_VALUE)
		with (
			patch("hwIo.base.winBindings.kernel32.CancelIoEx") as mockCancel,
			patch("hwIo.base.winKernel.closeHandle"),
		):
			obj.close()
		self.assertEqual(mockCancel.call_count, 1)


class TestBgThreadApc(unittest.TestCase):
	"""Tests whether an APC on the hwIo background thread executes correctly."""

	def setUp(self):
		"""Set up an event to be used in subsequent tests."""
		hwIo.initialize()
		self.event = threading.Event()

	def tearDown(self):
		hwIo.terminate()

	def test_apc(self):
		"""Test queuing an APC that executes correctly.
		As the param provided to the internal APC differs from the param passed to the Python function,
		This test also ensures that the expected param is propagated correctly.
		"""
		self.assertFalse(self.event.is_set())

		class Container:
			param: int

		paramContainer = Container()

		def apc(param: int) -> None:
			paramContainer.param = param
			self.event.set()

		hwIo.bgThread.queueAsApc(apc, 42)
		self.assertTrue(self.event.wait(2))
		self.assertEqual(paramContainer.param, 42)
