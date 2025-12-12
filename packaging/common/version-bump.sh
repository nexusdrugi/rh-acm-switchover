#!/usr/bin/env bash
set -euo pipefail

new_version="${1:-}"
new_date="${2:-}"

if [[ -z "$new_version" || -z "$new_date" ]]; then
  echo "Usage: $0 <version> <YYYY-MM-DD>"
  exit 1
fi

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

echo "$new_version" > "$repo_root/packaging/common/VERSION"
echo "$new_date" > "$repo_root/packaging/common/VERSION_DATE"

python_init="$repo_root/lib/__init__.py"
sed -i -E "s/^(__version__\s*=\s*\").*(\")/\1${new_version}\2/" "$python_init"
sed -i -E "s/^(__version_date__\s*=\s*\").*(\")/\1${new_date}\2/" "$python_init"

constants_sh="$repo_root/scripts/constants.sh"
if [[ -f "$constants_sh" ]]; then
  sed -i -E "s/^(SCRIPT_VERSION=).*/\1\"${new_version}\"/" "$constants_sh"
  sed -i -E "s/^(SCRIPT_VERSION_DATE=).*/\1\"${new_date}\"/" "$constants_sh"
fi

readme_md="$repo_root/README.md"
if [[ -f "$readme_md" ]]; then
  sed -i -E "s/(Version:\\s*)[0-9]+\\.[0-9]+\\.[0-9]+/\\1${new_version}/" "$readme_md" || true
fi

pyproject="$repo_root/pyproject.toml"
if [[ -f "$pyproject" ]]; then
  sed -i -E "s/^version\\s*=\\s*\".*\"/version = \"${new_version}\"/" "$pyproject"
fi

setup_cfg="$repo_root/setup.cfg"
if [[ -f "$setup_cfg" ]]; then
  sed -i -E "s/^version\\s*=\\s*.*/version = ${new_version}/" "$setup_cfg"
fi

chart_yaml="$repo_root/packaging/helm/acm-switchover/Chart.yaml"
if [[ -f "$chart_yaml" ]]; then
  sed -i -E "s/^(version:\\s*).*/\\1${new_version}/" "$chart_yaml"
  sed -i -E "s/^(appVersion:\\s*).*/\\1${new_version}/" "$chart_yaml"
fi

rpm_spec="$repo_root/packaging/rpm/acm-switchover.spec"
if [[ -f "$rpm_spec" ]]; then
  sed -i -E "s/^(Version:\\s*).*/\\1${new_version}/" "$rpm_spec"
fi

deb_changelog="$repo_root/packaging/deb/debian/changelog"
if [[ -f "$deb_changelog" ]]; then
  perl -0777 -pe "s/(\\(\\d+\\.\\d+\\.\\d+\\))/${new_version}/ if $.=1" "$deb_changelog" > "$deb_changelog.tmp" && mv "$deb_changelog.tmp" "$deb_changelog" || true
fi

echo "Updated version to ${new_version} (${new_date})"
