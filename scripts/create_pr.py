import urllib.request, json, os, sys, subprocess, yaml

with open(os.path.expanduser("~/.config/gh/hosts.yml")) as f:
    data = yaml.safe_load(f)
token = data.get("github.com", {}).get("oauth_token", "")
if not token:
    print("No token found", file=sys.stderr)
    sys.exit(1)

repos = [
    ("mistralai", "client-python"),
]

for owner, repo in repos:
    url = f'https://api.github.com/repos/{owner}/{repo}/pulls'
    body_text = 'Structural promotion of Mistral AI Python SDK from O0 to O2.\n\nThis PR implements a structural promotion from O0 (thin REST wrapper) to O2 (self-verifying agentic framework) via the Imscribing Grammar. Key additions:\n- DualToolResult + ToolContract (Frobenius verification μ∘δ=id)\n- AgentTrajectory with topological winding protection (Ω_z)\n- TrueAgenticLoop (THINK→ACT→OBSERVE→UPDATE)\n- PhiCriticalityGate (self-modeling criticality, φ̂_ÿ)'
    data = json.dumps({
        'title': 'feat: Structural Promotion O0→O2 — True Agentic Loop with Frobenius Verification',
        'head': 'umpolungfish:structural-promotion-O2',
        'base': 'main',
        'body': body_text,
    }).encode()
    req = urllib.request.Request(url, data=data, method='POST')
    req.add_header('Authorization', f'Bearer {token}')
    req.add_header('Accept', 'application/vnd.github.v3+json')
    req.add_header('Content-Type', 'application/json')
    req.add_header('User-Agent', 'Python-urllib/3.12')
    try:
        resp = urllib.request.urlopen(req)
        result = json.loads(resp.read())
        print(f"{owner}/{repo}: PR created: {result.get('html_url', 'unknown')}")
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"{owner}/{repo}: Error {e.code}: {body[:200]}")
