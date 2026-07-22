from prometheus_client import Counter, Histogram

REQUEST_COUNT = Counter(
    "sentinel_http_requests_total", "HTTP requests", ["method", "path", "status"]
)
REQUEST_LATENCY = Histogram(
    "sentinel_http_request_duration_seconds", "HTTP request latency", ["method", "path"]
)
PROBE_COUNT = Counter(
    "sentinel_probes_total", "Dependency probes", ["kind", "status"]
)
PROBE_LATENCY = Histogram(
    "sentinel_probe_duration_seconds", "Probe latency", ["kind"]
)
