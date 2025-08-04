import ctypes
from ctypes.wintypes import HANDLE, DWORD
from typing import List, Iterator, Optional
from contextlib import contextmanager
import logging
from dataclasses import dataclass
from enum import IntEnum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WindowsError(IntEnum):
    """Windows error codes used in event provider enumeration"""
    ERROR_INSUFFICIENT_BUFFER = 122
    ERROR_NO_MORE_ITEMS = 259


@dataclass
class EventProvider:
    """Represents a Windows event provider"""
    name: str
    
    def __str__(self) -> str:
        return self.name
    
    def __repr__(self) -> str:
        return f"EventProvider(name='{self.name}')"


class WindowsEventAPI:
    """Wrapper for Windows Event API functions"""
    
    def __init__(self):
        self._wevtapi = ctypes.windll.wevtapi
        self._kernel32 = ctypes.windll.kernel32
        
        # Configure function signatures
        self._configure_api_functions()
    
    def _configure_api_functions(self) -> None:
        """Configure ctypes function signatures for type safety"""
        self._wevtapi.EvtOpenPublisherEnum.restype = HANDLE
        self._wevtapi.EvtOpenPublisherEnum.argtypes = [ctypes.c_void_p, DWORD]
        
        self._wevtapi.EvtNextPublisherId.restype = DWORD
        self._wevtapi.EvtNextPublisherId.argtypes = [
            HANDLE, DWORD, ctypes.c_wchar_p, ctypes.POINTER(DWORD)
        ]
        
        self._wevtapi.EvtClose.restype = None
        self._wevtapi.EvtClose.argtypes = [HANDLE]
    
    @contextmanager
    def publisher_enumeration(self):
        """Context manager for publisher enumeration handle"""
        handle = self._wevtapi.EvtOpenPublisherEnum(None, 0)
        if not handle:
            error_code = self._kernel32.GetLastError()
            raise WindowsEventProviderError(
                f"Unable to open publisher enumeration. Error code: {error_code}"
            )
        
        try:
            yield handle
        finally:
            self._wevtapi.EvtClose(handle)
    
    def get_next_publisher_name(self, handle: HANDLE) -> Optional[str]:
        """Get the next publisher name from the enumeration handle"""
        buffer_size = DWORD(0)
        
        # First call to get required buffer size
        result = self._wevtapi.EvtNextPublisherId(
            handle, 0, None, ctypes.byref(buffer_size)
        )
        error_code = self._kernel32.GetLastError()
        
        if error_code == WindowsError.ERROR_NO_MORE_ITEMS:
            return None
        
        if error_code != WindowsError.ERROR_INSUFFICIENT_BUFFER:
            raise WindowsEventProviderError(
                f"Unexpected error getting buffer size. Error code: {error_code}"
            )
        
        # Second call with properly sized buffer
        buffer = ctypes.create_unicode_buffer(buffer_size.value)
        result = self._wevtapi.EvtNextPublisherId(
            handle, buffer_size.value, buffer, ctypes.byref(buffer_size)
        )
        error_code = self._kernel32.GetLastError()
        
        if not result:
            if error_code == WindowsError.ERROR_NO_MORE_ITEMS:
                return None
            raise WindowsEventProviderError(
                f"Unable to get publisher name. Error code: {error_code}"
            )
        
        return buffer.value


class WindowsEventProviderError(Exception):
    """Custom exception for Windows event provider operations"""
    pass


class EventProviderEnumerator:
    """High-level interface for enumerating Windows event providers"""
    
    def __init__(self):
        self._api = WindowsEventAPI()
    
    def enumerate_providers(self) -> List[EventProvider]:
        """
        Enumerate all registered event providers on the system.
        
        Returns:
            List of EventProvider objects
            
        Raises:
            WindowsEventProviderError: If enumeration fails
        """
        providers = []
        
        try:
            with self._api.publisher_enumeration() as handle:
                for provider_name in self._iterate_publishers(handle):
                    providers.append(provider_name)
        except Exception as e:
            logger.error(f"Failed to enumerate event providers: {e}")
            raise WindowsEventProviderError(f"Enumeration failed: {e}") from e
        
        logger.info(f"Found {len(providers)} event providers")
        return providers
    
    def _iterate_publishers(self, handle: HANDLE) -> Iterator[str]:
        """Iterator over publisher names"""
        while True:
            provider_name = self._api.get_next_publisher_name(handle)
            if provider_name is None:
                break
            yield provider_name
    
    def get_provider_names(self) -> List[str]:
        """Get just the provider names as strings"""
        return [provider.name for provider in self.enumerate_providers()]


def main() -> None:
    """Main function to demonstrate event provider enumeration"""
    try:
        enumerator = EventProviderEnumerator()
        providers = enumerator.enumerate_providers()
        
        print(f"Found {len(providers)} registered event providers:")
        print("-" * 50)
        
        for i, provider in enumerate(providers, 1):
            print(f"{i:3d}. {provider}")
            
    except WindowsEventProviderError as e:
        logger.error(f"Error: {e}")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return 1
    
    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main() or 0)