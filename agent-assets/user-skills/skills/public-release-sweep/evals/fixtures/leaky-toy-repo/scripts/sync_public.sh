#!/usr/bin/env bash
# Synthetic fixture: blacklist-style public sync script.
# Used by public-release-sweep evals to exercise Dimension 8 (sync mechanism)
# weaknesses; not a recommended pattern.
#
# Smell: relies on an EXCLUDE list to keep private content out of the public
# mirror. Anything new added to the repo (new env files, new private paths,
# renamed dirs) will leak by default unless this list is updated in lockstep.

set -euo pipefail

SRC_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DEST_ROOT="${SRC_ROOT}/../public/toy-demo"

EXCLUDE=(
  ".env"
  "AGENTS.md"
  "control/"
  "docs/plans/"
  "reports/"
  "specs/"
  "tool/"
)

RSYNC_ARGS=(-a --delete)
for pattern in "${EXCLUDE[@]}"; do
  RSYNC_ARGS+=(--exclude "${pattern}")
done

mkdir -p "${DEST_ROOT}"
rsync "${RSYNC_ARGS[@]}" "${SRC_ROOT}/" "${DEST_ROOT}/"

echo "Synced ${SRC_ROOT} -> ${DEST_ROOT} (blacklist mode)."
