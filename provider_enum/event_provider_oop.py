import ctypes
from ctypes.wintypes import HANDLE, DWORD, LPWSTR
from typing import List, Dict, Any, Optional, Union, Iterator
from contextlib import contextmanager
import logging
from dataclasses import dataclass, field
from enum import IntEnum
import json
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Reuse existing enums from enumerate_metadata.py
class WindowsError(IntEnum):
    """Common Windows error codes used in event provider enumeration"""
    ERROR_SUCCESS = 0
    ERROR_INSUFFICIENT_BUFFER = 122
    ERROR_NO_MORE_ITEMS = 259
    ERROR_OUTOFMEMORY = 14


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
class EventMetadataError(Exception):
    """Custom exception for event metadata operations"""
    message: str


class WindowsEventAPI:
    """Unified Windows Event API wrapper for both provider enumeration and metadata access"""
    
    def __init__(self):
        self._wevtapi = ctypes.windll.wevtapi
        self._kernel32 = ctypes.windll.kernel32
        self._ole32 = ctypes.windll.ole32
        self._configure_api_functions()
    
    def _configure_api_functions(self) -> None:
        """Configure ctypes function signatures for type safety"""
        # Windows error message formatting
        self._kernel32.FormatMessageW.restype = DWORD
        self._kernel32.FormatMessageW.argtypes = [
            DWORD, ctypes.c_void_p, DWORD, DWORD, ctypes.POINTER(LPWSTR), DWORD, ctypes.c_void_p
        ]
        
        self._kernel32.LocalFree.restype = ctypes.c_void_p
        self._kernel32.LocalFree.argtypes = [ctypes.c_void_p]
        
        # Provider enumeration functions
        self._wevtapi.EvtOpenPublisherEnum.restype = HANDLE
        self._wevtapi.EvtOpenPublisherEnum.argtypes = [ctypes.c_void_p, DWORD]
        
        self._wevtapi.EvtNextPublisherId.restype = DWORD
        self._wevtapi.EvtNextPublisherId.argtypes = [
            HANDLE, DWORD, ctypes.c_wchar_p, ctypes.POINTER(DWORD)
        ]
        
        # Metadata functions
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
    
    def get_last_error(self) -> int:
        """Get the last Windows error code"""
        return self._kernel32.GetLastError()
    
    def format_error_message(self, error_code: int) -> str:
        """Get Windows system error message for an error code using FormatMessage"""
        FORMAT_MESSAGE_FROM_SYSTEM = 0x00001000
        FORMAT_MESSAGE_ALLOCATE_BUFFER = 0x00000100
        FORMAT_MESSAGE_IGNORE_INSERTS = 0x00000200
        
        # Buffer to receive the error message pointer
        buffer = LPWSTR()
        
        flags = FORMAT_MESSAGE_FROM_SYSTEM | FORMAT_MESSAGE_ALLOCATE_BUFFER | FORMAT_MESSAGE_IGNORE_INSERTS
        
        # Call FormatMessage to get the error description
        chars_written = self._kernel32.FormatMessageW(
            flags,
            None,  # lpSource (NULL for system messages)
            error_code,
            0,  # Language ID (0 for default language)
            ctypes.byref(buffer),
            0,  # nSize (0 when using ALLOCATE_BUFFER)
            None  # Arguments
        )
        
        if chars_written == 0:
            # FormatMessage failed, return generic message
            return f"Error {error_code}"
        
        try:
            # Get the message and strip trailing whitespace
            message = buffer.value.rstrip() if buffer.value else f"Error {error_code}"
            return message
        finally:
            # Free the buffer allocated by FormatMessage
            if buffer:
                self._kernel32.LocalFree(buffer)
    
    def close_handle(self, handle: HANDLE) -> None:
        """Close an event handle"""
        if handle:
            self._wevtapi.EvtClose(handle)


@dataclass
class MessageString:
    """Container for message strings with associated values"""
    value: Optional[int] = None
    mask: Optional[int] = None  # For keywords
    message: Optional[str] = None
    
    def get_value(self) -> Union[int, None]:
        """Get the appropriate value (value or mask)"""
        return self.value if self.value is not None else self.mask


@dataclass
class MessageCollection:
    """Collection of message strings for a specific metadata type"""
    messages: List[MessageString] = field(default_factory=list)
    
    def add(self, msg_string: MessageString) -> None:
        """Add a message string to the collection"""
        self.messages.append(msg_string)
    
    def find_by_value(self, value: int) -> Optional[MessageString]:
        """Find message by value"""
        for msg in self.messages:
            if msg.value == value:
                return msg
        return None
    
    def find_by_mask(self, mask: int) -> Optional[MessageString]:
        """Find message by mask"""
        for msg in self.messages:
            if msg.mask == mask:
                return msg
        return None


@dataclass
class Event:
    """Represents an event with its metadata"""
    event_id: Optional[int] = None
    version: Optional[int] = None
    channel: Optional[str] = None
    level: Optional[str] = None
    opcode: Optional[str] = None
    task: Optional[str] = None
    keyword: Optional[str] = None
    message: Optional[str] = None
    template: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'event_id': self.event_id,
            'version': self.version,
            'channel': self.channel,
            'level': self.level,
            'opcode': self.opcode,
            'task': self.task,
            'keyword': self.keyword,
            'message': self.message,
            'template': self.template
        }


@dataclass
class ProviderMetadata:
    """Contains all metadata for a provider"""
    guid: Optional[str] = None
    resource_file_path: Optional[str] = None
    parameter_file_path: Optional[str] = None
    message_file_path: Optional[str] = None
    help_link: Optional[str] = None
    publisher_message: Optional[str] = None
    
    # Message collections
    channels: MessageCollection = field(default_factory=MessageCollection)
    levels: MessageCollection = field(default_factory=MessageCollection)
    tasks: MessageCollection = field(default_factory=MessageCollection)
    opcodes: MessageCollection = field(default_factory=MessageCollection)
    keywords: MessageCollection = field(default_factory=MessageCollection)
    
    # Events
    events: List[Event] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'guid': self.guid,
            'resource_file_path': self.resource_file_path,
            'parameter_file_path': self.parameter_file_path,
            'message_file_path': self.message_file_path,
            'help_link': self.help_link,
            'publisher_message': self.publisher_message,
            'channels': [{'value': msg.value, 'message': msg.message} 
                        for msg in self.channels.messages],
            'levels': [{'value': msg.value, 'message': msg.message} 
                      for msg in self.levels.messages],
            'tasks': [{'value': msg.value, 'message': msg.message} 
                     for msg in self.tasks.messages],
            'opcodes': [{'value': msg.value, 'message': msg.message} 
                       for msg in self.opcodes.messages],
            'keywords': [{'mask': msg.mask, 'message': msg.message} 
                        for msg in self.keywords.messages],
            'events': [event.to_dict() for event in self.events]
        }


class EventProvider:
    """Object-oriented representation of a Windows Event Provider"""
    
    def __init__(self, name: str, api: Optional[WindowsEventAPI] = None):
        self.name = name
        self._api = api or WindowsEventAPI()
        self._metadata: Optional[ProviderMetadata] = None
        self._metadata_handle: Optional[HANDLE] = None
    
    def __str__(self) -> str:
        return f"EventProvider('{self.name}')"
    
    def __repr__(self) -> str:
        return f"EventProvider(name='{self.name}')"
    
    def __enter__(self):
        """Context manager entry - open metadata"""
        self.open_metadata()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - close metadata"""
        self.close_metadata()
    
    def open_metadata(self) -> None:
        """Open metadata handle for this provider"""
        if self._metadata_handle:
            return  # Already open
        
        try:
            handle = self._api._wevtapi.EvtOpenPublisherMetadata(
                None, ctypes.c_wchar_p(self.name), None, 0, 0
            )
            
            if not handle:
                error_code = self._api.get_last_error()
                error_msg = self._api.format_error_message(error_code)
                raise EventMetadataError(
                    f"EvtOpenPublisherMetadata failed for '{self.name}'. Error ({error_code}): {error_msg}"
                )
            
            self._metadata_handle = handle
            self._metadata = ProviderMetadata()
            
        except Exception as e:
            logger.error(f"Error opening metadata for {self.name}: {e}")
            raise
    
    def close_metadata(self) -> None:
        """Close metadata handle"""
        if self._metadata_handle:
            self._api.close_handle(self._metadata_handle)
            self._metadata_handle = None
    
    @property
    def metadata(self) -> ProviderMetadata:
        """Get metadata (loads if not already loaded)"""
        if not self._metadata:
            self.load_metadata()
        return self._metadata
    
    def load_metadata(self) -> None:
        """Load all metadata for this provider"""
        with self:  # Ensures handle is open and closed
            logger.info(f"Loading metadata for provider: {self.name}")
            self._load_provider_properties()
            self._load_provider_events()
    
    def _load_provider_properties(self) -> None:
        """Load provider-level properties"""
        if not self._metadata_handle:
            raise EventMetadataError("Metadata handle not open")
        
        # Load basic properties
        self._load_basic_properties()
        
        # Load message collections
        self._load_channels()
        self._load_levels()
        self._load_tasks()
        self._load_opcodes()
        self._load_keywords()
    
    def _load_basic_properties(self) -> None:
        """Load basic provider properties like GUID, paths, etc."""
        # Get GUID
        variant = self._get_publisher_property(
            EvtPublisherMetadataPropertyId.EvtPublisherMetadataPublisherGuid
        )
        if variant and variant.value.GuidVal:
            self._metadata.guid = self._guid_to_string(variant.value.GuidVal.contents)
        
        # Get resource file path
        variant = self._get_publisher_property(
            EvtPublisherMetadataPropertyId.EvtPublisherMetadataResourceFilePath
        )
        if variant and variant.value.StringVal:
            self._metadata.resource_file_path = variant.value.StringVal
        
        # Get parameter file path
        variant = self._get_publisher_property(
            EvtPublisherMetadataPropertyId.EvtPublisherMetadataParameterFilePath
        )
        if variant and variant.Type != EvtVariantType.EvtVarTypeNull:
            self._metadata.parameter_file_path = variant.value.StringVal
        
        # Get message file path
        variant = self._get_publisher_property(
            EvtPublisherMetadataPropertyId.EvtPublisherMetadataMessageFilePath
        )
        if variant and variant.value.StringVal:
            self._metadata.message_file_path = variant.value.StringVal
        
        # Get help link
        variant = self._get_publisher_property(
            EvtPublisherMetadataPropertyId.EvtPublisherMetadataHelpLink
        )
        if variant and variant.value.StringVal:
            self._metadata.help_link = variant.value.StringVal
        
        # Get publisher message
        variant = self._get_publisher_property(
            EvtPublisherMetadataPropertyId.EvtPublisherMetadataPublisherMessageID
        )
        if variant and variant.value.UInt32Val != 0xFFFFFFFF:
            self._metadata.publisher_message = self._format_message(variant.value.UInt32Val)
    
    def _load_channels(self) -> None:
        """Load channel metadata"""
        variant = self._get_publisher_property(
            EvtPublisherMetadataPropertyId.EvtPublisherMetadataChannelReferences
        )
        if not variant:
            return
        
        array_handle = variant.value.EvtHandleVal
        if not array_handle:
            return
        
        try:
            array_size = self._get_array_size(array_handle)
            for i in range(array_size):
                self._load_channel_item(array_handle, i)
        finally:
            self._api.close_handle(array_handle)
    
    def _load_channel_item(self, array_handle: HANDLE, index: int) -> None:
        """Load a single channel item"""
        # Get channel ID
        variant = self._get_array_property(
            array_handle,
            EvtPublisherMetadataPropertyId.EvtPublisherMetadataChannelReferenceID,
            index
        )
        if not variant:
            return
        
        channel_id = variant.value.UInt32Val
        
        # Get channel message or path
        message = None
        variant = self._get_array_property(
            array_handle,
            EvtPublisherMetadataPropertyId.EvtPublisherMetadataChannelReferenceMessageID,
            index
        )
        if variant and variant.value.UInt32Val != 0xFFFFFFFF:
            message = self._format_message(variant.value.UInt32Val)
        
        if not message:
            # Use channel path as fallback
            variant = self._get_array_property(
                array_handle,
                EvtPublisherMetadataPropertyId.EvtPublisherMetadataChannelReferencePath,
                index
            )
            if variant and variant.value.StringVal:
                message = variant.value.StringVal
        
        self._metadata.channels.add(MessageString(value=channel_id, message=message))
    
    def _load_levels(self) -> None:
        """Load level metadata"""
        variant = self._get_publisher_property(
            EvtPublisherMetadataPropertyId.EvtPublisherMetadataLevels
        )
        if not variant:
            return
        
        array_handle = variant.value.EvtHandleVal
        if not array_handle:
            return
        
        try:
            array_size = self._get_array_size(array_handle)
            for i in range(array_size):
                self._load_level_item(array_handle, i)
        finally:
            self._api.close_handle(array_handle)
    
    def _load_level_item(self, array_handle: HANDLE, index: int) -> None:
        """Load a single level item"""
        # Get level value
        variant = self._get_array_property(
            array_handle,
            EvtPublisherMetadataPropertyId.EvtPublisherMetadataLevelValue,
            index
        )
        if not variant:
            return
        
        level_value = variant.value.UInt32Val
        
        # Get level message or name
        message = None
        variant = self._get_array_property(
            array_handle,
            EvtPublisherMetadataPropertyId.EvtPublisherMetadataLevelMessageID,
            index
        )
        if variant and variant.value.UInt32Val != 0xFFFFFFFF:
            message = self._format_message(variant.value.UInt32Val)
        
        if not message:
            # Use level name as fallback
            variant = self._get_array_property(
                array_handle,
                EvtPublisherMetadataPropertyId.EvtPublisherMetadataLevelName,
                index
            )
            if variant and variant.value.StringVal:
                message = variant.value.StringVal
        
        self._metadata.levels.add(MessageString(value=level_value, message=message))
    
    def _load_tasks(self) -> None:
        """Load task metadata"""
        variant = self._get_publisher_property(
            EvtPublisherMetadataPropertyId.EvtPublisherMetadataTasks
        )
        if not variant:
            return
        
        array_handle = variant.value.EvtHandleVal
        if not array_handle:
            return
        
        try:
            array_size = self._get_array_size(array_handle)
            for i in range(array_size):
                self._load_task_item(array_handle, i)
        finally:
            self._api.close_handle(array_handle)
    
    def _load_task_item(self, array_handle: HANDLE, index: int) -> None:
        """Load a single task item"""
        # Get task value
        variant = self._get_array_property(
            array_handle,
            EvtPublisherMetadataPropertyId.EvtPublisherMetadataTaskValue,
            index
        )
        if not variant:
            return
        
        task_value = variant.value.UInt32Val
        
        # Get task message or name
        message = None
        variant = self._get_array_property(
            array_handle,
            EvtPublisherMetadataPropertyId.EvtPublisherMetadataTaskMessageID,
            index
        )
        if variant and variant.value.UInt32Val != 0xFFFFFFFF:
            message = self._format_message(variant.value.UInt32Val)
        
        if not message:
            # Use task name as fallback
            variant = self._get_array_property(
                array_handle,
                EvtPublisherMetadataPropertyId.EvtPublisherMetadataTaskName,
                index
            )
            if variant and variant.value.StringVal:
                message = variant.value.StringVal
        
        self._metadata.tasks.add(MessageString(value=task_value, message=message))
    
    def _load_opcodes(self) -> None:
        """Load opcode metadata"""
        variant = self._get_publisher_property(
            EvtPublisherMetadataPropertyId.EvtPublisherMetadataOpcodes
        )
        if not variant:
            return
        
        array_handle = variant.value.EvtHandleVal
        if not array_handle:
            return
        
        try:
            array_size = self._get_array_size(array_handle)
            for i in range(array_size):
                self._load_opcode_item(array_handle, i)
        finally:
            self._api.close_handle(array_handle)
    
    def _load_opcode_item(self, array_handle: HANDLE, index: int) -> None:
        """Load a single opcode item"""
        # Get opcode value
        variant = self._get_array_property(
            array_handle,
            EvtPublisherMetadataPropertyId.EvtPublisherMetadataOpcodeValue,
            index
        )
        if not variant:
            return
        
        opcode_value = variant.value.UInt32Val
        
        # Get opcode message or name
        message = None
        variant = self._get_array_property(
            array_handle,
            EvtPublisherMetadataPropertyId.EvtPublisherMetadataOpcodeMessageID,
            index
        )
        if variant and variant.value.UInt32Val != 0xFFFFFFFF:
            message = self._format_message(variant.value.UInt32Val)
        
        if not message:
            # Use opcode name as fallback
            variant = self._get_array_property(
                array_handle,
                EvtPublisherMetadataPropertyId.EvtPublisherMetadataOpcodeName,
                index
            )
            if variant and variant.value.StringVal:
                message = variant.value.StringVal
        
        self._metadata.opcodes.add(MessageString(value=opcode_value, message=message))
    
    def _load_keywords(self) -> None:
        """Load keyword metadata"""
        variant = self._get_publisher_property(
            EvtPublisherMetadataPropertyId.EvtPublisherMetadataKeywords
        )
        if not variant:
            return
        
        array_handle = variant.value.EvtHandleVal
        if not array_handle:
            return
        
        try:
            array_size = self._get_array_size(array_handle)
            for i in range(array_size):
                self._load_keyword_item(array_handle, i)
        finally:
            self._api.close_handle(array_handle)
    
    def _load_keyword_item(self, array_handle: HANDLE, index: int) -> None:
        """Load a single keyword item"""
        # Get keyword value (mask)
        variant = self._get_array_property(
            array_handle,
            EvtPublisherMetadataPropertyId.EvtPublisherMetadataKeywordValue,
            index
        )
        if not variant:
            return
        
        keyword_mask = variant.value.UInt64Val
        
        # Get keyword message or name
        message = None
        variant = self._get_array_property(
            array_handle,
            EvtPublisherMetadataPropertyId.EvtPublisherMetadataKeywordMessageID,
            index
        )
        if variant and variant.value.UInt32Val != 0xFFFFFFFF:
            message = self._format_message(variant.value.UInt32Val)
        
        if not message:
            # Use keyword name as fallback
            variant = self._get_array_property(
                array_handle,
                EvtPublisherMetadataPropertyId.EvtPublisherMetadataKeywordName,
                index
            )
            if variant and variant.value.StringVal:
                message = variant.value.StringVal
        
        self._metadata.keywords.add(MessageString(mask=keyword_mask, message=message))
    
    def _load_provider_events(self) -> None:
        """Load all events for this provider"""
        if not self._metadata_handle:
            raise EventMetadataError("Metadata handle not open")
        
        # Open event enumeration
        events_handle = self._api._wevtapi.EvtOpenEventMetadataEnum(self._metadata_handle, 0)
        if not events_handle:
            error_code = self._api.get_last_error()
            error_msg = self._api.format_error_message(error_code)
            logger.error(f"EvtOpenEventMetadataEnum failed for provider '{self.name}' with error ({error_code}): {error_msg}")
            return
        
        try:
            while True:
                event_handle = self._api._wevtapi.EvtNextEventMetadata(events_handle, 0)
                if not event_handle:
                    error_code = self._api.get_last_error()
                    if error_code == WindowsError.ERROR_NO_MORE_ITEMS:
                        break
                    error_msg = self._api.format_error_message(error_code)
                    logger.error(f"EvtNextEventMetadata failed for provider '{self.name}' with error ({error_code}): {error_msg}")
                    break
                
                try:
                    event = self._load_event_metadata(event_handle)
                    if event:
                        self._metadata.events.append(event)
                finally:
                    self._api.close_handle(event_handle)
        finally:
            self._api.close_handle(events_handle)
    
    def _load_event_metadata(self, event_handle: HANDLE) -> Optional[Event]:
        """Load metadata for a single event"""
        event = Event()
        
        # Event ID
        variant = self._get_event_property(
            event_handle, EvtEventMetadataPropertyId.EventMetadataEventID
        )
        if variant:
            event.event_id = variant.value.UInt32Val
        
        # Version
        variant = self._get_event_property(
            event_handle, EvtEventMetadataPropertyId.EventMetadataEventVersion, event.event_id
        )
        if variant:
            event.version = variant.value.UInt32Val
        
        # Channel
        variant = self._get_event_property(
            event_handle, EvtEventMetadataPropertyId.EventMetadataEventChannel, event.event_id
        )
        if variant and variant.value.UInt32Val > 0:
            channel_msg = self._metadata.channels.find_by_value(variant.value.UInt32Val)
            event.channel = channel_msg.message if channel_msg else None
        
        # Level
        variant = self._get_event_property(
            event_handle, EvtEventMetadataPropertyId.EventMetadataEventLevel, event.event_id
        )
        if variant and variant.value.UInt32Val > 0:
            level_msg = self._metadata.levels.find_by_value(variant.value.UInt32Val)
            event.level = level_msg.message if level_msg else None
        
        # Task
        variant = self._get_event_property(
            event_handle, EvtEventMetadataPropertyId.EventMetadataEventTask, event.event_id
        )
        task_value = variant.value.UInt32Val if variant else 0
        if task_value > 0:
            task_msg = self._metadata.tasks.find_by_value(task_value)
            event.task = task_msg.message if task_msg else None
        
        # Opcode
        variant = self._get_event_property(
            event_handle, EvtEventMetadataPropertyId.EventMetadataEventOpcode, event.event_id
        )
        if variant and variant.value.UInt32Val > 0:
            opcode_name = self._get_opcode_name(variant.value.UInt32Val, task_value)
            event.opcode = opcode_name
        
        # Keyword
        variant = self._get_event_property(
            event_handle, EvtEventMetadataPropertyId.EventMetadataEventKeyword, event.event_id
        )
        if variant:
            keyword_mask = variant.value.UInt64Val & 0x00FFFFFFFFFFFFFF
            if keyword_mask > 0:
                keyword_names = self._get_keyword_names(keyword_mask)
                event.keyword = keyword_names
        
        # Message
        variant = self._get_event_property(
            event_handle, EvtEventMetadataPropertyId.EventMetadataEventMessageID, event.event_id
        )
        if variant and variant.value.UInt32Val != 0xFFFFFFFF:
            event.message = self._format_message(variant.value.UInt32Val)
        
        # Template
        variant = self._get_event_property(
            event_handle, EvtEventMetadataPropertyId.EventMetadataEventTemplate, event.event_id
        )
        if variant and variant.value.StringVal:
            event.template = variant.value.StringVal
        
        return event
    
    def _get_opcode_name(self, opcode_value: int, task_value: int) -> Optional[str]:
        """Get opcode name considering task-specific opcodes"""
        opcode_high = (opcode_value >> 16) & 0xFFFF
        global_opcode_msg = None
        
        for msg in self._metadata.opcodes.messages:
            if msg.value is None:
                continue
            
            msg_opcode_high = (msg.value >> 16) & 0xFFFF
            msg_task_low = msg.value & 0xFFFF
            
            if opcode_high == msg_opcode_high:
                if msg_task_low == 0:
                    global_opcode_msg = msg
                elif task_value == msg_task_low:
                    return msg.message
        
        return global_opcode_msg.message if global_opcode_msg else None
    
    def _get_keyword_names(self, keyword_mask: int) -> Optional[str]:
        """Get concatenated keyword names based on bitmask"""
        keyword_names = []
        
        for msg in self._metadata.keywords.messages:
            if msg.mask is None:
                continue
            
            if keyword_mask & msg.mask:
                if msg.message:
                    keyword_names.append(msg.message)
        
        return " ".join(keyword_names) if keyword_names else None
    
    def _get_publisher_property(self, property_id: EvtPublisherMetadataPropertyId) -> Optional[EvtVariant]:
        """Get a publisher metadata property"""
        buffer_size = DWORD(0)
        buffer_used = DWORD(0)
        
        # First call to get required buffer size
        result = self._api._wevtapi.EvtGetPublisherMetadataProperty(
            self._metadata_handle, property_id, 0, 0, None, ctypes.byref(buffer_used)
        )
        
        if not result:
            error_code = self._api.get_last_error()
            if error_code != WindowsError.ERROR_INSUFFICIENT_BUFFER:
                error_msg = self._api.format_error_message(error_code)
                logger.error(f"EvtGetPublisherMetadataProperty '{property_id.name}' failed for provider '{self.name}' with error ({error_code}): {error_msg}")
                return None
            
            buffer_size = buffer_used
        
        # Allocate buffer and get property
        if buffer_size.value == 0:
            buffer_size = DWORD(ctypes.sizeof(EvtVariant))
        
        property_buffer = (ctypes.c_byte * buffer_size.value)()
        evt_variant = ctypes.cast(property_buffer, ctypes.POINTER(EvtVariant)).contents
        
        result = self._api._wevtapi.EvtGetPublisherMetadataProperty(
            self._metadata_handle, property_id, 0, buffer_size, 
            ctypes.byref(evt_variant), ctypes.byref(buffer_used)
        )
        
        if not result:
            error_code = self._api.get_last_error()
            error_msg = self._api.format_error_message(error_code)
            logger.error(f"EvtGetPublisherMetadataProperty '{property_id.name}' failed for provider '{self.name}' with error ({error_code}): {error_msg}")
            return None
        
        return evt_variant
    
    def _get_event_property(self, event_handle: HANDLE, property_id: EvtEventMetadataPropertyId, event_id: Optional[int] = None) -> Optional[EvtVariant]:
        """Get an event metadata property"""
        buffer_size = DWORD(0)
        buffer_used = DWORD(0)
        
        # First call to get required buffer size
        result = self._api._wevtapi.EvtGetEventMetadataProperty(
            event_handle, property_id, 0, 0, None, ctypes.byref(buffer_used)
        )
        
        if not result:
            error_code = self._api.get_last_error()
            if error_code != WindowsError.ERROR_INSUFFICIENT_BUFFER:
                event_info = f" event {event_id}" if event_id is not None else ""
                error_msg = self._api.format_error_message(error_code)
                logger.error(f"EvtGetEventMetadataProperty failed to get {property_id.name} for provider '{self.name}'{event_info} with error ({error_code}): {error_msg}")
                return None
            
            buffer_size = buffer_used
        
        # Allocate buffer and get property
        if buffer_size.value == 0:
            buffer_size = DWORD(ctypes.sizeof(EvtVariant))
        
        property_buffer = (ctypes.c_byte * buffer_size.value)()
        evt_variant = ctypes.cast(property_buffer, ctypes.POINTER(EvtVariant)).contents
        
        result = self._api._wevtapi.EvtGetEventMetadataProperty(
            event_handle, property_id, 0, buffer_size,
            ctypes.byref(evt_variant), ctypes.byref(buffer_used)
        )
        
        if not result:
            error_code = self._api.get_last_error()
            event_info = f" event {event_id}" if event_id is not None else ""
            logger.error(f"EvtGetEventMetadataProperty failed to get {property_id.name} for provider '{self.name}'{event_info} with error {error_code}")
            return None
        
        return evt_variant
    
    def _get_array_property(self, array_handle: HANDLE, property_id: EvtPublisherMetadataPropertyId, index: int) -> Optional[EvtVariant]:
        """Get a property from an object array"""
        buffer_size = DWORD(0)
        buffer_used = DWORD(0)
        
        # First call to get required buffer size
        result = self._api._wevtapi.EvtGetObjectArrayProperty(
            array_handle, property_id, index, 0, 0, None, ctypes.byref(buffer_used)
        )
        
        if not result:
            error_code = self._api.get_last_error()
            if error_code != WindowsError.ERROR_INSUFFICIENT_BUFFER:
                error_msg = self._api.format_error_message(error_code)
                logger.error(f"EvtGetObjectArrayProperty failed to get {property_id.name} for provider '{self.name}' at index {index} with error ({error_code}): {error_msg}")
                return None
            
            buffer_size = buffer_used
        
        # Allocate buffer and get property
        if buffer_size.value == 0:
            buffer_size = DWORD(ctypes.sizeof(EvtVariant))
        
        property_buffer = (ctypes.c_byte * buffer_size.value)()
        evt_variant = ctypes.cast(property_buffer, ctypes.POINTER(EvtVariant)).contents
        
        result = self._api._wevtapi.EvtGetObjectArrayProperty(
            array_handle, property_id, index, 0, buffer_size,
            ctypes.byref(evt_variant), ctypes.byref(buffer_used)
        )
        
        if not result:
            error_code = self._api.get_last_error()
            error_msg = self._api.format_error_message(error_code)
            logger.error(f"EvtGetObjectArrayProperty failed to get {property_id.name} for provider '{self.name}' at index {index} with error ({error_code}): {error_msg}")
            return None
        
        return evt_variant
    
    def _get_array_size(self, array_handle: HANDLE) -> int:
        """Get the size of an object array"""
        array_size = DWORD(0)
        result = self._api._wevtapi.EvtGetObjectArraySize(array_handle, ctypes.byref(array_size))
        
        if not result:
            return 0
        
        return array_size.value
    
    def _format_message(self, message_id: int) -> Optional[str]:
        """Format a message string using EvtFormatMessage"""
        buffer_size = DWORD(0)
        buffer_used = DWORD(0)
        
        # First call to get required buffer size
        result = self._api._wevtapi.EvtFormatMessage(
            self._metadata_handle, None, message_id, 0, None,
            EvtFormatMessageFlags.EvtFormatMessageId, 0, None, ctypes.byref(buffer_used)
        )
        
        if not result:
            error_code = self._api.get_last_error()
            if error_code != WindowsError.ERROR_INSUFFICIENT_BUFFER:
                error_msg = self._api.format_error_message(error_code)
                logger.error(f"EvtFormatMessage failed for provider '{self.name}' with message ID {message_id} and error {error_name} ({error_code})")
                return None
            
            buffer_size = buffer_used
        
        # Allocate buffer and format message
        if buffer_size.value == 0:
            return ""
        
        buffer = ctypes.create_unicode_buffer(buffer_size.value)
        
        result = self._api._wevtapi.EvtFormatMessage(
            self._metadata_handle, None, message_id, 0, None,
            EvtFormatMessageFlags.EvtFormatMessageId, buffer_size, buffer, ctypes.byref(buffer_used)
        )
        
        if not result:
            error_code = self._api.get_last_error()
            error_msg = self._api.format_error_message(error_code)
            logger.error(f"EvtFormatMessage failed for provider '{self.name}' with message ID {message_id} and error {error_name} ({error_code})")
            return None
        
        return buffer.value
    
    def _guid_to_string(self, guid_bytes: ctypes.Array) -> str:
        """Convert GUID bytes to string"""
        buffer = ctypes.create_unicode_buffer(50)
        result = self._api._ole32.StringFromGUID2(
            ctypes.cast(guid_bytes, ctypes.POINTER(ctypes.c_byte * 16)),
            buffer, 50
        )
        return buffer.value if result > 0 else ""
    
    def get_events(self) -> List[Event]:
        """Get all events for this provider"""
        if not self._metadata:
            self.load_metadata()
        return self._metadata.events
    
    def get_event_by_id(self, event_id: int) -> Optional[Event]:
        """Find an event by its ID"""
        for event in self.get_events():
            if event.event_id == event_id:
                return event
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert provider and all its metadata to dictionary"""
        if not self._metadata:
            self.load_metadata()
        
        return {
            'provider_name': self.name,
            'metadata': self._metadata.to_dict()
        }


class EventProviderManager:
    """Manager class for enumerating and working with event providers"""
    
    def __init__(self):
        self._api = WindowsEventAPI()
    
    @contextmanager
    def _publisher_enumeration(self):
        """Context manager for publisher enumeration handle"""
        handle = self._api._wevtapi.EvtOpenPublisherEnum(None, 0)
        if not handle:
            error_code = self._api.get_last_error()
            error_msg = self._api.format_error_message(error_code)
            raise EventMetadataError(
                f"EvtOpenPublisherEnum failed. Error ({error_code}): {error_msg}"
            )
        
        try:
            yield handle
        finally:
            self._api.close_handle(handle)
    
    def enumerate_providers(self) -> List[EventProvider]:
        """Enumerate all registered event providers on the system"""
        providers = []
        
        try:
            with self._publisher_enumeration() as handle:
                for provider_name in self._iterate_publishers(handle):
                    providers.append(EventProvider(provider_name, self._api))
        except Exception as e:
            logger.error(f"Failed to enumerate event providers: {e}")
            raise EventMetadataError(f"Enumeration failed: {e}") from e
        
        logger.info(f"Found {len(providers)} event providers")
        return providers
    
    def _iterate_publishers(self, handle: HANDLE) -> Iterator[str]:
        """Iterator over publisher names"""
        while True:
            provider_name = self._get_next_publisher_name(handle)
            if provider_name is None:
                break
            yield provider_name
    
    def _get_next_publisher_name(self, handle: HANDLE) -> Optional[str]:
        """Get the next publisher name from the enumeration handle"""
        buffer_size = DWORD(0)
        
        # First call to get required buffer size
        result = self._api._wevtapi.EvtNextPublisherId(
            handle, 0, None, ctypes.byref(buffer_size)
        )
        error_code = self._api.get_last_error()
        
        if error_code == WindowsError.ERROR_NO_MORE_ITEMS:
            return None
        
        if error_code != WindowsError.ERROR_INSUFFICIENT_BUFFER:
            error_msg = self._api.format_error_message(error_code)
            raise EventMetadataError(
                f"EvtNextPublisherId failed getting buffer size. Error ({error_code}): {error_msg}"
            )
        
        # Second call with properly sized buffer
        buffer = ctypes.create_unicode_buffer(buffer_size.value)
        result = self._api._wevtapi.EvtNextPublisherId(
            handle, buffer_size.value, buffer, ctypes.byref(buffer_size)
        )
        error_code = self._api.get_last_error()
        
        if not result:
            if error_code == WindowsError.ERROR_NO_MORE_ITEMS:
                return None
            error_msg = self._api.format_error_message(error_code)
            raise EventMetadataError(
                f"EvtNextPublisherId failed. Error ({error_code}): {error_msg}"
            )
        
        return buffer.value
    
    def get_provider(self, provider_name: str) -> EventProvider:
        """Get a specific provider by name"""
        return EventProvider(provider_name, self._api)
    
    def get_provider_names(self) -> List[str]:
        """Get just the provider names as strings"""
        return [provider.name for provider in self.enumerate_providers()]


def main():
    """Example usage of the refactored OOP event provider system"""
    try:
        # Create manager
        manager = EventProviderManager()
        
        # Example 1: List all providers
        print("Enumerating all providers...")
        providers = manager.enumerate_providers()
        print(f"Found {len(providers)} providers")
        print()
        
        # Example 2: Get specific provider with metadata
        provider_name = "Microsoft-Windows-Security-Auditing"
        print(f"Loading metadata for {provider_name}...")
        
        provider = manager.get_provider(provider_name)
        provider.load_metadata()
        
        # Access metadata
        metadata = provider.metadata
        print(f"Provider GUID: {metadata.guid}")
        print(f"Number of events: {len(provider.get_events())}")
        print(f"Number of tasks: {len(metadata.tasks.messages)}")
        print(f"Number of keywords: {len(metadata.keywords.messages)}")
        print()
        
        # Example 3: Find specific event
        event_id = 4624  # Logon event
        event = provider.get_event_by_id(event_id)
        if event:
            print(f"Found event {event_id}:")
            print(f"  Message: {event.message}")
            print(f"  Level: {event.level}")
            print(f"  Task: {event.task}")
        
        # Example 4: Export to JSON
        provider_dict = provider.to_dict()
        # Uncomment to save to file:
        # with open(f"{provider_name}.json", "w") as f:
        #     json.dump(provider_dict, f, indent=2)
        
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