One-line: the base dark surface panel — wraps forms, week cards, settings rows and the login box.

```jsx
<Card>
  <h3>הוספת מאבטח</h3>
  …form fields…
</Card>

<Card interactive>…week card…</Card>
```

Pass `interactive` for the hover lift (stronger border + `--shadow-md`) used by the week-management cards. Default padding is `--space-5` (20px); override via `style`.
