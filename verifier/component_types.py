"""
Generic platform component types used by the secure hardware fleet lab.

These names intentionally avoid company-specific or internal program terminology.
They model common hardware and firmware security domains found in modern
data-center platforms.
"""

ROOT_OF_TRUST = "ROOT_OF_TRUST"
PLATFORM_SECURITY_MODULE = "PLATFORM_SECURITY_MODULE"
MANAGEMENT_CONTROLLER = "MANAGEMENT_CONTROLLER"
NETWORK_DEVICE = "NETWORK_DEVICE"
MEMORY_STORAGE_ENCRYPTION = "MEMORY_STORAGE_ENCRYPTION"
HOST_FIRMWARE = "HOST_FIRMWARE"
BOOT_STORAGE = "BOOT_STORAGE"
DATA_STORAGE = "DATA_STORAGE"

REQUIRED_PLATFORM_COMPONENTS = [
    ROOT_OF_TRUST,
    PLATFORM_SECURITY_MODULE,
    MANAGEMENT_CONTROLLER,
    NETWORK_DEVICE,
    MEMORY_STORAGE_ENCRYPTION,
    HOST_FIRMWARE,
]
