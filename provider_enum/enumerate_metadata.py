import ctypes
from ctypes.wintypes import HANDLE, DWORD, LPWSTR
from typing import List, Dict, Any, Optional, Union
from contextlib import contextmanager
import logging
from dataclasses import dataclass, field
from enum import IntEnum
import json
import uuid

# Configure logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


class WindowsError(IntEnum):
    """Windows error codes"""
    ERROR_SUCCESS = 0
    ERROR_INSUFFICIENT_BUFFER = 122
    ERROR_NO_MORE_ITEMS = 259
    ERROR_OUTOFMEMORY = 14


class FormatMessageFlags(IntEnum):
    """FormatMessage API flags"""
    FORMAT_MESSAGE_FROM_SYSTEM = 0x00001000
    FORMAT_MESSAGE_IGNORE_INSERTS = 0x00000200
    FORMAT_MESSAGE_MAX_WIDTH_MASK = 0x000000FF

    @property
    def name(self):
        return {
            self.FORMAT_MESSAGE_FROM_SYSTEM: "Format Message From System",
            self.FORMAT_MESSAGE_IGNORE_INSERTS: "Format Message Ignore Inserts",
            self.FORMAT_MESSAGE_MAX_WIDTH_MASK: "Format Message Max Width Mask",
        }


class EvtFormatMessageFlags(IntEnum):
    """Event format message flags"""
    EvtFormatMessageEvent = 1
    EvtFormatMessageLevel = 2
    EvtFormatMessageTask = 3
    EvtFormatMessageOpcode = 4
    EvtFormatMessageKeyword = 5
    EvtFormatMessageChannel = 6
    EvtFormatMessageProvider = 7
    EvtFormatMessageId = 8
    EvtFormatMessageXml = 9

    @property
    def name(self):
        return {
            self.EvtFormatMessageEvent: "EvtFormatMessageEvent",
            self.EvtFormatMessageLevel: "EvtFormatMessageLevel",
            self.EvtFormatMessageTask: "EvtFormatMessageTask",
            self.EvtFormatMessageOpcode: "EvtFormatMessageOpcode",
            self.EvtFormatMessageKeyword: "EvtFormatMessageKeyword",
            self.EvtFormatMessageChannel: "EvtFormatMessageChannel",
            self.EvtFormatMessageProvider: "EvtFormatMessageProvider",
            self.EvtFormatMessageId: "EvtFormatMessageId",
            self.EvtFormatMessageXml: "EvtFormatMessageXml"
        }[self]


class EvtEventMetadataPropertyId(IntEnum):
    """Event Metadata Property IDs"""
    EventMetadataEventID = 0
    EventMetadataEventVersion = 1
    EventMetadataEventChannel = 2
    EventMetadataEventLevel = 3
    EventMetadataEventOpcode = 4
    EventMetadataEventTask = 5
    EventMetadataEventKeyword = 6
    EventMetadataEventMessageID = 7
    EventMetadataEventTemplate = 8
    EvtEventMetadataPropertyIdEND = 9

    @property
    def name(self):
        return {
            self.EventMetadataEventID: "EventMetadataEventID",
            self.EventMetadataEventVersion: "EventMetadataEventVersion",
            self.EventMetadataEventChannel: "EventMetadataEventChannel",
            self.EventMetadataEventLevel: "EventMetadataEventLevel",
            self.EventMetadataEventOpcode: "EventMetadataEventOpcode",
            self.EventMetadataEventTask: "EventMetadataEventTask",
            self.EventMetadataEventKeyword: "EventMetadataEventKeyword",
            self.EventMetadataEventMessageID: "EventMetadataEventMessageID",
            self.EventMetadataEventTemplate: "EventMetadataEventTemplate",
            self.EvtEventMetadataPropertyIdEND: "EvtEventMetadataPropertyIdEND"
        }[self]


class EvtPublisherMetadataPropertyId(IntEnum):
    """Event Publisher Metadata Property IDs"""
    EvtPublisherMetadataPublisherGuid = 0
    EvtPublisherMetadataResourceFilePath = 1
    EvtPublisherMetadataParameterFilePath = 2
    EvtPublisherMetadataMessageFilePath = 3
    EvtPublisherMetadataHelpLink = 4
    EvtPublisherMetadataPublisherMessageID = 5
    EvtPublisherMetadataChannelReferences = 6
    EvtPublisherMetadataChannelReferencePath = 7
    EvtPublisherMetadataChannelReferenceIndex = 8
    EvtPublisherMetadataChannelReferenceID = 9
    EvtPublisherMetadataChannelReferenceFlags = 10
    EvtPublisherMetadataChannelReferenceMessageID = 11
    EvtPublisherMetadataLevels = 12
    EvtPublisherMetadataLevelName = 13
    EvtPublisherMetadataLevelValue = 14
    EvtPublisherMetadataLevelMessageID = 15
    EvtPublisherMetadataTasks = 16
    EvtPublisherMetadataTaskName = 17
    EvtPublisherMetadataTaskEventGuid = 18
    EvtPublisherMetadataTaskValue = 19
    EvtPublisherMetadataTaskMessageID = 20
    EvtPublisherMetadataOpcodes = 21
    EvtPublisherMetadataOpcodeName = 22
    EvtPublisherMetadataOpcodeValue = 23
    EvtPublisherMetadataOpcodeMessageID = 24
    EvtPublisherMetadataKeywords = 25
    EvtPublisherMetadataKeywordName = 26
    EvtPublisherMetadataKeywordValue = 27
    EvtPublisherMetadataKeywordMessageID = 28
    EvtPublisherMetadataPropertyIdEND = 29

    @property
    def name(self):
        return {
            self.EvtPublisherMetadataPublisherGuid: "EvtPublisherMetadataPublisherGuid",
            self.EvtPublisherMetadataResourceFilePath: "EvtPublisherMetadataResourceFilePath",
            self.EvtPublisherMetadataParameterFilePath: "EvtPublisherMetadataParameterFilePath",
            self.EvtPublisherMetadataMessageFilePath: "EvtPublisherMetadataMessageFilePath",
            self.EvtPublisherMetadataHelpLink: "EvtPublisherMetadataHelpLink",
            self.EvtPublisherMetadataPublisherMessageID: "EvtPublisherMetadataPublisherMessageID",
            self.EvtPublisherMetadataChannelReferences: "EvtPublisherMetadataChannelReferences",
            self.EvtPublisherMetadataChannelReferencePath: "EvtPublisherMetadataChannelReferencePath",
            self.EvtPublisherMetadataChannelReferenceIndex: "EvtPublisherMetadataChannelReferenceIndex",
            self.EvtPublisherMetadataChannelReferenceID: "EvtPublisherMetadataChannelReferenceID",
            self.EvtPublisherMetadataChannelReferenceFlags: "EvtPublisherMetadataChannelReferenceFlags",
            self.EvtPublisherMetadataChannelReferenceMessageID: "EvtPublisherMetadataChannelReferenceMessageID",
            self.EvtPublisherMetadataLevels: "EvtPublisherMetadataLevels",
            self.EvtPublisherMetadataLevelName: "EvtPublisherMetadataLevelName",
            self.EvtPublisherMetadataLevelValue: "EvtPublisherMetadataLevelValue",
            self.EvtPublisherMetadataLevelMessageID: "EvtPublisherMetadataLevelMessageID",
            self.EvtPublisherMetadataTasks: "EvtPublisherMetadataTasks",
            self.EvtPublisherMetadataTaskName: "EvtPublisherMetadataTaskName",
            self.EvtPublisherMetadataTaskEventGuid: "EvtPublisherMetadataTaskEventGuid",
            self.EvtPublisherMetadataTaskValue: "EvtPublisherMetadataTaskValue",
            self.EvtPublisherMetadataTaskMessageID: "EvtPublisherMetadataTaskMessageID",
            self.EvtPublisherMetadataOpcodes: "EvtPublisherMetadataOpcodes",
            self.EvtPublisherMetadataOpcodeName: "EvtPublisherMetadataOpcodeName",
            self.EvtPublisherMetadataOpcodeValue: "EvtPublisherMetadataOpcodeValue",
            self.EvtPublisherMetadataOpcodeMessageID: "EvtPublisherMetadataOpcodeMessageID",
            self.EvtPublisherMetadataKeywords: "EvtPublisherMetadataKeywords",
            self.EvtPublisherMetadataKeywordName: "EvtPublisherMetadataKeywordName",
            self.EvtPublisherMetadataKeywordValue: "EvtPublisherMetadataKeywordValue",
            self.EvtPublisherMetadataKeywordMessageID: "EvtPublisherMetadataKeywordMessageID",
            self.EvtPublisherMetadataPropertyIdEND: "EvtPublisherMetadataPropertyIdEND"
        }[self]


class EvtVariantType(IntEnum):
    """Event Variant Types"""
    EvtVarTypeNull = 0
    EvtVarTypeString = 1
    EvtVarTypeAnsiString = 2
    EvtVarTypeSByte = 3
    EvtVarTypeByte = 4
    EvtVarTypeInt16 = 5
    EvtVarTypeUInt16 = 6
    EvtVarTypeInt32 = 7
    EvtVarTypeUInt32 = 8
    EvtVarTypeInt64 = 9
    EvtVarTypeUInt64 = 10
    EvtVarTypeSingle = 11
    EvtVarTypeDouble = 12
    EvtVarTypeBoolean = 13
    EvtVarTypeBinary = 14
    EvtVarTypeGuid = 15
    EvtVarTypeSizeT = 16
    EvtVarTypeFileTime = 17
    EvtVarTypeSysTime = 18
    EvtVarTypeSid = 19
    EvtVarTypeHexInt32 = 20
    EvtVarTypeHexInt64 = 21
    EvtVarTypeEvtHandle = 32
    EvtVarTypeEvtXml = 35

    @property
    def name(self):
        return {
            self.EvtVarTypeNull: "EvtVarTypeNull",
            self.EvtVarTypeString: "EvtVarTypeString",
            self.EvtVarTypeAnsiString: "EvtVarTypeAnsiString",
            self.EvtVarTypeSByte: "EvtVarTypeSByte",
            self.EvtVarTypeByte: "EvtVarTypeByte",
            self.EvtVarTypeInt16: "EvtVarTypeInt16",
            self.EvtVarTypeUInt16: "EvtVarTypeUInt16",
            self.EvtVarTypeInt32: "EvtVarTypeInt32",
            self.EvtVarTypeUInt32: "EvtVarTypeUInt32",
            self.EvtVarTypeInt64: "EvtVarTypeInt64",
            self.EvtVarTypeUInt64: "EvtVarTypeUInt64",
            self.EvtVarTypeSingle: "EvtVarTypeSingle",
            self.EvtVarTypeDouble: "EvtVarTypeDouble",
            self.EvtVarTypeBoolean: "EvtVarTypeBoolean",
            self.EvtVarTypeBinary: "EvtVarTypeBinary",
            self.EvtVarTypeGuid: "EvtVarTypeGuid",
            self.EvtVarTypeSizeT: "EvtVarTypeSizeT",
            self.EvtVarTypeFileTime: "EvtVarTypeFileTime",
            self.EvtVarTypeSysTime: "EvtVarTypeSysTime",
            self.EvtVarTypeSid: "EvtVarTypeSid",
            self.EvtVarTypeHexInt32: "EvtVarTypeHexInt32",
            self.EvtVarTypeHexInt64: "EvtVarTypeHexInt64",
            self.EvtVarTypeEvtHandle: "EvtVarTypeEvtHandle",
            self.EvtVarTypeEvtXml: "EvtVarTypeEvtXml"
        }[self]


class EvtVariant(ctypes.Structure):
    """EVT_VARIANT structure for holding property values"""
    
    class _Value(ctypes.Union):
        _fields_ = [
            ("BooleanVal", ctypes.c_bool),
            ("SByteVal", ctypes.c_byte),
            ("Int16Val", ctypes.c_int16),
            ("UInt16Val", ctypes.c_uint16),
            ("Int32Val", ctypes.c_int32),
            ("UInt32Val", ctypes.c_uint32),
            ("Int64Val", ctypes.c_int64),
            ("UInt64Val", ctypes.c_uint64),
            ("SingleVal", ctypes.c_float),
            ("DoubleVal", ctypes.c_double),
            ("StringVal", LPWSTR),
            ("AnsiStringVal", ctypes.c_char_p),
            ("BinaryVal", ctypes.c_void_p),
            ("GuidVal", ctypes.POINTER(ctypes.c_byte * 16)),
            ("SizeTVal", ctypes.c_size_t),
            ("EvtHandleVal", HANDLE),
        ]
    
    _fields_ = [
        ("value", _Value),
        ("Count", DWORD),
        ("Type", DWORD),
    ]
@dataclass
class MsgString:
    """
    Pythonic version of MSG_STRING structure.
    Contains the value and message string for a type, such as
    an opcode or task that the provider defines or uses.
    """
    dw_value: Optional[int] = None      # Value attribute for opcode, task, and level
    ull_mask: Optional[int] = None      # Mask attribute for keyword
    message: Optional[str] = None       # Message string or name attribute
    
    @property
    def value(self) -> Union[int, None]:
        """Get the appropriate value (dw_value or ull_mask)"""
        return self.dw_value if self.dw_value is not None else self.ull_mask
    
    def __post_init__(self):
        if self.dw_value is None and self.ull_mask is None:
            raise ValueError("Either dw_value or ull_mask must be provided")


@dataclass
class Messages:
    """
    Pythonic version of MESSAGES structure.
    Header for the block of value/message string pairs.
    """
    messages: List[MsgString] = field(default_factory=list)
    
    @property
    def size(self) -> int:
        """Size in bytes equivalent to dwSize"""
        return len(self.messages) * 16  # Approximate size per MSG_STRING
    
    def add_message(self, msg_string: MsgString) -> None:
        """Add a message string to the collection"""
        self.messages.append(msg_string)
    
    def find_by_value(self, value: int) -> Optional[MsgString]:
        """Find message by value"""
        for msg in self.messages:
            if msg.value == value:
                return msg
        return None
    
    def find_by_mask(self, mask: int) -> Optional[MsgString]:
        """Find message by mask"""
        for msg in self.messages:
            if msg.ull_mask == mask:
                return msg
        return None


class EventMetadataError(Exception):
    """Custom exception for event metadata operations"""
    pass


class WindowsEventMetadataAPI:
    """Wrapper for Windows Event Metadata API functions"""
    
    def __init__(self):
        self._wevtapi = ctypes.windll.wevtapi
        self._kernel32 = ctypes.windll.kernel32
        self._ole32 = ctypes.windll.ole32
        
        # Configure function signatures
        self._configure_api_functions()
    
    def _configure_api_functions(self) -> None:
        """Configure ctypes function signatures for type safety"""
        self._wevtapi.EvtOpenPublisherMetadata.restype = HANDLE
        self._wevtapi.EvtOpenPublisherMetadata.argtypes = [
            HANDLE, LPWSTR, LPWSTR, DWORD, DWORD
        ]
        
        self._wevtapi.EvtClose.restype = None
        self._wevtapi.EvtClose.argtypes = [HANDLE]
        
        self._wevtapi.EvtGetPublisherMetadataProperty.restype = ctypes.c_bool
        self._wevtapi.EvtGetPublisherMetadataProperty.argtypes = [
            HANDLE, ctypes.c_int, DWORD, DWORD, 
            ctypes.POINTER(EvtVariant), ctypes.POINTER(DWORD)
        ]
        
        self._wevtapi.EvtGetObjectArraySize.restype = ctypes.c_bool
        self._wevtapi.EvtGetObjectArraySize.argtypes = [
            HANDLE, ctypes.POINTER(DWORD)
        ]
        
        self._wevtapi.EvtGetObjectArrayProperty.restype = ctypes.c_bool
        self._wevtapi.EvtGetObjectArrayProperty.argtypes = [
            HANDLE, ctypes.c_int, DWORD, DWORD, DWORD,
            ctypes.POINTER(EvtVariant), ctypes.POINTER(DWORD)
        ]
        
        self._wevtapi.EvtFormatMessage.restype = ctypes.c_bool
        self._wevtapi.EvtFormatMessage.argtypes = [
            HANDLE, HANDLE, DWORD, DWORD, ctypes.c_void_p,
            DWORD, DWORD, LPWSTR, ctypes.POINTER(DWORD)
        ]
        
        self._wevtapi.EvtOpenEventMetadataEnum.restype = HANDLE
        self._wevtapi.EvtOpenEventMetadataEnum.argtypes = [HANDLE, DWORD]
        
        self._wevtapi.EvtNextEventMetadata.restype = HANDLE
        self._wevtapi.EvtNextEventMetadata.argtypes = [HANDLE, DWORD]
        
        self._wevtapi.EvtGetEventMetadataProperty.restype = ctypes.c_bool
        self._wevtapi.EvtGetEventMetadataProperty.argtypes = [
            HANDLE, ctypes.c_int, DWORD, DWORD,
            ctypes.POINTER(EvtVariant), ctypes.POINTER(DWORD)
        ]
        
        self._ole32.StringFromGUID2.restype = ctypes.c_int
        self._ole32.StringFromGUID2.argtypes = [
            ctypes.POINTER(ctypes.c_byte * 16), LPWSTR, ctypes.c_int
        ]
        
        self._kernel32.FormatMessageW.restype = DWORD
        self._kernel32.FormatMessageW.argtypes = [
            DWORD, ctypes.c_void_p, DWORD, DWORD, LPWSTR, DWORD, ctypes.c_void_p
        ]
    
    def open_publisher_metadata(self, publisher_name: str, 
                              session: Optional[HANDLE] = None,
                              log_file_path: Optional[str] = None,
                              locale: int = 0,
                              flags: int = 0) -> HANDLE:
        """
        Open publisher metadata handle.
        
        Args:
            publisher_name: Name of the event provider
            session: Optional session handle
            log_file_path: Optional path to archived log file
            locale: Locale identifier for localized strings
            flags: Additional flags
            
        Returns:
            Handle to publisher metadata
            
        Raises:
            EventMetadataError: If operation fails
        """
        publisher_name_w = ctypes.c_wchar_p(publisher_name)
        log_file_path_w = ctypes.c_wchar_p(log_file_path) if log_file_path else None
        
        handle = self._wevtapi.EvtOpenPublisherMetadata(
            session, publisher_name_w, log_file_path_w, locale, flags
        )
        
        if not handle:
            error_code = self._kernel32.GetLastError()
            error_message = self.format_error_message(error_code)
            raise EventMetadataError(
                f"EvtOpenPublisherMetadata failed for '{publisher_name}'. {error_message}"
            )
        
        return handle
    
    def close_handle(self, handle: HANDLE) -> None:
        """Close an event handle"""
        if handle:
            self._wevtapi.EvtClose(handle)
    
    def get_publisher_metadata_property(self, handle: HANDLE, 
                                      property_id: int,
                                      flags: int = 0) -> Optional[EvtVariant]:
        """
        Get a publisher metadata property.
        
        Args:
            handle: Publisher metadata handle
            property_id: Property ID to retrieve
            flags: Additional flags
            
        Returns:
            EvtVariant containing the property value, or None if failed
        """
        buffer_size = DWORD(0)
        buffer_used = DWORD(0)
        
        # First call to get required buffer size
        result = self._wevtapi.EvtGetPublisherMetadataProperty(
            handle, property_id, flags, 0, None, ctypes.byref(buffer_used)
        )
        
        if not result:
            error_code = self._kernel32.GetLastError()
            if error_code != WindowsError.ERROR_INSUFFICIENT_BUFFER:
                error_message = self.format_error_message(error_code)
                logger.error(f"EvtGetPublisherMetadataProperty failed: {error_message}")
                return None
            
            buffer_size = buffer_used
        
        # Allocate buffer and get property
        if buffer_size.value == 0:
            buffer_size = DWORD(ctypes.sizeof(EvtVariant))
            
        property_buffer = (ctypes.c_byte * buffer_size.value)()
        evt_variant = ctypes.cast(property_buffer, ctypes.POINTER(EvtVariant)).contents
        
        result = self._wevtapi.EvtGetPublisherMetadataProperty(
            handle, property_id, flags, buffer_size, 
            ctypes.byref(evt_variant), ctypes.byref(buffer_used)
        )
        
        if not result:
            error_code = self._kernel32.GetLastError()
            error_message = self.format_error_message(error_code)
            logger.error(f"EvtGetPublisherMetadataProperty failed: {error_message}")
            return None
        
        return evt_variant
    
    def format_error_message(self, error_code: int) -> str:
        """
        Format a Windows error code into a human-readable error message.
        
        Args:
            error_code: Windows error code to format
            
        Returns:
            Formatted error message string
        """
        buffer_size = 1024
        buffer = ctypes.create_unicode_buffer(buffer_size)
        
        # Use FORMAT_MESSAGE_FROM_SYSTEM to get system error messages
        # FORMAT_MESSAGE_IGNORE_INSERTS to avoid parameter substitution issues
        flags = (FormatMessageFlags.FORMAT_MESSAGE_FROM_SYSTEM | 
                FormatMessageFlags.FORMAT_MESSAGE_IGNORE_INSERTS)
        
        result = self._kernel32.FormatMessageW(
            flags,          # dwFlags
            None,           # lpSource
            error_code,     # dwMessageId
            0,              # dwLanguageId (0 = default language)
            buffer,         # lpBuffer
            buffer_size,    # nSize
            None            # Arguments
        )
        
        if result > 0:
            # Remove trailing whitespace (FormatMessage often adds \r\n)
            message = buffer.value.rstrip()
            return f"Error {error_code} (0x{error_code:08X}): {message}"
        else:
            # If FormatMessage fails, return a basic error message
            return f"Error {error_code} (0x{error_code:08X}): Unknown error"
    
    def format_message(self, metadata_handle: HANDLE, message_id: int,
                      event_handle: Optional[HANDLE] = None,
                      value_count: int = 0,
                      values: Optional[ctypes.c_void_p] = None,
                      flags: int = EvtFormatMessageFlags.EvtFormatMessageId) -> Optional[str]:
        """
        Format a message string using EvtFormatMessage.
        
        Args:
            metadata_handle: Publisher metadata handle
            message_id: Message ID to format
            event_handle: Optional event handle
            value_count: Number of values for substitution
            values: Optional values for substitution
            flags: Format flags
            
        Returns:
            Formatted message string, or None if failed
        """
        buffer_size = DWORD(0)
        buffer_used = DWORD(0)
        
        # First call to get required buffer size
        result = self._wevtapi.EvtFormatMessage(
            metadata_handle, event_handle, message_id, value_count, values,
            flags, 0, None, ctypes.byref(buffer_used)
        )
        
        if not result:
            error_code = self._kernel32.GetLastError()
            if error_code != WindowsError.ERROR_INSUFFICIENT_BUFFER:
                error_message = self.format_error_message(error_code)
                logger.error(f"EvtFormatMessage failed: {error_message}")
                return None
            
            buffer_size = buffer_used
        
        # Allocate buffer and format message
        if buffer_size.value == 0:
            return ""
            
        buffer = ctypes.create_unicode_buffer(buffer_size.value)
        
        result = self._wevtapi.EvtFormatMessage(
            metadata_handle, event_handle, message_id, value_count, values,
            flags, buffer_size, buffer, ctypes.byref(buffer_used)
        )
        
        if not result:
            error_code = self._kernel32.GetLastError()
            error_message = self.format_error_message(error_code)
            logger.error(f"EvtFormatMessage failed: {error_message}")
            return None
        
        return buffer.value
    
    def open_event_metadata_enum(self, metadata_handle: HANDLE, flags: int = 0) -> Optional[HANDLE]:
        """
        Open an event metadata enumeration handle.
        
        Args:
            metadata_handle: Publisher metadata handle
            flags: Additional flags
            
        Returns:
            Handle to event metadata enumeration, or None if failed
        """
        handle = self._wevtapi.EvtOpenEventMetadataEnum(metadata_handle, flags)
        if not handle:
            error_code = self._kernel32.GetLastError()
            error_message = self.format_error_message(error_code)
            logger.error(f"EvtOpenEventMetadataEnum failed: {error_message}")
            return None
        return handle
    
    def next_event_metadata(self, enum_handle: HANDLE, flags: int = 0) -> Optional[HANDLE]:
        """
        Get the next event metadata from enumeration.
        
        Args:
            enum_handle: Event metadata enumeration handle
            flags: Additional flags
            
        Returns:
            Handle to next event metadata, or None if no more items
        """
        handle = self._wevtapi.EvtNextEventMetadata(enum_handle, flags)
        if not handle:
            error_code = self._kernel32.GetLastError()
            if error_code != WindowsError.ERROR_NO_MORE_ITEMS:
                error_message = self.format_error_message(error_code)
                logger.error(f"EvtNextEventMetadata failed: {error_message}")
            return None
        return handle
    
    def get_event_metadata_property(self, event_handle: HANDLE, 
                                   property_id: EvtEventMetadataPropertyId,
                                   flags: int = 0) -> Optional[EvtVariant]:
        """
        Get an event metadata property.
        
        Args:
            event_handle: Event metadata handle
            property_id: Property ID to retrieve
            flags: Additional flags
            
        Returns:
            EvtVariant containing the property value, or None if failed
        """
        buffer_size = DWORD(0)
        buffer_used = DWORD(0)
        
        # First call to get required buffer size
        result = self._wevtapi.EvtGetEventMetadataProperty(
            event_handle, property_id, flags, 0, None, ctypes.byref(buffer_used)
        )
        
        if not result:
            error_code = self._kernel32.GetLastError()
            if error_code != WindowsError.ERROR_INSUFFICIENT_BUFFER:
                error_message = self.format_error_message(error_code)
                logger.error(f"EvtGetEventMetadataProperty failed: {error_message}")
                return None
            
            buffer_size = buffer_used
        
        # Allocate buffer and get property
        if buffer_size.value == 0:
            buffer_size = DWORD(ctypes.sizeof(EvtVariant))
            
        property_buffer = (ctypes.c_byte * buffer_size.value)()
        evt_variant = ctypes.cast(property_buffer, ctypes.POINTER(EvtVariant)).contents
        
        result = self._wevtapi.EvtGetEventMetadataProperty(
            event_handle, property_id, flags, buffer_size,
            ctypes.byref(evt_variant), ctypes.byref(buffer_used)
        )
        
        if not result:
            error_code = self._kernel32.GetLastError()
            error_message = self.format_error_message(error_code)
            logger.error(f"EvtGetEventMetadataProperty failed: {error_message}")
            return None
        
        return evt_variant
    
    def get_object_array_size(self, handle: HANDLE) -> Optional[int]:
        """Get the size of an object array"""
        array_size = DWORD(0)
        result = self._wevtapi.EvtGetObjectArraySize(handle, ctypes.byref(array_size))
        
        if not result:
            error_code = self._kernel32.GetLastError()
            error_message = self.format_error_message(error_code)
            logger.error(f"EvtGetObjectArraySize failed: {error_message}")
            return None
            
        return array_size.value
    
    def guid_to_string(self, guid_bytes: ctypes.Array) -> str:
        """Convert GUID bytes to string"""
        buffer = ctypes.create_unicode_buffer(50)
        result = self._ole32.StringFromGUID2(
            ctypes.cast(guid_bytes, ctypes.POINTER(ctypes.c_byte * 16)),
            buffer, 50
        )
        return buffer.value if result > 0 else ""
    
    def get_object_array_property(self, handle: HANDLE, property_id: EvtPublisherMetadataPropertyId,
                                 index: int, flags: int = 0) -> Optional[EvtVariant]:
        """
        Get a property from an object array.
        
        Args:
            handle: Handle to the object array
            property_id: Property ID to retrieve
            index: Index in the array
            flags: Additional flags
            
        Returns:
            EvtVariant containing the property value, or None if failed
        """
        buffer_size = DWORD(0)
        buffer_used = DWORD(0)
        
        # First call to get required buffer size
        result = self._wevtapi.EvtGetObjectArrayProperty(
            handle, property_id, index, flags, 0, None, ctypes.byref(buffer_used)
        )
        
        if not result:
            error_code = self._kernel32.GetLastError()
            if error_code != WindowsError.ERROR_INSUFFICIENT_BUFFER:
                error_message = self.format_error_message(error_code)
                logger.error(f"EvtGetObjectArrayProperty failed: {error_message}")
                return None
            
            buffer_size = buffer_used
        
        # Allocate buffer and get property
        if buffer_size.value == 0:
            buffer_size = DWORD(ctypes.sizeof(EvtVariant))
            
        property_buffer = (ctypes.c_byte * buffer_size.value)()
        evt_variant = ctypes.cast(property_buffer, ctypes.POINTER(EvtVariant)).contents
        
        result = self._wevtapi.EvtGetObjectArrayProperty(
            handle, property_id, index, flags, buffer_size,
            ctypes.byref(evt_variant), ctypes.byref(buffer_used)
        )
        
        if not result:
            error_code = self._kernel32.GetLastError()
            error_message = self.format_error_message(error_code)
            logger.error(f"EvtGetObjectArrayProperty failed: {error_message}")
            return None
        
        return evt_variant


@dataclass
class EventMetadata:
    """Container for individual event metadata"""
    event_id: Optional[int] = None
    version: Optional[int] = None
    channel: Optional[str] = None
    level: Optional[str] = None
    opcode: Optional[str] = None
    task: Optional[str] = None
    keyword: Optional[str] = None
    message: Optional[str] = None
    template: Optional[str] = None


@dataclass
class EventProviderMetadata:
    """Container for all event provider metadata"""
    provider_name: str
    channel_messages: Messages = field(default_factory=Messages)
    level_messages: Messages = field(default_factory=Messages)
    task_messages: Messages = field(default_factory=Messages)
    opcode_messages: Messages = field(default_factory=Messages)
    keyword_messages: Messages = field(default_factory=Messages)
    provider_properties: Dict[str, Any] = field(default_factory=dict)
    events: List[EventMetadata] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'provider_name': self.provider_name,
            'provider_properties': self.provider_properties,
            'events': [
                {
                    'event_id': event.event_id,
                    'version': event.version,
                    'channel': event.channel,
                    'level': event.level,
                    'opcode': event.opcode,
                    'task': event.task,
                    'keyword': event.keyword,
                    'message': event.message,
                    'template': event.template
                } for event in self.events
            ],
            'channels': [{'value': msg.value, 'message': msg.message} 
                        for msg in self.channel_messages.messages],
            'levels': [{'value': msg.value, 'message': msg.message} 
                      for msg in self.level_messages.messages],
            'tasks': [{'value': msg.value, 'message': msg.message} 
                     for msg in self.task_messages.messages],
            'opcodes': [{'value': msg.value, 'message': msg.message} 
                       for msg in self.opcode_messages.messages],
            'keywords': [{'mask': msg.ull_mask, 'message': msg.message} 
                        for msg in self.keyword_messages.messages]
        }


class EventMetadataEnumerator:
    """High-level interface for enumerating Windows event provider metadata"""
    
    def __init__(self):
        self._api = WindowsEventMetadataAPI()
        self._current_metadata: Optional[EventProviderMetadata] = None
    
    @contextmanager
    def metadata_context(self, publisher_name: str):
        """Context manager for metadata handle and cleanup"""
        metadata = EventProviderMetadata(provider_name=publisher_name)
        handle = None
        
        try:
            handle = self._api.open_publisher_metadata(publisher_name)
            self._current_metadata = metadata
            yield handle, metadata
        except Exception as e:
            logger.error(f"Error processing metadata for {publisher_name}: {e}")
            raise EventMetadataError(f"Failed to process metadata: {e}") from e
        finally:
            if handle:
                self._api.close_handle(handle)
            self._cleanup_messages(metadata)
            self._current_metadata = None
    
    def get_metadata(self, publisher_name: str) -> Dict[str, Any]:
        """
        Get complete metadata for a publisher.
        
        Args:
            publisher_name: Name of the event provider
            
        Returns:
            Dictionary containing all metadata
            
        Raises:
            EventMetadataError: If metadata retrieval fails
        """
        logger.info(f"Processing metadata for provider: {publisher_name}")
        
        try:
            with self.metadata_context(publisher_name) as (handle, metadata):
                logger.info(f"Provider Metadata for {publisher_name}")
                
                # Print provider properties (placeholder for now)
                status = self._print_provider_properties(handle, metadata)
                if status != WindowsError.ERROR_SUCCESS:
                    logger.warning(f"Failed to get provider properties: {status}")
                
                logger.info(f"Event Metadata for {publisher_name}")
                
                # Print provider events (placeholder for now)
                status = self._print_provider_events(handle, metadata)
                if status != WindowsError.ERROR_SUCCESS:
                    logger.warning(f"Failed to get provider events: {status}")
                
                return metadata.to_dict()
                
        except Exception as e:
            logger.error(f"Failed to get metadata for {publisher_name}: {e}")
            raise
    
    def _print_provider_properties(self, handle: HANDLE, 
                                 metadata: EventProviderMetadata) -> int:
        """
        Enumerate and print all provider metadata properties.
        
        This implements the C++ PrintProviderProperties function.
        """
        logger.info("Enumerating provider metadata properties...")
        
        try:
            for property_id in range(EvtPublisherMetadataPropertyId.EvtPublisherMetadataPropertyIdEND):
                property_id = EvtPublisherMetadataPropertyId(property_id)
                # Get the metadata property
                evt_variant = self._api.get_publisher_metadata_property(handle, property_id)
                
                if evt_variant is None:
                    continue
                
                # Print the property
                status = self._print_provider_property(handle, property_id, evt_variant, metadata)
                if status != WindowsError.ERROR_SUCCESS:
                    logger.error(f"Failed to print provider property {property_id.name}: {status}")
                    return status
                
                # Skip type-specific IDs as per C++ implementation
                if property_id == EvtPublisherMetadataPropertyId.EvtPublisherMetadataChannelReferences:
                    property_id = EvtPublisherMetadataPropertyId.EvtPublisherMetadataChannelReferenceMessageID
                elif property_id == EvtPublisherMetadataPropertyId.EvtPublisherMetadataLevels:
                    property_id = EvtPublisherMetadataPropertyId.EvtPublisherMetadataLevelMessageID
                elif property_id == EvtPublisherMetadataPropertyId.EvtPublisherMetadataOpcodes:
                    property_id = EvtPublisherMetadataPropertyId.EvtPublisherMetadataOpcodeMessageID
                elif property_id == EvtPublisherMetadataPropertyId.EvtPublisherMetadataTasks:
                    property_id = EvtPublisherMetadataPropertyId.EvtPublisherMetadataTaskMessageID
                elif property_id == EvtPublisherMetadataPropertyId.EvtPublisherMetadataKeywords:
                    property_id = EvtPublisherMetadataPropertyId.EvtPublisherMetadataKeywordMessageID
                    
            return WindowsError.ERROR_SUCCESS
            
        except Exception as e:
            logger.error(f"Error enumerating provider properties: {e}")
            return WindowsError.ERROR_OUTOFMEMORY
    
    def _print_event_properties(self, metadata_handle: HANDLE, event_handle: HANDLE,
                               metadata: EventProviderMetadata) -> int:
        """
        Print all properties for a specific event.
        
        This implements the C++ PrintEventProperties function.
        """
        try:
            event_metadata = EventMetadata()
            
            # Use the EVT_EVENT_METADATA_PROPERTY_ID's enumeration values to loop
            # through all the metadata for the event
            for property_id in range(EvtEventMetadataPropertyId.EvtEventMetadataPropertyIdEND):
                # Get the specified metadata property
                evt_variant = self._api.get_event_metadata_property(event_handle, property_id)
                
                if evt_variant is None:
                    continue
                
                # Print the property
                status = self._print_event_property(
                    metadata_handle, property_id, evt_variant, event_metadata, metadata
                )
                if status != WindowsError.ERROR_SUCCESS:
                    logger.error(f"Failed to print event property {property_id.name}: {status}")
                    return status
            
            # Add the completed event metadata to the collection
            metadata.events.append(event_metadata)
            return WindowsError.ERROR_SUCCESS
            
        except Exception as e:
            logger.error(f"Error printing event properties: {e}")
            return WindowsError.ERROR_OUTOFMEMORY
    
    def _print_event_property(self, metadata_handle: HANDLE, property_id: int,
                             evt_variant: EvtVariant, event_metadata: EventMetadata,
                             provider_metadata: EventProviderMetadata) -> int:
        """
        Print a specific event property.
        
        This implements the C++ PrintEventProperty function.
        """
        try:
            prop_id = EvtEventMetadataPropertyId(property_id)
            
            if prop_id == EvtEventMetadataPropertyId.EventMetadataEventID:
                event_id = evt_variant.value.UInt32Val
                logger.info(f"ID: {event_id}")
                event_metadata.event_id = event_id
                
            elif prop_id == EvtEventMetadataPropertyId.EventMetadataEventVersion:
                version = evt_variant.value.UInt32Val
                logger.info(f"Version: {version}")
                event_metadata.version = version
                
            elif prop_id == EvtEventMetadataPropertyId.EventMetadataEventChannel:
                if evt_variant.value.UInt32Val > 0:
                    channel_name = self._get_property_name(
                        metadata_handle, provider_metadata.channel_messages, evt_variant.value.UInt32Val
                    )
                    logger.info(f"Channel: {channel_name or '(unknown)'}")
                    event_metadata.channel = channel_name
                else:
                    logger.info("Channel: ")
                    event_metadata.channel = None
                    
            elif prop_id == EvtEventMetadataPropertyId.EventMetadataEventLevel:
                if evt_variant.value.UInt32Val > 0:
                    level_name = self._get_property_name(
                        metadata_handle, provider_metadata.level_messages, evt_variant.value.UInt32Val
                    )
                    logger.info(f"Level: {level_name or '(unknown)'}")
                    event_metadata.level = level_name
                else:
                    logger.info("Level: ")
                    event_metadata.level = None
                    
            elif prop_id == EvtEventMetadataPropertyId.EventMetadataEventOpcode:
                # Store opcode value for later processing with task
                if not hasattr(event_metadata, '_opcode_value'):
                    event_metadata._opcode_value = evt_variant.value.UInt32Val
                    
            elif prop_id == EvtEventMetadataPropertyId.EventMetadataEventTask:
                task_value = evt_variant.value.UInt32Val
                if task_value > 0:
                    task_name = self._get_property_name(
                        metadata_handle, provider_metadata.task_messages, task_value
                    )
                    logger.info(f"Task: {task_name or '(unknown)'}")
                    event_metadata.task = task_name
                else:
                    logger.info("Task: ")
                    event_metadata.task = None
                
                # Now that we know the task, get the opcode string and print it
                opcode_value = getattr(event_metadata, '_opcode_value', 0)
                if opcode_value > 0:
                    opcode_name = self._get_opcode_name(
                        metadata_handle, provider_metadata.opcode_messages, 
                        opcode_value, task_value
                    )
                    logger.info(f"Opcode: {opcode_name or '(unknown)'}")
                    event_metadata.opcode = opcode_name
                else:
                    logger.info("Opcode: ")
                    event_metadata.opcode = None
                    
            elif prop_id == EvtEventMetadataPropertyId.EventMetadataEventKeyword:
                # The upper 8 bits can contain reserved bit values, so do not include them
                keyword_mask = evt_variant.value.UInt64Val & 0x00FFFFFFFFFFFFFF
                if keyword_mask > 0:
                    keyword_names = self._get_keyword_name(
                        metadata_handle, provider_metadata.keyword_messages, keyword_mask
                    )
                    logger.info(f"Keyword: {keyword_names or '(unknown)'}")
                    event_metadata.keyword = keyword_names
                else:
                    logger.info("Keyword: ")
                    event_metadata.keyword = None
                    
            elif prop_id == EvtEventMetadataPropertyId.EventMetadataEventMessageID:
                if evt_variant.value.UInt32Val == 0xFFFFFFFF:  # -1 as unsigned
                    logger.info("Message string: ")
                    event_metadata.message = None
                else:
                    message = self._get_message_string(metadata_handle, evt_variant.value.UInt32Val)
                    logger.info(f"Message string: {message or '(empty)'}")
                    event_metadata.message = message
                    
            elif prop_id == EvtEventMetadataPropertyId.EventMetadataEventTemplate:
                template = evt_variant.value.StringVal or ""
                logger.info(f"Template: {template}\n")
                event_metadata.template = template
                
            else:
                logger.warning(f"Unknown event property Id: {property_id}")
            
            return WindowsError.ERROR_SUCCESS
            
        except Exception as e:
            logger.error(f"Error processing event property {property_id}: {e}")
            return WindowsError.ERROR_OUTOFMEMORY
    
    def _get_property_name(self, metadata_handle: HANDLE, messages: Messages, value: int) -> Optional[str]:
        """
        Get property name by value from messages collection.
        
        This implements the C++ GetPropertyName function.
        """
        msg_string = messages.find_by_value(value)
        return msg_string.message if msg_string else None
    
    def _get_opcode_name(self, metadata_handle: HANDLE, messages: Messages,
                        opcode_value: int, task_value: int) -> Optional[str]:
        """
        Get opcode name considering task-specific opcodes.
        
        This implements the C++ GetOpcodeName function.
        """
        # Extract the opcode from the high word
        opcode_high = (opcode_value >> 16) & 0xFFFF
        global_opcode_msg = None
        
        # Search for matching opcodes
        for msg in messages.messages:
            if msg.dw_value is None:
                continue
                
            msg_opcode_high = (msg.dw_value >> 16) & 0xFFFF
            msg_task_low = msg.dw_value & 0xFFFF
            
            if opcode_high == msg_opcode_high:
                if msg_task_low == 0:
                    # This is a global opcode (low word is zero)
                    global_opcode_msg = msg
                elif task_value == msg_task_low:
                    # This is a task-specific opcode that matches our task
                    return msg.message
        
        # If no task-specific opcode was found, return the global opcode
        return global_opcode_msg.message if global_opcode_msg else None
    
    def _get_keyword_name(self, metadata_handle: HANDLE, messages: Messages,
                         keyword_mask: int) -> Optional[str]:
        """
        Get concatenated keyword names based on bitmask.
        
        This implements the C++ GetKeywordName function.
        """
        keyword_names = []
        
        for msg in messages.messages:
            if msg.ull_mask is None:
                continue
                
            if keyword_mask & msg.ull_mask:
                if msg.message:
                    keyword_names.append(msg.message)
        
        return " ".join(keyword_names) if keyword_names else None
    
    def _dump_channel_properties(self, metadata_handle: HANDLE, array_handle: HANDLE, index: int, 
                                messages: Messages) -> int:
        """
        Dump channel properties (implements DumpChannelProperties).
        
        Print the metadata for a channel and capture the message string and value.
        """
        try:
            message = None
            
            # Get channel message string
            variant = self._api.get_object_array_property(
                array_handle, EvtPublisherMetadataPropertyId.EvtPublisherMetadataChannelReferenceMessageID, index
            )
            if variant:
                if variant.value.UInt32Val != 0xFFFFFFFF:  # -1 as unsigned
                    message = self._get_message_string(metadata_handle, variant.value.UInt32Val)
                logger.info(f"\tChannel message string: {message or '(empty)'}")
            else:
                error_code = self._api._kernel32.GetLastError()
                error_message = self._api.format_error_message(error_code)
                logger.error(f"Failed to get channel message ID: {error_message}")
                return error_code
            
            # Get channel path
            variant = self._api.get_object_array_property(
                array_handle, EvtPublisherMetadataPropertyId.EvtPublisherMetadataChannelReferencePath, index
            )
            if variant:
                channel_path = variant.value.StringVal or ""
                logger.info(f"\tChannel path is {channel_path}")
            else:
                return self._api._kernel32.GetLastError()
            
            # Get channel index
            variant = self._api.get_object_array_property(
                array_handle, EvtPublisherMetadataPropertyId.EvtPublisherMetadataChannelReferenceIndex, index
            )
            if variant:
                channel_index = variant.value.UInt32Val
                logger.info(f"\tChannel index is {channel_index}")
            else:
                return self._api._kernel32.GetLastError()
            
            # Get channel ID and capture for later use
            variant = self._api.get_object_array_property(
                array_handle, EvtPublisherMetadataPropertyId.EvtPublisherMetadataChannelReferenceID, index
            )
            if variant:
                channel_id = variant.value.UInt32Val
                logger.info(f"\tChannel ID is {channel_id}")
                
                # Create message string entry
                msg_string = MsgString(
                    dw_value=channel_id,
                    message=message or channel_path
                )
                messages.add_message(msg_string)
            else:
                return self._api._kernel32.GetLastError()
            
            # Get channel flags
            variant = self._api.get_object_array_property(
                array_handle, EvtPublisherMetadataPropertyId.EvtPublisherMetadataChannelReferenceFlags, index
            )
            if variant:
                flags = variant.value.UInt32Val
                if flags & 0x1:  # EvtChannelReferenceImported
                    logger.info("\tChannel is imported")
            else:
                return self._api._kernel32.GetLastError()
            
            return WindowsError.ERROR_SUCCESS
            
        except Exception as e:
            logger.error(f"Error dumping channel properties: {e}")
            return WindowsError.ERROR_OUTOFMEMORY
    
    def _dump_level_properties(self, metadata_handle: HANDLE, array_handle: HANDLE, index: int,
                              messages: Messages) -> int:
        """
        Dump level properties (implements DumpLevelProperties).
        
        Print the metadata for a level and capture the message string and value.
        """
        try:
            message = None
            
            # Get level message string
            variant = self._api.get_object_array_property(
                array_handle, EvtPublisherMetadataPropertyId.EvtPublisherMetadataLevelMessageID, index
            )
            if variant:
                if variant.value.UInt32Val != 0xFFFFFFFF:  # -1 as unsigned
                    message = self._get_message_string(metadata_handle, variant.value.UInt32Val)
                logger.info(f"\tLevel message string: {message or '(empty)'}")
            else:
                return self._api._kernel32.GetLastError()
            
            # Get level name
            variant = self._api.get_object_array_property(
                array_handle, EvtPublisherMetadataPropertyId.EvtPublisherMetadataLevelName, index
            )
            if variant:
                level_name = variant.value.StringVal or ""
                logger.info(f"\tLevel name is {level_name}")
            else:
                return self._api._kernel32.GetLastError()
            
            # Get level value and capture for later use
            variant = self._api.get_object_array_property(
                array_handle, EvtPublisherMetadataPropertyId.EvtPublisherMetadataLevelValue, index
            )
            if variant:
                level_value = variant.value.UInt32Val
                logger.info(f"\tLevel value is {level_value}")
                
                # Create message string entry
                msg_string = MsgString(
                    dw_value=level_value,
                    message=message or level_name
                )
                messages.add_message(msg_string)
            else:
                return self._api._kernel32.GetLastError()
            
            return WindowsError.ERROR_SUCCESS
            
        except Exception as e:
            logger.error(f"Error dumping level properties: {e}")
            return WindowsError.ERROR_OUTOFMEMORY
    
    def _dump_task_properties(self, metadata_handle: HANDLE, array_handle: HANDLE, index: int,
                             messages: Messages) -> int:
        """
        Dump task properties (implements DumpTaskProperties).
        
        Print the metadata for a task and capture the message string and value.
        """
        try:
            message = None
            
            # Get task message string
            variant = self._api.get_object_array_property(
                array_handle, EvtPublisherMetadataPropertyId.EvtPublisherMetadataTaskMessageID, index
            )
            if variant:
                if variant.value.UInt32Val != 0xFFFFFFFF:  # -1 as unsigned
                    message = self._get_message_string(metadata_handle, variant.value.UInt32Val)
                logger.info(f"\tTask message string: {message or '(empty)'}")
            else:
                return self._api._kernel32.GetLastError()
            
            # Get task name
            variant = self._api.get_object_array_property(
                array_handle, EvtPublisherMetadataPropertyId.EvtPublisherMetadataTaskName, index
            )
            if variant:
                task_name = variant.value.StringVal or ""
                logger.info(f"\tTask name is {task_name}")
            else:
                return self._api._kernel32.GetLastError()
            
            # Get task event GUID
            variant = self._api.get_object_array_property(
                array_handle, EvtPublisherMetadataPropertyId.EvtPublisherMetadataTaskEventGuid, index
            )
            if variant:
                # Check if GUID is not null (simplified check)
                if variant.value.GuidVal:
                    guid_str = self._api.guid_to_string(variant.value.GuidVal.contents)
                    if guid_str and guid_str != "{00000000-0000-0000-0000-000000000000}":
                        logger.info(f"\tTask event GUID is {guid_str}")
            else:
                return self._api._kernel32.GetLastError()
            
            # Get task value and capture for later use
            variant = self._api.get_object_array_property(
                array_handle, EvtPublisherMetadataPropertyId.EvtPublisherMetadataTaskValue, index
            )
            if variant:
                task_value = variant.value.UInt32Val
                logger.info(f"\tTask value is {task_value}")
                
                # Create message string entry
                msg_string = MsgString(
                    dw_value=task_value,
                    message=message or task_name
                )
                messages.add_message(msg_string)
            else:
                return self._api._kernel32.GetLastError()
            
            return WindowsError.ERROR_SUCCESS
            
        except Exception as e:
            logger.error(f"Error dumping task properties: {e}")
            return WindowsError.ERROR_OUTOFMEMORY
    
    def _dump_opcode_properties(self, metadata_handle: HANDLE, array_handle: HANDLE, index: int,
                               messages: Messages) -> int:
        """
        Dump opcode properties (implements DumpOpcodeProperties).
        
        Print the metadata for an opcode and capture the message string and value.
        """
        try:
            message = None
            
            # Get opcode message string
            variant = self._api.get_object_array_property(
                array_handle, EvtPublisherMetadataPropertyId.EvtPublisherMetadataOpcodeMessageID, index
            )
            if variant:
                if variant.value.UInt32Val != 0xFFFFFFFF:  # -1 as unsigned
                    message = self._get_message_string(metadata_handle, variant.value.UInt32Val)
                logger.info(f"\tOpcode message string: {message or '(empty)'}")
            else:
                return self._api._kernel32.GetLastError()
            
            # Get opcode name
            variant = self._api.get_object_array_property(
                array_handle, EvtPublisherMetadataPropertyId.EvtPublisherMetadataOpcodeName, index
            )
            if variant:
                opcode_name = variant.value.StringVal or ""
                logger.info(f"\tOpcode name is {opcode_name}")
            else:
                return self._api._kernel32.GetLastError()
            
            # Get opcode value and capture for later use
            variant = self._api.get_object_array_property(
                array_handle, EvtPublisherMetadataPropertyId.EvtPublisherMetadataOpcodeValue, index
            )
            if variant:
                opcode_value = variant.value.UInt32Val
                # Extract task and opcode values (HIWORD/LOWORD equivalent)
                task_value = (opcode_value >> 16) & 0xFFFF
                opcode_only = opcode_value & 0xFFFF
                logger.info(f"\tOpcode value is {opcode_only} (task: {task_value})")
                
                # Create message string entry
                msg_string = MsgString(
                    dw_value=opcode_value,
                    message=message or opcode_name
                )
                messages.add_message(msg_string)
            else:
                return self._api._kernel32.GetLastError()
            
            return WindowsError.ERROR_SUCCESS
            
        except Exception as e:
            logger.error(f"Error dumping opcode properties: {e}")
            return WindowsError.ERROR_OUTOFMEMORY
    
    def _dump_keyword_properties(self, metadata_handle: HANDLE, array_handle: HANDLE, index: int,
                                messages: Messages) -> int:
        """
        Dump keyword properties (implements DumpKeywordProperties).
        
        Print the metadata for a keyword and capture the message string and mask.
        """
        try:
            message = None
            
            # Get keyword message string
            variant = self._api.get_object_array_property(
                array_handle, EvtPublisherMetadataPropertyId.EvtPublisherMetadataKeywordMessageID, index
            )
            if variant:
                if variant.value.UInt32Val != 0xFFFFFFFF:  # -1 as unsigned
                    message = self._get_message_string(metadata_handle, variant.value.UInt32Val)
                logger.info(f"\tKeyword message string: {message or '(empty)'}")
            else:
                return self._api._kernel32.GetLastError()
            
            # Get keyword name
            variant = self._api.get_object_array_property(
                array_handle, EvtPublisherMetadataPropertyId.EvtPublisherMetadataKeywordName, index
            )
            if variant:
                keyword_name = variant.value.StringVal or ""
                logger.info(f"\tKeyword name is {keyword_name}")
            else:
                return self._api._kernel32.GetLastError()
            
            # Get keyword value and capture for later use
            variant = self._api.get_object_array_property(
                array_handle, EvtPublisherMetadataPropertyId.EvtPublisherMetadataKeywordValue, index
            )
            if variant:
                # Note: C++ code has a bug - it assigns UInt32Val to ullMask (should be UInt64Val)
                # We'll use the correct UInt64Val here
                keyword_value = variant.value.UInt64Val
                logger.info(f"\tKeyword value is {keyword_value}")
                
                # Create message string entry with mask
                msg_string = MsgString(
                    ull_mask=keyword_value,
                    message=message or keyword_name
                )
                messages.add_message(msg_string)
            else:
                return self._api._kernel32.GetLastError()
            
            return WindowsError.ERROR_SUCCESS
            
        except Exception as e:
            logger.error(f"Error dumping keyword properties: {e}")
            return WindowsError.ERROR_OUTOFMEMORY
    
    def _print_provider_property(self, handle: HANDLE, property_id: int,
                                evt_variant: EvtVariant, 
                                metadata: EventProviderMetadata) -> int:
        """
        Print a specific provider property.
        
        This implements the C++ PrintProviderProperty function.
        """
        try:
            prop_id = EvtPublisherMetadataPropertyId(property_id)
            
            if prop_id == EvtPublisherMetadataPropertyId.EvtPublisherMetadataPublisherGuid:
                guid_str = self._api.guid_to_string(evt_variant.value.GuidVal.contents)
                logger.info(f"Guid: {guid_str}")
                metadata.provider_properties['guid'] = guid_str
                
            elif prop_id == EvtPublisherMetadataPropertyId.EvtPublisherMetadataResourceFilePath:
                resource_path = evt_variant.value.StringVal if evt_variant.value.StringVal else ""
                logger.info(f"ResourceFilePath: {resource_path}")
                metadata.provider_properties['resource_file_path'] = resource_path
                
            elif prop_id == EvtPublisherMetadataPropertyId.EvtPublisherMetadataParameterFilePath:
                param_path = evt_variant.value.StringVal if evt_variant.Type != EvtVariantType.EvtVarTypeNull else ""
                logger.info(f"ParameterFilePath: {param_path}")
                metadata.provider_properties['parameter_file_path'] = param_path
                
            elif prop_id == EvtPublisherMetadataPropertyId.EvtPublisherMetadataMessageFilePath:
                message_path = evt_variant.value.StringVal if evt_variant.value.StringVal else ""
                logger.info(f"MessageFilePath: {message_path}")
                metadata.provider_properties['message_file_path'] = message_path
                
            elif prop_id == EvtPublisherMetadataPropertyId.EvtPublisherMetadataHelpLink:
                help_link = evt_variant.value.StringVal if evt_variant.value.StringVal else ""
                logger.info(f"HelpLink: {help_link}")
                metadata.provider_properties['help_link'] = help_link
                
            elif prop_id == EvtPublisherMetadataPropertyId.EvtPublisherMetadataPublisherMessageID:
                if evt_variant.value.UInt32Val == 0xFFFFFFFF:  # -1 as unsigned
                    logger.info("Message string: (not specified)")
                    metadata.provider_properties['publisher_message'] = None
                else:
                    message = self._get_message_string(handle, evt_variant.value.UInt32Val)
                    logger.info(f"Publisher message string: {message or '(empty)'}")
                    metadata.provider_properties['publisher_message'] = message
                    
            elif prop_id == EvtPublisherMetadataPropertyId.EvtPublisherMetadataChannelReferences:
                logger.info("Channels:")
                return self._process_channel_references(handle, evt_variant.value.EvtHandleVal, metadata)
                
            elif prop_id == EvtPublisherMetadataPropertyId.EvtPublisherMetadataLevels:
                logger.info("Levels:")
                return self._process_levels(handle, evt_variant.value.EvtHandleVal, metadata)
                
            elif prop_id == EvtPublisherMetadataPropertyId.EvtPublisherMetadataTasks:
                logger.info("Tasks:")
                return self._process_tasks(handle, evt_variant.value.EvtHandleVal, metadata)
                
            elif prop_id == EvtPublisherMetadataPropertyId.EvtPublisherMetadataOpcodes:
                logger.info("Opcodes:")
                return self._process_opcodes(handle, evt_variant.value.EvtHandleVal, metadata)
                
            elif prop_id == EvtPublisherMetadataPropertyId.EvtPublisherMetadataKeywords:
                logger.info("Keywords:")
                return self._process_keywords(handle, evt_variant.value.EvtHandleVal, metadata)
                
            # Skip type-specific properties (handled by their parent cases)
            elif prop_id in [
                EvtPublisherMetadataPropertyId.EvtPublisherMetadataChannelReferencePath,
                EvtPublisherMetadataPropertyId.EvtPublisherMetadataChannelReferenceIndex,
                EvtPublisherMetadataPropertyId.EvtPublisherMetadataChannelReferenceID,
                EvtPublisherMetadataPropertyId.EvtPublisherMetadataChannelReferenceFlags,
                EvtPublisherMetadataPropertyId.EvtPublisherMetadataChannelReferenceMessageID,
                EvtPublisherMetadataPropertyId.EvtPublisherMetadataLevelName,
                EvtPublisherMetadataPropertyId.EvtPublisherMetadataLevelValue,
                EvtPublisherMetadataPropertyId.EvtPublisherMetadataLevelMessageID,
                EvtPublisherMetadataPropertyId.EvtPublisherMetadataTaskName,
                EvtPublisherMetadataPropertyId.EvtPublisherMetadataTaskEventGuid,
                EvtPublisherMetadataPropertyId.EvtPublisherMetadataTaskValue,
                EvtPublisherMetadataPropertyId.EvtPublisherMetadataTaskMessageID,
                EvtPublisherMetadataPropertyId.EvtPublisherMetadataOpcodeName,
                EvtPublisherMetadataPropertyId.EvtPublisherMetadataOpcodeValue,
                EvtPublisherMetadataPropertyId.EvtPublisherMetadataOpcodeMessageID,
                EvtPublisherMetadataPropertyId.EvtPublisherMetadataKeywordName,
                EvtPublisherMetadataPropertyId.EvtPublisherMetadataKeywordValue,
                EvtPublisherMetadataPropertyId.EvtPublisherMetadataKeywordMessageID,
            ]:
                pass  # These are handled by their parent cases
                
            else:
                logger.warning(f"Unknown property Id: {property_id}")
                
            return WindowsError.ERROR_SUCCESS
            
        except Exception as e:
            logger.error(f"Error processing property {property_id}: {e}")
            return WindowsError.ERROR_OUTOFMEMORY
    
    def _process_channel_references(self, metadata_handle: HANDLE, array_handle: HANDLE, 
                                  metadata: EventProviderMetadata) -> int:
        """Process channel reference array"""
        try:
            array_size = self._api.get_object_array_size(array_handle)
            if array_size is None:
                return self._api._kernel32.GetLastError()
            
            if array_size > 0:
                for i in range(array_size):
                    status = self._dump_channel_properties(metadata_handle, array_handle, i, metadata.channel_messages)
                    if status != WindowsError.ERROR_SUCCESS:
                        logger.error(f"Failed to dump channel properties at index {i}")
                        return status
                    
            self._api.close_handle(array_handle)
            return WindowsError.ERROR_SUCCESS
            
        except Exception as e:
            logger.error(f"Error processing channels: {e}")
            return WindowsError.ERROR_OUTOFMEMORY
    
    def _process_levels(self, metadata_handle: HANDLE, array_handle: HANDLE, metadata: EventProviderMetadata) -> int:
        """Process levels array"""
        try:
            array_size = self._api.get_object_array_size(array_handle)
            if array_size is None:
                return self._api._kernel32.GetLastError()
            
            if array_size > 0:
                for i in range(array_size):
                    status = self._dump_level_properties(metadata_handle, array_handle, i, metadata.level_messages)
                    if status != WindowsError.ERROR_SUCCESS:
                        logger.error(f"Failed to dump level properties at index {i}")
                        return status
                    
            self._api.close_handle(array_handle)
            return WindowsError.ERROR_SUCCESS
            
        except Exception as e:
            logger.error(f"Error processing levels: {e}")
            return WindowsError.ERROR_OUTOFMEMORY
    
    def _process_tasks(self, metadata_handle: HANDLE, array_handle: HANDLE, metadata: EventProviderMetadata) -> int:
        """Process tasks array"""
        try:
            array_size = self._api.get_object_array_size(array_handle)
            if array_size is None:
                return self._api._kernel32.GetLastError()
            
            if array_size > 0:
                for i in range(array_size):
                    status = self._dump_task_properties(metadata_handle, array_handle, i, metadata.task_messages)
                    if status != WindowsError.ERROR_SUCCESS:
                        logger.error(f"Failed to dump task properties at index {i}")
                        return status
                    
            self._api.close_handle(array_handle)
            return WindowsError.ERROR_SUCCESS
            
        except Exception as e:
            logger.error(f"Error processing tasks: {e}")
            return WindowsError.ERROR_OUTOFMEMORY
    
    def _process_opcodes(self, metadata_handle: HANDLE, array_handle: HANDLE, metadata: EventProviderMetadata) -> int:
        """Process opcodes array"""
        try:
            array_size = self._api.get_object_array_size(array_handle)
            if array_size is None:
                return self._api._kernel32.GetLastError()
            
            if array_size > 0:
                for i in range(array_size):
                    status = self._dump_opcode_properties(metadata_handle, array_handle, i, metadata.opcode_messages)
                    if status != WindowsError.ERROR_SUCCESS:
                        logger.error(f"Failed to dump opcode properties at index {i}")
                        return status
                    
            self._api.close_handle(array_handle)
            return WindowsError.ERROR_SUCCESS
            
        except Exception as e:
            logger.error(f"Error processing opcodes: {e}")
            return WindowsError.ERROR_OUTOFMEMORY
    
    def _process_keywords(self, metadata_handle: HANDLE, array_handle: HANDLE, metadata: EventProviderMetadata) -> int:
        """Process keywords array"""
        try:
            array_size = self._api.get_object_array_size(array_handle)
            if array_size is None:
                return self._api._kernel32.GetLastError()
            
            if array_size > 0:
                for i in range(array_size):
                    status = self._dump_keyword_properties(metadata_handle, array_handle, i, metadata.keyword_messages)
                    if status != WindowsError.ERROR_SUCCESS:
                        logger.error(f"Failed to dump keyword properties at index {i}")
                        return status
                    
            self._api.close_handle(array_handle)
            return WindowsError.ERROR_SUCCESS
            
        except Exception as e:
            logger.error(f"Error processing keywords: {e}")
            return WindowsError.ERROR_OUTOFMEMORY
    
    def _print_provider_events(self, handle: HANDLE,
                             metadata: EventProviderMetadata) -> int:
        """
        Enumerate and print all provider events.
        
        This implements the C++ PrintProviderEvents function.
        """
        logger.info("Enumerating provider events...")
        
        try:
            # Get a handle to the provider's events
            events_handle = self._api.open_event_metadata_enum(handle)
            if events_handle is None:
                return self._api._kernel32.GetLastError()
            
            try:
                # Enumerate the events and print each event's metadata
                while True:
                    event_handle = self._api.next_event_metadata(events_handle)
                    if event_handle is None:
                        # Check if it's end of enumeration or an error
                        error_code = self._api._kernel32.GetLastError()
                        if error_code == WindowsError.ERROR_NO_MORE_ITEMS:
                            break
                        else:
                            error_message = self._api.format_error_message(error_code)
                            logger.error(f"EvtNextEventMetadata failed: {error_message}")
                            return error_code
                    
                    try:
                        # Print event properties
                        status = self._print_event_properties(handle, event_handle, metadata)
                        if status != WindowsError.ERROR_SUCCESS:
                            logger.error(f"Failed to print event properties")
                            return status
                    finally:
                        self._api.close_handle(event_handle)
                        
            finally:
                self._api.close_handle(events_handle)
            
            return WindowsError.ERROR_SUCCESS
            
        except Exception as e:
            logger.error(f"Error enumerating provider events: {e}")
            return WindowsError.ERROR_OUTOFMEMORY
    
    def _cleanup_messages(self, metadata: EventProviderMetadata) -> None:
        """Clean up message resources"""
        # In Python, garbage collection handles this automatically
        # This method is kept for consistency with the C++ version
        logger.debug("Cleaning up message resources")
        
        # Clear all message collections
        metadata.channel_messages.messages.clear()
        metadata.level_messages.messages.clear()
        metadata.task_messages.messages.clear()
        metadata.opcode_messages.messages.clear()
        metadata.keyword_messages.messages.clear()
    
    def _get_message_string(self, metadata_handle: HANDLE, message_id: int) -> Optional[str]:
        """
        Get formatted message string by ID.
        
        This implements the C++ GetMessageString function.
        
        Args:
            metadata_handle: Publisher metadata handle
            message_id: Message ID to format
            
        Returns:
            Formatted message string, or None if failed
        """
        return self._api.format_message(metadata_handle, message_id)


def main():
    """
    Example usage of the event metadata enumerator.
    
    Enhanced with detailed Windows error message formatting using FormatMessage API.
    """
    try:
        enumerator = EventMetadataEnumerator()
        
        # Example with Microsoft Windows Security Auditing provider
        provider_name = "Microsoft-Windows-Security-Auditing"
        metadata = enumerator.get_metadata(provider_name)
        
        # Convert to JSON for output
        json_output = json.dumps(metadata, indent=2)
        print(json_output)
        
    except EventMetadataError as e:
        logger.error(f"Metadata error: {e}")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return 1
    
    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main() or 0)