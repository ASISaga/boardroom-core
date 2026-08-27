# boardroom_core

Wire contracts — `Envelope`, `Evt`, `Digest` — shared by the Boardroom
Function app **F** (`boardroom_function/`) and the Foundry orchestration
container **O** (`orchestration/`). Pure contract code: nothing here performs
I/O, so both sides of the wire can depend on it without inheriting each
other's runtime.

Packaged independently (own `pyproject.toml`) so it can be installed on its
own by either consumer. See `.github/specs/20-repository-topology.md` for the
repository-split plan this package layout is groundwork for.

## Install (editable, from a checkout of the repo)

```bash
pip install -e .
```

## Test

```bash
pip install -e ".[dev]"
pytest -q
```
