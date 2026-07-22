# Architecture

## Context
CloudCart Sentinel is a reliability control plane for e-commerce and managed-hosting operations. The first release favors a modular monolith because the domain is cohesive and the operational burden is lower than premature microservices.

## Components
- **API:** validates commands, authenticates operators, and exposes health/SLO data.
- **Probe runner:** executes bounded HTTP, PostgreSQL, Redis, and DNS checks.
- **Repository layer:** isolates SQLAlchemy from route and business logic.
- **PostgreSQL:** source of truth for monitored services and immutable probe history.
- **Redis:** readiness dependency and future home for distributed locks, cache, and job queues.
- **Prometheus/Grafana:** metrics and dashboards.

## Scaling path
1. Move scheduled probing into an independent worker deployment.
2. Use Redis Streams or SQS for durable work distribution.
3. Partition probe history by month and add retention policies.
4. Add OpenTelemetry tracing and managed Prometheus.
5. Deploy private subnets, NAT, Secrets Manager, WAF, TLS, and Aurora/RDS Multi-AZ.

## Failure strategy
Probe failures are data, not application crashes. Timeouts and unexpected exceptions become persisted DOWN results. Database and cache failures fail readiness so the orchestrator stops routing traffic.
