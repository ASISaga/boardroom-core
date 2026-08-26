# Copilot Cloud agent prompt — refactor code for an aos-infra dependency bump

One per application repository, whenever `aos-infra`'s requirements files
change. Fill in `<<REPO>>` before submitting.

---

## Goal

`ASISaga/aos-infra` updated one or more platform dependency pins
(`requirements.python-base.txt`, `requirements.azure-sdk.txt`,
`requirements.runtime.txt`, `requirements.maf.txt`,
`requirements.agent-hosting.txt`). You have read-only access to
`ASISaga/aos-infra` via the GitHub MCP server — use it to see exactly what
changed and check each changed package's actual changelog/release notes
between the old and new pinned version.

Refactor this repository's (`<<REPO>>`) own code so it is fully correct
against the new pinned versions — not just verify whether it still works.
Where a version bump changed behavior this repository depends on (a renamed
import, an altered signature, a changed default, a deprecated API, a new
required argument, and similar), make the actual code change. Don't stop at
identifying what's affected — fix it.

## Constraints

- `aos-infra` is the single source of truth for every platform package
  version — this repository must not declare a platform package's version
  anywhere in `pyproject.toml` (main dependencies, any extras group, or
  otherwise). If you find one — whether left over from before this
  repository adopted the aos-infra consolidation, or reintroduced as a
  side effect of this bump — remove it as part of this task, don't leave
  it in place.
- Don't make speculative edits to code a version bump didn't actually
  affect — every change must trace back to a real behavior difference you
  found in the new version's changelog or source, not a guess.
- If you're not confident a given behavior change affects this repository,
  or not confident how to fix it correctly, say so explicitly in the PR
  rather than making a best-effort edit you're unsure of.
- The result must actually install and pass this repository's existing
  tests — use the verify-against-ci skill before finalizing.

Use your own judgment on how to find affected call sites and how deep to
verify each one.

## Report back

In the PR description: which `aos-infra` version changes you evaluated,
which required a code fix and what you changed, which didn't and why not,
anything you weren't confident enough to fix, and confirmation from
verify-against-ci that CI passes.

---

<<REPO: name>>
