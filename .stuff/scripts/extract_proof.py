import json
import sys

# Read the entire JSON from stdin
data = json.load(sys.stdin)

# Extract all proof-related content from fragments
proof_sections = []

for session in data:
    title = session.get("title", "")
    mapping = session.get("mapping", {})
    for node_id, node in mapping.items():
        if node_id == "root":
            continue
        msg = node.get("message")
        if not msg:
            continue
        fragments = msg.get("fragments", [])
        for frag in fragments:
            if frag.get("type") == "RESPONSE":
                content = frag.get("content", "")
                if content.strip():
                    proof_sections.append(f"=== Section from '{title}' (node {node_id}) ===\n")
                    proof_sections.append(content)
                    proof_sections.append("\n\n")

# Write to stdout
print("".join(proof_sections))
