from enumerate_metadata import EventMetadataEnumerator
from enumerate_providers import EventProviderEnumerator

providers = EventProviderEnumerator().enumerate_providers()
metadata = {"success": {}, "failure": []}

for provider in providers:
    # metadata["success"][provider.name] = EventMetadataEnumerator().get_metadata(provider.name)
    try:
        metadata["success"][provider.name] = EventMetadataEnumerator().get_metadata(provider.name)
    except:
        metadata["failure"].append(provider.name)
print("done")