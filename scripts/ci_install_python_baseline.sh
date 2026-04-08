#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0
#
# Install the shared Python dependency baseline used by merge-surface jobs.
# Keep this script intentionally small so lint/test/docs jobs consume the same
# lockfile contract and avoid bootstrap drift across matrix entries.
set -euo pipefail

include_backend_lock=0
include_docs_lock=0

while (($#)); do
    case "$1" in
    --include-backend-lock)
        include_backend_lock=1
        ;;
    --include-docs-lock)
        include_docs_lock=1
        ;;
    *)
        echo "Unknown argument: $1" >&2
        exit 2
        ;;
    esac
    shift
done

python -m pip install --upgrade pip
pip install -r requirements.lock
pip install -r requirements-dev.lock

if [[ "$include_backend_lock" -eq 1 ]]; then
    pip install -r alpha_factory_v1/backend/requirements-lock.txt
fi

if [[ "$include_docs_lock" -eq 1 ]]; then
    pip install -r requirements-docs.lock
fi
