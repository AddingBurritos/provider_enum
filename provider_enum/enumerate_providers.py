import ctypes
from ctypes.wintypes import HANDLE, DWORD, ULONG
import sys

# Define necessary Windows API constants
ERROR_INSUFFICIENT_BUFFER = 122
ERROR_NO_MORE_ITEMS = 259

def enumerate_event_providers():
    EvtOpenPublisherEnum = ctypes.windll.wevtapi.EvtOpenPublisherEnum
    EvtOpenPublisherEnum.restype = HANDLE

    EvtNextPublisherId = ctypes.windll.wevtapi.EvtNextPublisherId
    EvtNextPublisherId.restype = DWORD

    EvtClose = ctypes.windll.wevtapi.EvtClose

    publisher_enum_handle = EvtOpenPublisherEnum(None, 0)
    if not publisher_enum_handle:
        print(f"Unable to open publisher enumeration. Error code: {ctypes.windll.kernel32.GetLastError()}")
        sys.exit(1)

    publishers = []
    buffer = ctypes.create_unicode_buffer(0)
    buffer_size = ULONG(0)

    while True:
        # First call to get the required buffer size
        result = EvtNextPublisherId(publisher_enum_handle, buffer_size.value, buffer, ctypes.byref(buffer_size))
        error_code = ctypes.windll.kernel32.GetLastError()

        if error_code == ERROR_INSUFFICIENT_BUFFER:
            buffer = ctypes.create_unicode_buffer(buffer_size.value)
            result = EvtNextPublisherId(publisher_enum_handle, buffer_size.value, buffer, ctypes.byref(buffer_size))
            error_code = ctypes.windll.kernel32.GetLastError()

        if error_code == ERROR_NO_MORE_ITEMS:
            break

        if not result:
            print(f"Unable to enumerate publishers. Error code: {error_code}")
            sys.exit(1)

        publishers.append(buffer.value)

    EvtClose(publisher_enum_handle)
    return publishers

if __name__ == '__main__':
    event_providers = enumerate_event_providers()
    print("Registered event providers on this machine:")
    for provider in event_providers:
        print(provider)
