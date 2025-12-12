# ACM Switchover Helm Chart

- Provides a Job to run validation or execution of switchover
- Mounts a PVC for state at `/var/lib/acm-switchover`
- Sets `ACM_SWITCHOVER_STATE_DIR` accordingly
- Optional kubeconfig secret mount under `/app/.kube`

## Values

- `image.repository`: container repository
- `image.tag`: image tag
- `rbac.create`: create namespace/SA/Role/RoleBinding
- `rbac.namespace`: namespace to deploy job/resources
- `kubeconfig.enabled`: mount kubeconfig secret
- `kubeconfig.secretName`: secret name containing kubeconfig
- `kubeconfig.key`: key within secret (default `config`)

## Install (dry-run)

```bash
helm template --debug --dry-run acm-switchover ./packaging/helm/acm-switchover
```
