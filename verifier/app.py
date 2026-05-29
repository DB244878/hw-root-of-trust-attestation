from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
import uuid

app = FastAPI(
    title="Cloud Fleet Attestation Verifier",
    description="Phase 2 verifier API for hardware root-of-trust attestation lab",
    version="0.1.0"
)

devices = {
    "esp32-test-01": {
        "device_id": "esp32-test-01",
        "expected_firmware_hash": "firmware_v1_hash",
        "status": "registered",
        "last_seen": None,
        "reason": "Device registered but not yet attested"
    }
}

challenges = {}

class ChallengeRequest(BaseModel):
    device_id: str

class AttestationRequest(BaseModel):
    device_id: str
    nonce: str
    firmware_hash: str
    firmware_version: int
    signature: str

@app.get("/")
def root():
    return {
        "service": "Cloud Fleet Attestation Verifier",
        "status": "running",
        "version": "0.1.0"
    }

@app.post("/challenge")
def create_challenge(request: ChallengeRequest):
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
    device = devices.get(request.device_id)

    if device is None:
        return {
            "device_id": request.device_id,
            "status": "quarantined",
            "reason": "Unknown device"
        }

    if expected_nonce != request.nonce:
        device["status"] = "quarantined"
        device["reason"] = "Invalid or missing nonce"
    elif request.firmware_hash != device["expected_firmware_hash"]:
        device["status"] = "quarantined"
        device["reason"] = "Firmware hash mismatch"
    else:
        device["status"] = "trusted"
        device["reason"] = "Nonce and firmware hash matched"

    device["last_seen"] = datetime.utcnow().isoformat()

    return {
        "device_id": request.device_id,
        "status": device["status"],
        "reason": device["reason"],
        "last_seen": device["last_seen"]
    }

@app.get("/devices")
def get_devices():
    return devices
