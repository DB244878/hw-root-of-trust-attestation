# Cloud Fleet Attestation Lab

## Current Architecture

Device
    |
    | Attestation Request
    v
Verifier API
    |
    | Policy Evaluation
    v
Trust Decision

Possible Outcomes

- Trusted
- Quarantined

Current Checks

- Nonce validation
- Firmware hash validation

Planned Checks

- ATECC608 signature verification
- Device registration database
- Rollback protection
- Firmware allow-list
- Fleet dashboard
