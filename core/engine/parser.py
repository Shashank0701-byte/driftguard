import yaml
from pathlib import Path
from typing import Dict, Any

def parse_compose(path: str) -> Dict[str, Any]:
    """Parse a Docker Compose file and return its contents as a dictionary."""
    compose_path = Path(path)
    if not compose_path.is_file():
        raise FileNotFoundError(f"Compose file not found at: {path}")
    
    with compose_path.open() as f:
        data = yaml.safe_load(f)

    services = data.get("services", {})
    desired = {}

    for name, cfg in services.items():
        desired[name] = {
            "image": cfg.get("image"),
            "ports": cfg.get("ports", []),
            "environment": cfg.get("environment", {}),
            "volumes": cfg.get("volumes", []),
            "restart": cfg.get("restart", "no"),
            "commands": cfg.get("command",),
        }
    return desired
