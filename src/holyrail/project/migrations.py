from __future__ import annotations

from copy import deepcopy
from typing import Any

from holyrail.models.project import CURRENT_APP_VERSION, CURRENT_SCHEMA_VERSION


class ProjectMigrationError(ValueError):
    pass


def migrate_project_data(data: dict[str, Any]) -> dict[str, Any]:
    migrated = deepcopy(data)
    version = int(migrated.get("schema_version", 1))

    if version > CURRENT_SCHEMA_VERSION:
        raise ProjectMigrationError(
            f"Project schema {version} is newer than supported schema " f"{CURRENT_SCHEMA_VERSION}."
        )

    if version == 1:
        migrated = _migrate_v1_to_v2(migrated)
        version = 2

    if version == 2:
        migrated = _migrate_v2_to_v3(migrated)
        version = 3

    migrated["schema_version"] = version
    return migrated


def _migrate_v1_to_v2(data: dict[str, Any]) -> dict[str, Any]:
    app_version = str(data.pop("app_version", CURRENT_APP_VERSION))
    data.setdefault("created_with_app_version", app_version)
    data.setdefault("last_saved_with_app_version", app_version)
    data["schema_version"] = 2
    return data


def _migrate_v2_to_v3(data: dict[str, Any]) -> dict[str, Any]:
    metrics = data.setdefault("metrics", {})
    metrics.setdefault("analysis_report", {})
    data["schema_version"] = 3
    return data
