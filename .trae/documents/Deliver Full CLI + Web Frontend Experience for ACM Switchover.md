## Merge Decision
- Yes: merge both PRDs and both Architecture docs into unified system-level documents to reduce duplication and align requirements across CLI and Web.
- Target files to update directly: `docs/PRD.md` and `docs/ARCHITECTURE.md`.
- After merge, remove `docs/web-frontend/` (or move to `docs/appendices/` before deletion if you prefer archival).

## No-Redis Streaming
- Stream progress without Redis by tailing Kubernetes Job Pod logs from the backend and broadcasting over WebSocket.
- Use `read_namespaced_pod_log(..., follow=true, timestamps=true)`; parse JSON-formatted lines from the CLI.
- Persist structured events and operation snapshots in PostgreSQL for reconnects and history.

## JSON Event & State Format
- CLI emits JSON lines with clear types:
  - `EVENT`: `{type, timestamp, step, step_name, message, progress_pct}`.
  - `STATE`: full or incremental state snapshot mirroring the CLI state file.
- Prefix each stdout line with `EVENT:` or `STATE:` to simplify parsing.

## State & History Storage
- State file location: PVC path `'/var/lib/acm-switchover/state/<operation_id>.json'` passed via `--state-file`.
- Access policy: Jobs-only writer/reader; API does not mount the PVC (single-writer consistency, simpler permissions).
- Resume: subsequent Jobs mount the same PVC and reuse the exact `--state-file` path.
- History in PostgreSQL:
  - `switchovers`: operation summary + optional mirror of final state JSON (`state_json` JSONB).
  - `switchover_steps`: per-step status, timestamps, outputs.
  - `audit_logs`: user identity, action, parameters, result.
  - Optional `switchover_events`: raw/structured progress entries with retention.
- Retention: PVC state until explicit purge; DB summaries 12 months; steps/events 90 days (configurable).

## docs/PRD.md Edits
- Title: "ACM Switchover System PRD".
- Executive Summary: full experience via CLI and Web; OpenShift OAuth; REST/WebSocket; PVC-based state; DB-backed history.
- Personas: unify Platform Engineer, Operations Manager, SRE.
- Functional Requirements:
  - CLI FRs remain intact.
  - Add Web FRs: OAuth, RBAC, endpoints, WebSocket progress, dashboard/history, resume semantics.
  - Explicit requirement for PVC state (`--state-file`) and JSON event/state format.
- Non-Functional Requirements:
  - Performance targets: API < 500ms, WebSocket < 100ms latency; CLI targets retained.
  - Security: TLS, token handling, rate limiting, audit logging; Jobs-only PVC access.
  - Scalability: per-pod tailing and client reconnect; no Redis.
- Authentication Flow: Authorization Code with TokenReview validation.
- State & History: define paths, access, lifecycle, retention, purge.
- Success Metrics: adoption, success rate, duration, auth success, NPS.
- Roadmap: combined backend/frontend milestones; testing and packaging.
- Risks & Mitigations: token expiry, credential leakage, network partitions, PVC availability.
- Appendices: component-specific acceptance criteria for CLI and Web.

## docs/ARCHITECTURE.md Edits
- Title: "ACM Switchover System Architecture".
- High-Level Diagram: React SPA → FastAPI → K8s Job → Python CLI → ACM; include PVC and PostgreSQL; remove Redis.
- Component Architecture:
  - Frontend: OAuth flow, wizard, progress view, dashboard.
  - Backend: routers, OAuth client, TokenReview, Job manager, kubeconfig generator, log tailer, WebSocket broadcaster, DB models.
  - CLI: flags, state machine, JSON events; `--state-file` on PVC.
- Data Flow: OAuth → API → Job → Secret `KUBECONFIG` → CLI → state updates (PVC) → logs (WebSocket) → DB history.
- Deployment Architecture: OpenShift resources (Deployments for `api` and `ui`, PostgreSQL, PVC), OAuthClient, SA/Role for Job/PVC, NetworkPolicies, CORS.
- Database Schema: `switchovers`, `switchover_steps`, `audit_logs`, optional `switchover_events` with indexes.
- Event & State Schemas: define JSON fields and prefixes; snapshot frequency guidance.
- Scaling Without Redis: per-API-pod tailing; reconnect flows; optional sticky sessions via Route config.
- Security: token handling, TLS, RBAC checks, Jobs-only PVC access.
- Monitoring: Prometheus metrics and alert rules covering API latency, operation outcomes, WebSocket connections.
- Environment Variables: `OAUTH_*`, `FRONTEND_URL`, `DATABASE_URL`, `ACM_HUB_*`, `CLI_IMAGE`, `LOG_LEVEL`, `CORS_ORIGINS`.

## Removal of `docs/web-frontend/`
- After merging content into `docs/PRD.md` and `docs/ARCHITECTURE.md`, remove `docs/web-frontend/` to avoid drift.
- Optionally keep a short stub file that points to unified docs before deletion, or move originals to `docs/appendices/`.

## Implementation Steps (Post-Docs Approval)
- Align CLI stdout to emit `EVENT`/`STATE` JSON.
- Implement FastAPI OAuth, RBAC guard, Job manager, kubeconfig generator, log tailer, WebSocket broadcaster.
- Provision PVC (`RWX` preferred; if `RWO`, use per-operation claims) and mount in Jobs.
- Build React wizard and progress view; dashboard with history.
- Deploy to test cluster; run integration and performance tests; finalize retention/purge runbooks.

## Confirmed Decisions
- No Redis; WebSocket streaming via pod log tailing.
- JSON event/state format is accepted.
- PVC holds state files; Jobs-only access; API does not need read access to PVC.
- We will update `docs/PRD.md` and `docs/ARCHITECTURE.md` directly and remove `docs/web-frontend/` after merge.

## Next Actions
- On approval, perform the doc edits in `docs/PRD.md` and `docs/ARCHITECTURE.md`, then proceed with backend/frontend scaffolding aligned to the unified design.