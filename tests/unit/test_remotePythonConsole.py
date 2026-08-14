# A part of NonVisual Desktop Access (NVDA)
# Copyright (C) 2026 NV Access Limited
# This file may be used under the terms of the GNU General Public License, version 2 or later.
# For more details see: https://www.gnu.org/licenses/gpl-2.0.html

"""Unit tests for the remote Python console transport."""

from io import BytesIO
import unittest

import remotePythonConsole


class TestRequestHandlerOutput(unittest.TestCase):
	def setUp(self) -> None:
		self.handler = object.__new__(remotePythonConsole.RequestHandler)
		self.handler.wfile = BytesIO()
		self.handler._keepRunning = True

	def test_writeEncodesUnicodeAsUtf8(self) -> None:
		self.handler._write("NVDA é" + chr(0xD800))

		self.assertEqual(b"NVDA \xc3\xa9?", self.handler.wfile.getvalue())

	def test_promptUsesByteTransport(self) -> None:
		self.handler.setPrompt("»")

		self.assertEqual("» ".encode("utf-8"), self.handler.wfile.getvalue())

	def test_promptIsSuppressedAfterExit(self) -> None:
		self.handler.exit()
		self.handler.setPrompt(">>>")

		self.assertEqual(b"", self.handler.wfile.getvalue())


class TestTerminate(unittest.TestCase):
	def test_terminateWithoutServer(self) -> None:
		remotePythonConsole.server = None

		remotePythonConsole.terminate()
