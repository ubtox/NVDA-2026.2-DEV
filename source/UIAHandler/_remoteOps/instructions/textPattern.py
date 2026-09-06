# A part of NonVisual Desktop Access (NVDA)
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.
# Copyright (C) 2023-2024 NV Access Limited

"""
This module contains the instructions that operate on UI Automation text patterns.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import cast

from UIAHandler import UIA

from .. import builder, lowLevel
from ._base import _TypedInstruction


@dataclass
class TextPatternRangeFromChild(_TypedInstruction):
	opCode = lowLevel.InstructionType.TextPatternRangeFromChild
	result: builder.Operand
	target: builder.Operand
	child: builder.Operand

	def localExecute(self, registers: dict[lowLevel.OperandId, object]):
		textPattern = cast(UIA.IUIAutomationTextPattern, registers[self.target.operandId])
		child = cast(UIA.IUIAutomationElement, registers[self.child.operandId])
		registers[self.result.operandId] = textPattern.RangeFromChild(child)
