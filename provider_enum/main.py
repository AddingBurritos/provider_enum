import ctypes
import sys
from ctypes.wintypes import HANDLE, DWORD, LPWSTR, ULONG

# Define necessary Windows API constants
EvtFormatMessageEvent = 1
EvtFormatMessageLevel = 2
EvtFormatMessageTask = 3
EvtFormatMessageOpcode = 4
EvtFormatMessageKeyword = 5
EvtFormatMessageChannel = 6
EvtFormatMessageProvider = 7
EvtFormatMessageId = 8

def get_event_publisher_metadata(event_source):
    EvtOpenPublisherMetadata = ctypes.windll.wevtapi.EvtOpenPublisherMetadata
    EvtOpenPublisherMetadata.restype = HANDLE

    metadata = EvtOpenPublisherMetadata(None, event_source, None, 0, 0)
    if not metadata:
        print(f"Unable to open publisher metadata for event source '{event_source}'. Error code: {ctypes.windll.kernel32.GetLastError()}")
        sys.exit(1)

    return metadata

def get_event_description(metadata, event_id):
    EvtFormatMessage = ctypes.windll.wevtapi.EvtFormatMessage
    EvtFormatMessage.restype = DWORD

    buffer = ctypes.create_unicode_buffer(0)
    buffer_size = ULONG(0)

    # First call to get the required buffer size
    result = EvtFormatMessage(metadata, None, event_id, 0, None, EvtFormatMessageEvent, 0, buffer, ctypes.byref(buffer_size))
    if ctypes.windll.kernel32.GetLastError() != 122:  # ERROR_INSUFFICIENT_BUFFER
        print(f"Unable to format message for event ID {event_id}. Error code: {ctypes.windll.kernel32.GetLastError()}")
        sys.exit(1)

    buffer = ctypes.create_unicode_buffer(buffer_size.value)
    result = EvtFormatMessage(metadata, None, event_id, 0, None, EvtFormatMessageEvent, buffer_size.value, buffer, ctypes.byref(buffer_size))
    if not result:
        print(f"Unable to format message for event ID {event_id}. Error code: {ctypes.windll.kernel32.GetLastError()}")
        sys.exit(1)

    return buffer.value

if __name__ == '__main__':
    event_source = 'Microsoft-Windows-Security-Auditing'  # Replace with your event source
    event_id = 4624  # Replace with your event ID

    metadata = get_event_publisher_metadata(event_source)
    event_message = get_event_description(metadata, event_id)
    print(f"Event message for event ID {event_id} from source '{event_source}':")
    print(event_message)
