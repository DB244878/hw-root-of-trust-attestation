import sqlite3
from datetime import datetime

DB_NAME = "devices.db"

def get_connection():
    return sqlite3.connect(DB_NAME)

def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS devices (
        device_id TEXT PRIMARY KEY,
        expected_firmware_hash TEXT NOT NULL,
        min_firmware_version INTEGER NOT NULL,
        status TEXT NOT NULL,
        reason TEXT,
        last_seen TEXT
    )
    """)

    conn.commit()
    conn.close()

def register_device(device_id, expected_firmware_hash, min_firmware_version):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    INSERT OR REPLACE INTO devices (
        device_id,
        expected_firmware_hash,
        min_firmware_version,
        status,
        reason,
        last_seen
    )
    VALUES (?, ?, ?, ?, ?, ?)
    """, (
        device_id,
        expected_firmware_hash,
        min_firmware_version,
        "registered",
        "Device registered but not yet attested",
        None
    ))

    conn.commit()
    conn.close()

def get_device(device_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM devices WHERE device_id = ?", (device_id,))
    row = cur.fetchone()
    conn.close()

    if row is None:
        return None

    return {
        "device_id": row[0],
        "expected_firmware_hash": row[1],
        "min_firmware_version": row[2],
        "status": row[3],
        "reason": row[4],
        "last_seen": row[5]
    }

def update_device_status(device_id, status, reason):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    UPDATE devices
    SET status = ?, reason = ?, last_seen = ?
    WHERE device_id = ?
    """, (
        status,
        reason,
        datetime.utcnow().isoformat(),
        device_id
    ))

    conn.commit()
    conn.close()

def get_all_devices():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM devices")
    rows = cur.fetchall()
    conn.close()

    return [
        {
            "device_id": row[0],
            "expected_firmware_hash": row[1],
            "min_firmware_version": row[2],
            "status": row[3],
            "reason": row[4],
            "last_seen": row[5]
        }
        for row in rows
    ]
