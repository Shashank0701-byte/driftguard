from typing import List
from .differ import DriftEvent, Severity

WEIGHTS = { Severity.HIGH: 10, Severity.MEDIUM: 5, Severity.LOW: 2 }

def score(drifts: List[DriftEvent]) -> int:
    """Return total risk score for a set of drift events."""
    return sum(WEIGHTS[d.severity] for d in drifts)