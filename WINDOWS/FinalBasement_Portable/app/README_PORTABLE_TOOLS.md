# FinalBasement Portable Tools

Put these files inside:

```text
finalbasement-localized/app/
```

## Files

### build_portable_windows.bat

This creates a portable Windows zip that does **not** require Python on the other computer.

Run it on your computer by double-clicking:

```text
build_portable_windows.bat
```

It creates:

```text
portable_build/FinalBasement_Portable.zip
```

Send that zip to someone. They extract it and double-click:

```text
START_FINALBASEMENT.bat
```

The final portable zip includes:
- `FinalBasement.exe`
- the bundled Python runtime/dependencies from PyInstaller
- your `app/` folder
- `local_data/`
- the built-in loop checker/miner cleaner

### START_FINALBASEMENT_DEV.bat

This is the simple dev version. It only works on computers that already have Python + Streamlit installed.

It starts:
- Streamlit
- the separate loop checker
- browser at `http://localhost:8501`

Use this for your own computer if you do not want to build the full portable exe every time.

## Important

The full portable build is Windows-only. If you want a Mac version, it must be built on a Mac.
