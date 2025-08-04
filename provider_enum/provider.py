import ctypes
from ctypes.wintypes import HANDLE, DWORD, LPWSTR
from typing import List, Dict, Any, Optional, Union, Iterator
from contextlib import contextmanager
import logging
from dataclasses import dataclass, field
from enum import IntEnum
import json
import uuid
import winreg

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WindowsError(IntEnum):
    """Windows error codes"""
    ERROR_SUCCESS = 0
    ERROR_FILE_NOT_FOUND = 2
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


class EventProviderError(Exception):
    """Custom exception for event provider operations"""
    pass


@dataclass
class ProviderRegistryData:
    """Provider data from registry"""
    guid: str
    name: str
    enabled: bool = True
    message_file_path: Optional[str] = None
    resource_file_path: Optional[str] = None
    parameter_file_path: Optional[str] = None


class ProviderRegistry:
    """Reads and manages Windows Event providers from the registry"""
    
    REGISTRY_PATH = r"SOFTWARE\Microsoft\Windows\CurrentVersion\WINEVT\Publishers"
    
    def __init__(self):
        self.providers: Dict[str, ProviderRegistryData] = {}
        self.guid_lookup: Dict[str, ProviderRegistryData] = {}
        self.name_lookup: Dict[str, ProviderRegistryData] = {}
        self._load_providers()
    
    def _load_providers(self) -> None:
        """Load all providers from the registry"""
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, self.REGISTRY_PATH) as key:
                index = 0
                while True:
                    try:
                        # Enumerate subkeys (each is a provider GUID)
                        guid = winreg.EnumKey(key, index)
                        index += 1
                        
                        # Read provider data
                        provider_data = self._read_provider_data(key, guid)
                        if provider_data:
                            self.providers[guid] = provider_data
                            self.guid_lookup[guid.lower()] = provider_data
                            if provider_data.name:
                                self.name_lookup[provider_data.name.lower()] = provider_data
                                
                    except OSError as e:
                        if e.winerror == 259:  # ERROR_NO_MORE_ITEMS
                            break
                        else:
                            logger.error(f"Error reading provider {guid}: {e}")
                            
        except Exception as e:
            logger.error(f"Failed to open registry key: {e}")
            raise EventProviderError(f"Failed to access registry: {e}")
    
    def _read_provider_data(self, parent_key: winreg.HKEYType, guid: str) -> Optional[ProviderRegistryData]:
        """Read provider data from a registry key"""
        try:
            with winreg.OpenKey(parent_key, guid) as provider_key:
                # Read default value (provider name)
                try:
                    name, _ = winreg.QueryValueEx(provider_key, "")
                except OSError:
                    name = None
                
                # Read Enabled DWORD
                enabled = self._read_dword_as_bool(provider_key, "Enabled", default=True)
                
                # Read file paths
                message_file = self._read_registry_value(provider_key, "MessageFileName")
                resource_file = self._read_registry_value(provider_key, "ResourceFileName")
                parameter_file = self._read_registry_value(provider_key, "ParameterFileName")
                
                if name:
                    return ProviderRegistryData(
                        guid=guid,
                        name=name,
                        enabled=enabled,
                        message_file_path=message_file,
                        resource_file_path=resource_file,
                        parameter_file_path=parameter_file
                    )
                    
        except Exception as e:
            logger.debug(f"Failed to read provider data for {guid}: {e}")
            
        return None
    
    def _read_registry_value(self, key: winreg.HKEYType, value_name: str) -> Optional[str]:
        """Read a string value from registry"""
        try:
            value, _ = winreg.QueryValueEx(key, value_name)
            return value if value else None
        except OSError:
            return None
    
    def _read_dword_as_bool(self, key: winreg.HKEYType, value_name: str, default: bool = True) -> bool:
        """Read a DWORD value from registry and convert to boolean"""
        try:
            value, reg_type = winreg.QueryValueEx(key, value_name)
            # REG_DWORD type is 4
            if reg_type == winreg.REG_DWORD:
                return bool(value)
            return default
        except OSError:
            return default
    
    def get_by_guid(self, guid: str) -> Optional[ProviderRegistryData]:
        """Lookup provider by GUID (case-insensitive)"""
        # Normalize GUID format
        guid = guid.strip().lower()
        if not guid.startswith('{'):
            guid = '{' + guid
        if not guid.endswith('}'):
            guid = guid + '}'
            
        return self.guid_lookup.get(guid)
    
    def get_by_name(self, name: str) -> Optional[ProviderRegistryData]:
        """Lookup provider by name (case-insensitive)"""
        return self.name_lookup.get(name.lower())
    
    def get_all_providers(self) -> List[ProviderRegistryData]:
        """Get list of all providers"""
        return list(self.providers.values())
    
    def get_provider_names(self) -> List[str]:
        """Get list of all provider names"""
        return [p.name for p in self.providers.values() if p.name]
    
    def get_provider_guids(self) -> List[str]:
        """Get list of all provider GUIDs"""
        return list(self.providers.keys())
    
    def __len__(self) -> int:
        """Return the number of providers"""
        return len(self.providers)
    
    def __contains__(self, key: str) -> bool:
        """Check if provider exists by GUID or name"""
        return (key.lower() in self.guid_lookup or 
                key.lower() in self.name_lookup)
    
    def __repr__(self) -> str:
        return f"ProviderRegistry({len(self)} providers)"


@dataclass
class ChannelInfo:
    """Information about an event channel"""
    id: int
    name: str
    path: str
    index: int
    is_imported: bool
    message: Optional[str] = None


@dataclass
class LevelInfo:
    """Information about an event level"""
    value: int
    name: str
    message: Optional[str] = None


@dataclass
class TaskInfo:
    """Information about an event task"""
    value: int
    name: str
    event_guid: Optional[str] = None
    message: Optional[str] = None


@dataclass
class OpcodeInfo:
    """Information about an event opcode"""
    value: int
    name: str
    task_value: int
    opcode_value: int
    message: Optional[str] = None


@dataclass
class KeywordInfo:
    """Information about an event keyword"""
    mask: int
    name: str
    message: Optional[str] = None


class WindowsEventAPI:
    """Low-level Windows Event API wrapper"""
    
    def __init__(self):
        self._wevtapi = ctypes.windll.wevtapi
        self._kernel32 = ctypes.windll.kernel32
        self._ole32 = ctypes.windll.ole32
        self._configure_api_functions()
    
    def _configure_api_functions(self) -> None:
        """Configure ctypes function signatures for type safety"""
        # Publisher metadata functions
        self._wevtapi.EvtOpenPublisherMetadata.restype = HANDLE
        self._wevtapi.EvtOpenPublisherMetadata.argtypes = [
            HANDLE, LPWSTR, LPWSTR, DWORD, DWORD
        ]
        
        self._wevtapi.EvtGetPublisherMetadataProperty.restype = ctypes.c_bool
        self._wevtapi.EvtGetPublisherMetadataProperty.argtypes = [
            HANDLE, ctypes.c_int, DWORD, DWORD, 
            ctypes.POINTER(EvtVariant), ctypes.POINTER(DWORD)
        ]
        
        # Object array functions
        self._wevtapi.EvtGetObjectArraySize.restype = ctypes.c_bool
        self._wevtapi.EvtGetObjectArraySize.argtypes = [
            HANDLE, ctypes.POINTER(DWORD)
        ]
        
        self._wevtapi.EvtGetObjectArrayProperty.restype = ctypes.c_bool
        self._wevtapi.EvtGetObjectArrayProperty.argtypes = [
            HANDLE, ctypes.c_int, DWORD, DWORD, DWORD,
            ctypes.POINTER(EvtVariant), ctypes.POINTER(DWORD)
        ]
        
        # Event enumeration functions
        self._wevtapi.EvtOpenEventMetadataEnum.restype = HANDLE
        self._wevtapi.EvtOpenEventMetadataEnum.argtypes = [HANDLE, DWORD]
        
        self._wevtapi.EvtNextEventMetadata.restype = HANDLE
        self._wevtapi.EvtNextEventMetadata.argtypes = [HANDLE, DWORD]
        
        self._wevtapi.EvtGetEventMetadataProperty.restype = ctypes.c_bool
        self._wevtapi.EvtGetEventMetadataProperty.argtypes = [
            HANDLE, ctypes.c_int, DWORD, DWORD,
            ctypes.POINTER(EvtVariant), ctypes.POINTER(DWORD)
        ]
        
        # Message formatting
        self._wevtapi.EvtFormatMessage.restype = ctypes.c_bool
        self._wevtapi.EvtFormatMessage.argtypes = [
            HANDLE, HANDLE, DWORD, DWORD, ctypes.c_void_p,
            DWORD, DWORD, LPWSTR, ctypes.POINTER(DWORD)
        ]
        
        # Handle management
        self._wevtapi.EvtClose.restype = None
        self._wevtapi.EvtClose.argtypes = [HANDLE]
        
        # GUID conversion
        self._ole32.StringFromGUID2.restype = ctypes.c_int
        self._ole32.StringFromGUID2.argtypes = [
            ctypes.POINTER(ctypes.c_byte * 16), LPWSTR, ctypes.c_int
        ]
        
        # Error formatting
        self._kernel32.FormatMessageW.restype = DWORD
        self._kernel32.FormatMessageW.argtypes = [
            DWORD, ctypes.c_void_p, DWORD, DWORD, LPWSTR, DWORD, ctypes.c_void_p
        ]
    
    def format_error_message(self, error_code: int) -> str:
        """Format a Windows error code into a human-readable error message"""
        buffer_size = 1024
        buffer = ctypes.create_unicode_buffer(buffer_size)
        
        flags = (FormatMessageFlags.FORMAT_MESSAGE_FROM_SYSTEM | 
                FormatMessageFlags.FORMAT_MESSAGE_IGNORE_INSERTS)
        
        result = self._kernel32.FormatMessageW(
            flags, None, error_code, 0, buffer, buffer_size, None
        )
        
        if result > 0:
            message = buffer.value.rstrip()
            return f"Error {error_code} (0x{error_code:08X}): {message}"
        else:
            return f"Error {error_code} (0x{error_code:08X}): Unknown error"
    
    @contextmanager
    def publisher_metadata_context(self, publisher_name: str):
        """Context manager for publisher metadata handle"""
        handle = self._wevtapi.EvtOpenPublisherMetadata(
            None, ctypes.c_wchar_p(publisher_name), None, 0, 0
        )
        
        if not handle:
            error_code = self._kernel32.GetLastError()
            # Just propagate the raw error - let the caller add context
            raise EventProviderError(error_code)
        
        try:
            yield handle
        finally:
            self._wevtapi.EvtClose(handle)


class Event:
    """Represents a single event with its metadata and properties"""
    
    def __init__(self, provider: 'Provider'):
        self.provider = provider
        self.event_id: Optional[int] = None
        self.version: Optional[int] = None
        self.channel_id: Optional[int] = None
        self.level_value: Optional[int] = None
        self.opcode_value: Optional[int] = None
        self.task_value: Optional[int] = None
        self.keyword_mask: Optional[int] = None
        self.message_id: Optional[int] = None
        self.template: Optional[str] = None
        
        # Resolved names
        self._channel_name: Optional[str] = None
        self._level_name: Optional[str] = None
        self._opcode_name: Optional[str] = None
        self._task_name: Optional[str] = None
        self._keyword_names: Optional[str] = None
        self._message: Optional[str] = None
    
    @property
    def channel_name(self) -> Optional[str]:
        """Get the channel name for this event"""
        if self._channel_name is None and self.channel_id is not None:
            channel = self.provider.get_channel_by_id(self.channel_id)
            self._channel_name = channel.name if channel else f"Channel_{self.channel_id}"
        return self._channel_name
    
    @property
    def level_name(self) -> Optional[str]:
        """Get the level name for this event"""
        if self._level_name is None and self.level_value is not None:
            level = self.provider.get_level_by_value(self.level_value)
            self._level_name = level.name if level else f"Level_{self.level_value}"
        return self._level_name
    
    @property
    def task_name(self) -> Optional[str]:
        """Get the task name for this event"""
        if self._task_name is None and self.task_value is not None:
            task = self.provider.get_task_by_value(self.task_value)
            self._task_name = task.name if task else f"Task_{self.task_value}"
        return self._task_name
    
    @property
    def opcode_name(self) -> Optional[str]:
        """Get the opcode name for this event"""
        if self._opcode_name is None and self.opcode_value is not None:
            opcode = self.provider.get_opcode_by_value(self.opcode_value, self.task_value or 0)
            self._opcode_name = opcode.name if opcode else f"Opcode_{self.opcode_value}"
        return self._opcode_name
    
    @property
    def keyword_names(self) -> Optional[str]:
        """Get the keyword names for this event"""
        if self._keyword_names is None and self.keyword_mask is not None:
            names = []
            for keyword in self.provider.keywords:
                if self.keyword_mask & keyword.mask:
                    names.append(keyword.name)
            self._keyword_names = " ".join(names) if names else None
        return self._keyword_names
    
    @property
    def message(self) -> Optional[str]:
        """Get the formatted message for this event"""
        if self._message is None and self.message_id is not None and self.message_id != 0xFFFFFFFF:
            self._message = self.provider._format_message(self.message_id)
        return self._message
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary for JSON serialization"""
        return {
            'event_id': self.event_id,
            'version': self.version,
            'channel': {
                'id': self.channel_id,
                'name': self.channel_name
            },
            'level': {
                'value': self.level_value,
                'name': self.level_name
            },
            'task': {
                'value': self.task_value,
                'name': self.task_name
            },
            'opcode': {
                'value': self.opcode_value,
                'name': self.opcode_name
            },
            'keywords': {
                'mask': self.keyword_mask,
                'names': self.keyword_names
            },
            'message': self.message,
            'template': self.template
        }
    
    def __str__(self) -> str:
        return f"Event {self.event_id} (v{self.version}): {self.message or '(no message)'}"
    
    def __repr__(self) -> str:
        return f"Event(id={self.event_id}, version={self.version}, channel={self.channel_name})"


class Provider:
    """Represents an event provider with all its metadata"""
    
    def __init__(self, name: str):
        self.name = name
        self.api = WindowsEventAPI()
        
        # Provider properties
        self.guid: Optional[str] = None
        self.resource_file_path: Optional[str] = None
        self.parameter_file_path: Optional[str] = None
        self.message_file_path: Optional[str] = None
        self.help_link: Optional[str] = None
        self.publisher_message: Optional[str] = None
        
        # Metadata collections
        self.channels: List[ChannelInfo] = []
        self.levels: List[LevelInfo] = []
        self.tasks: List[TaskInfo] = []
        self.opcodes: List[OpcodeInfo] = []
        self.keywords: List[KeywordInfo] = []
        self.events: List[Event] = []
        
        # Private handle for message formatting
        self._metadata_handle: Optional[HANDLE] = None
    
    def load_metadata(self) -> None:
        """Load all metadata for this provider"""
        logger.info(f"Loading metadata for provider: {self.name}")
        
        try:
            with self.api.publisher_metadata_context(self.name) as handle:
                self._metadata_handle = handle
                
                try:
                    self._load_provider_properties(handle)
                    self._load_channels(handle)
                    self._load_levels(handle)
                    self._load_tasks(handle)
                    self._load_opcodes(handle)
                    self._load_keywords(handle)
                    self._load_events(handle)
                    
                    logger.info(f"Loaded metadata: {len(self.channels)} channels, "
                               f"{len(self.levels)} levels, {len(self.tasks)} tasks, "
                               f"{len(self.opcodes)} opcodes, {len(self.keywords)} keywords, "
                               f"{len(self.events)} events")
                               
                finally:
                    self._metadata_handle = None
        except EventProviderError as e:
            # If we have an error code, enhance the error message with registry data
            if isinstance(e.args[0], int):
                error_code = e.args[0]
                error_message = self.api.format_error_message(error_code)
                
                # Try to get registry data to provide more context
                registry_info = self._get_registry_info()
                if registry_info:
                    enhanced_message = (
                        f"Failed to open publisher metadata for '{self.name}': {error_message}"
                    )
                    if error_code == WindowsError.ERROR_FILE_NOT_FOUND:
                        if registry_info.resource_file_path:
                            enhanced_message += f"\nResource file path: {registry_info.resource_file_path}"
                        if registry_info.message_file_path:
                            enhanced_message += f"\nMessage file path: {registry_info.message_file_path}"
                    raise EventProviderError(enhanced_message)
                else:
                    raise EventProviderError(
                        f"Failed to open publisher metadata for '{self.name}': {error_message}"
                    )
            else:
                # Re-raise if not an error code
                raise
    
    def _load_provider_properties(self, handle: HANDLE) -> None:
        """Load basic provider properties"""
        logger.info("Loading provider properties...")
        
        # GUID
        variant = self._get_property(handle, EvtPublisherMetadataPropertyId.EvtPublisherMetadataPublisherGuid)
        if variant and variant.value.GuidVal:
            self.guid = self._guid_to_string(variant.value.GuidVal.contents)
            logger.info(f"Provider GUID: {self.guid}")
        
        # File paths
        for prop_id, attr_name, desc in [
            (EvtPublisherMetadataPropertyId.EvtPublisherMetadataResourceFilePath, 'resource_file_path', 'Resource file'),
            (EvtPublisherMetadataPropertyId.EvtPublisherMetadataParameterFilePath, 'parameter_file_path', 'Parameter file'),
            (EvtPublisherMetadataPropertyId.EvtPublisherMetadataMessageFilePath, 'message_file_path', 'Message file'),
            (EvtPublisherMetadataPropertyId.EvtPublisherMetadataHelpLink, 'help_link', 'Help link'),
        ]:
            variant = self._get_property(handle, prop_id)
            if variant and variant.value.StringVal:
                value = variant.value.StringVal
                setattr(self, attr_name, value)
                logger.info(f"{desc}: {value}")
        
        # Publisher message
        variant = self._get_property(handle, EvtPublisherMetadataPropertyId.EvtPublisherMetadataPublisherMessageID)
        if variant and variant.value.UInt32Val != 0xFFFFFFFF:
            self.publisher_message = self._format_message(variant.value.UInt32Val)
            logger.info(f"Publisher message: {self.publisher_message}")
    
    def _load_channels(self, handle: HANDLE) -> None:
        """Load channel information"""
        logger.info("Loading channels...")
        
        variant = self._get_property(handle, EvtPublisherMetadataPropertyId.EvtPublisherMetadataChannelReferences)
        if not variant or not variant.value.EvtHandleVal:
            return
        
        array_handle = variant.value.EvtHandleVal
        try:
            array_size = self._get_array_size(array_handle)
            if array_size is None:
                return
            
            for i in range(array_size):
                channel = self._load_channel_info(array_handle, i)
                if channel:
                    self.channels.append(channel)
                    logger.info(f"  Channel: {channel.name} (ID: {channel.id})")
        finally:
            self.api._wevtapi.EvtClose(array_handle)
    
    def _load_channel_info(self, array_handle: HANDLE, index: int) -> Optional[ChannelInfo]:
        """Load information for a specific channel"""
        try:
            # Get channel ID
            variant = self._get_array_property(array_handle, index, 
                                             EvtPublisherMetadataPropertyId.EvtPublisherMetadataChannelReferenceID)
            if not variant:
                return None
            channel_id = variant.value.UInt32Val
            
            # Get channel path
            variant = self._get_array_property(array_handle, index,
                                             EvtPublisherMetadataPropertyId.EvtPublisherMetadataChannelReferencePath)
            channel_path = variant.value.StringVal if variant and variant.value.StringVal else f"Channel_{channel_id}"
            
            # Get channel index
            variant = self._get_array_property(array_handle, index,
                                             EvtPublisherMetadataPropertyId.EvtPublisherMetadataChannelReferenceIndex)
            channel_index = variant.value.UInt32Val if variant else 0
            
            # Get channel flags
            variant = self._get_array_property(array_handle, index,
                                             EvtPublisherMetadataPropertyId.EvtPublisherMetadataChannelReferenceFlags)
            is_imported = bool(variant.value.UInt32Val & 0x1) if variant else False
            
            # Get channel message
            variant = self._get_array_property(array_handle, index,
                                             EvtPublisherMetadataPropertyId.EvtPublisherMetadataChannelReferenceMessageID)
            message = None
            if variant and variant.value.UInt32Val != 0xFFFFFFFF:
                message = self._format_message(variant.value.UInt32Val)
            
            return ChannelInfo(
                id=channel_id,
                name=message or channel_path,
                path=channel_path,
                index=channel_index,
                is_imported=is_imported,
                message=message
            )
        except Exception as e:
            logger.error(f"Error loading channel info at index {index}: {e}")
            return None
    
    def _load_levels(self, handle: HANDLE) -> None:
        """Load level information"""
        logger.info("Loading levels...")
        self._load_metadata_array(
            handle, 
            EvtPublisherMetadataPropertyId.EvtPublisherMetadataLevels,
            self._load_level_info,
            self.levels,
            "levels"
        )
    
    def _load_level_info(self, array_handle: HANDLE, index: int) -> Optional[LevelInfo]:
        """Load information for a specific level"""
        try:
            # Get level value
            variant = self._get_array_property(array_handle, index,
                                             EvtPublisherMetadataPropertyId.EvtPublisherMetadataLevelValue)
            if not variant:
                return None
            level_value = variant.value.UInt32Val
            
            # Get level name
            variant = self._get_array_property(array_handle, index,
                                             EvtPublisherMetadataPropertyId.EvtPublisherMetadataLevelName)
            level_name = variant.value.StringVal if variant and variant.value.StringVal else f"Level_{level_value}"
            
            # Get level message
            variant = self._get_array_property(array_handle, index,
                                             EvtPublisherMetadataPropertyId.EvtPublisherMetadataLevelMessageID)
            message = None
            if variant and variant.value.UInt32Val != 0xFFFFFFFF:
                message = self._format_message(variant.value.UInt32Val)
            
            return LevelInfo(
                value=level_value,
                name=message or level_name,
                message=message
            )
        except Exception as e:
            logger.error(f"Error loading level info at index {index}: {e}")
            return None
    
    def _load_tasks(self, handle: HANDLE) -> None:
        """Load task information"""
        logger.info("Loading tasks...")
        self._load_metadata_array(
            handle,
            EvtPublisherMetadataPropertyId.EvtPublisherMetadataTasks,
            self._load_task_info,
            self.tasks,
            "tasks"
        )
    
    def _load_task_info(self, array_handle: HANDLE, index: int) -> Optional[TaskInfo]:
        """Load information for a specific task"""
        try:
            # Get task value
            variant = self._get_array_property(array_handle, index,
                                             EvtPublisherMetadataPropertyId.EvtPublisherMetadataTaskValue)
            if not variant:
                return None
            task_value = variant.value.UInt32Val
            
            # Get task name
            variant = self._get_array_property(array_handle, index,
                                             EvtPublisherMetadataPropertyId.EvtPublisherMetadataTaskName)
            task_name = variant.value.StringVal if variant and variant.value.StringVal else f"Task_{task_value}"
            
            # Get task GUID
            variant = self._get_array_property(array_handle, index,
                                             EvtPublisherMetadataPropertyId.EvtPublisherMetadataTaskEventGuid)
            event_guid = None
            if variant and variant.value.GuidVal:
                event_guid = self._guid_to_string(variant.value.GuidVal.contents)
                if event_guid == "{00000000-0000-0000-0000-000000000000}":
                    event_guid = None
            
            # Get task message
            variant = self._get_array_property(array_handle, index,
                                             EvtPublisherMetadataPropertyId.EvtPublisherMetadataTaskMessageID)
            message = None
            if variant and variant.value.UInt32Val != 0xFFFFFFFF:
                message = self._format_message(variant.value.UInt32Val)
            
            return TaskInfo(
                value=task_value,
                name=message or task_name,
                event_guid=event_guid,
                message=message
            )
        except Exception as e:
            logger.error(f"Error loading task info at index {index}: {e}")
            return None
    
    def _load_opcodes(self, handle: HANDLE) -> None:
        """Load opcode information"""
        logger.info("Loading opcodes...")
        self._load_metadata_array(
            handle,
            EvtPublisherMetadataPropertyId.EvtPublisherMetadataOpcodes,
            self._load_opcode_info,
            self.opcodes,
            "opcodes"
        )
    
    def _load_opcode_info(self, array_handle: HANDLE, index: int) -> Optional[OpcodeInfo]:
        """Load information for a specific opcode"""
        try:
            # Get opcode value
            variant = self._get_array_property(array_handle, index,
                                             EvtPublisherMetadataPropertyId.EvtPublisherMetadataOpcodeValue)
            if not variant:
                return None
            full_value = variant.value.UInt32Val
            
            # Extract task and opcode values
            task_value = full_value & 0xFFFF
            opcode_value = (full_value >> 16) & 0xFFFF
            
            # Get opcode name
            variant = self._get_array_property(array_handle, index,
                                             EvtPublisherMetadataPropertyId.EvtPublisherMetadataOpcodeName)
            opcode_name = variant.value.StringVal if variant and variant.value.StringVal else f"Opcode_{opcode_value}"
            
            # Get opcode message
            variant = self._get_array_property(array_handle, index,
                                             EvtPublisherMetadataPropertyId.EvtPublisherMetadataOpcodeMessageID)
            message = None
            if variant and variant.value.UInt32Val != 0xFFFFFFFF:
                message = self._format_message(variant.value.UInt32Val)
            
            return OpcodeInfo(
                value=full_value,
                name=message or opcode_name,
                task_value=task_value,
                opcode_value=opcode_value,
                message=message
            )
        except Exception as e:
            logger.error(f"Error loading opcode info at index {index}: {e}")
            return None
    
    def _load_keywords(self, handle: HANDLE) -> None:
        """Load keyword information"""
        logger.info("Loading keywords...")
        self._load_metadata_array(
            handle,
            EvtPublisherMetadataPropertyId.EvtPublisherMetadataKeywords,
            self._load_keyword_info,
            self.keywords,
            "keywords"
        )
    
    def _load_keyword_info(self, array_handle: HANDLE, index: int) -> Optional[KeywordInfo]:
        """Load information for a specific keyword"""
        try:
            # Get keyword mask
            variant = self._get_array_property(array_handle, index,
                                             EvtPublisherMetadataPropertyId.EvtPublisherMetadataKeywordValue)
            if not variant:
                return None
            keyword_mask = variant.value.UInt64Val
            
            # Get keyword name
            variant = self._get_array_property(array_handle, index,
                                             EvtPublisherMetadataPropertyId.EvtPublisherMetadataKeywordName)
            keyword_name = variant.value.StringVal if variant and variant.value.StringVal else f"Keyword_{keyword_mask:X}"
            
            # Get keyword message
            variant = self._get_array_property(array_handle, index,
                                             EvtPublisherMetadataPropertyId.EvtPublisherMetadataKeywordMessageID)
            message = None
            if variant and variant.value.UInt32Val != 0xFFFFFFFF:
                message = self._format_message(variant.value.UInt32Val)
            
            return KeywordInfo(
                mask=keyword_mask,
                name=message or keyword_name,
                message=message
            )
        except Exception as e:
            logger.error(f"Error loading keyword info at index {index}: {e}")
            return None
    
    def _load_events(self, handle: HANDLE) -> None:
        """Load all events for this provider"""
        logger.info("Loading events...")
        
        events_handle = self.api._wevtapi.EvtOpenEventMetadataEnum(handle, 0)
        if not events_handle:
            error_code = self.api._kernel32.GetLastError()
            error_message = self.api.format_error_message(error_code)
            logger.error(f": EvtOpenEventMetadataEnum: {error_message} [ {self.name} ]")
            return
        
        try:
            while True:
                event_handle = self.api._wevtapi.EvtNextEventMetadata(events_handle, 0)
                if not event_handle:
                    error_code = self.api._kernel32.GetLastError()
                    if error_code == WindowsError.ERROR_NO_MORE_ITEMS:
                        break
                    else:
                        error_message = self.api.format_error_message(error_code)
                        logger.error(f"Failed to get next event: {error_message}")
                        break
                
                try:
                    event = self._load_event_info(handle, event_handle)
                    if event:
                        self.events.append(event)
                finally:
                    self.api._wevtapi.EvtClose(event_handle)
        finally:
            self.api._wevtapi.EvtClose(events_handle)
            
        logger.info(f"Loaded {len(self.events)} events")
    
    def _load_event_info(self, event_handle: HANDLE) -> Optional[Event]:
        """Load information for a specific event"""
        try:
            event = Event(self)
            
            # Process all event properties
            for property_id in range(EvtEventMetadataPropertyId.EvtEventMetadataPropertyIdEND):
                variant = self._get_event_property(event_handle, property_id)
                if variant:
                    self._process_event_property(event, property_id, variant)
            
            return event
        except Exception as e:
            logger.error(f"Error loading event info: {e}")
            return None
    
    def _process_event_property(self, event: Event, property_id: int, variant: EvtVariant) -> None:
        """Process a single event property"""
        prop_id = EvtEventMetadataPropertyId(property_id)
        
        if prop_id == EvtEventMetadataPropertyId.EventMetadataEventID:
            event.event_id = variant.value.UInt32Val
        elif prop_id == EvtEventMetadataPropertyId.EventMetadataEventVersion:
            event.version = variant.value.UInt32Val
        elif prop_id == EvtEventMetadataPropertyId.EventMetadataEventChannel:
            event.channel_id = variant.value.UInt32Val if variant.value.UInt32Val > 0 else None
        elif prop_id == EvtEventMetadataPropertyId.EventMetadataEventLevel:
            event.level_value = variant.value.UInt32Val if variant.value.UInt32Val > 0 else None
        elif prop_id == EvtEventMetadataPropertyId.EventMetadataEventOpcode:
            event.opcode_value = variant.value.UInt32Val if variant.value.UInt32Val > 0 else None
        elif prop_id == EvtEventMetadataPropertyId.EventMetadataEventTask:
            event.task_value = variant.value.UInt32Val if variant.value.UInt32Val > 0 else None
        elif prop_id == EvtEventMetadataPropertyId.EventMetadataEventKeyword:
            # Filter reserved bits
            keyword_mask = variant.value.UInt64Val & 0x00FFFFFFFFFFFFFF
            event.keyword_mask = keyword_mask if keyword_mask > 0 else None
        elif prop_id == EvtEventMetadataPropertyId.EventMetadataEventMessageID:
            event.message_id = variant.value.UInt32Val if variant.value.UInt32Val != 0xFFFFFFFF else None
        elif prop_id == EvtEventMetadataPropertyId.EventMetadataEventTemplate:
            event.template = variant.value.StringVal if variant.value.StringVal else None
    
    # Helper methods for lookups
    def get_channel_by_id(self, channel_id: int) -> Optional[ChannelInfo]:
        """Get channel info by ID"""
        return next((c for c in self.channels if c.id == channel_id), None)
    
    def get_level_by_value(self, level_value: int) -> Optional[LevelInfo]:
        """Get level info by value"""
        return next((l for l in self.levels if l.value == level_value), None)
    
    def get_task_by_value(self, task_value: int) -> Optional[TaskInfo]:
        """Get task info by value"""
        return next((t for t in self.tasks if t.value == task_value), None)
    
    def get_opcode_by_value(self, opcode_value: int, task_value: int) -> Optional[OpcodeInfo]:
        """Get opcode info by value, considering task-specific opcodes"""
        opcode_high = (opcode_value >> 16) & 0xFFFF
        
        # First look for task-specific opcode
        for opcode in self.opcodes:
            if opcode.opcode_value == opcode_high and opcode.task_value == task_value:
                return opcode
        
        # Fall back to global opcode (task_value = 0)
        for opcode in self.opcodes:
            if opcode.opcode_value == opcode_high and opcode.task_value == 0:
                return opcode
        
        return None
    
    # Utility methods
    def _load_metadata_array(self, handle: HANDLE, property_id: EvtPublisherMetadataPropertyId, 
                            loader_func, target_list: List, description: str) -> None:
        """Generic method to load metadata arrays"""
        variant = self._get_property(handle, property_id)
        if not variant or not variant.value.EvtHandleVal:
            return
        
        array_handle = variant.value.EvtHandleVal
        try:
            array_size = self._get_array_size(array_handle)
            if array_size is None:
                return
            
            for i in range(array_size):
                item = loader_func(array_handle, i)
                if item:
                    target_list.append(item)
        finally:
            self.api._wevtapi.EvtClose(array_handle)
    
    def _get_property(self, handle: HANDLE, property_id: EvtPublisherMetadataPropertyId) -> Optional[EvtVariant]:
        """Get a publisher metadata property"""
        buffer_size = DWORD(0)
        buffer_used = DWORD(0)
        
        # First call to get required buffer size
        result = self.api._wevtapi.EvtGetPublisherMetadataProperty(
            handle, property_id, 0, 0, None, ctypes.byref(buffer_used)
        )
        
        if not result:
            error_code = self.api._kernel32.GetLastError()
            if error_code != WindowsError.ERROR_INSUFFICIENT_BUFFER:
                logger.error(f"{self.name}: EvtGetPublisherMetadataProperty failed to get property '{EvtPublisherMetadataPropertyId(property_id).name}': {WindowsEventAPI.format_error_message(error_code)}")
                return None
            buffer_size = buffer_used
        
        if buffer_size.value == 0:
            buffer_size = DWORD(ctypes.sizeof(EvtVariant))
            
        property_buffer = (ctypes.c_byte * buffer_size.value)()
        evt_variant = ctypes.cast(property_buffer, ctypes.POINTER(EvtVariant)).contents
        
        result = self.api._wevtapi.EvtGetPublisherMetadataProperty(
            handle, property_id, 0, buffer_size, 
            ctypes.byref(evt_variant), ctypes.byref(buffer_used)
        )
        
        return evt_variant if result else None
    
    def _get_array_size(self, array_handle: HANDLE) -> Optional[int]:
        """Get the size of an object array"""
        array_size = DWORD(0)
        result = self.api._wevtapi.EvtGetObjectArraySize(array_handle, ctypes.byref(array_size))
        return array_size.value if result else None
    
    def _get_array_property(self, array_handle: HANDLE, index: int, property_id: EvtPublisherMetadataPropertyId) -> Optional[EvtVariant]:
        """Get a property from an object array"""
        buffer_size = DWORD(0)
        buffer_used = DWORD(0)
        
        # First call to get required buffer size
        result = self.api._wevtapi.EvtGetObjectArrayProperty(
            array_handle, property_id, index, 0, 0, None, ctypes.byref(buffer_used)
        )
        
        if not result:
            error_code = self.api._kernel32.GetLastError()
            if error_code != WindowsError.ERROR_INSUFFICIENT_BUFFER:
                return None
            buffer_size = buffer_used
        
        if buffer_size.value == 0:
            buffer_size = DWORD(ctypes.sizeof(EvtVariant))
            
        property_buffer = (ctypes.c_byte * buffer_size.value)()
        evt_variant = ctypes.cast(property_buffer, ctypes.POINTER(EvtVariant)).contents
        
        result = self.api._wevtapi.EvtGetObjectArrayProperty(
            array_handle, property_id, index, 0, buffer_size,
            ctypes.byref(evt_variant), ctypes.byref(buffer_used)
        )
        
        return evt_variant if result else None
    
    def _get_event_property(self, event_handle: HANDLE, property_id: EvtEventMetadataPropertyId) -> Optional[EvtVariant]:
        """Get an event metadata property"""
        buffer_size = DWORD(0)
        buffer_used = DWORD(0)
        
        # First call to get required buffer size
        result = self.api._wevtapi.EvtGetEventMetadataProperty(
            event_handle, property_id, 0, 0, None, ctypes.byref(buffer_used)
        )
        
        if not result:
            error_code = self.api._kernel32.GetLastError()
            if error_code != WindowsError.ERROR_INSUFFICIENT_BUFFER:
                return None
            buffer_size = buffer_used
        
        if buffer_size.value == 0:
            buffer_size = DWORD(ctypes.sizeof(EvtVariant))
            
        property_buffer = (ctypes.c_byte * buffer_size.value)()
        evt_variant = ctypes.cast(property_buffer, ctypes.POINTER(EvtVariant)).contents
        
        result = self.api._wevtapi.EvtGetEventMetadataProperty(
            event_handle, property_id, 0, buffer_size,
            ctypes.byref(evt_variant), ctypes.byref(buffer_used)
        )
        
        return evt_variant if result else None
    
    def _format_message(self, message_id: int) -> Optional[str]:
        """Format a message string using EvtFormatMessage"""
        if not self._metadata_handle:
            return None
            
        buffer_size = DWORD(0)
        buffer_used = DWORD(0)
        
        # First call to get required buffer size
        result = self.api._wevtapi.EvtFormatMessage(
            self._metadata_handle, None, message_id, 0, None,
            EvtFormatMessageFlags.EvtFormatMessageId, 0, None, ctypes.byref(buffer_used)
        )
        
        if not result:
            error_code = self.api._kernel32.GetLastError()
            if error_code != WindowsError.ERROR_INSUFFICIENT_BUFFER:
                return None
            buffer_size = buffer_used
        
        if buffer_size.value == 0:
            return ""
            
        buffer = ctypes.create_unicode_buffer(buffer_size.value)
        
        result = self.api._wevtapi.EvtFormatMessage(
            self._metadata_handle, None, message_id, 0, None,
            EvtFormatMessageFlags.EvtFormatMessageId, buffer_size, buffer, ctypes.byref(buffer_used)
        )
        
        return buffer.value if result else None
    
    def _guid_to_string(self, guid_bytes: ctypes.Array) -> str:
        """Convert GUID bytes to string"""
        buffer = ctypes.create_unicode_buffer(50)
        result = self.api._ole32.StringFromGUID2(
            ctypes.cast(guid_bytes, ctypes.POINTER(ctypes.c_byte * 16)),
            buffer, 50
        )
        return buffer.value if result > 0 else ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert provider to dictionary for JSON serialization"""
        return {
            'name': self.name,
            'guid': self.guid,
            'resource_file_path': self.resource_file_path,
            'parameter_file_path': self.parameter_file_path,
            'message_file_path': self.message_file_path,
            'help_link': self.help_link,
            'publisher_message': self.publisher_message,
            'channels': [
                {
                    'id': ch.id,
                    'name': ch.name,
                    'path': ch.path,
                    'index': ch.index,
                    'is_imported': ch.is_imported,
                    'message': ch.message
                } for ch in self.channels
            ],
            'levels': [
                {
                    'value': lv.value,
                    'name': lv.name,
                    'message': lv.message
                } for lv in self.levels
            ],
            'tasks': [
                {
                    'value': tk.value,
                    'name': tk.name,
                    'event_guid': tk.event_guid,
                    'message': tk.message
                } for tk in self.tasks
            ],
            'opcodes': [
                {
                    'value': op.value,
                    'name': op.name,
                    'task_value': op.task_value,
                    'opcode_value': op.opcode_value,
                    'message': op.message
                } for op in self.opcodes
            ],
            'keywords': [
                {
                    'mask': kw.mask,
                    'name': kw.name,
                    'message': kw.message
                } for kw in self.keywords
            ],
            'events': [event.to_dict() for event in self.events]
        }
    
    def __str__(self) -> str:
        return f"Provider '{self.name}' ({len(self.events)} events)"
    
    def _get_registry_info(self) -> Optional[ProviderRegistryData]:
        """Get registry information for this provider"""
        try:
            registry = ProviderRegistry()
            return registry.get_by_name(self.name)
        except Exception:
            return None
    
    def __repr__(self) -> str:
        return f"Provider(name='{self.name}', events={len(self.events)})"


def main():
    """
    Example usage of the Provider class and ProviderRegistry.
    
    Enhanced object-oriented design with comprehensive Windows error message formatting.
    """
    try:
        # Example 1: Use ProviderRegistry to lookup providers
        print("Loading provider registry...")
        registry = ProviderRegistry()
        print(f"Found {len(registry)} providers in registry\n")
        
        # Lookup by name
        # provider_name = "Microsoft-Windows-Security-Auditing"
        # provider_name = ".NET Runtime"
        provider_name = 'Microsoft-Windows-AllJoyn'
        reg_data = registry.get_by_name(provider_name)
        if reg_data:
            print(f"Provider found by name: {reg_data.name}")
            print(f"  GUID: {reg_data.guid}")
            print(f"  Enabled: {reg_data.enabled}")
            print(f"  Message file: {reg_data.message_file_path}")
            
        # Lookup by GUID
        test_guid = "{54849625-5478-4994-A5BA-3E3B0328C30D}"
        reg_data = registry.get_by_guid(test_guid)
        if reg_data:
            print(f"\nProvider found by GUID: {reg_data.guid}")
            print(f"  Name: {reg_data.name}")
            print(f"  Enabled: {reg_data.enabled}")
            
        # Show first 10 provider names
        print(f"\nFirst 10 providers:")
        for name in registry.get_provider_names()[:10]:
            print(f"  - {name}")
        
        # Example 2: Load detailed metadata for a specific provider
        print(f"\n{'='*60}")
        print("Loading detailed metadata for a provider...")
        provider = Provider(provider_name)
        provider.load_metadata()
        
        # Display summary
        print(f"\n{provider}")
        print(f"GUID: {provider.guid}")
        print(f"Channels: {len(provider.channels)}")
        print(f"Levels: {len(provider.levels)}")
        print(f"Tasks: {len(provider.tasks)}")
        print(f"Opcodes: {len(provider.opcodes)}")
        print(f"Keywords: {len(provider.keywords)}")
        print(f"Events: {len(provider.events)}")
        
        # Show some example events
        print(f"\nFirst 5 events:")
        for event in provider.events[:5]:
            print(f"  {event}")
            print(f"    Channel: {event.channel_name}")
            print(f"    Level: {event.level_name}")
            print(f"    Task: {event.task_name}")
        
        # Convert to JSON for full export
        json_output = json.dumps(provider.to_dict(), indent=2)
        print(f"\nJSON export size: {len(json_output)} characters")
        
    except EventProviderError as e:
        logger.error(f"Provider error: {e}")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return 1
    
    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main() or 0)