One-line: the form controls behind every admin form — guard editor, login, settings, constraint filling.

```jsx
<Field label="שם פרטי">
  <TextInput value={first} onChange={e => setFirst(e.target.value)} />
</Field>

<Field label="תפקיד">
  <Select value={role} onChange={e => setRole(e.target.value)}>
    <option value="AHMASH">אחמ"ש</option>
    <option value="BASIC_GUARD">מאבטח בסיסי</option>
  </Select>
</Field>

<Field label="הערות כלליות" hint="אופציונלי">
  <Textarea value={notes} onChange={e => setNotes(e.target.value)} />
</Field>
```

All controls are RTL, sit on `--surface-2`, and show the indigo focus ring (`--primary` border + `--primary-soft` glow). Always wrap a control in `Field` for the label + hint rhythm.
