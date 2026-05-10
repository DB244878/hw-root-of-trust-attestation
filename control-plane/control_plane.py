from dataclasses import dataclass
from enum import Enum

class TrustState(str, Enum):
    TRUSTED_HARDWARE = "TRUSTED_HARDWARE_BACKED_NODE"
    TRUSTED_SIM = "TRUSTED_SIMULATION_ONLY"
    QUARANTINED = "QUARANTINED"

@dataclass
class Node:
    node_id: str
    trust_state: TrustState
    workload: str | None = None

class MiniControlPlane:
    def __init__(self):
        self.nodes = {
            "node-a-esp32-atecc608a": Node("node-a-esp32-atecc608a", TrustState.TRUSTED_HARDWARE),
            "node-b-simulated": Node("node-b-simulated", TrustState.TRUSTED_SIM),
            "node-c-quarantined": Node("node-c-quarantined", TrustState.QUARANTINED),
        }

    def create_bare_metal_instance(self, workload_name: str) -> str:
        for node in self.nodes.values():
            if node.trust_state == TrustState.TRUSTED_HARDWARE and node.workload is None:
                node.workload = workload_name
                return f"BARE_METAL_INSTANCE_CREATED: {workload_name} on {node.node_id}"

        return "NO_TRUSTED_HARDWARE_NODE_AVAILABLE"

    def create_virtual_instance(self, workload_name: str) -> str:
        for node in self.nodes.values():
            if node.trust_state in [TrustState.TRUSTED_HARDWARE, TrustState.TRUSTED_SIM] and node.workload is None:
                node.workload = workload_name
                return f"VIRTUAL_INSTANCE_CREATED: {workload_name} on {node.node_id}"

        return "NO_TRUSTED_NODE_AVAILABLE"

    def show_nodes(self):
        print("=== Mini Control Plane Node State ===")
        for node in self.nodes.values():
            print(f"{node.node_id}: trust={node.trust_state.value}, workload={node.workload}")

def main():
    cp = MiniControlPlane()
    cp.show_nodes()
    print(cp.create_bare_metal_instance("tenant-baremetal-demo"))
    print(cp.create_virtual_instance("tenant-vm-demo"))
    cp.show_nodes()

if __name__ == "__main__":
    main()
