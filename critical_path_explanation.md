# How Ilana PM Determines Critical Path

## Overview

The critical path is calculated using the **Critical Path Method (CPM)**, a standard project management algorithm that identifies which tasks cannot be delayed without delaying the entire project.

## Algorithm: Forward and Backward Pass

### Step 1: Forward Pass (Earliest Times)
Starting from the beginning, calculate when each task can **earliest start** and **earliest finish**:

```
For each task in topological order:
    Earliest Start = MAX(predecessor earliest finish + lag)
    Earliest Finish = Earliest Start + Duration
```

**Example (Kenya Three-Layer):**
```
Task                                      Duration  Earliest Start  Earliest Finish
──────────────────────────────────────────────────────────────────────────────────
Institutional EC Approval                 30 days   Day 0          Day 30
Pharmacy and Poisons Board Approval       30 days   Day 30         Day 60
NACOSTI Clearance                         30 days   Day 60         Day 90
──────────────────────────────────────────────────────────────────────────────────
Protocol Development (parallel)           180 days  Day 0          Day 180
```

### Step 2: Backward Pass (Latest Times)
Starting from the end, calculate when each task can **latest start** and **latest finish** without delaying the project:

```
Project End Time = MAX(all earliest finish times)

For each task in reverse topological order:
    Latest Finish = MIN(successor latest start - lag)
    Latest Start = Latest Finish - Duration
```

**Example (Kenya Three-Layer):**
```
Task                                      Latest Start  Latest Finish
───────────────────────────────────────────────────────────────────
Institutional EC Approval                 Day 0         Day 30
Pharmacy and Poisons Board Approval       Day 30        Day 60
NACOSTI Clearance                         Day 60        Day 90
───────────────────────────────────────────────────────────────────
Protocol Development (has flexibility)    Day 0         Day 180
```

### Step 3: Calculate Slack (Float)

```
Slack = Latest Start - Earliest Start
```

**Tasks with ZERO slack are on the CRITICAL PATH**

**Example:**
```
Task                                      Slack     Critical Path?
─────────────────────────────────────────────────────────────────
Institutional EC Approval                 0 days    ✅ YES
Pharmacy and Poisons Board Approval       0 days    ✅ YES
NACOSTI Clearance                         0 days    ✅ YES
─────────────────────────────────────────────────────────────────
Protocol Development                      0 days    ✅ YES (if longest task)
Data Collection Forms                     60 days   ❌ NO (can be delayed)
```

## How Dependencies Affect Critical Path

### Parallel Workflows (US: FDA || IRB)
```
┌─────────────┐
│ FDA Approval│─────┐
│   30 days   │     │
└─────────────┘     ├──► Both must finish
                    │    before trial starts
┌─────────────┐     │
│ IRB Approval│─────┘
│   30 days   │
└─────────────┘

Critical Path: BOTH are critical (parallel critical paths)
If either is delayed, project is delayed
```

### Sequential Workflows (Kenya: EC → PPB → NACOSTI)
```
┌──────────────┐    ┌─────────────┐    ┌──────────────┐
│ EC Approval  │───→│ PPB Approval│───→│NACOSTI Clear.│
│   30 days    │    │   30 days   │    │   30 days    │
└──────────────┘    └─────────────┘    └──────────────┘

Critical Path: ALL THREE are critical (sequential chain)
Total Duration: 90 days
Any delay in any task delays the entire project
```

## Why This Matters

1. **Risk Management**: Critical path tasks need closest monitoring
2. **Resource Allocation**: Focus resources on critical tasks
3. **Timeline Optimization**: Only accelerating critical tasks reduces project duration
4. **Delay Impact**: Non-critical tasks can be delayed by their slack without impact

## Implementation in Ilana PM

### Backend (Python + NetworkX)
- File: `backend/graph_analytics/dependency_graph.py`
- Algorithm: Forward/Backward pass using topological sort
- Library: NetworkX (industry-standard graph library)
- Output: Tasks with zero slack = critical path

### Frontend (MS Project Desktop Add-in)
- Critical Path button calls: `POST /api/v1/analytics/critical-path`
- Highlights critical tasks in yellow in MS Project
- Shows dialog with critical path details
- Displays earliest start/finish for each critical task

## Example API Response

```json
{
  "path": ["REG-KE-EC", "REG-KE-REG", "REG-KE-NACOSTI"],
  "tasks": [
    {
      "id": "REG-KE-EC",
      "name": "Institutional Ethics Committee (EC) Approval - Kenya",
      "duration_days": 30,
      "earliest_start": 0,
      "earliest_finish": 30
    },
    {
      "id": "REG-KE-REG",
      "name": "Pharmacy and Poisons Board Approval - Kenya",
      "duration_days": 30,
      "earliest_start": 30,
      "earliest_finish": 60
    },
    {
      "id": "REG-KE-NACOSTI",
      "name": "National Commission for Science, Technology and Innovation Clearance - Kenya",
      "duration_days": 30,
      "earliest_start": 60,
      "earliest_finish": 90
    }
  ],
  "total_duration": 90,
  "task_count": 3
}
```

## Key Insight

**The critical path is NOT manually defined** - it's automatically calculated from:
1. Task durations
2. Dependencies between tasks
3. Mathematical algorithm (CPM)

Sequential workflows naturally create longer critical paths.
Parallel workflows create multiple simultaneous critical paths.
