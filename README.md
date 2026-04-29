# Caliptra-Inspired Hardware Attestation Lab

## Overview

This project implements a minimal, end-to-end **reference model** of a hardware-rooted attestation system, inspired by modern cloud infrastructure security architectures such as Caliptra, AWS Nitro, and Azure attestation services.

The system demonstrates how a device proves its runtime state and how a cloud control plane evaluates that state to make trust decisions—extended with **rollback protection (SVN enforcement)**.

---

## System Architecture

### Architecture Overview

```text id="arch1"
+---------------------------+        +-----------------------------+
| Device (Root of Trust)    |        | Cloud Verifier              |
|---------------------------|        |-----------------------------|
| ROM Boot                  |        | Signature Verification      |
| DICE Identity Chain       | -----> | Policy Engine               |
| Firmware Measurement      |        | SVN (Rollback) Enforcement  |
| Attestation (Sign)        |        | Allow / Deny Decision       |
+---------------------------+        +-----------------------------+

        Attestation Evidence (MEASURE + SVN + SIGNATURE)
```

---

## System Components

### 1. Device (Simulated Root of Trust)

Implemented on Arduino Mega 2560.

Models:

* ROM-style boot initialization
* DICE-style identity derivation
* Firmware measurement
* Security Version Number (SVN)
* Attestation generation

---

### 2. Verifier (Cloud Control Plane)

Trust decisions are computed dynamically using attestation verification logic.
Nodes are quarantined automatically based on policy violations.

Implemented in Python.

Responsibilities:

* Signature validation
* Firmware integrity validation
* **Rollback protection (SVN policy)**
* Trust decision (allow / deny)

---

## End-to-End Flow

```text id="flow1"
Device Boot:
  ROM → Measure → Derive Identity → Generate Attestation

Verifier:
  Request attestation
    → Validate signature
    → Validate firmware measurement
    → Enforce SVN (no rollback)
    → Apply policy
    → Allow / Deny
```

---

## Fleet-Level Simulation

Run:

```bash
python3 verifier/fleet_verifier.py
```

Simulates a rack of 10 nodes:

* 8 nodes → valid firmware (SVN = 2)
* 1 node → rollback attack (SVN = 1)
* 1 node → compromised firmware (SVN = 0)

### Behavior:

```text id="fleet1"
✔ Trusted nodes → allowed
❌ Rollback node → blocked (SVN violation)
❌ Compromised node → blocked (measurement mismatch)
```

---

## Key Concepts Modeled

### Root of Trust (RoT)

A foundational secret anchors identity derivation.

---

### DICE Identity Chain

```text id="dice1"
IDEV → LDEV → Runtime Identity
```

Each stage derives identity from measured state.

---

### Firmware Measurement

```text id="measure1"
MEASURE = hash(firmware)
```

Represents BIOS / BMC / OS state.

---

### Attestation

```text id="att1"
MEASURE + SVN + SIGNATURE
```

* MEASURE → integrity
* SVN → freshness
* SIGNATURE → authenticity

---

### Rollback Protection (NEW)

Security Version Number (SVN) prevents downgrade attacks.

```text id="svn1"
if svn < minimum_allowed:
    reject device
```

---

### Verifier Policy

```text id="policy1"
1. Signature must be valid
2. Measurement must match approved firmware
3. SVN must meet minimum requirement
```

---

## Implementation Details

### Device

* Arduino Mega 2560
* C++ (Arduino)
* Serial communication
* Simulated cryptography (to be replaced by hardware)

### Verifier

* Python
* pyserial
* Policy + validation logic

---

## Mapping to Real Systems

| Lab Component    | Real System Equivalent    |
| ---------------- | ------------------------- |
| Arduino          | Server / host platform    |
| ATECC (future)   | TPM / Caliptra / Nitro    |
| deviceSecret     | Hardware root key         |
| boot_rom()       | Immutable ROM             |
| derive()         | DICE / CDI                |
| hashStr()        | SHA engine                |
| Serial           | RPC / network API         |
| verifier.py      | Cloud attestation service |
| SVN              | Firmware security version |
| Fleet simulation | Data center rack          |

---

## Current Limitations

* Software-based root key (until ATECC integration)
* Simplified cryptography
* Serial instead of network API
* No persistent device identity yet

---

## Next Steps

* Integrate ATECC608A (hardware root of trust)
* Replace simulated signatures with real ECC
* Add secure provisioning flow
* Extend to network-based API
* Add telemetry / monitoring

---

## Why This Matters

Modern cloud platforms enforce trust at hardware level.

This project models:

* Device-side trust (measurement + signing)
* Cloud-side trust (policy + enforcement)
* **Rollback protection (critical production requirement)**

At scale:

```text id="scale1"
Thousands of nodes
→ continuous attestation
→ automated isolation of compromised systems
```

---

## Critical Insight

Attestation answers:

```text id="ci1"
"What is this device running?"
```

Policy answers:

```text id="ci2"
"Is this acceptable?"
```

SVN enforcement ensures:

```text id="ci3"
"Is this sufficiently up-to-date?"
```

---

## How to Run

### Device

* Open `device/mini_rot.ino`
* Select Arduino Mega 2560
* Upload

---

### Verifier

```bash
pip3 install -r verifier/requirements.txt
python3 verifier/verifier.py
```

---

### Fleet Simulation

```bash
python3 verifier/fleet_verifier.py
```

---

## Control Plane (NEW)

A Raspberry Pi acts as a **mini cloud control plane**, simulating how AWS/Azure make scheduling decisions based on hardware trust.

### API Endpoints

GET /nodes  
POST /launch  

### Behavior

- Retrieves node trust state
- Selects trusted nodes for workload placement
- Denies launch if no trusted nodes are available

---

## Control Plane Flow

```text
User → API (/launch)
   ↓
Control Plane (Raspberry Pi)
   ↓
Verifier + Policy Engine
   ↓
Scheduler
   ↓
ALLOW / DENY decision

