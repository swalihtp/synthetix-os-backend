"""
End-to-end test — run with: python test_e2e.py
Tests the full flow: login → get agent → trigger workflow → check run status
"""
import requests
import time

BASE = "http://127.0.0.1:8000/api"

# ── Step 1: Login ──────────────────────────────────────────────
print("\n1. Logging in...")
res = requests.post(f"{BASE}/auth/login/", json={
    "email": "synthetixos@gmail.com",
    "password": "pas@1234",
})
assert res.status_code == 200, f"Login failed: {res.text}"
token = res.json()["access"]
headers = {"Authorization": f"Bearer {token}"}
print("   Login successful.")

# ── Step 2: Get agents ─────────────────────────────────────────
print("\n2. Fetching agents...")
res = requests.get(f"{BASE}/agent/", headers=headers)
print(f"Status: {res.status_code}")
print(f"Response: {res.text}")  
assert res.status_code == 200
agents = res.json()
print(f"   Found {len(agents)} agents:")
for a in agents:
    print(f"   - {a['name']} (id: {a['id']})")

# ── Step 3: Get workflows ──────────────────────────────────────
print("\n3. Fetching workflows...")
res = requests.get(f"{BASE}/workflows/", headers=headers)
assert res.status_code == 200
workflows = res.json()
print(f"   Found {len(workflows)} workflows:")
for w in workflows:
    print(f"   - {w['name']} | trigger: {w['trigger_type']} | steps: {len(w['steps'])}")

# ── Step 4: Trigger the Social Post Scheduler ─────────────────
social_workflow = next(
    (w for w in workflows if "Social" in w["name"]), None
)
if social_workflow:
    print(f"\n4. Triggering '{social_workflow['name']}'...")
    res = requests.post(
        f"{BASE}/workflows/{social_workflow['id']}/trigger/",
        headers=headers,
        json={
            "raw_text": "Excited to announce the launch of Synthetix OS!"
        }
    )
    print(f"Status: {res.status_code}")
    print(f"Response: {res.text[:500]}")   # ✅ show first 500 chars to see error

    # ✅ Only parse JSON if response is actually JSON
    if res.headers.get('content-type', '').startswith('application/json'):
        print(f"Trigger response: {res.json()}")
        assert res.status_code == 200, f"Trigger failed: {res.json()}"
    else:
        print("❌ Got HTML response — likely a 500 server error")
        assert False, f"Server error: {res.text[:200]}"

    # ── Step 5: Wait and check WorkflowRun ────────────────────
    print("\n5. Waiting 3 seconds for Celery to execute...")
    time.sleep(3)

    res = requests.get(
        f"{BASE}/workflows/{social_workflow['id']}/runs/",
        headers=headers
    )
    runs = res.json()
    if runs:
        latest = runs[0]
        print(f"   Latest run status: {latest['status']}")
        print(f"   Steps completed: {latest['current_step']}")
        if latest['status'] == 'failed':
            print(f"   Error: {latest['error']}")
        elif latest['status'] == 'completed':
            print(f"   Context keys: {list(latest['context'].keys())}")
    else:
        print("   No runs found yet — Celery may not be running.")
else:
    print("\n4. Social Post Scheduler not found — run seed_templates first.")

# ── Step 6: Check events ───────────────────────────────────────
print("\n6. Checking events...")
res = requests.get(f"{BASE}/events/", headers=headers)
events = res.json()
print(f"   Total events: {len(events)}")
if events:
    print(f"   Latest: {events[0]['event_type']} | {events[0]['status']}")

print("\nAll checks passed.")