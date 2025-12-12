# Packaging Strategy: Container, Python, RPM/COPR, DEB, Helm

A directive, acceptance-driven plan to deliver production-ready packaging for rh-acm-switchover:
- Container image (non-root, OpenShift-safe)
- Python package (pip-installable; optional PyPI)
- RPM + COPR
- Debian/Ubuntu (.deb)
- Helm deployment for Kubernetes/OpenShift

Aligned with repo baseline v1.4.0 (2025-12-12), including state-file precedence and atomic persistence.

## Baseline Facts
- Flat Python layout:
  - Top-level CLIs: `acm_switchover.py`, `check_rbac.py`, `show_state.py`
  - Packages: `lib/`, `modules/`
- Version constants exist:
  - `lib/__init__.py`: `__version__ = "1.4.0"`, `__version_date__ = "2025-12-12"`
  - `scripts/constants.sh`: `SCRIPT_VERSION="1.4.0"`, `SCRIPT_VERSION_DATE="2025-12-12"`
  - Some files carry older strings and require synchronization.
- State-file precedence in code:
  1. `--state-file <path>`
  2. `$ACM_SWITCHOVER_STATE_DIR/switchover-<primary>__<secondary>.json` if `ACM_SWITCHOVER_STATE_DIR` is set
  3. `.state/switchover-<primary>__<secondary>.json`
- Atomic writes and path validation implemented.
- CI container build uses `container-bootstrap/Containerfile`.

## Version Synchronization (Single Source)
Required changes:
- Add `packaging/common/VERSION` = `1.4.0` and `packaging/common/VERSION_DATE` = `2025-12-12`.
- Implement `packaging/common/version-bump.sh` to update:
  - `packaging/common/VERSION`, `VERSION_DATE`
  - `lib/__init__.py`
  - `scripts/constants.sh`
  - `README.md` banner
  - `pyproject.toml` or `setup.cfg` version (prefer `pyproject.toml`; treat `setup.cfg` as tool-only if retained)
  - Container labels/build args
  - Helm `Chart.yaml` `version` and `appVersion`
  - RPM spec `Version:` and Debian changelog version
- Add `--version` to all CLIs.
- Create `packaging/common/validate-versions.sh` for CI drift detection.
Acceptance checklist:
- Running `version-bump.sh 1.4.1 2025-12-20` updates all targets deterministically.
- CI fails on any drift detected by `validate-versions.sh`.
- `acm-switchover --version`, `acm-switchover-rbac --version`, `acm-switchover-state --version` print `1.4.0`.

## Man Pages
Required changes:
- Add `packaging/common/man/` sources:
  - `acm-switchover.1.md`, `acm-switchover-rbac.1.md`, `acm-switchover-state.1.md`
- Provide `packaging/common/man/Makefile` using `pandoc -s -t man` and gzip.
- Document `pandoc` as a system dependency; add CI check with clear failure message if missing.
Acceptance checklist:
- `make -C packaging/common/man` produces gzipped `.1` files.
- RPM/DEB packages install man pages under `/usr/share/man/man1/`.
- `man acm-switchover` renders correctly.

## Python Packaging (Flat Layout)
Required changes:
- Add root `pyproject.toml` with:
  - `requires-python = ">=3.9"`
  - Dependencies from `requirements.txt` (`kubernetes`, `PyYAML`, `rich`, `tenacity`)
  - Console scripts:
    - `acm-switchover = acm_switchover:main`
    - `acm-switchover-rbac = check_rbac:main`
    - `acm-switchover-state = show_state:main`
- Configure setuptools:
  - `py-modules`: `acm_switchover`, `check_rbac`, `show_state`
  - `packages`: include `lib` and `modules` recursively
- Version wiring:
  - Read from `lib.__version__` or sync from `packaging/common/VERSION`.
- Add root `MANIFEST.in` to include non-code assets.
- Provide `packaging/python/README.md` explaining flat layout trade-offs and future namespacing option.
- Optional: `.github/workflows/pypi-publish.yml` with Trusted Publishing.
Acceptance checklist:
- `pip install .` succeeds from a clean environment.
- All three console scripts run and `--version` prints `1.4.0`.
- `python -c "import lib, modules"` succeeds after install.

## RPM + COPR
Required changes:
- Create `packaging/rpm/acm-switchover.spec` with FHS install:
  - `/usr/bin/`: `acm-switchover`, `acm-switchover-rbac`, `acm-switchover-state`
  - `/usr/libexec/acm-switchover/`: helper scripts, `quick-start.sh`
  - `/etc/acm-switchover/`: optional config
  - `/var/lib/acm-switchover/`: state directory
  - `/usr/share/doc/acm-switchover/`: docs
  - `/usr/share/man/man1/`: man pages
  - `/usr/share/bash-completion/completions/`: completions
  - `/usr/share/acm-switchover/deploy/`: `deploy/` content
- Add wrapper scripts (`/usr/bin/*`) that set default only if unset:
  - `: "${ACM_SWITCHOVER_STATE_DIR:=/var/lib/acm-switchover}"; export ACM_SWITCHOVER_STATE_DIR`
  - `exec /usr/bin/python3 -m <module>`
- Post-install: create `/var/lib/acm-switchover` with `0750 root:root`.
- Optional: ship `/etc/sysconfig/acm-switchover` for overrides.
- Add COPR docs under `packaging/rpm/copr/`.
Acceptance checklist:
- `rpmbuild -ba packaging/rpm/acm-switchover.spec` succeeds.
- Installed RPM places files at listed locations.
- Running `acm-switchover` without `ACM_SWITCHOVER_STATE_DIR` uses `/var/lib/acm-switchover`.
- Man pages and bash completions are installed and functional.
- COPR pipeline builds and publishes artifacts for tags.

## Debian/Ubuntu Packaging
Required changes:
- Add `packaging/deb/debian/`:
  - `control`, `rules`, `changelog`, `install`, `postinst`, and licensing files
- Use same wrapper scripts behavior as RPM.
- `postinst` creates `/var/lib/acm-switchover` with secure perms.
- Optional: ship `/etc/default/acm-switchover` for overrides.
- Optional CI: `.github/workflows/deb-build.yml` building artifacts and attaching to Releases.
Acceptance checklist:
- `dpkg-buildpackage -us -uc` succeeds locally or in CI.
- Installed DEB places files at listed locations.
- Default state directory behavior matches RPM.
- Man pages and bash completions are installed and functional.

## Helm Chart
Required changes:
- Create `packaging/helm/acm-switchover/`:
  - `Chart.yaml` with `version: 1.4.0`, `appVersion: 1.4.0`
  - `values.yaml` for image repo/tag and runtime settings
  - Templates for Job/CronJob, PVC, RBAC, ConfigMap, Secret
- In-cluster state:
  - Mount PVC at `/var/lib/acm-switchover`
  - Set `ACM_SWITCHOVER_STATE_DIR=/var/lib/acm-switchover`
- OpenShift security:
  - `runAsNonRoot: true`; arbitrary UID compatible file perms
- Preserve `rbacOnly` mode in existing chart under `deploy/helm/acm-switchover-rbac/`.
Acceptance checklist:
- `helm lint` and `helm template --debug --dry-run` succeed.
- Job manifests show env `ACM_SWITCHOVER_STATE_DIR=/var/lib/acm-switchover` and PVC mount.
- Deploys on OpenShift with arbitrary UID without permission errors.
- Chart versions align with `packaging/common/VERSION`.

## Container Image (OpenShift + Multi-Arch)
Required changes:
- Keep `container-bootstrap/Containerfile` as build input.
- Ensure runtime includes:
  - `check_rbac.py`, `show_state.py`, `completions/`
- Set `ENV ACM_SWITCHOVER_STATE_DIR=/var/lib/acm-switchover`.
- Provide multi-arch build docs/scripts:
  - Docker Buildx and Podman manifest flows
- Add `packaging/container/SECURITY.md` with SCC compatibility and CLI entrypoint examples.
Acceptance checklist:
- Built image runs all three CLIs:
  - `podman run --rm <img> acm-switchover --version`
- With a mounted volume:
  - `-v /tmp/state:/var/lib/acm-switchover` persists state between runs
- Passes OpenShift arbitrary UID checks (files readable/writable via group 0, `g=u`).
- CI multi-arch builds succeed and push manifests.

## Package `deploy/` Contents
Required changes:
- Install `deploy/kustomize/`, `deploy/acm-policies/`, `deploy/rbac/` to `/usr/share/acm-switchover/deploy/`.
- Install `quick-start.sh` to `/usr/libexec/acm-switchover/quick-start.sh`.
Acceptance checklist:
- Files present at target locations after RPM/DEB install.
- Docs reference installed paths; examples run successfully.

## Helper Scripts
Required changes:
- `packaging/common/build-all.sh` — build container, wheel/sdist, RPM, DEB.
- `packaging/common/test-install.sh` — smoke tests in clean containers.
- `packaging/common/validate-versions.sh` — version drift detection.
- `packaging/README.md` — directory layout, supported formats, version bump, state-dir semantics.
Acceptance checklist:
- Scripts run clean locally and in CI; produce expected artifacts.
- README links valid; steps reproducible by a new contributor.

## CI/CD + Docs
Required changes:
- `.github/workflows/version-sync.yml` — validate version consistency.
- Optional `.github/workflows/packaging-release.yml` — tag builds for:
  - container
  - PyPI (if enabled)
  - RPM via COPR
  - DEB artifacts
  - Helm chart packaging and repo index
- Update docs to standardize on `ACM_SWITCHOVER_STATE_DIR` precedence and container defaults.
Acceptance checklist:
- CI fails on version drift; passes on synchronized versions.
- Tag builds produce and publish artifacts; missing tools (e.g., `pandoc`) fail with clear messages.

## Critical Gaps (Must Fix)
Required changes:
- Include `check_rbac.py`, `show_state.py`, and `completions/` in the image.
- Align state persistence in container/helm with `ACM_SWITCHOVER_STATE_DIR=/var/lib/acm-switchover`.
- Resolve version drift; ensure deterministic `--version` flags across CLIs.
- Ensure `show_state.py` honors `ACM_SWITCHOVER_STATE_DIR` when locating state files.
Acceptance checklist:
- Image contains all CLIs and completions; Helm sets correct env and PVC.
- `--version` outputs match `packaging/common/VERSION`.
- `show_state.py` lists and reads state from the default dir when `--state-file` is not provided.

## Directory Structure
Required changes:
- Create `packaging/` with subdirs:
  - `common/`, `python/`, `rpm/`, `deb/`, `container/`, `helm/acm-switchover/`
Acceptance checklist:
- All packaging artifacts live under `packaging/`, leaving app code layout intact.
- Installers include `lib/`, `modules/`, and the three top-level CLIs.
