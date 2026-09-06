# A part of NonVisual Desktop Access (NVDA)
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.
# Copyright (C) 2023-2024 NV Access Limited

"""
This package contains all the instructions that can be executed by the remote ops framework.
Each instruction contains the appropriate op code and parameter types.
Most instructions also contain a `localExecute` method,
which provides an implementation of the instruction that can be executed locally.
"""


# Import all instructions so that they can be accessed as attributes of this module.
# flake8: noqa: F401

from ..builder import InstructionBase
from .arithmetic import (
	BinaryAdd,
	BinaryDivide,
	BinaryMultiply,
	BinarySubtract,
	InplaceAdd,
	InplaceDivide,
	InplaceMultiply,
	InplaceSubtract,
)
from .array import (
	ArrayAppend,
	ArrayGetAt,
	ArrayRemoveAt,
	ArraySetAt,
	ArraySize,
	IsArray,
	NewArray,
)
from .bool import (
	BoolAnd,
	BoolNot,
	BoolOr,
	IsBool,
	NewBool,
)
from .cacheRequest import (
	CacheRequestAddPattern,
	CacheRequestAddProperty,
	IsCacheRequest,
	NewCacheRequest,
	PopulateCache,
)
from .controlFlow import (
	BreakLoop,
	ContinueLoop,
	EndLoopBlock,
	EndTryBlock,
	Fork,
	ForkIfFalse,
	Halt,
	JumpCatch,
	JumpElse,
	NewLoopBlock,
	NewTryBlock,
)
from .element import (
	ElementGetPropertyValue,
	ElementGetTextPattern,
	ElementNavigate,
	IsElement,
)
from .extension import (
	CallExtension,
	IsExtensionSupported,
)
from .float import (
	IsFloat,
	NewFloat,
)
from .general import (
	Compare,
	IsNotSupported,
	Set,
)
from .guid import (
	GuidLookupId,
	IsGuid,
	LookupGuid,
	NewGuid,
)
from .int import (
	IsInt,
	IsUint,
	NewInt,
	NewUint,
)
from .null import (
	IsNull,
	NewNull,
)
from .status import (
	GetOperationStatus,
	SetOperationStatus,
)
from .string import (
	IsString,
	NewString,
	StringConcat,
	Stringify,
)
from .stringMap import (
	IsStringmap,
	NewStringMap,
	StringMapHasKey,
	StringMapInsert,
	StringMapLookup,
	StringMapRemove,
	StringMapSize,
)
from .textPattern import (
	TextPatternRangeFromChild,
)
from .textRange import (
	TextRangeClone,
	TextRangeCompare,
	TextRangeCompareEndpoints,
	TextRangeExpandToEnclosingUnit,
	TextRangeFindAttribute,
	TextRangeFindText,
	TextRangeGetAttributeValue,
	TextRangeGetBoundingRectangles,
	TextRangeGetEnclosingElement,
	TextRangeGetText,
	TextRangeMove,
	TextRangeMoveEndpointByRange,
	TextRangeMoveEndpointByUnit,
)
