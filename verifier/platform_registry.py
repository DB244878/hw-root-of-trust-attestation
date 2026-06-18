"""
SQLite-backed platform and component registry for the secure hardware fleet lab.

This module models a data-center platform as a collection of security-sensitive
hardware and firmware components. Registry state persists across API restarts.
"""

import sqlite3
from pathlib import Path
from typing import List, Optional

from component_types import REQUIRED_PLATFORM_COMPONENTS


DB_PATH = Path(__file__).parent / "platforms.db"


class PlatformRegistry:
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self._init_db()

    def _connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS platforms (
                    platform_id TEXT PRIMARY KEY,
                    platform_type TEXT NOT NULL,
                    location TEXT NOT NULL,
                    owner TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'registered',
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS components (
                    component_id TEXT PRIMARY KEY,
                    platform_id TEXT NOT NULL,
                    component_type TEXT NOT NULL,
                    supplier TEXT NOT NULL,
                    expected_firmware_hash TEXT NOT NULL,
                    min_firmware_version INTEGER NOT NULL,
                    status TEXT NOT NULL DEFAULT 'registered',
                    reason TEXT NOT NULL DEFAULT 'PENDING_ATTESTATION',
                    last_updated TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(platform_id) REFERENCES platforms(platform_id)
                )
                """
            )

    def register_platform(
        self,
        platform_id: str,
        platform_type: str,
        location: str,
        owner: str,
    ) -> dict:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO platforms (
                    platform_id,
                    platform_type,
                    location,
                    owner,
                    status
                )
                VALUES (?, ?, ?, ?, 'registered')
                ON CONFLICT(platform_id) DO UPDATE SET
                    platform_type = excluded.platform_type,
                    location = excluded.location,
                    owner = excluded.owner,
                    status = 'registered'
                """,
                (platform_id, platform_type, location, owner),
            )

        platform = self.get_platform(platform_id)
        if platform is None:
            raise RuntimeError("Platform registration failed")
        return platform

    def register_component(
        self,
        platform_id: str,
        component_id: str,
        component_type: str,
        supplier: str,
        expected_firmware_hash: str,
        min_firmware_version: int,
    ) -> dict:
        if self.get_platform(platform_id) is None:
            raise ValueError(f"Unknown platform_id: {platform_id}")

        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO components (
                    component_id,
                    platform_id,
                    component_type,
                    supplier,
                    expected_firmware_hash,
                    min_firmware_version,
                    status,
                    reason,
                    last_updated
                )
                VALUES (?, ?, ?, ?, ?, ?, 'registered', 'PENDING_ATTESTATION', CURRENT_TIMESTAMP)
                ON CONFLICT(component_id) DO UPDATE SET
                    platform_id = excluded.platform_id,
                    component_type = excluded.component_type,
                    supplier = excluded.supplier,
                    expected_firmware_hash = excluded.expected_firmware_hash,
                    min_firmware_version = excluded.min_firmware_version,
                    status = 'registered',
                    reason = 'PENDING_ATTESTATION',
                    last_updated = CURRENT_TIMESTAMP
                """,
                (
                    component_id,
                    platform_id,
                    component_type,
                    supplier,
                    expected_firmware_hash,
                    min_firmware_version,
                ),
            )

        component = self.get_component(component_id)
        if component is None:
            raise RuntimeError("Component registration failed")
        return component

    def update_component_status(
        self,
        component_id: str,
        status: str,
        reason: str,
    ) -> Optional[dict]:
        if self.get_component(component_id) is None:
            return None

        with self._connect() as conn:
            conn.execute(
                """
                UPDATE components
                SET status = ?,
                    reason = ?,
                    last_updated = CURRENT_TIMESTAMP
                WHERE component_id = ?
                """,
                (status, reason, component_id),
            )

        return self.get_component(component_id)

    def get_platform(self, platform_id: str) -> Optional[dict]:
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT
                    platform_id,
                    platform_type,
                    location,
                    owner,
                    status,
                    created_at
                FROM platforms
                WHERE platform_id = ?
                """,
                (platform_id,),
            ).fetchone()

        if row is None:
            return None
        return dict(row)

    def get_component(self, component_id: str) -> Optional[dict]:
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT
                    platform_id,
                    component_id,
                    component_type,
                    supplier,
                    expected_firmware_hash,
                    min_firmware_version,
                    status,
                    reason,
                    last_updated
                FROM components
                WHERE component_id = ?
                """,
                (component_id,),
            ).fetchone()

        if row is None:
            return None
        return dict(row)

    def get_components_for_platform(self, platform_id: str) -> List[dict]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT
                    platform_id,
                    component_id,
                    component_type,
                    supplier,
                    expected_firmware_hash,
                    min_firmware_version,
                    status,
                    reason,
                    last_updated
                FROM components
                WHERE platform_id = ?
                ORDER BY component_type, component_id
                """,
                (platform_id,),
            ).fetchall()

        return [dict(row) for row in rows]

    def get_missing_required_components(self, platform_id: str) -> List[str]:
        components = self.get_components_for_platform(platform_id)

        registered_types = {
            component["component_type"]
            for component in components
        }

        return [
            required_type
            for required_type in REQUIRED_PLATFORM_COMPONENTS
            if required_type not in registered_types
        ]
