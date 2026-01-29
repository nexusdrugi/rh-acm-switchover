# Plan: GitOps Marker Detection (Final)

Add GitOps-managed resource detection to preflight/postflight scripts and Python workflow. Scans 6 resource types for ArgoCD/Flux markers, emits consolidated end-of-run warnings so operators can coordinate with GitOps to avoid drift.

## Steps

1. **Create `lib/gitops_detector.py`** with `detect_gitops_markers(metadata: Dict) -> List[str]` function (extracted from `modules/finalization.py` `_gitops_markers()`) and `GitOpsCollector` singleton class with `record(context, namespace, kind, name, markers)` and `print_report()` methods. Initialize in `acm_switchover.py` `main()`, call `print_report()` before exit.

2. **Add Bash helper `collect_gitops_markers()`** to `scripts/lib-common.sh` using indexed arrays `GITOPS_DETECTED_RESOURCES[]` and `GITOPS_DETECTED_MARKERS[]`. Caller passes resource identifier string. Add `print_gitops_report()` function that samples first 10 ManagedClusters with "and X more" note if exceeded.

3. **Integrate Python detection at 9 points** across 6 resource types:
   | Resource | Integration Points |
   |----------|-------------------|
   | `BackupSchedule` | `BackupScheduleValidator.run()`, `PrimaryPrep._pause_backup_schedule()`, `Finalization._enable_backup_schedule()` |
   | `ManagedCluster` | `ManagedClusterValidator.run()`, `Activation._activate_clusters()` |
   | `MultiClusterObservability` | `Finalization` (refactor existing `_gitops_markers()` to use shared utility) |
   | `Restore` | `Activation._create_restore()` or `_verify_passive_restore()` |
   | `MultiClusterHub` | `MCHValidator.run()` |
   | `ConfigMap` (import-controller-config) | `ClusterValidator` auto-import checks |

4. **Integrate Bash detection at 4 points** in `scripts/preflight-check.sh` and `scripts/postflight-check.sh`: `check_backup_schedule()`, `check_managed_clusters()` (sample first 10), `check_mch_health()`, `check_restore_resources()`.

5. **Standardize output format** for both implementations:
   ```
   === GitOps-managed objects detected (N warnings) ===
   [primary] open-cluster-management-backup/BackupSchedule/acm-backup-schedule
     → label:app.kubernetes.io/managed-by=argocd
   [secondary] open-cluster-management/ManagedCluster/cluster1
     → annotation:argocd.argoproj.io/sync-wave
   ... and 15 more ManagedClusters
   ```

6. **Add `--skip-gitops-check` flag** to `acm_switchover.py` CLI args and Bash scripts. When set, skip all `collect_gitops_markers()` calls and `print_report()`.

7. **Add test fixtures** under `tests/fixtures/gitops_markers/` with JSON samples: `argocd_backupschedule.json`, `flux_mco.json`, `unmarked_mch.json`. Use in Python unit tests for `GitOpsCollector` and Bash validation script.

8. **Update `modules/finalization.py`** to import and use shared `detect_gitops_markers()` from `lib/gitops_detector.py`, removing duplicate `_gitops_markers()` method.

## Implementation Order

1. `lib/gitops_detector.py` + Python unit tests
2. Bash helper in `lib-common.sh` + fixture validation
3. Python integration points (one PR)
4. Bash integration points (separate PR)
5. CLI flag + docs update
