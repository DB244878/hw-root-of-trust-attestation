from flask import Flask, jsonify

app = Flask(__name__)

nodes = [
    {"id": "rack1-node01", "firmware": "firmware_v2", "svn": 2, "trusted": True},
    {"id": "rack1-node02", "firmware": "firmware_v2", "svn": 2, "trusted": True},
    {"id": "rack1-node03", "firmware": "firmware_v1", "svn": 1, "trusted": False},
]

@app.route("/nodes", methods=["GET"])
def get_nodes():
    return jsonify(nodes)

@app.route("/launch", methods=["POST"])
def launch():
    trusted_nodes = [n for n in nodes if n["trusted"]]

    if not trusted_nodes:
        return jsonify({
            "status": "DENY",
            "reason": "No trusted nodes available"
        })

    selected = trusted_nodes[0]

    return jsonify({
        "status": "ALLOW",
        "selected_node": selected["id"],
        "message": "Instance launched on trusted node"
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
