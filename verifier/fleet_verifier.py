from dataclasses import dataclass

EXPECTED_FIRMWARE = "firmware_v1"
EXPECTED_CONFIG = "config_v1"
MIN_SVN = 2

@dataclass
class NodeQuote:
    node_id: str
    firmware: str
    config: str
    svn: int
    signature_valid: bool
    hardware_backed: bool

def verify_node(quote: NodeQuote) -> str:
    if not quote.signature_valid:
        return "QUARANTINE: invalid attestation signature"

    if quote.firmware != EXPECTED_FIRMWARE:
        return "QUARANTINE: firmware measurement mismatch"

    if quote.config != EXPECTED_CONFIG:
        return "QUARANTINE: config measurement mismatch"

    if quote.svn < MIN_SVN:
        return "QUARANTINE: rollback detected"

    if not quote.hardware_backed:
        return "TRUSTED_SIMULATION_ONLY: valid software model, not hardware-backed"

    return "TRUSTED_HARDWARE_BACKED_NODE"

def main():
    fleet = [
        NodeQuote("node-a-esp32-atecc608a", "firmware_v1", "config_v1", 2, True, True),
        NodeQuote("node-b-simulated", "firmware_v1", "config_v1", 2, True, False),
        NodeQuote("node-c-bad-fw", "firmware_tampered", "config_v1", 2, True, False),
        NodeQuote("node-d-rollback", "firmware_v1", "config_v1", 1, True, False),
        NodeQuote("node-e-bad-signature", "firmware_v1", "config_v1", 2, False, False),
    ]

    print("=== Mini Caliptra Fleet Verifier ===")
    for quote in fleet:
        decision = verify_node(quote)
        print(f"{quote.node_id}: {decision}")

if __name__ == "__main__":
    main()
