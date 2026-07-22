from app.schemas import SLORead


def calculate_slo(service_id, total: int, healthy: int, target: float) -> SLORead:
    availability = 100.0 if total == 0 else healthy / total * 100
    allowed_failure = 100 - target
    actual_failure = 100 - availability
    remaining = 100.0 if allowed_failure == 0 and actual_failure == 0 else (
        max(0.0, (allowed_failure - actual_failure) / allowed_failure * 100)
        if allowed_failure > 0
        else 0.0
    )
    return SLORead(
        service_id=service_id,
        sample_size=total,
        availability_percent=round(availability, 4),
        target_percent=target,
        budget_remaining_percent=round(remaining, 2),
        meeting_slo=availability >= target,
    )
