from uuid import uuid4
from app.services.slo import calculate_slo

def test_slo_meets_target():
    result = calculate_slo(uuid4(), total=1000, healthy=999, target=99.9)
    assert result.meeting_slo is True
    assert result.availability_percent == 99.9
    assert result.budget_remaining_percent == 0.0

def test_empty_sample_is_not_false_alarm():
    result = calculate_slo(uuid4(), total=0, healthy=0, target=99.9)
    assert result.availability_percent == 100.0
    assert result.meeting_slo is True
