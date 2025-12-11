# Plan: Complete Packaging Strategy—Container, Python, RPM/COPR, DEB, and Helm

A production-ready packaging strategy for rh-acm-switchover supporting Docker/Podman containers (non-root, OpenShift-safe), Python/PyPI, RPM/COPR, Debian/Ubuntu, and Kubernetes/OpenShift deployment via Helm. All packaging methods unified under `packaging/` directory with shared metadata, automated version management, and CI/CD integration.

## Steps

### 1. Create unified `packaging/` directory structure ([packaging/](packaging/))

- `packaging/python/` — PyPI package files (pyproject.toml, MANIFEST.in, entry points)
- `packaging/rpm/` — RPM spec file, build helpers, COPR configuration
- `packaging/deb/` — Debian control files, rules, changelog, postinst scripts
- `packaging/container/` — Containerfile (move from container-bootstrap/), multi-arch build scripts, OpenShift security docs
- `packaging/helm/acm-switchover/` — Full application Helm chart (Job/CronJob, PVC, RBAC, ConfigMap, Secret templates)
- `packaging/common/` — Shared VERSION file, metadata, man page sources (Markdown), build/test/version-bump helper scripts, Makefile for man page generation

**Note**: All Python modules in `lib/` and `modules/` (including `backup_schedule.py`, `rollback.py` if present) are automatically included in packages.

### 2. Establish single version source and synchronization ([packaging/common/VERSION](packaging/common/VERSION))

- Create `packaging/common/VERSION` file containing `1.3.0` (canonical version source)
- Create `packaging/common/version-bump.sh` script to update version across: `packaging/common/VERSION`, `setup.cfg`, `pyproject.toml`, RPM spec, Debian changelog, Helm Chart.yaml/appVersion, Containerfile labels
- Add `__version__ = "X.Y.Z"` to `lib/__init__.py` (synced by `version-bump.sh`)
- Add `--version` argument to all three Python entry points (`acm_switchover.py`, `check_rbac.py`, `show_state.py`)
- Add validation step to confirm all files are in sync (CI pre-commit check)
- Document version management in `packaging/README.md`

### 3. Generate man pages from Markdown source ([packaging/common/man/](packaging/common/man/))

- Create `packaging/common/man/acm-switchover.1.md` with comprehensive man page content (NAME, SYNOPSIS, DESCRIPTION, OPTIONS with all CLI flags, EXAMPLES, FILES, ENVIRONMENT, EXIT STATUS, SEE ALSO, AUTHORS, COPYRIGHT)
- Create `packaging/common/man/acm-switchover-rbac.1.md` for RBAC checker
- Create `packaging/common/man/acm-switchover-state.1.md` for state viewer
- Create `packaging/common/man/Makefile` to convert .md → .1 roff using `pandoc -s -t man`, gzip compress to .1.gz
- Add `pandoc >= 2.0` to `requirements-dev.txt`
- Add `man: generate-man` target to root `Makefile` or packaging Makefile

### 4. Build Python/PyPI packaging ([packaging/python/pyproject.toml](packaging/python/pyproject.toml))

- Create `packaging/python/pyproject.toml` with `[project]` metadata: name=acm-switchover, dynamic version (read from `../../packaging/common/VERSION`), description, license=MIT, requires-python=>=3.9, authors=[{name="Platform Engineering"}], homepage/repository/documentation URLs
- Define `[project.scripts]` entry points: `acm-switchover`, `acm-switchover-rbac`, `acm-switchover-state` (point to main functions)
- Add `[project.optional-dependencies]` for dev (pytest, flake8, mypy, black, isort, bandit, safety, pip-audit), docs (sphinx, mkdocs)
- Configure `[build-system]` with backend=setuptools, requires=[setuptools>=61.0, wheel]
- Create `packaging/python/MANIFEST.in` to include README.md, LICENSE, docs/, scripts/, deploy/, completions/, and exclude .git, tests, venv
- Create `.github/workflows/pypi-publish.yml` to build and publish to PyPI on git tags (v*.*.*) using Trusted Publishing (OIDC), publish sdist + wheels
- **Python package structure**: Current layout has `lib/` and `modules/` as top-level directories. For proper PyPI packaging, restructure to `src/acm_switchover/` layout:
  - Move `lib/` → `src/acm_switchover/lib/`
  - Move `modules/` → `src/acm_switchover/modules/`
  - Move entry point scripts (`acm_switchover.py`, `check_rbac.py`, `show_state.py`) → `src/acm_switchover/cli/` as modules with `main()` functions
  - Update all imports accordingly (e.g., `from lib.kube_client import KubeClient` → `from acm_switchover.lib.kube_client import KubeClient`)
  - Configure pyproject.toml with `[tool.setuptools.packages.find] where = ["src"]`
  - This is the recommended approach for modern Python projects, provides clean namespace, and works seamlessly with pip install

### 5. Create RPM spec file and COPR integration ([packaging/rpm/acm-switchover.spec](packaging/rpm/acm-switchover.spec))

- Write `.spec` file with Name: acm-switchover, dynamic Version (read from spec file macro or git tag), Release: 1, License: MIT, Summary, URL, Source0, BuildArch: noarch
- BuildRequires: python3-devel>=3.9, python3-setuptools, python3-pytest, python3-wheel (build dependencies)
- Requires: python3>=3.9, python3-kubernetes>=28.0, python3-pyyaml>=6.0, python3-rich>=13.0, python3-tenacity>=8.2
- Recommends: openshift-clients (provides `oc`) or kubernetes-client, jq>=1.7
- Implement `%prep`, `%build` (python -m build), `%check` (pytest), `%install` sections
- Install to FHS: `/usr/bin/` (entry point scripts), `/usr/lib/python3.*/site-packages/acm_switchover/` (package), `/usr/libexec/acm-switchover/` (helper scripts including `quick-start.sh`), `/etc/acm-switchover/` (config dir), `/var/lib/acm-switchover/` (state dir), `/usr/share/doc/acm-switchover/` (docs), `/usr/share/man/man1/` (man pages), `/usr/share/bash-completion/completions/` (completions), `/usr/share/acm-switchover/deploy/` (RBAC manifests, Kustomize, ACM policies)
- Add `%files` with proper `%attr`, `%doc`, `%license`, `%dir %attr(1777, root, root)` directives
- Include `%post` to create `/var/lib/acm-switchover/` with mode 1777
- Create `packaging/copr/README.md` with COPR project setup instructions (`@tomazborstnar/acm-switchover`), webhook configuration for GitHub auto-builds on tags, target distributions (RHEL 8, RHEL 9, Fedora 40+, CentOS Stream 9)
- Document in `packaging/copr/gpg-setup.md` GPG key generation and registration for package signing

### 6. Implement Debian/Ubuntu packaging ([packaging/deb/debian/](packaging/deb/debian/))

- Create `debian/control` with Source: acm-switchover, Build-Depends: debhelper-compat (= 13), dh-python, python3-all, python3-setuptools, python3-pytest
- Define binary package with Package: acm-switchover, Depends: python3 (>=3.9), python3-kubernetes (>=28.0), python3-yaml (>=6.0), python3-rich (>=13.0), python3-tenacity (>=8.2)
- Add Recommends: kubectl | openshift-client, jq (>=1.7)
- Create `debian/rules` using dh sequencer: `dh $@ --with python3 --buildsystem=pybuild`
- Generate `debian/changelog` with entry for v1.3.0-1 using `dch --create`
- Set `debian/compat` to 13
- Write `debian/copyright` in DEP-5 format with MIT license and copyright info
- Create `debian/install` to map source files to `/usr` paths
- Add `debian/postinst` to create `/var/lib/acm-switchover/` directory
- Optional: `.github/workflows/deb-build.yml` to build .deb on Ubuntu, upload to GitHub Releases

### 7. Build comprehensive Helm chart for full app deployment ([packaging/helm/acm-switchover/](packaging/helm/acm-switchover/))

- Create `Chart.yaml` with apiVersion: v2, name: acm-switchover, description, version: 1.3.0, appVersion: 1.3.0, keywords, home, sources, maintainers, icon
- Create `values.yaml` with:
  - image (repository: quay.io/tomazborstnar/acm-switchover, tag: "latest" [overridable], pullPolicy: IfNotPresent)
  - imagePullSecrets: [] (for private registries)
  - resources (requests/limits CPU/memory)
  - nodeSelector, tolerations, affinity
  - podSecurityContext (runAsNonRoot: true, runAsUser: 1001, fsGroup: 0, seccompProfile: RuntimeDefault, supplementalGroups: [0])
  - containerSecurityContext (allowPrivilegeEscalation: false, readOnlyRootFilesystem: false [app needs to write state], runAsNonRoot: true, capabilities.drop: [ALL])
- Add persistence config: enabled: true, storageClassName: "" [uses default], size: 1Gi, accessMode: ReadWriteOnce
- Add switchover parameters: primaryContext, secondaryContext, validateOnly: false, dryRun: false, nonInteractive: true, resetState: false
- Add kubeconfig handling: kubeconfig.fromSecret (mount Secret) or inCluster: false
- Add `rbacOnly: false` toggle — when true, only deploy RBAC resources (ServiceAccount, ClusterRole, ClusterRoleBinding, Role, RoleBinding) without Job/CronJob/PVC, enabling users to use the chart solely for RBAC setup
- Create `templates/namespace.yaml` to create acm-switchover namespace (optional, configurable with `createNamespace: true`)
- Create `templates/serviceaccount.yaml` for operator and validator service accounts
- Create `templates/configmap.yaml` for switchover CLI arguments (primaryContext, secondaryContext, etc.)
- Create `templates/secret.yaml` for kubeconfig data (base64 encoded)
- Create `templates/pvc.yaml` for state directory persistence (size, storageClass configurable)
- Create `templates/job.yaml` for one-shot switchover Job with: image, securityContext, volumeMounts (kubeconfig, state PVC), env vars, resources, nodeSelector, tolerations, affinity, imagePullPolicy, serviceAccountName
- Create `templates/cronjob.yaml` (optional, disabled by default) for periodic validation runs
- Create `templates/rbac-clusterrole.yaml`, `templates/rbac-clusterrolebinding.yaml`, `templates/rbac-role.yaml`, `templates/rbac-rolebinding.yaml` with full operator/validator permissions (bundled, toggle with `rbac.create: true`)
- Create `templates/networkpolicy.yaml` (disabled by default via `networkPolicy.enabled: false`)
- Add `templates/NOTES.txt` with post-install instructions: check Job status, view logs, resume interrupted switchover, access state file, SCC compatibility note for OpenShift
- Add `templates/_helpers.tpl` for label selectors, chart name, service account name

### 8. Containerize and verify OpenShift compliance ([packaging/container/Containerfile](packaging/container/Containerfile))

- Move `container-bootstrap/Containerfile` to `packaging/container/Containerfile`
- Add missing files to Containerfile:
  - `COPY --chown=1001:0 check_rbac.py show_state.py /app/`
  - `COPY --chown=1001:0 completions/ /app/completions/` — provides bash completion scripts in the image
- Add note in container docs: bash completions available at `/app/completions/`, can be sourced with `source /app/completions/_acm_completion_lib.sh`
- Verify non-root execution: USER 1001, fsGroup 0 (OpenShift-compatible, allows arbitrary UID assignment)
- Document security context in `packaging/container/SECURITY.md`: OpenShift restricted SCC compliance, read-only root handling, volume permissions, alternative entry points for `check_rbac.py` and `show_state.py`
- Create `packaging/container/build-multiarch.sh` for local multi-arch builds: `podman buildx build --platform linux/amd64,linux/arm64 -t acm-switchover:latest .`
- Add `packaging/container/test-openshift.sh` to validate image runs with restricted SCC (runAsNonRoot enforced)

### 9. Package `deploy/` directory contents

- Include `deploy/kustomize/` in RPM under `/usr/share/acm-switchover/deploy/kustomize/`
- Include `deploy/acm-policies/` under `/usr/share/acm-switchover/deploy/acm-policies/`
- Include `deploy/rbac/` under `/usr/share/acm-switchover/deploy/rbac/`
- Clarify relationship: keep existing `deploy/helm/acm-switchover-rbac/` for backward compatibility as standalone RBAC chart; new `packaging/helm/acm-switchover/` is the full application chart with bundled RBAC
- Include `quick-start.sh` in packages under `/usr/libexec/acm-switchover/quick-start` or `/usr/share/acm-switchover/quick-start.sh`

### 10. Create helper scripts for packaging workflow ([packaging/common/](packaging/common/))

- `packaging/common/build-all.sh` — Build all formats: RPM (via mock), DEB (dpkg-buildpackage), Python wheel (python -m build), container (podman/docker)
- `packaging/common/test-install.sh` — Test installations in clean containers (ubi9, fedora:40, ubuntu:22.04) to verify package integrity and basic functionality
- `packaging/common/validate-versions.sh` — Check version consistency across all files (CI pre-commit check)
- Create `packaging/common/metadata.yaml` with: project name, description, homepage, authors, license, keywords (for reference/documentation)
- Create `packaging/README.md` documenting packaging directory structure, versioning strategy, build instructions, CI/CD integration

### 11. Update CI/CD and root documentation (.github/workflows/, README.md, setup.cfg)

- Update `setup.cfg`: keep metadata, remove version (read from pyproject.toml), point to packaging directory structure in comments
- Update root `README.md` to reference `docs/INSTALL.md` and `packaging/README.md` for multiple installation methods (container, pip, RPM, DEB, Helm)
- Update `docs/CONTRIBUTING.md` to reference `packaging/README.md` for packaging development instructions
- Update `docs/CHANGELOG.md` as part of release process (add entry for each version before tagging)
- Add `.github/workflows/packaging-release.yml` to build and publish all formats on git tags: RPM (upload to COPR via copr-cli), DEB (build + upload to Releases), Python (PyPI via setuptools), container (already exists), Helm chart (.tgz upload to Releases + update gh-pages index.yaml)
- Create `.github/workflows/version-sync.yml` to validate version consistency on PRs/commits
- Set up `gh-pages` branch with Helm repository `index.yaml` for `helm repo add https://tomazb.github.io/rh-acm-switchover/` support

---

## Critical Gaps Identified (Must Fix)

1. **Missing `check_rbac.py` and `show_state.py` from Container image** — Containerfile only copies `acm_switchover.py`. Fix: Add COPY statements for these files.

2. **Missing `completions/` directory in Container image** — Bash completions not copied. Fix: Add COPY for completions/.

3. **No `__version__` defined in Python code** — Version only in `setup.cfg`, no `--version` CLI flag. Fix: Add `__version__` to `lib/__init__.py` and `--version` to all entry points.

4. **Missing `quick-start.sh` in packaging plan** — Interactive wizard not included. Fix: Package under `/usr/libexec/acm-switchover/` or `/usr/share/`.

5. **Container alternative entry points undocumented** — No way to run `check_rbac.py` or `show_state.py` from container. Fix: Document `--entrypoint python3` override in container docs.

---

## Further Considerations

1. **Helm chart namespace** — Create or assume namespace exists? Recommend: Create with conditional (`createNamespace: true` in values, optional).

2. **Kubeconfig mounting strategy** — User provides kubeconfig Secret or in-cluster Service Account? Recommend: Both via toggles—`kubeconfig.fromSecret: true` (mount Secret) or `kubeconfig.inCluster: false` (use default SA).

3. **Job retry policy** — Should failed switchover Jobs auto-retry? Recommend: `backoffLimit: 0` (no retry, resume via state), document manual resume process in NOTES.txt.

4. **CronJob for validation** — Useful for periodic health checks? Recommend: Include template (optional, disabled by default), document schedule in values as example.

5. **Helm chart: RBAC bundled** — RBAC is bundled in main chart with toggle (`rbac.create: true`). Add `rbacOnly: true` mode to deploy only RBAC resources without Job/PVC. Keep standalone `deploy/helm/acm-switchover-rbac/` for backward compatibility.

6. **DEB upload to Releases** — Automate or manual? Recommend: Automate in CI with `softprops/action-gh-release@v1` for all artifacts.

7. **Container image in Helm values** — Allow image pull secret for private registries? Recommend: Add `imagePullSecrets: []` in values for flexibility.

8. **State directory ownership in Helm** — Job runs as UID 1001, does PVC mount work without explicit fsGroup? Recommend: Set `fsGroup: 0` in securityContext; OpenShift handles UID/GID mapping automatically.

9. **Container alternative entry points** — How to allow users to run `check_rbac.py` or `show_state.py` from container? Recommend: Document `--entrypoint python3` override clearly in `packaging/container/SECURITY.md`.

10. **Helm repository hosting** — Set up `gh-pages` branch with `index.yaml` for proper `helm repo add` support, in addition to GitHub Releases `.tgz` download.

11. **`--version` implementation** — Static string vs. read from file vs. importlib.metadata? Recommend: Static `__version__` in `lib/__init__.py`, synced by `version-bump.sh`. Entry points import and use it.

12. **SELinux policy for `/var/lib/acm-switchover/`** — Document `semanage fcontext` commands in post-install notes and RPM `%post` scriptlet comments rather than custom policy module.

13. **OpenShift SecurityContextConstraints (SCC) documentation** — Recommend: Add to `packaging/container/SECURITY.md` and Helm chart NOTES: "Works with restricted SCC by default."

14. **Shell completion for zsh/fish** — Only bash completions exist currently. Start with bash completions and add a note about `--help` for command reference. zsh/fish support as future enhancement (v1.2+).

15. **Tests exclusion** — Confirm the following are excluded from all packages:
    - `tests/`, `htmlcov/`, `coverage.xml`, `__pycache__/`
    - `run_tests.sh` (dev-only script)
    - `.editorconfig`, `.vscode/`, `.github/` (dev tooling)
    - `venv/`, `.venv/`, `node_modules/` (local environments)
    - Root-level dev docs: `COMPREHENSIVE-VALIDATION-AND-ERROR-HANDLING.md`, `EXCEPTION_HANDLING_IMPROVEMENTS.md`, `SECURITY_FIX_DOCUMENTATION.md` (keep only in source repo, exclude from packages)

16. **`container-bootstrap/get-pip.py` handling** — Unused file. Recommend: Remove from repo or use in Containerfile if needed.
