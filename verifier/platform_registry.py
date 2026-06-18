"""
Platform and component registry for the secure hardware fleet lab.

This module models a data-center platform as a collection of security-sensitive
hardware and firmware components. A platform can later be evaluated for fleet
admission only after each required component is registered and assessed.
"""

from dataclasses import dataclass, asdict
from typing import Dict, List, Optional

from component_types import REQUIRED_PLATFORM_COMPONENTS


@dataclass
class Platform:
    platform_id: str
    platform_type: str
    location: str
    owner: str
    status: str = "registered"


@dataclass
class Component:
    platform_id: str
    component_id: str
    component_type: str
    supplier: str
    expected_firmware_hash: str
    min_firmware_version: int
    status: str = "registered"
    reason: str = "PENDING_ATTESTATION"


class PlatformRegistry:
    def __init__(self):
        self.platforms: Dict[str, Platform] = {}
        self.components: Dict[str, Component] = {}

    def register_platform(
        self,
        platform_id: str,
        platform_type: str,
        location: str,
        owner: str,
    ) -> dict:
        platform = Platform(
            platform_id=platform_id,
            platform_type=platform_type,
            location=location,
            owner=owner,
        )
        self.platforms[platform_id] = platform
        return asdict(platform)

    def register_component(
        self,
        platform_id: str,
        component_id: str,
        component_type: str,
        supplier: str,
        expected_firmware_hash: str,
        min_firmware_version: int,
    ) -> dict:
        if platform_id not in self.platforms:
            raise ValueError(f"Unknown platform_id: {platform_id}")

        component = Component(
            platform_id=platform_id,
            component_id=component_id,
            component_type=component_type,
            supplier=supplier,
            expected_firmware_hash=expected_firmware_hash,
            min_firmware_version=min_firmware_version,
        )
        self.components[component_id] = component
        return asdict(component)


    def update_component_status(
        self,
        component_id: str,
        status: str,
        reason: str,
    ) -> Optional[dict]:
        component = self.components.get(component_id)

        if component is None:
            return None

        component.status = status
        component.reason = reason
        return asdict(component)

    def get_platform(self, platform_id: str) -> Optional[dict]:
        platform = self.platforms.get(platform_id)
        if platform is None:
            return None
        return asdict(platform)

    def get_components_for_platform(self, platform_id: str) -> List[dict]:
        return [
            asdict(component)
            for component in self.components.values()
            if component.platform_id == platform_id
        ]

    def get_missing_required_components(self, platform_id: str) -> List[str]:
        registered_types = {
            component.component_type
            for component in self.components.values()
            if component.platform_id == platform_id
        }

        return [
            required_type
            for required_type in REQUIRED_PLATFORM_COMPONENTS
            if required_type not in registered_types
        ]
