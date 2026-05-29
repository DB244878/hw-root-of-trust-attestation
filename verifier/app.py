from fastapi import FastAPI
from pydantic import BaseModel
import uuid

from db import (
    init_db,
    register_device,
    get_device,
    update_device_status,
    get_all_devices
)

app = FastAPI(
    title="Cloud Fleet Attestation Verifier",
    description="SQLite-backed verifier API for hardware root-of-trust attestation lab",
    version="0.2.0"
)

challenges = {}

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

@app.on_event("startup")
def startup():
    init_db()

@app.get("/")
def root():
    return {
        "service": "Cloud Fleet Attestation Verifier",
        "status": "running",
        "version": "0.2.0",
        "storage": "sqlite"
    }

@app.post("/register_device")
def register(request: RegisterDeviceRequest):
    register_device(
        request.device_id,
        request.expected_firmware_hash,
        request.min_firmware_version
    )

    return {
        "device_id": request.device_id,
        "status": "registered",
        "message": "Device registered in fleet database"
    }

@app.post("/challenge")
def create_challenge(request: ChallengeRequest):
    device = get_device(request.device_id)

    if device is None:
        return {
            "device_id": request.device_id,
            "status": "rejected",
            "reason": "Unknown device. Register device first."
        }

    nonce = str(uuid.uuid4())
    challenges[request.device_id] = nonce

    return {
        "device_id": request.device_id,
        "nonce": nonce,
        "message": "Challenge created"
    }

@app.post("/attest")
def attest(request: AttestationRequest):
    expected_nonce = challenges.get(request.device_id)
    device = get_device(request.device_id)

    if device is None:
        return {
            "device_id": request.device_id,
            "status": "quarantined",
            "reason": "Unknown device"
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
        "last_seen": updated_device["last_seen"]
    }

@app.get("/devices")
def devices():
    return get_all_devices()
