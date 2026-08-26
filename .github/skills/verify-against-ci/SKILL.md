---
name: verify-against-ci
description: Use before finalizing any change that touches platform-dependent code (imports of agent_framework, azure.*, mcp, or anything sourced from aos-infra) or before opening/updating a pull request. Triggers this repository's standard CI workflow (.github/workflows/ci.yml, calling aos-infra's shared ci-reusable.yml) to get a real result, instead of relying on a local pip install alone.
---

# Verify against CI

Every repository in this pipeline uses the same CI convention: a thin
`.github/workflows/ci.yml` that calls `ASISaga/aos-infra`'s shared
`ci-reusable.yml`, with three jobs — `ci / unit-tests`, `ci / integration-
tests`, `ci / lint`. Platform packages (`agent_framework`, `azure-ai-
projects`, `mcp`, etc.) are intentionally absent from `pyproject.toml`;
`ci-reusable.yml` installs them via `.github/scripts/install-platform-
deps.sh` before running anything. A plain local `pip install -e .` will not
resolve those imports — that's expected, not a bug to fix locally.

## When to use this

- Before finalizing a change to this repository's own source.
- Before opening or updating a pull request.
- Any time a local `pytest`/`pylint` run fails with `ModuleNotFoundError`
  for a platform package.

## How to invoke it

```bash
gh workflow run ci.yml --repo <this-repo> --ref <branch>
gh run list --repo <this-repo> --workflow=ci.yml --branch <branch> --limit 1
gh run watch --repo <this-repo> <run-id>
```

If `ci.yml` doesn't exist in this repository yet, that's a gap to report,
not to work around — this repository hasn't adopted the pipeline-wide CI
convention yet. Don't invent a substitute; flag it.

## Interpreting results

- All three jobs must pass.
- `integration-tests`' platform-import check failing means `aos-infra`'s
  pins are out of sync with what this repo's code imports — an `aos-infra`
  issue, not something to fix by editing this repository's dependencies.
- Report the actual CI result (pass/fail, which job) in your summary —
  never infer success from a clean local run alone.
