"""
Fleet admission controller for the secure hardware fleet lab.

The controller evaluates whether a platform is eligible to join the trusted
fleet based on required component presence and component trust state.
"""

from typing import Dict, List

from component_types import REQUIRED_PLATFORM_COMPONENTS
from reason_codes import (
    FLEET_ADMISSION_ALLOWED,
    FLEET_ADMISSION_DENIED,
    POLICY_PASS,
    ROOT_OF_TRUST_EVIDENCE_MISSING,
    PLATFORM_SECURITY_MODULE_MISSING,
    MANAGEMENT_CONTROLLER_MISSING,
    NETWORK_DEVICE_MISSING,
    HOST_FIRMWARE_MISSING,
    ROOT_OF_TRUST_NOT_TRUSTED,
    PLATFORM_SECURITY_MODULE_NOT_TRUSTED,
    MANAGEMENT_CONTROLLER_NOT_TRUSTED,
    NETWORK_DEVICE_NOT_TRUSTED,
    HOST_FIRMWARE_NOT_TRUSTED,
    ENCRYPTION_DOMAIN_NOT_TRUSTED,
)


MISSING_REASON_BY_COMPONENT_TYPE: Dict[str, str] = {
    "ROOT_OF_TRUST": ROOT_OF_TRUST_EVIDENCE_MISSING,
    "PLATFORM_SECURITY_MODULE": PLATFORM_SECURITY_MODULE_MISSING,
    "MANAGEMENT_CONTROLLER": MANAGEMENT_CONTROLLER_MISSING,
    "NETWORK_DEVICE": NETWORK_DEVICE_MISSING,
    "MEMORY_STORAGE_ENCRYPTION": ENCRYPTION_DOMAIN_NOT_TRUSTED,
    "HOST_FIRMWARE": HOST_FIRMWARE_MISSING,
}


NOT_TRUSTED_REASON_BY_COMPONENT_TYPE: Dict[str, str] = {
    "ROOT_OF_TRUST": ROOT_OF_TRUST_NOT_TRUSTED,
    "PLATFORM_SECURITY_MODULE": PLATFORM_SECURITY_MODULE_NOT_TRUSTED,
    "MANAGEMENT_CONTROLLER": MANAGEMENT_CONTROLLER_NOT_TRUSTED,
    "NETWORK_DEVICE": NETWORK_DEVICE_NOT_TRUSTED,
    "MEMORY_STORAGE_ENCRYPTION": ENCRYPTION_DOMAIN_NOT_TRUSTED,
    "HOST_FIRMWARE": HOST_FIRMWARE_NOT_TRUSTED,
}


def evaluate_platform_admission(platform_id: str, components: List[dict]) -> dict:
    """
    Evaluate whether a platform is allowed to join the trusted fleet.

    A platform is admitted only when:
    - all required component types are present
    - every required component has status == trusted
    """

    failed_checks = []

    components_by_type = {
        component["component_type"]: component
        for component in components
    }

    for required_component_type in REQUIRED_PLATFORM_COMPONENTS:
        component = components_by_type.get(required_component_type)

        if component is None:
            failed_checks.append(
                {
                    "component_type": required_component_type,
                    "reason": MISSING_REASON_BY_COMPONENT_TYPE.get(
                        required_component_type,
                        "REQUIRED_COMPONENT_MISSING",
                    ),
                }
            )
            continue

        if component.get("status") != "trusted":
            failed_checks.append(
                {
                    "component_id": component["component_id"],
                    "component_type": component["component_type"],
                    "status": component.get("status"),
                    "reason": NOT_TRUSTED_REASON_BY_COMPONENT_TYPE.get(
                        component["component_type"],
                        "COMPONENT_NOT_TRUSTED",
                    ),
                }
            )

    if failed_checks:
        return {
            "platform_id": platform_id,
            "admission": "denied",
            "overall_status": "quarantined",
            "reason": FLEET_ADMISSION_DENIED,
            "failed_checks": failed_checks,
            "action": "block_fleet_join",
        }

    return {
        "platform_id": platform_id,
        "admission": "allowed",
        "overall_status": "trusted",
        "reason": FLEET_ADMISSION_ALLOWED,
        "failed_checks": [],
        "action": "allow_fleet_join",
        "policy_result": POLICY_PASS,
    }
