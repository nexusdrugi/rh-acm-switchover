% acm-switchover(1) ACM Switchover User Manuals
% RH ACM Switchover Maintainers
% 2025-12-12

# NAME
acm-switchover - Automate hub switchover with stateful, idempotent phases

# SYNOPSIS
**acm-switchover** [OPTIONS]

# DESCRIPTION
Automates switchover from a primary ACM hub to a secondary hub with validation,
activation and finalization phases. Supports passive sync and full restore.

# OPTIONS
--primary-context, --secondary-context, --method, --old-hub-action, --state-file, --dry-run, --validate-only, --version

# ENVIRONMENT
ACM_SWITCHOVER_STATE_DIR - default state directory when --state-file is not provided.

# SEE ALSO
acm-switchover-rbac(1), acm-switchover-state(1)
