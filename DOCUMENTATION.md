# Documentation

Open the generated API docs in your browser by double-clicking:

[open-documentation.cmd](open-documentation.cmd)

To rebuild the docs after code changes, run:

```powershell
.\.venv\Scripts\Activate.ps1
python -m sphinx -b html docs/sphinx docs/sphinx/_build/html
```
