from enumerate_metadata import EventMetadataEnumerator
from enumerate_providers import EventProviderEnumerator
from provider import Provider

providers = EventProviderEnumerator().enumerate_providers()
metadata = {"success": {}, "failure": []}

for provider_name in providers:
    try:
        # metadata["success"][provider.name] = EventMetadataEnumerator().get_metadata(provider.name)
        provider = Provider(provider_name)
        provider.load_metadata()
        metadata["success"][provider_name] = provider.to_dict()
    except:
        metadata["failure"].append(provider_name)
print("done")