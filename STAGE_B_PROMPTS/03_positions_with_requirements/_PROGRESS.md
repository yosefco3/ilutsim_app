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
