from __future__ import annotations

from .provenance import generate_provenance


def bind_execution_provenance(
    *,
    request: dict,
    resolution: dict,
) -> dict:

    transformation = {
        "actor": request.get("actor_class"),
        "operation": request.get("operation"),
        "input_state": request,
        "output_state": resolution.get("consequence"),
        "authority_basis": resolution.get("authority"),
    }

    provenance = generate_provenance(
        origin={
            "source_anchor": request.get("source_anchor"),
        },
        transformations=[transformation],
        current_state=resolution,
    )

    return {
        "resolution": resolution,
        "provenance": provenance,
    }
