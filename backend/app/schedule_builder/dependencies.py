"""
Part B — schedule builder dependency providers.

FastAPI ``Depends()`` factories for the schedule-builder services live here
(NOT in ``app/dependencies.py``) to keep the part-A / part-B boundary explicit.
It is fine to import session/auth helpers from part A (dependency rule: B → A).

Empty for now — providers are added alongside the services that need them
(see prompt 02: ``get_profile_service``).
"""
