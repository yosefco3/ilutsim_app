One-line: the dark-indigo action button used for every admin action — submit, save, open week, delete.

```jsx
<Button variant="primary" icon="🟢" onClick={openWeek}>פתח להגשה</Button>
<Button variant="danger" size="sm" icon="🗑️">מחק</Button>
<Button variant="outline" size="sm">רענון</Button>
```

Variants: `primary` (indigo), `danger` (red), `success` (green), `secondary` (raised surface), `outline`, `ghost`. Sizes: `md` (default), `sm`. Use `block` for full-width form/login buttons. Icons are emoji strings — that is the brand's icon system. Hover and press states are built in.
