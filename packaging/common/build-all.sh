#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

echo "Building Python sdist/wheel..."
python3 -m build "$repo_root"

echo "Building container image (local)..."
docker build -f "$repo_root/container-bootstrap/Containerfile" -t acm-switchover:local "$repo_root"

echo "RPM and DEB builds are environment-specific; refer to packaging docs."
echo "All builds completed."
