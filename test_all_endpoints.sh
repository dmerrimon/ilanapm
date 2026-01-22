#!/bin/bash

BASE_URL="https://ilanapm.onrender.com/api/v1"

echo "================================"
echo "Testing Ilana PM API Endpoints"
echo "================================"
echo

# 1. Health endpoint
echo "1. Testing /health..."
curl -s "$BASE_URL/health" | python3 -m json.tool
echo
echo "---"
echo

# 2. Config endpoints
echo "2. Testing /config/countries..."
curl -s "$BASE_URL/config/countries" | python3 -m json.tool | head -50
echo "..."
echo "---"
echo

echo "3. Testing /config/tasks..."
curl -s "$BASE_URL/config/tasks" | python3 -m json.tool | head -30
echo "..."
echo "---"
echo

echo "4. Testing /config/summary..."
curl -s "$BASE_URL/config/summary" | python3 -m json.tool
echo "---"
echo

# 3. Validate endpoint (needs sample data)
echo "5. Testing /validate (POST)..."
cat > /tmp/test_timeline.json <<'EOF'
{
  "study_name": "Test Study",
  "phase": "Phase III",
  "authority": "FDA",
  "tasks": [
    {
      "id": "1",
      "name": "Protocol Development",
      "duration_days": 180,
      "category": "Planning",
      "phase": "Phase III",
      "authority": "FDA",
      "is_mandatory": true,
      "checklist_completion_pct": 100
    },
    {
      "id": "2",
      "name": "IND Submission",
      "duration_days": 30,
      "category": "Regulatory",
      "phase": "Phase III",
      "authority": "FDA",
      "is_mandatory": true,
      "checklist_completion_pct": 90
    }
  ],
  "dependencies": [
    {
      "predecessor_id": "1",
      "successor_id": "2",
      "type": "finish-to-start",
      "lag_days": 0
    }
  ]
}
EOF

curl -s -X POST "$BASE_URL/validate" \
  -H "Content-Type: application/json" \
  -d @/tmp/test_timeline.json | python3 -m json.tool
echo "---"
echo

# 4. Analytics - Critical Path
echo "6. Testing /analytics/critical-path (POST)..."
curl -s -X POST "$BASE_URL/analytics/critical-path" \
  -H "Content-Type: application/json" \
  -d @/tmp/test_timeline.json | python3 -m json.tool
echo "---"
echo

# 5. Advisory - Timeline
echo "7. Testing /advisory/timeline (POST)..."
curl -s -X POST "$BASE_URL/advisory/timeline" \
  -H "Content-Type: application/json" \
  -d @/tmp/test_timeline.json | python3 -m json.tool | head -100
echo "..."
echo "---"
echo

# 6. Advisory - Duration Prediction
echo "8. Testing /advisory/duration (POST)..."
cat > /tmp/test_task.json <<'EOF'
{
  "id": "test-1",
  "name": "Protocol Development",
  "duration_days": 180,
  "category": "Planning",
  "phase": "Phase III",
  "authority": "FDA",
  "is_mandatory": true,
  "checklist_completion_pct": 100
}
EOF

curl -s -X POST "$BASE_URL/advisory/duration" \
  -H "Content-Type: application/json" \
  -d @/tmp/test_task.json | python3 -m json.tool
echo "---"
echo

# 7. Advisory - Risk Score
echo "9. Testing /advisory/risk (POST)..."
curl -s -X POST "$BASE_URL/advisory/risk" \
  -H "Content-Type: application/json" \
  -d @/tmp/test_task.json | python3 -m json.tool
echo "---"
echo

echo "================================"
echo "Endpoint Testing Complete"
echo "================================"
