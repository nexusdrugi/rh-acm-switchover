## Plan: Add Pytest Tests For Bash Scripts

Add pytest-based tests for `scripts/preflight-check.sh` and `scripts/postflight-check.sh` using mock `oc`/`jq` binaries injected via PATH. Cover argument handling, success path, and key failure scenarios with environment flags to drive stub behavior.

### Steps
1. Create `tests/test_scripts.py` with fixtures: temp mock bin dir, `run_script()` helper, ANSI strip utility.
2. Implement parametrized success tests (help, missing args, full success) for both scripts.
3. Add targeted failure tests (ACM version mismatch, missing restore, backup in progress, preserveOnDelete missing).
4. Build mock `oc` stub supporting required command pattern branches and env-driven failure toggles.
5. Update `requirements-dev.txt` to ensure `pytest` is present and add run instructions to `tests/README.md` (new file).

### Further Considerations
1. Optional: add `--no-color` flag to scripts for cleaner assertion vs ANSI stripping.
2. Optional: normalize backup phase terms (Finished vs Completed) to simplify mocks.
3. Future: add JSON summary output flag for machine-readable testing.
