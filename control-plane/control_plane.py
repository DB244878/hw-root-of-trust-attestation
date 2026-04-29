from flask import Flask, jsonify

app = Flask(__name__)

EXPECTED_MEASURE = "161061760"  # firmware_v2
MIN_ALLOWED_SVN = 2


def hash_str(s):
    h = 0
    for ch in s:
        h = h * 31 + ord(ch)
        h = ((h + 2**31) % 2**32) - 2**31
    return str(h)


def derive(parent, measurement):
    return hash_str(parent + "|" + measurement)


def build_node_evidence(node_id, firmware, svn, device_secret):
    measurement = hash_str(firmware)

    idev = derive(device_secret, measurement)
    ldev = derive(idev, hash_str("config_v1"))
    runtime_id = derive(ldev, hash_str("runtime_v1"))

    signature = hash_str(runtime_id + "|" + measurement + "|" + str(svn))

    return {
        "id": node_id,
        "firmware": firmware,
        "svn": svn,
        "measurement": measurement,
        "runtime_id": runtime_id,
        "signature": signature,
    }


def verify_node(node):
    expected_signature = hash_str(
        node["runtime_id"] + "|" + node["measurement"] + "|" + str(node["svn"])
    )

    reasons = []

    if node["signature"] != expected_signature:
        reasons.append("INVALID_SIGNATURE")

    if node["measurement"] != EXPECTED_MEASURE:
        reasons.append("UNTRUSTED_FIRMWARE")

    if node["svn"] < MIN_ALLOWED_SVN:
        reasons.append("ROLLBACK_DETECTED")

    trusted = len(reasons) == 0

    return {
        **node,
        "trusted": trusted,
        "reasons": reasons,
    }


raw_nodes = [
    build_node_evidence("rack1-node01", "firmware_v2", 2, "device_secret_1"),
    build_node_evidence("rack1-node02", "firmware_v2", 2, "device_secret_2"),
    build_node_evidence("rack1-node03", "firmware_v1", 1, "device_secret_3"),
    build_node_evidence("rack1-node04", "firmware_hacked", 0, "device_secret_4"),
]


@app.route("/nodes", methods=["GET"])
def get_nodes():
    verified_nodes = [verify_node(n) for n in raw_nodes]
    return jsonify(verified_nodes)


@app.route("/launch", methods=["POST"])
def launch():
    verified_nodes = [verify_node(n) for n in raw_nodes]
    trusted_nodes = [n for n in verified_nodes if n["trusted"]]

    if not trusted_nodes:
        return jsonify({
            "status": "DENY",
            "reason": "No trusted nodes available",
            "quarantined": [
                {"id": n["id"], "reasons": n["reasons"]}
                for n in verified_nodes
                if not n["trusted"]
            ],
        })

    selected = trusted_nodes[0]

    return jsonify({
        "status": "ALLOW",
        "selected_node": selected["id"],
        "message": "Instance launched on trusted node",
        "trusted_nodes": [n["id"] for n in trusted_nodes],
        "quarantined_nodes": [
            {"id": n["id"], "reasons": n["reasons"]}
            for n in verified_nodes
            if not n["trusted"]
        ],
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
