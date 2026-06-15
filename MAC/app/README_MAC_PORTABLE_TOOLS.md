# FinalBasement Mac Portable Tools v3

This version fixes the Python 3.14 problem.

Your log showed Python 3.14 trying to install `Pillow==10.2.0`.
That package is too old for Python 3.14, so the build fails.

Use Python 3.12 for this project.

## Steps

1. Install Python 3.12 on the Mac.
2. Verify:

```bash
python3.12 --version
```

3. Put these files inside:

```text
finalbasement-localized/app/
```

4. Run:

```bash
bash build_portable_mac.command
```

It creates:

```text
portable_build/FinalBasement_Portable_mac.zip
```

## Do not use Python 3.14 for this build

The script now specifically looks for `python3.12` and stops if it cannot find it.
