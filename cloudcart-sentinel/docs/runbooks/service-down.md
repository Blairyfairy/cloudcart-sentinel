# Runbook: service reported DOWN

1. Confirm alert scope and customer impact.
2. Retrieve the most recent probe and request ID.
3. Re-run the probe once to rule out transient network failure.
4. For HTTP: inspect DNS, TLS, status code, redirect chain, and upstream latency.
5. For PostgreSQL: inspect connection saturation, locks, replication, CPU, memory, and disk.
6. For Redis: inspect reachability, memory policy, blocked clients, persistence, and failover state.
7. Check recent deployment and configuration changes.
8. Mitigate: rollback, fail over, scale, clear only safe caches, or disable a failing dependency.
9. Record timeline, root cause, customer communication, and preventive action.

Never delete evidence or perform destructive remediation without a tested rollback path.
