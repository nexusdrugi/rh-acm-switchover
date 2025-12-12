# Packaging

- common: VERSION, VERSION_DATE, version-bump.sh, validate-versions.sh, man/
- python: pyproject.toml at repo root, MANIFEST.in
- rpm: acm-switchover.spec, wrappers, man pages, deploy assets, completions
- deb: debian/ control, rules, changelog, install
- container: Containerfile docs and helpers
- helm/acm-switchover: chart, values, templates

## Version Bump

- Run: `packaging/common/version-bump.sh <version> <YYYY-MM-DD>`
- Validate: `packaging/common/validate-versions.sh`

## Man Pages

- Requires: `pandoc`, `make`
- Build: `make -C packaging/common/man`

## State Directory Defaults

- Packaged installs default `ACM_SWITCHOVER_STATE_DIR=/var/lib/acm-switchover` via wrapper scripts.
- CLI `--state-file` always overrides the default.
