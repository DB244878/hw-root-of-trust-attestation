from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uuid

from db import (
    init_db,
    register_device,
    get_device,
    update_device_status,
    get_all_devices,
)

from platform_registry import PlatformRegistry
from component_types import REQUIRED_PLATFORM_COMPONENTS
from fleet_admission_controller import evaluate_platform_admission

app = FastAPI(
    title="Secure Hardware Fleet Verifier",
    description="Verifier API for hardware root-of-trust attestation and platform-level fleet security modeling",
    version="0.3.0",
)

challenges = {}
platform_registry = PlatformRegistry()


class RegisterDeviceRequest(BaseModel):
    device_id: str
    expected_firmware_hash: str
    min_firmware_version: int


class ChallengeRequest(BaseModel):
    device_id: str


class AttestationRequest(BaseModel):
    device_id: str
    nonce: str
    firmware_hash: str
    firmware_version: int
    signature: str


class RegisterPlatformRequest(BaseModel):
    platform_id: str
    platform_type: str
    location: str
    owner: str


class RegisterComponentRequest(BaseModel):
    platform_id: str
    component_id: str
    component_type: str
    supplier: str
    expected_firmware_hash: str
    min_firmware_version: int


class UpdateComponentStatusRequest(BaseModel):
    component_id: str
    status: str
    reason: str


@app.on_event("startup")
def startup():
    init_db()


@app.get("/")
def root():
    return {
        "service": "Secure Hardware Fleet Verifier",
        "status": "running",
        "version": "0.3.0",
        "storage": "sqlite_for_device_attestation_in_memory_for_platform_registry",
        "capabilities": [
            "device_registration",
            "challenge_response_attestation",
            "firmware_hash_validation",
            "rollback_detection",
            "platform_registration",
            "component_registration",
            "missing_required_component_detection",
        ],
    }


@app.post("/register_device")
def register(request: RegisterDeviceRequest):
    register_device(
        request.device_id,
        request.expected_firmware_hash,
        request.min_firmware_version,
    )

    return {
        "device_id": request.device_id,
        "status": "registered",
        "message": "Device registered in fleet database",
    }


@app.post("/challenge")
def create_challenge(request: ChallengeRequest):
    device = get_device(request.device_id)

    if device is None:
        return {
            "device_id": request.device_id,
            "status": "rejected",
            "reason": "Unknown device. Register device first.",
        }

    nonce = str(uuid.uuid4())
    challenges[request.device_id] = nonce

    return {
        "device_id": request.device_id,
        "nonce": nonce,
        "message": "Challenge created",
    }


@app.post("/attest")
def attest(request: AttestationRequest):
    expected_nonce = challenges.get(request.device_id)
    device = get_device(request.device_id)

    if device is None:
        return {
            "device_id": request.device_id,
            "status": "quarantined",
            "reason": "Unknown device",
        }

    if expected_nonce != request.nonce:
        status = "quarantined"
        reason = "Invalid or missing nonce"
    elif request.firmware_version < device["min_firmware_version"]:
        status = "quarantined"
        reason = "Rollback detected"
    elif request.firmware_hash != device["expected_firmware_hash"]:
        status = "quarantined"
        reason = "Firmware hash mismatch"
    else:
        status = "trusted"
        reason = "Nonce, firmware hash, and firmware version matched policy"

    update_device_status(request.device_id, status, reason)

    updated_device = get_device(request.device_id)

    return {
        "device_id": request.device_id,
        "status": updated_device["status"],
        "reason": updated_device["reason"],
        "last_seen": updated_device["last_seen"],
    }


@app.get("/devices")
def devices():
    return get_all_devices()


@app.post("/platform/register")
def register_platform(request: RegisterPlatformRequest):
    platform = platform_registry.register_platform(
        platform_id=request.platform_id,
        platform_type=request.platform_type,
        location=request.location,
        owner=request.owner,
    )

    return {
        "status": "registered",
        "platform": platform,
        "message": "Platform registered for secure fleet admission modeling",
    }


@app.get("/platform/{platform_id}")
def get_platform(platform_id: str):
    platform = platform_registry.get_platform(platform_id)

    if platform is None:
        raise HTTPException(status_code=404, detail="Unknown platform_id")

    return platform


@app.post("/component/register")
def register_component(request: RegisterComponentRequest):
    if request.component_type not in REQUIRED_PLATFORM_COMPONENTS:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Unsupported component_type",
                "allowed_component_types": REQUIRED_PLATFORM_COMPONENTS,
            },
        )

    try:
        component = platform_registry.register_component(
            platform_id=request.platform_id,
            component_id=request.component_id,
            component_type=request.component_type,
            supplier=request.supplier,
            expected_firmware_hash=request.expected_firmware_hash,
            min_firmware_version=request.min_firmware_version,
        )
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error

    return {
        "status": "registered",
        "component": component,
        "message": "Component registered under platform",
    }


@app.get("/platform/{platform_id}/components")
def get_platform_components(platform_id: str):
    platform = platform_registry.get_platform(platform_id)

    if platform is None:
        raise HTTPException(status_code=404, detail="Unknown platform_id")

    return {
        "platform_id": platform_id,
        "components": platform_registry.get_components_for_platform(platform_id),
    }


@app.get("/platform/{platform_id}/missing-components")
def get_missing_components(platform_id: str):
    platform = platform_registry.get_platform(platform_id)

    if platform is None:
        raise HTTPException(status_code=404, detail="Unknown platform_id")

    missing_components = platform_registry.get_missing_required_components(platform_id)

    return {
        "platform_id": platform_id,
        "required_components": REQUIRED_PLATFORM_COMPONENTS,
        "missing_components": missing_components,
        "ready_for_platform_admission_evaluation": len(missing_components) == 0,
    }

@app.get("/fleet/admission/{platform_id}")
def get_fleet_admission(platform_id: str):
    platform = platform_registry.get_platform(platform_id)

    if platform is None:
        raise HTTPException(status_code=404, detail="Unknown platform_id")

    components = platform_registry.get_components_for_platform(platform_id)
    return evaluate_platform_admission(platform_id, components)

@app.post("/component/status")
def update_component_status(request: UpdateComponentStatusRequest):
    if request.status not in ["registered", "trusted", "quarantined"]:
        raise HTTPException(
            status_code=400,
            detail="status must be one of: registered, trusted, quarantined",
        )

    component = platform_registry.update_component_status(
        component_id=request.component_id,
        status=request.status,
        reason=request.reason,
    )

    if component is None:
        raise HTTPException(status_code=404, detail="Unknown component_id")

    return {
        "status": "updated",
        "component": component,
        "message": "Component trust state updated",
    }

