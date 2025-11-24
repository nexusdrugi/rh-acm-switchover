# Bash Script Test Suite

This suite validates the two operational Bash scripts:

* `scripts/preflight-check.sh`
* `scripts/postflight-check.sh`

## Test Organization

### Unit Tests (`test_scripts.py`) - 12 tests

Fast-running tests without external dependencies:

* **Argument parsing**: Help output, missing/invalid arguments
* **Error handling**: Unknown options, exit codes
* **Output formatting**: Section headers, summary display

### Integration Tests (`test_scripts_integration.py`) - 8 tests

Mocked end-to-end scenarios:

* **Success paths**: All validation checks pass (passive & full methods)
* **Failure scenarios**: 
  - ACM version mismatch between hubs
  - Backups in progress
  - Missing namespaces/contexts
  - Missing restore resources

## Implementation Details

* **ANSI stripping**: Color codes removed for stable assertions
* **Mocked binaries**: Temporary `PATH` injection with bash script mocks
* **Exit code semantics**: 
  - `0` = success
  - `1` = validation failure
  - `2` = argument error
  - `127` = command not found
* **Bug fixes applied**: 
  - `|| true` on counter increments for `set -e` compatibility
  - `|| echo "0"` on `grep -c` calls to prevent exits on zero matches
* **Parameterized tests**: Multiple scenarios tested with single test function
* **Test markers**: `@pytest.mark.integration` for categorization

## Running Tests

### All script tests
```bash
pytest tests/test_scripts.py tests/test_scripts_integration.py -v
```

### Quick unit tests only (no mocks)
```bash
pytest tests/test_scripts.py -v
```

### Integration tests only
```bash
pytest -m integration -v
```

### Run with coverage report
```bash
pytest tests/test_scripts*.py --cov-report=term-missing:skip-covered
```

### Filter by test name pattern
```bash
pytest -k "preflight" -v      # Only preflight tests
pytest -k "success" -v         # Only success scenario tests
pytest -k "version" -v         # Version mismatch tests
```

## Test Statistics

* **Total tests**: 20
* **Unit tests**: 12 (argument parsing, help, errors)
* **Integration tests**: 8 (mocked cluster scenarios)
* **Parameterized variations**: 7 (different args, methods, scripts)
* **Average runtime**: ~1.2 seconds

## Future Enhancements

* Add `--no-color` flag to scripts for cleaner output parsing
* JSON summary output option for CI/CD integration
* Additional failure scenarios:
  - ClusterDeployment without `preserveOnDelete`
  - Observability pod failures
  - DPA reconciliation failures
* Performance benchmarking for large cluster counts
* Script timeout tests to ensure proper error handling
* Mock jq filters for more realistic JSON processing tests
