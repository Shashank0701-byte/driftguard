import docker
from typing import Dict, Any


def _image_name(container) -> str:
    """Best-effort image identifier without crashing on missing local metadata."""
    config_image = container.attrs.get("Config", {}).get("Image")

    try:
        image = container.image
        if image.tags:
            return image.tags[0]
        if getattr(image, "id", None):
            return image.id[:12]
    except docker.errors.DockerException:
        pass

    return config_image or "<missing-image>"


def snapshot_live(socket: str = "unix:///var/run/docker.sock") -> Dict[str, Any]:
    """Capture current live Docker container state."""
    client = docker.DockerClient(base_url=socket)
    containers = client.containers.list(all=True)
    live = {}

    for c in containers:
        # Use compose service label if available, else container name
        labels = c.labels or {}
        service_name = labels.get("com.docker.compose.service", c.name)

        # Parse ports into same format as compose
        ports = []
        for internal, bindings in (c.ports or {}).items():
            if bindings:
                for b in bindings:
                    ports.append(f"{b['HostPort']}:{internal.split('/')[0]}")

        # Parse environment variables
        env = {}
        for e in (c.attrs.get("Config", {}).get("Env") or []):
            if "=" in e:
                k, v = e.split("=", 1)
                env[k] = v

        live[service_name] = {
            "image":       _image_name(c),
            "ports":       ports,
            "environment": env,
            "status":      c.status,
            "container_id": c.short_id,
        }

    client.close()
    return live
