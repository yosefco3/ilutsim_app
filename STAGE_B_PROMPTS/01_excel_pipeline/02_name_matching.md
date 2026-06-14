# צעד 02 · התאמת שמות למאבטחים קיימים

## מטרה
לקחת את `ParsedGuard.name` ולהתאים אותו ל**מאבטח קיים** (`User`) בדף המאבטחים. **לא יוצרים מאבטחים
חדשים** — שם שלא נמצא מדווח כ"לא זוהה". פונקציה טהורה ככל האפשר (מקבלת את רשימת ה-Users כקלט).

## קרא קודם
- `STAGE_B_PROMPTS/README.md` → "התאמת מאבטח = לפי שם".
- `app/models/user.py` (יש `first_name`,`last_name`), `app/repositories/user_repository.py`.

## קבצים (2-3)
- חדש: `backend/app/services/constraints_import/matcher.py`
- חדש: `backend/tests/test_constraints_matcher.py`
- (אולי) הרחבת `UserRepository` אם חסרה שליפה נוחה — אך עדיף לקבל את ה-users כפרמטר (טהור/בדיק).

## דרישות
1. בנה מפתח-נורמליזציה לשם: trim, רווחים כפולים → יחיד, הסרת גרשיים/מקפים מיותרים, השוואה case/ניקוד-עברי
   סלחנית. שם ה-`User` נבנה מ-`f"{first_name} {last_name}".strip()`.
2. `match_guards(parsed_guards, users) -> MatchResult`:
   ```python
   @dataclass
   class MatchResult:
       matched: list[tuple[ParsedGuard, User]]
       unmatched: list[ParsedGuard]     # שם לא נמצא
       ambiguous: list[tuple[ParsedGuard, list[User]]]  # יותר מהתאמה אחת (לא אמור לקרות לפי המשתמש, אבל מדווח)
   ```
3. התאמה לפי שם מנורמל. אם יש כפילות שם → `ambiguous` (לא לנחש). אם אין → `unmatched`.
4. אל תיצור Users. אל תזרוק על unmatched — זה פלט רגיל לדיווח.

## טסטים
- רשימת users מדומה הכוללת חלק מהשמות בקובץ הדוגמה → אותם ב-`matched`, השאר ב-`unmatched`.
- וריאציות רווח/גרשיים מתאימות נכון.
- שני users עם אותו שם → `ambiguous`.

הרץ: `cd backend && .venv/bin/python -m pytest tests/test_constraints_matcher.py -q`

## קריטריון הצלחה
- ✅ הטסטים עוברים. אישור ידני של המשתמש — בצעד 04 (דרך מסך התצוגה: יראה מי זוהה ומי לא).

## סיום
קומיט: `feat(import): match parsed constraint names to existing guards`. push. עדכן `_PROGRESS.md` ומחק קובץ זה.
