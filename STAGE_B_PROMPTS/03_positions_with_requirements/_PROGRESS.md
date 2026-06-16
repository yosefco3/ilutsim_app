# _PROGRESS — 03 עמדות עם דרישות

> ריק = טרם התחלנו. הוסף שורת סיכום אחרי כל צעד שהושלם.

- **01** · מודל `Position` (שייך ל-`ActivationProfile`): `profile_id` FK עם `ondelete=CASCADE`
  (updatable), `name`, `shift` (enum `shift_type` קיים), `day_schedules` JSON (יום→{start,end},
  נוכחות=פעיל), `required_attributes` JSON (מפתחות רכים), `display_order`. יחס `positions`
  ב-`ActivationProfile` (`cascade="all, delete-orphan"`, ממוין). `JSON().with_variant(JSONB,"postgresql")`
  לתאימות SQLite בטסטים. נרשם ל-Alembic. מיגרציה `aae292ee0218` (נוקתה מ-`drop schedule_events`;
  enum `create_type=False`; round-trip נקי). · קבצים: `schedule_builder/models/position.py`,
  `models/activation_profile.py`, `schedule_builder/models/__init__.py`, `app/models/__init__.py`,
  `alembic/versions/aae292ee0218_*.py`, `tests/test_position_model.py` (4 טסטים) · backend 269 ·
  commit `feat(builder): Position model + migration (per-day hours, required attrs)`
- **02** · אוצר-מאפיינים קונפיגורבילי. מודל `RequirementAttribute` (`key` ייחודי/`label`/`display_order`).
  `AttributeRepository` (get_all_ordered/get_by_key/count/max_display_order) + `AttributeService`
  (list/create/update/delete + `seed_default_attributes` idempotent מ-`data.js` ATTRS: armed/roni/vehicle/walking).
  כפל-מפתח חוסם (גם ב-update). חריגים `AttributeNotFoundException`/`AttributeKeyConflictException`.
  factory `get_attribute_service`. זריעה ב-`main.py` lifespan. מיגרציה `95be7724eba5` (נוקתה; round-trip נקי).
  · קבצים: `models/requirement_attribute.py`, `repositories/attribute_repository.py`,
  `services/attribute_service.py`, `dependencies.py`, `app/exceptions.py`, `app/main.py`,
  `models/__init__.py` ×2, `alembic/versions/95be7724eba5_*.py`, `tests/test_requirement_attribute_model.py` (3),
  `tests/test_attribute_service.py` (9) · backend 281 ·
  commit `feat(builder): configurable requirement-attributes vocabulary + seed`
- **03** · שכבת דאטה+לוגיקה לעמדות + חיבור deep-copy. `PositionRepository`
  (get_by_profile/max_display_order_in_profile). `PositionService` (list/get/create/update/delete,
  scoped לפרופיל, `display_order` פר-פרופיל, update רק שדות שסופקו, אין מגבלת "עמדה אחרונה").
  חריג `PositionNotFoundException`. `ProfileService._copy_positions` מומש (deep-copy אמיתי, העתק
  עמוק של ה-JSON), `__init__` מקבל `position_repo` אופציונלי (fallback לאותו session). `dependencies.py`:
  `get_position_service` + `get_profile_service` מזריק `PositionRepository`. · קבצים:
  `repositories/position_repository.py`, `services/position_service.py`, `services/profile_service.py`,
  `dependencies.py`, `app/exceptions.py`, `tests/test_position_service.py` (7),
  `tests/test_profile_service.py` (+1 deep-copy) · backend 289 ·
  commit `feat(builder): position repository + service + deep-copy on profile duplicate`
