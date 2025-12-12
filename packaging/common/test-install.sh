#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

python3 -m venv "$repo_root/.venv-test"
. "$repo_root/.venv-test/bin/activate"
pip install -r "$repo_root/requirements.txt"
pip install "$repo_root"

acm-switchover --version
acm-switchover-rbac --version
acm-switchover-state --version

echo "Smoke test passed"
