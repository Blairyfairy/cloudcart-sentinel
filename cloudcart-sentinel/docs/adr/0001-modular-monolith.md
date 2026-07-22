# ADR 0001: Start as a modular monolith

**Status:** Accepted

## Decision
Use one deployable FastAPI application with strict internal modules rather than independent microservices.

## Rationale
The product has one team, one transactional data model, and low initial throughput. A modular monolith preserves clear boundaries while avoiding distributed tracing, deployment, and consistency complexity before it creates customer value.

## Consequences
- Faster local development and simpler incident response.
- Business modules can later be extracted behind queue or HTTP contracts.
- The team must enforce module boundaries in reviews.
