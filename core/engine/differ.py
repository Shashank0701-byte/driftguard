from typing import Dict, Any, List
from dataclasses import dataclass
from enum import Enum

class Severity(str, Enum):
    HIGH   = "HIGH"
    MEDIUM = "MEDIUM"
    LOW    = "LOW"

@dataclass
class DriftEvent:
    service:  str
    field:    str
    expected: Any
    actual:   Any
    severity: Severity

def diff(desired: Dict[str, Any], actual: Dict[str, Any]) -> List[DriftEvent]:
    """Compare desired state (compose) vs actual state (live Docker)."""
    drifts = []

    # Check for unexpected containers (running but not in compose)
    for service in actual:
        if service not in desired:
            drifts.append(DriftEvent(
                service=service,
                field="existence",
                expected=None,
                actual="running",
                severity=Severity.MEDIUM
            ))

    # Check for missing containers (in compose but not running)
    for service in desired:
        if service not in actual:
            drifts.append(DriftEvent(
                service=service,
                field="existence",
                expected="running",
                actual=None,
                severity=Severity.HIGH
            ))
            continue

        d = desired[service]
        a = actual[service]

        # Image drift — most critical
        if d.get("image") and d["image"] != a.get("image"):
            drifts.append(DriftEvent(
                service=service,
                field="image",
                expected=d["image"],
                actual=a.get("image"),
                severity=Severity.HIGH
            ))

        # Port drift
        desired_ports = set(str(p) for p in d.get("ports", []))
        actual_ports  = set(str(p) for p in a.get("ports", []))
        if desired_ports != actual_ports:
            drifts.append(DriftEvent(
                service=service,
                field="ports",
                expected=list(desired_ports),
                actual=list(actual_ports),
                severity=Severity.MEDIUM
            ))

        # Environment drift (only keys defined in compose)
        for key, val in (d.get("environment") or {}).items():
            actual_val = a.get("environment", {}).get(key)
            if str(val) != str(actual_val or ""):
                drifts.append(DriftEvent(
                    service=service,
                    field=f"env.{key}",
                    expected=val,
                    actual=actual_val,
                    severity=Severity.LOW
                ))

    return drifts