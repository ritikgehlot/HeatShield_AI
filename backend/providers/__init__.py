"""Provider adapters: weather, satellite, urban features, geocoding.

Every adapter returns a ProviderResult (see provider_base.py) so the API and
frontend can render identical freshness/confidence/demo-vs-live UI regardless
of which provider answered. No adapter invents values when live access fails
or isn't configured — see provider_base.ProviderMode.
"""
