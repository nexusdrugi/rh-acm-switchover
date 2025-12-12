#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

expected_version="$(cat "$repo_root/packaging/common/VERSION")"
expected_date="$(cat "$repo_root/packaging/common/VERSION_DATE")"

failures=0

check_file() {
  local file="$1" pattern="$2" value="$3" label="$4"
  if [[ -f "$file" ]]; then
    if ! grep -E "$pattern" "$file" >/dev/null; then
      echo "MISSING [$label]: $file does not contain expected pattern"
      failures=$((failures+1))
    elif ! grep -E "$pattern" "$file" | grep -F "$value" >/dev/null; then
      echo "DRIFT [$label]: $file does not match expected value '$value'"
      failures=$((failures+1))
    fi
  fi
}

check_file "$repo_root/lib/__init__.py" '^__version__\s*=' "$expected_version" "python_version"
check_file "$repo_root/lib/__init__.py" '^__version_date__\s*=' "$expected_date" "python_version_date"
check_file "$repo_root/scripts/constants.sh" '^SCRIPT_VERSION=' "\"$expected_version\"" "script_version"
check_file "$repo_root/scripts/constants.sh" '^SCRIPT_VERSION_DATE=' "\"$expected_date\"" "script_version_date"
check_file "$repo_root/pyproject.toml" '^version\s*=' "\"$expected_version\"" "pyproject_version"
check_file "$repo_root/setup.cfg" '^version\s*=' "$expected_version" "setup_cfg_version"
check_file "$repo_root/packaging/helm/acm-switchover/Chart.yaml" '^version:\s*' "$expected_version" "helm_chart_version"
check_file "$repo_root/packaging/helm/acm-switchover/Chart.yaml" '^appVersion:\s*' "$expected_version" "helm_chart_appVersion"

if [[ $failures -gt 0 ]]; then
  echo "Version validation FAILED with $failures issue(s)"
  exit 2
fi

echo "Version validation PASSED"
