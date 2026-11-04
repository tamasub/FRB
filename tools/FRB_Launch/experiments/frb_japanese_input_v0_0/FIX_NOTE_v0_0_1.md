# FRB Japanese Input v0.0.1 - Windows BAT startup fix

The previous `run_windows.bat` was UTF-8 with Japanese comments and output.
On Windows Command Prompt using a different code page, this could be
misparsed as commands. `run_windows.bat` is now ASCII-only.

No changes to Python UI, behavior, kana mapping or the FRB Launch app.
To apply the DIFF ZIP, extract it at the same FRB Launch root path,
overwriting `experiments/frb_japanese_input_v0_0/run_windows.bat`.

If startup still fails, open Command Prompt in the experiment folder and run:
`python frb_japanese_input.py`
If it reports `No module named PySide6`, install from requirements.txt
using the same Python interpreter that you run the app with.
