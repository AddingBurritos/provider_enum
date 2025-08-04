#!/usr/bin/env python3
"""
Windows Legacy Event Provider Registry Parser

Parses Windows registry to extract configuration information for legacy
event providers (Event Log API providers, not ETW providers).

Requires: Windows system with appropriate registry access
"""

import winreg
import json
import sys
import os
from typing import Dict, List, Optional, Tuple, Annotated, Any
from dataclasses import dataclass, asdict
from pathlib import Path
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from pydantic.alias_generators import to_pascal
from uuid import  UUID


class EventSource(BaseModel):
    """Represents a legacy event source configuration"""
    name: str
    category_name: str
    category_count: Optional[int] = None
    """Number of event categories supported. This value is of type REG_DWORD."""
    category_message_file: Optional[Path] = None
    """Path to the category message file. A category message file contains language-dependent strings that describe the categories. This value can be of type REG_SZ or REG_EXPAND_SZ."""
    event_message_file: Optional[Path] = None
    """Path to one or more event message files; use a semicolon to delimit multiple files. An event message file contains language-dependent strings that describe the events. This value can be of type REG_SZ or REG_EXPAND_SZ."""
    parameter_message_file: Optional[Path] = None
    """Path to the parameter message file. A parameter message file contains language-independent strings that are to be inserted into the event description strings. This value can be of type REG_SZ or REG_EXPAND_SZ."""
    types_supported: List[str] = []
    """Bitmask of supported types. This value is of type REG_DWORD. It can be one or more of the following values:\n
        EVENTLOG_AUDIT_FAILURE (0x0010)\n
        EVENTLOG_AUDIT_SUCCESS (0x0008)\n
        EVENTLOG_ERROR_TYPE (0x0001)\n
        EVENTLOG_INFORMATION_TYPE (0x0004)\n
        EVENTLOG_WARNING_TYPE (0x0002)"""
    provider_guid: UUID | None = None
    model_config = ConfigDict(validate_by_name=True, use_attribute_docstrings=True, alias_generator=to_pascal)
    
    @model_validator(mode="before")
    @classmethod
    def get_reg(cls, data: Dict) -> Dict:
        category_name = data.get("category_name")
        source_name = data.get("name")

        EVENTLOG_BASE_KEY = "SYSTEM\\CurrentControlSet\\Services\\EventLog"

        """Parse configuration for an event log category"""
        source = dict(Name=source_name, CategoryName=category_name)
        
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, f"{EVENTLOG_BASE_KEY}\\{category_name}\\{source_name}") as source_key:

                try:
                    i = 0
                    while True:
                        try:
                            value_name, value_data, _data_type = winreg.EnumValue(source_key, i)
                            source[value_name] = value_data
                            i += 1

                        except OSError:
                            break
                except Exception as e:
                    print(f"Error enumerating EventSource values for {category_name}\\{source_name}: {e}")
        except Exception as e:
            print(f"Error parsing EventSource {category_name}\\{source_name}: {e}")
        
        return source

    @field_validator('types_supported', mode="before")
    def lookup_supported_types_enum(types_value: int | str) -> List[str]:
        if isinstance(types_value, str):
            print(types_value)
            types_value = int(types_value, 16)
        EVENT_TYPES = {
            0x0001: "Error", 
            0x0002: "Warning",
            0x0004: "Information",
            0x0008: "Audit Success",
            0x0010: "Audit Failure"
        }
        supported_types = []
        for flag, name in EVENT_TYPES.items():
            if types_value & flag:
                supported_types.append(name)
        return supported_types
    
    @field_validator("category_message_file", "event_message_file", "parameter_message_file", mode="before")
    def expand_path_vars(v: str) -> str:
        return os.path.expandvars(v)


class EventLogCategory(BaseModel):
    """Represents an event log category (Application, System, etc.)"""
    name: str
    custom_sd: str | None = None
    """Restricts access to the event log. This value is of type REG_SZ. The format used is Security Descriptor Definition Language (SDDL). Construct an ACL that grants one or more of the following rights:\n
        Clear (0x0004)\n
        Read (0x0001)\n
        Write (0x0002)\n
        To be a syntactically valid SDDL, the CustomSD value must specify an owner and a group owner (for example, O:BAG:SY), but the owner and group owner are not used. If CustomSD is set to a wrong value, an event is fired in the System event log when the event log service starts, and the event log gets a default security descriptor which is identical to the original CustomSD value for the Application log. SACLs are not supported.\n
        For more information, see https://learn.microsoft.com/en-us/windows/win32/eventlog/event-logging-security.\n
        Windows Server 2003: SACLs are supported.\n
        Windows XP/2000: This value is not supported."""
    display_name_file: Path | None = None
    """This value is not used. Windows Server 2003 and Windows XP/2000: Name of the file that stores the localized name of the event log. The name stored in this file appears as the log name in Event Viewer. If this entry does not appear in the registry for an event log, Event Viewer displays the name of the registry subkey as the log name. This value is of type REG_EXPAND_SZ. The default value is %SystemRoot%\\system32\\els.dll."""
    display_name_id: int | None = None
    """This value is not used. Windows Server 2003 and Windows XP/2000: Message identification number of the log name string. This number indicates the message in which the localized display name appears. The message is stored in the file specified by the DisplayNameFile value. This value is of type REG_DWORD."""
    file: Path | None = None
    """Fully qualified path to the file where each event log is stored. This enables Event Viewer and other applications to find the log files. This value is of type REG_SZ or REG_EXPAND_SZ. This value is optional. If the value is not specified, it defaults to %SystemRoot%\\system32\\winevt\\logs\\ followed by a file name that is based on the event log registry key name.The specific event log file path should be set using the command line utility wevtutil.exe or by using the EvtSetChannelConfigProperty function with EvtChannelLoggingConfigLogFilePath passed into the PropertyId parameter.
        If a specific file is set, make sure that the event log service has full permissions on the file.\n
        This value needs to be a valid file name for a file that is located on a local directory (not a remote computer, not a DOS device, not a floppy, and not a pipe). If the file setting is wrong, an event is fired in the System event log when the event log service starts.\n
        Do not use environment variables, in the path to the file, that cannot be expanded in the context of the event log service.\n
        Windows Server 2003 and Windows XP/2000: This value defaults to %SystemRoot%\\system32\\config\\ followed by a file name that is based on the event log registry key name. If the File setting is set to an invalid value, the log will either not be initialized properly, or all requests will silently go to the default log (Application)."""
    max_size: Annotated[int, Field(default=2**20)]
    """Maximum size, in bytes, of the log file. This value is of type REG_DWORD. The value must be set to a multiple of 64K for a System, Application, or Security log. The default value is 1MB. Windows Server 2003 and Windows XP/2000: The value is limited to 0xFFFFFFFF, and the default value is 512K."""
    primary_module: str | None = None
    """This value is not used. Windows Server 2003 and Windows XP/2000: This value is the name of the subkey that contains the default values for the entries in the subkey for the event source. This value is of type REG_SZ."""
    retention: Annotated[int, Field(default=0)]
    """This value is of type REG_DWORD. The default value is 0. If this value is 0, the records of events are always overwritten. If this value is 0xFFFFFFFF or any nonzero value, records are never overwritten. When the log file reaches its maximum size, you must clear the log manually; otherwise, new events are discarded. You must also clear the log before you can change its size. Windows Server 2003 and Windows XP/2000: This value is the time interval, in seconds, that records of events are protected from being overwritten. When the age of an event reaches or exceeds this value, it can be overwritten."""
    sources: List[str] = []
    """This value is not used. Windows Server 2003 and Windows XP/2000: Names of the applications, services, or groups of applications that write events to this log. This value should only be read and not altered. The event log service maintains the list based on each program listed in a subkey under the log. This value is of type REG_MULTI_SZ."""
    auto_backup_log_files: Annotated[int, Field(default=0)]
    """This value is of type REG_DWORD, and is used by the event log service to determine whether an event log should be automatically saved. The default value is 0, which disables auto-backup. The service will back up the log file only if the retention value is -1 (0xFFFFFFFF). Other values will be ignored. Windows Server 2003: Retention can be set to -1 (0xFFFFFFFF) or 1 (0x00000001) for AutoBackupLogFiles to work. Other values will be ignored."""
    restrict_guest_access: int | None = None
    """This value is not used. Windows XP/2000: This value is of type REG_DWORD, and the default value is 1. When the value is set to 1, it restricts the Guest and Anonymous account access to the event log, and when this value is 0, it allows Guest account access to the event log."""
    isolation: Annotated[str, Field(default="Application")]
    """Defines the default access permissions for the log."""
    evt_sources: List[EventSource] = []
    """EventSource objects registered as subkeys to this category."""
    model_config = ConfigDict(validate_by_name=True, use_attribute_docstrings=True, alias_generator=to_pascal)
    
    @model_validator(mode="before")
    @classmethod
    def get_reg(cls, category_name: str) -> Dict:
        EVENTLOG_BASE_KEY = "SYSTEM\\CurrentControlSet\\Services\\EventLog"
        """Parse configuration for an event log category"""
        category = dict(Name=category_name, EvtSources=[])
        
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, f"{EVENTLOG_BASE_KEY}\\{category_name}") as category_key:

                try:
                    i = 0
                    while True:
                        try:
                            value_name, value_data, _data_type = winreg.EnumValue(category_key, i)
                            category[value_name] = value_data
                            i += 1

                        except OSError:
                            break
                except Exception as e:
                    print(f"Error enumerating EventLog values for category {category_name}: {e}")
                
                # Enumerate event sources (subkeys)
                try:
                    i = 0
                    while True:
                        try:
                            source_name = winreg.EnumKey(category_key, i)
                            source = EventSource(category_name=category_name, name=source_name)
                            category['EvtSources'].append(source)
                            i += 1
                        except OSError:
                            break
                            
                except Exception as e:
                    print(f"Error enumerating sources for category {category_name}: {e}")
        except PermissionError:
            # Re-raise PermissionError to let the caller handle it
            raise
        except Exception as e:
            print(f"Error parsing event category {category_name}: {e}")
        
        return category

    @field_validator('isolation', mode="before")
    def lookup_isolation_enum(v: Any) -> str:
        if isinstance(v, int):
            EVENT_LOG_ISOLATION = {
                0x00: "Application",
                0x01: "System",
                0x02: "Custom"
            }
            return EVENT_LOG_ISOLATION[v]
        return v
    
    @field_validator("display_name_file", "file", mode="before")
    def expand_path_vars(v: str) -> str:
        return os.path.expandvars(v)


class EventProviderParser:
    """Parser for Windows legacy event provider registry data"""
    
    EVENTLOG_BASE_KEY = "SYSTEM\\CurrentControlSet\\Services\\EventLog"
    
    def parse_all_providers(self) -> List[EventLogCategory]:
        """Parse all legacy event provider configurations"""
        self.categories = []
        skipped_categories = []
        
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, self.EVENTLOG_BASE_KEY) as eventlog_key:
                
                # Enumerate event log categories
                i = 0
                while True:
                    try:
                        category_name = winreg.EnumKey(eventlog_key, i)
                        try:
                            category = EventLogCategory.model_validate(category_name)
                            # print(category.model_dump_json(indent=4))
                            self.categories.append(category)
                        except PermissionError as e:
                            # Handle access denied for specific category
                            print(f"Access denied for category '{category_name}'. Skipping... (Error: {e})")
                            skipped_categories.append(category_name)
                        except Exception as e:
                            # Handle other errors for specific category
                            print(f"Error parsing category '{category_name}': {e}")
                            skipped_categories.append(category_name)
                        i += 1
                    except OSError:
                        break
                        
        except Exception as e:
            print(f"Error accessing EventLog registry key: {e}")
            return []
        
        if skipped_categories:
            print(f"Skipped {len(skipped_categories)} categories due to errors: {', '.join(skipped_categories)}")
        
        return self.categories
    


def main():
    """Main function to run the parser"""
    if sys.platform != "win32":
        print("This script requires Windows to access the registry.")
        sys.exit(1)
    
    parser = EventProviderParser()
    
    print("Parsing Windows legacy event provider registry data...")
    try:
        categories = parser.parse_all_providers()
        
        if not categories:
            print("No event log categories found or access denied.")
            sys.exit(1)
        
        print(f"Found {len(categories)} event log categories")

        # Display summary
        total_sources = sum(len(cat.evt_sources) for cat in categories)
        print(f"\nSummary:")
        print(f"  Categories: {len(categories)}")
        print(f"  Total Sources: {total_sources}")
    
    except PermissionError:
        print("Access denied. Run as administrator to access all registry keys.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()