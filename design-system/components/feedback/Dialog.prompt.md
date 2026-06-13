One-line: centered confirmation modal over a blurred dark scrim — used before destructive actions.

```jsx
<Dialog
  title="מחק שבוע"
  message="האם למחוק את השבוע? פעולה זו אינה ניתנת לביטול."
  confirmLabel="מחק"
  onConfirm={doDelete}
  onCancel={() => setOpen(false)}
/>
```

Clicking the scrim cancels. `confirmVariant` defaults to `danger`; set `primary`/`success` for non-destructive confirms. Pass `children` instead of `message` for richer bodies.
