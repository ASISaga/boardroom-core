#!/usr/bin/env bash
# Installs aos-infra's pinned platform packages into the current Python
# environment, without ever declaring them in this repository's own
# pyproject.toml. aos-infra is the single source of truth for every
# platform package version (see dependency-consolidation-plan.md) — this
# script's only job is to fetch its current pins and install them.
#
# NOT verified against any existing script by this name — reconstructed
# from how it's invoked in ci-reusable.yml and copilot-setup-steps.yml.
# If purpose-agent already has a real version of this file, diff against
# it and reconcile rather than assuming this one is correct.
#
# Requires AOS_INFRA_TOKEN in the environment: a token with at least
# read access to the private ASISaga/aos-infra repository.

set -euo pipefail

if [[ -z "${AOS_INFRA_TOKEN:-}" ]]; then
  echo "ERROR: AOS_INFRA_TOKEN is not set — cannot authenticate to aos-infra." >&2
  exit 1
fi

AOS_INFRA_REPO="ASISaga/aos-infra"
AOS_INFRA_REF="${AOS_INFRA_REF:-main}"
RAW_BASE="https://raw.githubusercontent.com/${AOS_INFRA_REPO}/${AOS_INFRA_REF}"

# Every layer's requirements file. Installing all five, every time, keeps
# this script identical across every repository regardless of which
# layers a given package actually needs at runtime — pip will simply
# install a superset. If install time becomes a real problem, this can be
# narrowed per-repo later; correctness over speed for now.
REQUIREMENTS_FILES=(
  "requirements.python-base.txt"
  "requirements.azure-sdk.txt"
  "requirements.runtime.txt"
  "requirements.maf.txt"
  "requirements.agent-hosting.txt"
)

WORKDIR="$(mktemp -d)"
trap 'rm -rf "$WORKDIR"' EXIT

echo "Fetching aos-infra requirements files (ref: ${AOS_INFRA_REF})..."
for f in "${REQUIREMENTS_FILES[@]}"; do
  curl -sf \
    -H "Authorization: Bearer ${AOS_INFRA_TOKEN}" \
    -H "Accept: application/vnd.github.raw" \
    "${RAW_BASE}/${f}" \
    -o "${WORKDIR}/${f}" \
    || { echo "ERROR: failed to fetch ${f} from ${AOS_INFRA_REPO}@${AOS_INFRA_REF}" >&2; exit 1; }
done

echo "Installing platform packages from aos-infra..."
for f in "${REQUIREMENTS_FILES[@]}"; do
  pip install --no-cache-dir -r "${WORKDIR}/${f}"
done

echo "OK: platform packages installed from ${AOS_INFRA_REPO}@${AOS_INFRA_REF}"
