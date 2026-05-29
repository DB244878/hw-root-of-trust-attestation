# Cloud Fleet Attestation Lab

## Hardware Root of Trust + Infrastructure Verification

A hands-on hardware security project demonstrating a simplified hardware-backed attestation flow using an ESP32, ATECC608A secure element, and verifier-side policy enforcement.

This project models how modern cloud infrastructure determines whether a device or node should be trusted before allowing it into a secure fleet.

---

## Latest Milestone (May 2026)

Phase 2 introduces a cloud-style verifier service implementing challenge-response attestation and trust policy enforcement.

### Implemented

* FastAPI verifier service
* Challenge generation API (`/challenge`)
* Attestation API (`/attest`)
* Nonce-based challenge-response flow
* Firmware hash validation
* Trusted / Quarantined policy decisions
* Interactive Swagger/OpenAPI interface
* Architecture documentation

### Example Attestation Flow

Device
→ Request Challenge
→ Receive Nonce
→ Submit Attestation Evidence
→ Verifier Policy Evaluation
→ Trusted or Quarantined

### Example Outcomes

TRUSTED

* Device known
* Nonce valid
* Firmware hash matches approved policy

QUARANTINED

* Unknown device
* Invalid nonce
* Firmware hash mismatch

---

## Cloud Fleet Attestation Verifier

The verifier service models how a cloud control plane evaluates attestation evidence before admitting infrastructure into a trusted fleet.

Current API Endpoints:

GET /

POST /challenge

POST /attest

GET /devices

The verifier currently performs:

* Nonce validation
* Firmware hash validation
* Trust policy evaluation
* Quarantine decisions

Future versions will add:

* SQLite device registry
* Device enrollment APIs
* Real ATECC608A signature verification
* Firmware allow-list management
* Rollback protection
* Fleet dashboard
* Compliance reporting

---

## Current Architecture

+-----------------------------+
| Device                      |
| ESP32 + ATECC608A           |
+-------------+---------------+
|
|
v
+-----------------------------+
| Challenge API               |
| Generates Nonce             |
+-------------+---------------+
|
|
v
+-----------------------------+
| Attestation API             |
| Receives Evidence           |
+-------------+---------------+
|
|
v
+-----------------------------+
| Policy Engine               |
| Firmware Validation         |
| Trust Decisions             |
+-------------+---------------+
|
|
v
+-----------------------------+
| Trusted / Quarantined       |
+-----------------------------+

---

## Roadmap

### Phase 1 (Completed)

* ESP32 device identity
* ATECC608A integration
* Firmware measurement
* Signed attestation quotes
* Fleet policy simulation

### Phase 2 (In Progress)

* FastAPI verifier service
* Challenge-response attestation
* Policy engine
* Trust and quarantine decisions

### Phase 2.1

* SQLite fleet database
* Device enrollment
* Firmware allow-lists

### Phase 2.2

* Real signature verification
* Public key management
* Attestation quote validation

### Phase 3

* Fleet dashboard
* Compliance reporting
* Attestation history
* Multi-device fleet management

---

## Why This Matters

Modern cloud platforms must verify infrastructure trustworthiness before allowing systems to participate in production workloads.

This project demonstrates the same high-level concepts used in:

* Hardware Root of Trust
* Secure Boot
* DICE Attestation
* Platform Integrity Verification
* Datacenter Security
* Infrastructure Fleet Management
* Confidential Computing
* Cloud Control Plane Security

The objective is to understand not only how devices establish identity, but how cloud infrastructure makes trust decisions at fleet scale.
