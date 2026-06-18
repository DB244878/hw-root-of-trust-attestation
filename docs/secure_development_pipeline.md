# Secure Development Pipeline

## Objective

This project uses a layered security review pipeline because security tooling is part of the trust boundary.

The lab models hardware and firmware trust decisions, but the software that implements those decisions must also be protected from insecure code, vulnerable dependencies, weak CI/CD permissions, and unsafe AI-generated changes.

## Principles

1. Deterministic security scanners run before AI-assisted review.
2. CI jobs use least-privilege permissions.
3. Pull request workflows should not expose secrets to untrusted code.
4. AI-assisted security review is advisory, not authoritative.
5. Security findings must be reviewed before merge.
6. Dependency and workflow risk are treated as part of the platform threat model.

## Baseline Controls

- CodeQL for semantic code scanning
- Bandit for Python security checks
- pip-audit for Python dependency vulnerability scanning
- OpenSSF Scorecard for repository security posture

## Future Controls

- SBOM generation
- signed releases
- dependency pinning
- branch protection
- security review checklist
- local AI-assisted security review before merge
- agentic CI/CD threat model

## Review Rule

No platform-security feature should be considered complete until:

1. Tests pass
2. Security baseline passes
3. Threat model impact is reviewed
4. Any AI-generated code is manually inspected
