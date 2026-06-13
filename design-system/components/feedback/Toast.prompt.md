One-line: transient top-center notification used for save/success/error feedback across the admin app (replaces native `alert()`).

```jsx
<Toast variant="success" onClose={dismiss}>הפעולה בוצעה בהצלחה</Toast>
<Toast variant="error" onClose={dismiss}>אירעה שגיאה — נסה שוב</Toast>
```

Variants: `success` / `error` / `warning` / `info`. Presentational only — stack several in a fixed, top-center, `pointer-events:none` container (each toast re-enables pointer events) and auto-dismiss on a timer (~3.5–5s). Icon chips use ✓ ✕ ! i.
