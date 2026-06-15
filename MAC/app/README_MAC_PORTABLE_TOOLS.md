# FinalBasement Mac Portable Tools v5

This version improves the background online cleanup.

## What changed

The launcher now:
- prints `[loop] Background cleanup loop started`
- prints a heartbeat every minute showing who is online
- accepts `True`, `"True"`, and `1` as online values
- sets users offline with dot updates:
  - `active.online = False`
  - `active.date = <now>`
- prints when it turns someone offline

## Use

Replace old Mac tool files with these, then run:

```bash
bash build_portable_mac.command
```

Use the new output:

```text
portable_build/FinalBasement_Portable_mac.zip
```

## What to check

When you launch the portable app, the Terminal window should show:

```text
[loop] Background cleanup loop started
```

After a minute, it should show something like:

```text
[loop] heartbeat: currently online = [...]
```

After 5 minutes idle, it should print the account it set offline.
