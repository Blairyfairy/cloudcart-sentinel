# Product brief

## Problem
Support engineers lose time switching between monitoring tools, ticket history, database consoles, and ad-hoc scripts. This increases mean time to acknowledge and repair customer-impacting incidents.

## Users
- L2/L3 hosting support engineer
- database reliability engineer
- e-commerce product owner
- incident commander

## MVP outcomes
- Register a dependency in under one minute.
- Execute a probe and retrieve evidence in under ten seconds.
- Calculate rolling SLO attainment without spreadsheets.
- Correlate every API request with a request ID.

## KPIs
- MTTA and MTTR
- percentage of incidents with complete probe evidence
- false-positive alert rate
- SLO attainment per service
- p50/p95 probe latency

## Roadmap
### Now
HTTP/PostgreSQL/Redis/DNS checks, API, metrics, Docker, Terraform, tests.
### Next
Scheduler workers, Slack/PagerDuty notifications, alert deduplication, maintenance windows.
### Later
Multi-tenant RBAC, anomaly detection, cost recommendations, automated remediation approvals.
