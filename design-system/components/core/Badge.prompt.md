One-line: soft-tinted pill that labels a week's lifecycle status, a guard's activity, or a submission's state.

```jsx
<Badge tone="open" icon="🔓">פתוח להגשה</Badge>
<Badge tone="published" icon="📢">פורסם</Badge>
<Badge tone="missing">לא שלח</Badge>
<Badge tone="active">פעיל</Badge>
```

Tones mirror the live app: week → `open` / `locked` / `published` / `closed`; guard → `active` / `inactive`; submission → `submitted` / `missing`; plus generic `success` / `warning` / `danger` / `info` / `secondary`. All soft-tinted for the dark surface.
