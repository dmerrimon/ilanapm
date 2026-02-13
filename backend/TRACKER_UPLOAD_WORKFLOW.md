# Tracker Upload Workflow Documentation

## Overview

Seleen's tracker upload system enables CPMs to integrate Excel-based tracker data (Risk Logs, TMF Completeness, Budget, Vendor Management) with timeline intelligence. This document describes the complete workflow from initial configuration to daily use.

**Key Principles:**
- ✅ **One-time configuration** by Account Admin in web portal
- ✅ **Daily uploads via MS Project add-in ONLY** (CPMs never use web portal for uploads)
- ✅ **Automatic signal extraction** and correlation to timeline milestones
- ✅ **Real-time notifications** in MS Project add-in
- ✅ **Leadership visibility** in unified dashboard

---

## Workflow Overview

```
┌─────────────────────────────────────────────────────────────────┐
│ PHASE 1: ONE-TIME SETUP (Account Admin - Web Portal)           │
└─────────────────────────────────────────────────────────────────┘
                              ↓
        Upload sample tracker → Configure column mappings → Save
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ PHASE 2: DAILY USE (CPM - MS Project Add-in ONLY)              │
└─────────────────────────────────────────────────────────────────┘
                              ↓
   Update Excel tracker → Click "Upload Tracker" in add-in →
   Select file → Auto-process → View notification
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ PHASE 3: INTELLIGENCE SYNTHESIS (Backend - Automatic)          │
└─────────────────────────────────────────────────────────────────┘
                              ↓
   Parse rows → Extract signals → Correlate to milestones →
   Generate escalations → Update health score → Refresh dashboard
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ PHASE 4: LEADERSHIP CONSUMPTION (Web Portal Dashboard)         │
└─────────────────────────────────────────────────────────────────┘
```

---

## Phase 1: One-Time Configuration (Account Admin)

### Prerequisites
- Account Admin role in Seleen
- Access to sample tracker files from your organization
- Understanding of your organization's tracker column naming conventions

### Step 1: Access Tracker Configuration

1. Log in to **app.seleen.io**
2. Navigate to **Account Management** view
3. Click **Tracker Configuration** in the sidebar

```
┌────────────────────────────────────────────────────────┐
│ Account Management                                     │
├────────────────────────────────────────────────────────┤
│ → Users & Seats                                        │
│ → Billing                                              │
│ → Tracker Configuration          ← YOU ARE HERE        │
│ → Organization Settings                                │
│ → API Keys                                             │
└────────────────────────────────────────────────────────┘
```

### Step 2: Select Tracker Type

Choose which tracker you want to configure:

**Standard Tracker Types:**
- ☐ Risk Log
- ☐ TMF Completeness Tracker
- ☐ Budget Tracker
- ☐ Vendor Management Tracker

Click **[+ Add Tracker]** to start configuration.

```
┌────────────────────────────────────────────────────────┐
│ Tracker Configuration                                  │
├────────────────────────────────────────────────────────┤
│                                                        │
│ Standard Trackers:                                     │
│ ☐ Risk Log                                            │
│ ☐ TMF Completeness Tracker                           │
│ ☐ Budget Tracker                                      │
│ ☐ Vendor Management Tracker                          │
│                                                        │
│ [+ Add Tracker]                                       │
│                                                        │
└────────────────────────────────────────────────────────┘
```

### Step 3: Upload Sample File

Upload a sample tracker file from your organization:

1. Click **[Upload Sample File]** or drag-and-drop
2. Select an Excel file (`.xlsx`, `.xls`) or CSV (`.csv`)
3. System validates file format
4. System detects columns automatically

```
┌────────────────────────────────────────────────────────┐
│ Add Risk Log Tracker                                   │
├────────────────────────────────────────────────────────┤
│                                                        │
│ Upload a sample Risk Log file from your organization: │
│                                                        │
│ ┌──────────────────────────────────────────────────┐ │
│ │                                                  │ │
│ │  Drag & Drop File Here                          │ │
│ │                                                  │ │
│ │           or [Browse Files]                     │ │
│ │                                                  │ │
│ └──────────────────────────────────────────────────┘ │
│                                                        │
│ Risk_Log_Sample.xlsx uploaded ✓                       │
│ • File size: 45 KB                                    │
│ • Detected columns: 12                                │
│ • Detected rows: 23                                   │
│                                                        │
│ [Next: Map Columns]                                   │
│                                                        │
└────────────────────────────────────────────────────────┘
```

### Step 4: Map Columns

Map your organization's column names to Seleen's standard schema:

```
┌─────────────────────────────────────────────────────────────────┐
│ Map Your Organization's Columns to Seleen Schema               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ Your Column              →   Seleen Field        Preview       │
│ ──────────────────────────────────────────────────────────────│
│ ID                       →   [Risk #]            1, 2, 3...    │
│ Risk Type                →   [Category]          Clinical...   │
│ Description              →   [Risk Detail]       "Enrollm..."  │
│ Severity                 →   [Impact]            1, 2, 3       │
│ Likelihood               →   [Probability]       1, 2, 3       │
│ Score                    →   [Priority]          2, 6, 9       │
│ Mitigation               →   [Mitigation Plan]   "Expedite..." │
│ Owner                    →   [Owner]             Jane Doe      │
│ Status                   →   [Status]            Open, Closed  │
│ Target Date              →   [Target Date]       2026-03-15    │
│ Completion Date          →   [Actual Date]       2026-03-10    │
│ Escalation Notes         →   [Escalation Notes]  "VP aware"    │
│                                                                 │
│ Required fields: Risk #, Category, Risk Detail, Impact,        │
│                  Probability, Priority                          │
│                                                                 │
│ ⚠️ Warning: "Score" column detected but appears to be          │
│    calculated (Impact × Probability). Map to [Priority].       │
│                                                                 │
│ [← Back]                              [Save Configuration →]   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Column Mapping Tips:**
- **Auto-suggestion**: System suggests likely mappings based on column names
- **Preview**: Shows sample data from your file to verify correct mapping
- **Required fields**: Must be mapped for tracker to work (marked with *)
- **Optional fields**: Can be left unmapped (e.g., internal reference columns)
- **Calculated fields**: Map calculated columns (like "Score = Impact × Probability") to the appropriate Seleen field

**Common Column Name Variations:**

| Seleen Field | Your Organization Might Use |
|--------------|----------------------------|
| Risk # | ID, Risk ID, Number, Risk Number |
| Category | Risk Type, Type, Classification, Area |
| Risk Detail | Description, Risk Description, Detail, Summary |
| Impact | Severity, Impact Level, Consequence |
| Probability | Likelihood, Chance, Frequency |
| Priority | Score, Risk Score, Rating, Severity Score |
| Mitigation Plan | Mitigation, Response, Action Plan, Plan |
| Owner | Responsible Party, Assigned To, Lead, POC |
| Status | State, Current Status, Progress |
| Target Date | Due Date, Deadline, Expected Date, Target |
| Actual Date | Completion Date, Closed Date, Resolved Date |

### Step 5: Configure Signal Extraction Rules (Optional)

Customize signal extraction thresholds (all tiers can customize):

```
┌─────────────────────────────────────────────────────────────────┐
│ Signal Extraction Rules                                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ Seleen Default:                                                │
│ ✓ Priority ≥6 → Director Escalation                           │
│ ✓ Priority = 9 → VP Escalation                                │
│ ✓ Category = "Safety" AND Priority ≥6 → VP Escalation         │
│ ✓ Escalation Notes populated → VP Escalation                   │
│                                                                 │
│ Or customize:                                                  │
│                                                                 │
│ Director Escalation Threshold:                                 │
│ Priority ≥ [6 ▼]                                              │
│                                                                 │
│ VP Escalation Threshold:                                       │
│ Priority ≥ [9 ▼]                                              │
│                                                                 │
│ Safety Risk Escalation:                                        │
│ [x] Category = "Safety" AND Priority ≥ [6 ▼] → VP            │
│                                                                 │
│ Other Rules:                                                   │
│ [x] Escalation Notes populated → VP Escalation                │
│ [x] Target Date overdue → Director Escalation                 │
│ [x] Mitigation Plan missing for Priority ≥6 → Director        │
│                                                                 │
│ [← Back]                              [Save Configuration →]   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Step 6: Configuration Complete

```
┌─────────────────────────────────────────────────────────────────┐
│ ✅ Risk Log Tracker Configured                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ Your CPMs can now upload Risk Log files via the MS Project    │
│ add-in. They should use the "Upload Tracker" button in the    │
│ Seleen ribbon.                                                 │
│                                                                 │
│ Configuration Summary:                                         │
│ • Tracker Type: Risk Log                                      │
│ • Columns Mapped: 12 of 12                                    │
│ • Required Fields: All mapped ✓                               │
│ • Signal Rules: Using Seleen defaults                         │
│ • Configured By: admin@yourorg.com                            │
│ • Configured On: 2026-02-13 10:45 AM                          │
│                                                                 │
│ [Download Standard Template]  [Configure Another Tracker]     │
│                                                                 │
│ [Done]                                                         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Download Standard Template:**
- Provides an Excel template with your organization's configured column names
- CPMs can use this template to maintain consistency
- Includes data validation rules and dropdown lists

---

## Phase 2: Daily CPM Use (MS Project Add-in)

### Prerequisites
- MS Project Desktop with Seleen add-in installed
- Seleen account with CPM role
- Updated Excel tracker file ready to upload

### Step 1: Update Your Excel Tracker

CPMs maintain trackers as usual in Excel:
1. Open your Excel tracker file (Risk Log, TMF, Budget, etc.)
2. Add new rows, update statuses, adjust priorities
3. Save the file locally

**No changes to CPM workflow** - continue using Excel exactly as before.

### Step 2: Open MS Project

1. Launch MS Project Desktop
2. Open your study's project file
3. Ensure Seleen add-in is loaded (look for "Seleen" ribbon)

```
┌────────────────────────────────────────────────────────────────┐
│ MS Project - Study XYZ-123                                     │
├────────────────────────────────────────────────────────────────┤
│ File  Task  Resource  View  [Seleen] ← Ribbon                 │
│                                                                │
│ [Sync Timeline] [Upload Tracker] [Dashboard] [Settings]       │
│                        ↑                                       │
│                   CLICK HERE                                   │
└────────────────────────────────────────────────────────────────┘
```

### Step 3: Click "Upload Tracker"

In the Seleen ribbon, click **[Upload Tracker]** button.

A dialog appears:

```
┌────────────────────────────────────────────────────────────────┐
│ Upload Tracker to Seleen                                       │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│ Select tracker type:                                          │
│ ○ Risk Log                                                    │
│ ○ TMF Completeness Tracker                                   │
│ ○ Budget Tracker                                             │
│ ○ Vendor Management Tracker                                  │
│                                                                │
│ Select file:                                                  │
│ [Browse for file...]                                          │
│                                                                │
│ C:\Users\Jane\Documents\Risk_Log_Jan2026.xlsx                 │
│                                                                │
│ Study: XYZ-123 (auto-detected)                               │
│ Organization: Acme Clinical Trials (auto-detected)           │
│                                                                │
│ [Cancel]                                    [Upload]          │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

**Notes:**
- **Study and Org auto-detected**: Add-in automatically detects current project ID and org ID
- **Tracker type**: Must match configuration in web portal (Account Admin setup)
- **File validation**: Add-in validates file format before upload

### Step 4: Upload Processing

After clicking **[Upload]**, the add-in shows progress:

```
┌────────────────────────────────────────────────────────────────┐
│ Uploading Risk Log...                                          │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│ ⏳ Processing:                                                 │
│ ✓ File validated                                              │
│ ✓ Uploading to Seleen (2.3 MB)                               │
│ ⏳ Parsing rows...                                             │
│                                                                │
│ [████████████████░░░░░░░░] 75%                                │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

**Processing Steps:**
1. **File validation**: Check format, size, columns
2. **Upload**: Send to Seleen API
3. **Parsing**: Backend extracts rows using saved column mapping
4. **Signal extraction**: Identify risks, issues, escalations
5. **Correlation**: Match signals to timeline milestones
6. **Health score update**: Recalculate study health
7. **Dashboard refresh**: Update Leadership Dashboard cache

**Typical Processing Time:**
- Small files (<100 rows): 2-5 seconds (real-time)
- Large files (100-500 rows): 30-60 seconds (background)

### Step 5: View Results

Upon completion, notification appears:

```
┌────────────────────────────────────────────────────────────────┐
│ ✅ Upload Complete!                                            │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│ Risk_Log_Jan2026.xlsx processed successfully                  │
│                                                                │
│ 📊 Summary:                                                    │
│ • 23 risks processed                                          │
│ • 5 signals extracted                                         │
│ • 3 correlations generated                                    │
│ • 2 escalations detected                                      │
│                                                                │
│ 🎯 Study Health:                                              │
│ • Score: 68 (Warning)                                         │
│ • Status: Warning (was Healthy)                               │
│ • Trend: Declining ↓                                          │
│                                                                │
│ ⚠️ Top Risks:                                                 │
│ • Risk #13: Site activation slower (Priority 7)              │
│ • Risk #8: Enrollment below target (Priority 6)              │
│                                                                │
│ [View Dashboard]                              [Close]         │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

**Notification Details:**
- **Risks processed**: Total rows parsed from tracker
- **Signals extracted**: Rows meeting escalation criteria
- **Correlations**: Signals matched to timeline milestones
- **Escalations**: Director or VP-level alerts generated
- **Study health**: Current health score and trend
- **Top risks**: Highest priority issues for CPM awareness

### Step 6: Continue Working

CPM continues working in MS Project. No additional action required.

**Key Benefit**: CPM gets immediate feedback on tracker upload without switching tools.

---

## Phase 3: Backend Processing (Automatic)

### Processing Pipeline

```python
# Backend processing pipeline (automatic, no user action)

def process_tracker_upload(file_bytes, tracker_type, org_id, project_id):
    """
    Complete backend processing pipeline
    """

    # 1. Validate file format
    if not valid_file_type(file_bytes):
        return error("Invalid file format. Use .xlsx, .xls, or .csv")

    # 2. Retrieve saved column mapping
    column_mapping = db.get_column_mapping(org_id, tracker_type)
    if not column_mapping:
        return error(
            "Tracker not configured. Contact Account Admin to configure "
            f"{tracker_type} tracker."
        )

    # 3. Parse rows using saved mapping
    rows = parse_rows(file_bytes, column_mapping)
    # Example row after mapping:
    # {
    #   "risk_number": 13,
    #   "category": "Site",
    #   "risk_detail": "Site activation slower than anticipated",
    #   "impact": 2,
    #   "probability": 2,
    #   "priority": 4,
    #   "mitigation_plan": "Expedite contracts",
    #   "owner": "Jane Doe",
    #   "status": "Open",
    #   "target_date": "2026-03-15",
    #   "escalation_notes": ""
    # }

    # 4. Extract signals using configured rules
    signals = extract_signals(rows, tracker_type, org_id)
    # Example signal:
    # {
    #   "signal_type": "risk_high_priority",
    #   "signal_category": "Site",
    #   "signal_description": "Risk #13: Site activation slower",
    #   "priority": 7,
    #   "status": "open",
    #   "date_identified": "2026-02-13",
    #   "escalation_level": "director"
    # }

    # 5. Store in database
    upload_id = store_tracker_upload(org_id, project_id, tracker_type, rows)
    for signal in signals:
        store_signal(upload_id, signal)

    # 6. Correlate signals to timeline milestones
    timeline = get_project_timeline(project_id)
    correlations = correlate_signals(signals, timeline)
    # Example correlation:
    # {
    #   "signal_id": "sig_123",
    #   "affected_milestone": "Site Activation",
    #   "affected_milestone_code": "SITE_ACT",
    #   "correlation_type": "risk",
    #   "confidence_score": 0.85,
    #   "estimated_delay_days": 14,
    #   "estimated_cost_impact": 343333.33,
    #   "correlation_reasoning": "High priority site risk affects Site "
    #                            "Activation milestone. Historical data shows "
    #                            "similar risks cause 14-day delays."
    # }

    # 7. Evaluate escalations
    escalations = evaluate_escalations(signals, correlations)
    for escalation in escalations:
        store_escalation(escalation)

    # 8. Calculate study health score
    health_score = calculate_health_score(project_id, signals, correlations)
    store_health_snapshot(project_id, health_score)

    # 9. Refresh dashboard cache
    refresh_dashboard(org_id, project_id)

    # 10. Return results to add-in
    return {
        "success": True,
        "rows_processed": len(rows),
        "signals_extracted": len(signals),
        "correlations_generated": len(correlations),
        "escalations_detected": len(escalations),
        "health_score": health_score.score,
        "health_status": health_score.status,
        "health_trend": health_score.trend,
        "top_risks": get_top_risks(signals, limit=5)
    }
```

### Signal Extraction Rules

Example: Risk Log signal extraction

```python
def extract_signals_from_risk_log(rows: List[Dict], org_id: str) -> List[Signal]:
    """
    Extract signals from Risk Log rows based on configured rules
    """
    signals = []

    for row in rows:
        priority = row.get('priority', 0)
        category = row.get('category', '')
        status = row.get('status', '')
        escalation_notes = row.get('escalation_notes', '')
        mitigation_plan = row.get('mitigation_plan', '')
        target_date = row.get('target_date')

        # Rule 1: High priority risks (Priority ≥6) → Director escalation
        if priority >= 6 and status == 'Open':
            signals.append(Signal(
                signal_type='risk_high_priority',
                signal_category=category,
                signal_description=f"Risk #{row['risk_number']}: {row['risk_detail']}",
                priority=priority,
                status='open',
                escalation_level='director'
            ))

        # Rule 2: Critical priority risks (Priority = 9) → VP escalation
        if priority == 9 and status == 'Open':
            signals.append(Signal(
                signal_type='risk_critical',
                signal_category=category,
                signal_description=f"CRITICAL Risk #{row['risk_number']}: {row['risk_detail']}",
                priority=priority,
                status='open',
                escalation_level='vp'
            ))

        # Rule 3: Safety risks (Category = "Safety" AND Priority ≥6) → VP escalation
        if category == 'Safety' and priority >= 6 and status == 'Open':
            signals.append(Signal(
                signal_type='risk_safety',
                signal_category='Safety',
                signal_description=f"SAFETY Risk #{row['risk_number']}: {row['risk_detail']}",
                priority=priority,
                status='open',
                escalation_level='vp'
            ))

        # Rule 4: Explicit escalations (Escalation Notes populated) → VP escalation
        if escalation_notes and status == 'Open':
            signals.append(Signal(
                signal_type='risk_escalated',
                signal_category=category,
                signal_description=f"Escalated Risk #{row['risk_number']}: {row['risk_detail']}",
                priority=priority,
                status='open',
                escalation_level='vp',
                escalation_notes=escalation_notes
            ))

        # Rule 5: No mitigation plan for high priority → Director escalation
        if priority >= 6 and not mitigation_plan and status == 'Open':
            signals.append(Signal(
                signal_type='risk_no_mitigation',
                signal_category=category,
                signal_description=f"Risk #{row['risk_number']} lacks mitigation plan",
                priority=7,  # Bump priority
                status='open',
                escalation_level='director'
            ))

        # Rule 6: Overdue risks → Director escalation
        if target_date and is_overdue(target_date) and status == 'Open':
            signals.append(Signal(
                signal_type='risk_overdue',
                signal_category=category,
                signal_description=f"Overdue Risk #{row['risk_number']}: {row['risk_detail']}",
                priority=max(priority, 6),  # At least Priority 6
                status='open',
                escalation_level='director'
            ))

    return signals
```

### Correlation Logic

Example: Correlating Site risk to Site Activation milestone

```python
def correlate_site_risk_to_site_activation(
    signal: Signal,
    timeline: Dict
) -> Optional[Correlation]:
    """
    Correlate site-related risks to Site Activation milestone
    """

    # Check if signal is site-related
    if signal.signal_category != 'Site':
        return None

    # Find Site Activation milestone in timeline
    site_activation_milestone = find_milestone_by_code(timeline, 'SITE_ACT')
    if not site_activation_milestone:
        return None

    # Calculate estimated delay based on priority
    # Formula: Priority × 7 days (e.g., Priority 6 = 42 days delay)
    estimated_delay_days = signal.priority * 7

    # Calculate cost impact
    # Benchmark: $733K/month = $24,433/day
    cost_per_day = 733000 / 30
    estimated_cost_impact = estimated_delay_days * cost_per_day

    # Create correlation
    correlation = Correlation(
        signal_id=signal.signal_id,
        affected_milestone_name='Site Activation',
        affected_milestone_code='SITE_ACT',
        correlation_type='risk',
        confidence_score=0.85,
        impact_type='delay',
        estimated_delay_days=estimated_delay_days,
        estimated_cost_impact=estimated_cost_impact,
        correlation_reasoning=(
            f"Risk Priority {signal.priority} ({signal.signal_description}) "
            f"affects Site Activation milestone. Historical data shows similar "
            f"site risks cause {estimated_delay_days}-day delays."
        )
    )

    return correlation
```

---

## Phase 4: Leadership Dashboard (Web Portal)

### Viewing Uploaded Tracker Signals

Directors and Executives log into **app.seleen.io** → **Leadership Dashboard** to view intelligence.

```
┌─────────────────────────────────────────────────────────────────┐
│ Leadership Dashboard                                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ Study XYZ-123                                                  │
│ Health: 68 (Warning) ↓ Declining                              │
│ Updated: 5 minutes ago by Jane Doe (Risk Log upload)          │
│                                                                 │
│ ──────────────────────────────────────────────────────────────│
│                                                                 │
│ 📍 Latest Signals (5):                                         │
│                                                                 │
│ • Risk #13: Site activation slower (Priority 7)               │
│   Source: Risk Log uploaded by Jane Doe at 10:45 AM           │
│   Category: Site | Status: Open | Owner: Jane Doe             │
│   Escalation: Director level                                   │
│                                                                 │
│ • Risk #8: Enrollment below target (Priority 6)               │
│   Source: Risk Log uploaded by Jane Doe at 10:45 AM           │
│   Category: Clinical | Status: Open | Owner: John Smith       │
│   Escalation: Director level                                   │
│                                                                 │
│ • TMF: 12 missing regulatory documents                         │
│   Source: TMF Tracker uploaded by Jane Doe at 8:30 AM         │
│   Category: Regulatory | Status: Missing | Owner: Sarah Lee    │
│   Escalation: Director level                                   │
│                                                                 │
│ ──────────────────────────────────────────────────────────────│
│                                                                 │
│ 🔗 Correlations (3):                                           │
│                                                                 │
│ • Risk #13 → Site Activation milestone                        │
│   Type: Risk | Confidence: 85%                                │
│   Est. delay: 14 days | Cost impact: $344K                    │
│                                                                 │
│   Reasoning: "High priority site risk affects Site Activation  │
│   milestone. Historical data shows similar risks cause 14-day  │
│   delays."                                                     │
│                                                                 │
│ • Risk #8 → LPI (Last Patient In) milestone                   │
│   Type: Risk | Confidence: 90%                                │
│   Est. delay: 21 days | Cost impact: $512K                    │
│                                                                 │
│ • TMF Completeness → Regulatory Submission                     │
│   Type: Risk | Confidence: 80%                                │
│   Est. delay: 30 days | Cost impact: $733K                    │
│                                                                 │
│ ──────────────────────────────────────────────────────────────│
│                                                                 │
│ 🚨 Escalations (3):                                            │
│                                                                 │
│ • [DIRECTOR] Risk #13: Site activation at risk                │
│   Recommended Actions:                                         │
│   - Expedite site contract negotiations                        │
│   - Activate backup sites                                      │
│   - Review site selection criteria                             │
│   Status: Open | Created: 5 min ago                           │
│   [Acknowledge] [Add Note] [Mark Resolved]                    │
│                                                                 │
│ • [DIRECTOR] Risk #8: Enrollment below target                 │
│   Recommended Actions:                                         │
│   - Review enrollment forecasts                                │
│   - Adjust screen failure assumptions                          │
│   - Consider protocol amendments to widen criteria             │
│   Status: Open | Created: 5 min ago                           │
│   [Acknowledge] [Add Note] [Mark Resolved]                    │
│                                                                 │
│ [View Full Study Details] [Export Report]                     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Dashboard Features:**
- **Real-time updates**: Dashboard refreshes automatically after tracker uploads
- **Signal traceability**: Each signal shows upload source, timestamp, uploader
- **Correlation explanations**: Clear reasoning for why signals affect milestones
- **Recommended actions**: Prescriptive interventions for each escalation
- **Escalation management**: Acknowledge, add notes, mark resolved
- **Export**: Download PDF/Excel reports for executive reviews

---

## Error Handling

### Error 1: Tracker Not Configured

**Scenario**: CPM uploads tracker before Account Admin configures it

**Error Message**:
```
┌────────────────────────────────────────────────────────────────┐
│ ❌ Upload Failed                                               │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│ Risk Log tracker not configured for your organization.        │
│                                                                │
│ Contact your Account Admin to configure this tracker type    │
│ before uploading.                                             │
│                                                                │
│ Account Admin can configure trackers at:                      │
│ app.seleen.io → Account Management → Tracker Configuration   │
│                                                                │
│ [Contact Admin]                           [Close]             │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

**Resolution**: Account Admin must complete Phase 1 configuration first.

### Error 2: Column Mismatch

**Scenario**: Uploaded file columns don't match configured mapping

**Error Message**:
```
┌────────────────────────────────────────────────────────────────┐
│ ❌ Column Mismatch Detected                                    │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│ The uploaded file columns don't match your organization's     │
│ configured column mapping:                                     │
│                                                                │
│ Expected columns:                                              │
│ • ID, Risk Type, Description, Severity, Likelihood, Score,    │
│   Mitigation, Owner, Status, Target Date, Completion Date     │
│                                                                │
│ Found in your file:                                            │
│ • Risk Number, Type, Detail, Impact Level, Probability,       │
│   Rating, Plan, Assigned To, State, Due Date, Closed Date     │
│                                                                │
│ Solutions:                                                     │
│ 1. Use the standard template: [Download Template]            │
│ 2. Update column mapping: Contact Account Admin              │
│                                                                │
│ [Download Template]  [Contact Admin]  [Close]                │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

**Resolution**:
- Option 1: CPM downloads and uses standard template
- Option 2: Account Admin updates column mapping to match new column names

### Error 3: Validation Errors

**Scenario**: File contains invalid data (e.g., Impact = 5 when max is 3)

**Error Message**:
```
┌────────────────────────────────────────────────────────────────┐
│ ❌ Validation Errors Found                                     │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│ Found 3 validation errors in your file:                       │
│                                                                │
│ Row 5:                                                         │
│ • Impact must be 1-3 (found: 5)                              │
│                                                                │
│ Row 12:                                                        │
│ • Missing required field 'Category'                           │
│                                                                │
│ Row 18:                                                        │
│ • Target Date invalid format (found: "Q1 2026")              │
│   Use: YYYY-MM-DD (e.g., 2026-03-15)                         │
│                                                                │
│ Please fix these errors in your Excel file and re-upload.     │
│                                                                │
│ [View Full Error Log]                [Close]                  │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

**Resolution**: CPM fixes errors in Excel file and re-uploads.

### Error 4: File Too Large

**Scenario**: File exceeds 10 MB limit

**Error Message**:
```
┌────────────────────────────────────────────────────────────────┐
│ ❌ File Too Large                                              │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│ File size: 15.2 MB                                            │
│ Maximum allowed: 10 MB                                        │
│                                                                │
│ Recommendations:                                               │
│ • Remove unnecessary sheets                                    │
│ • Remove historical data (keep current snapshot only)         │
│ • Remove embedded images/charts                               │
│ • Save as .xlsx (not .xls) for better compression            │
│                                                                │
│ If you need to upload larger files, contact support.          │
│                                                                │
│ [Close]                                                        │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

**Resolution**: CPM reduces file size and re-uploads.

### Error 5: Network Timeout

**Scenario**: Upload interrupted by network issue

**Error Message**:
```
┌────────────────────────────────────────────────────────────────┐
│ ⚠️ Upload Interrupted                                          │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│ Network connection lost during upload.                        │
│                                                                │
│ Please check your internet connection and try again.          │
│                                                                │
│ [Retry]                                   [Close]              │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

**Resolution**: CPM retries upload.

---

## Standard Tracker Templates

### Risk Log Template

**Columns:**

| Column Name | Data Type | Required | Example | Notes |
|------------|-----------|----------|---------|-------|
| Risk # | Integer | Yes | 13 | Unique risk identifier |
| Category | Text | Yes | Site, Clinical, Regulatory | Dropdown list |
| Risk Detail | Text | Yes | "Site activation slower..." | Description |
| Impact | Integer (1-3) | Yes | 2 | 1=Low, 2=Medium, 3=High |
| Probability | Integer (1-3) | Yes | 2 | 1=Low, 2=Medium, 3=High |
| Priority | Integer (1-9) | Yes | 4 | Auto-calculated: Impact × Probability |
| Mitigation Plan | Text | No | "Expedite contracts" | Response strategy |
| Owner | Text | Yes | Jane Doe | Responsible party |
| Status | Text | Yes | Open, In Progress, Closed | Dropdown list |
| Target Date | Date | No | 2026-03-15 | Target resolution date |
| Actual Date | Date | No | 2026-03-10 | Actual completion date |
| Escalation Notes | Text | No | "VP aware, monitoring weekly" | Explicit escalations |

**Data Validation Rules:**
- Impact: Must be 1, 2, or 3
- Probability: Must be 1, 2, or 3
- Priority: Auto-calculated (Impact × Probability) = 1-9
- Status: Dropdown (Open, In Progress, Closed)
- Category: Dropdown (Site, Clinical, Regulatory, Safety, Financial, Operational)

**Download**: `/api/v1/trackers/templates/risk_log`

### TMF Completeness Template

**Main Sheet: TMF Artifacts**

| Column Name | Data Type | Required | Example | Notes |
|------------|-----------|----------|---------|-------|
| Artifact Number | Text | Yes | 01.01.001 | TMF numbering system |
| Artifact Name | Text | Yes | "Protocol Approval Letter" | Document name |
| Status | Text | Yes | Complete, Missing Document, Pending | Dropdown |
| Reviewer | Text | No | Sarah Lee | QC reviewer name |
| Missing Documents | Text | No | "Site 05 missing signature page" | Details |
| Responsible Party | Text | Yes | Jane Doe | Document owner |
| Resolution | Text | No | "Requested from site 2026-02-10" | Action taken |
| Closed By | Text | No | Sarah Lee | Who resolved |
| Closed Date | Date | No | 2026-02-12 | Resolution date |

**Review Log Sheet: Issues & Escalations**

| Column Name | Data Type | Required | Example | Notes |
|------------|-----------|----------|---------|-------|
| Item # | Integer | Yes | 1 | Unique issue ID |
| Item Type | Text | Yes | Question, Finding, Escalation | Dropdown |
| Category | Text | Yes | Regulatory, Site, Vendor | Dropdown |
| Description | Text | Yes | "Site 03 TMF access delayed" | Issue detail |
| Priority | Integer (1-9) | Yes | 7 | Severity |
| Status | Text | Yes | Open, Closed | Dropdown |
| Owner | Text | Yes | Jane Doe | Responsible |
| Due Date | Date | No | 2026-03-01 | Target |
| Resolution | Text | No | "Access granted 2026-02-15" | Outcome |

**Download**: `/api/v1/trackers/templates/tmf_completeness`

---

## Best Practices

### For Account Admins

1. **Configure trackers early**: Set up column mappings during onboarding
2. **Download templates**: Provide CPMs with standard templates
3. **Test with sample data**: Upload sample files to verify configuration
4. **Document custom rules**: If customizing signal thresholds, document rationale
5. **Review escalations**: Periodically review escalation effectiveness

### For CPMs

1. **Use standard templates**: Maintain consistency with configured column names
2. **Upload regularly**: Upload trackers at least weekly (daily for active studies)
3. **Keep data clean**: Validate data before upload (no missing required fields)
4. **Review notifications**: Check upload results in MS Project add-in
5. **Update statuses**: Close resolved risks/issues to reduce noise

### For Directors & Executives

1. **Acknowledge escalations**: Mark escalations as "Acknowledged" to show awareness
2. **Add resolution notes**: Document actions taken for audit trail
3. **Export reports**: Download PDF reports for executive meetings
4. **Review trends**: Monitor health score trends to identify declining studies
5. **Act on interventions**: Implement recommended actions for high-priority escalations

---

## Troubleshooting

### Q: CPM uploaded tracker but signals not appearing in dashboard

**A:** Check these steps:
1. Verify tracker type matches configuration (Risk Log vs TMF vs Budget)
2. Ensure rows meet signal extraction thresholds (e.g., Priority ≥6 for risks)
3. Check that Status = "Open" (closed items don't generate signals)
4. Verify upload succeeded (check notification in MS Project)
5. Refresh dashboard (F5) to clear cache

### Q: Column mapping keeps failing

**A:** Common issues:
1. **Hidden columns**: Excel file has hidden columns not in sample file → Unhide all columns
2. **Multiple sheets**: System can't auto-detect sheet → Use single-sheet file or specify sheet name
3. **Merged cells**: System can't parse merged headers → Unmerge header row
4. **Typos in column names**: "Severity" vs "Severty" → Fix typos in Excel file

### Q: Escalations going to wrong level (Director vs VP)

**A:** Review signal extraction rules:
1. Check configured thresholds (Account Management → Tracker Configuration)
2. Verify Priority calculation (Impact × Probability)
3. Check Category field (Safety risks always escalate to VP)
4. Check Escalation Notes field (any text triggers VP escalation)

### Q: Upload taking too long (>5 minutes)

**A:** Performance troubleshooting:
1. **File size**: If >10 MB, reduce file size
2. **Row count**: If >500 rows, consider splitting into multiple files
3. **Network speed**: Check internet connection
4. **Server load**: If persistent, contact support (may be server capacity issue)

### Q: Dashboard showing stale data

**A:** Cache refresh:
1. Hard refresh browser (Ctrl+F5 or Cmd+Shift+R)
2. Check "Updated" timestamp on dashboard
3. If >24 hours old, run manual refresh: `/api/v1/dashboard/portfolio/refresh`
4. Check daily intelligence refresh job status: `scripts/daily_intelligence_refresh.py`

---

## API Reference

### Tracker Upload Endpoint

```http
POST /api/v1/trackers/upload
Content-Type: multipart/form-data
Authorization: Bearer {API_KEY}

Query Parameters:
- org_id (required): Organization ID
- project_id (required): Project ID
- tracker_type (required): "risk_log", "tmf_completeness", "budget", "vendor"

Form Data:
- file (required): Excel or CSV file

Response:
{
  "success": true,
  "upload_id": "upload_abc123",
  "rows_processed": 23,
  "signals_extracted": 5,
  "correlations_generated": 3,
  "escalations_detected": 2,
  "health_score": 68,
  "health_status": "warning",
  "health_trend": "declining",
  "top_risks": [
    {
      "risk_number": 13,
      "description": "Site activation slower",
      "priority": 7,
      "category": "Site"
    }
  ],
  "processing_time_seconds": 3.2
}
```

### Get Tracker Upload History

```http
GET /api/v1/trackers/uploads
Authorization: Bearer {API_KEY}

Query Parameters:
- org_id (required): Organization ID
- project_id (optional): Filter by project
- tracker_type (optional): Filter by tracker type
- limit (optional): Max results (default: 50)
- offset (optional): Pagination offset (default: 0)

Response:
{
  "uploads": [
    {
      "upload_id": "upload_abc123",
      "tracker_type": "risk_log",
      "uploaded_by": "jane@example.com",
      "upload_timestamp": "2026-02-13T10:45:23Z",
      "original_filename": "Risk_Log_Jan2026.xlsx",
      "rows_parsed": 23,
      "signals_extracted": 5,
      "parse_status": "success"
    }
  ],
  "total": 150,
  "limit": 50,
  "offset": 0
}
```

### Get Signals from Upload

```http
GET /api/v1/trackers/uploads/{upload_id}/signals
Authorization: Bearer {API_KEY}

Response:
{
  "upload_id": "upload_abc123",
  "signals": [
    {
      "signal_id": "sig_123",
      "signal_type": "risk_high_priority",
      "signal_category": "Site",
      "signal_description": "Risk #13: Site activation slower",
      "priority": 7,
      "status": "open",
      "escalation_level": "director",
      "date_identified": "2026-02-13"
    }
  ],
  "total_signals": 5
}
```

---

## Appendix: Configuration Examples

### Example 1: Risk Log with Custom Thresholds

**Organization**: Acme Clinical Trials
**Tracker**: Risk Log
**Customization**: Higher thresholds for Director escalation (Priority ≥7 instead of ≥6)

**Column Mapping:**
```json
{
  "ID": "risk_number",
  "Risk Type": "category",
  "Description": "risk_detail",
  "Severity": "impact",
  "Likelihood": "probability",
  "Score": "priority",
  "Mitigation": "mitigation_plan",
  "Owner": "owner",
  "Status": "status",
  "Target Date": "target_date",
  "Completion Date": "actual_completion_date",
  "Escalation Notes": "escalation_notes"
}
```

**Signal Extraction Rules:**
```json
{
  "director_threshold": 7,
  "vp_threshold": 9,
  "safety_vp_threshold": 7,
  "escalation_notes_triggers_vp": true,
  "no_mitigation_triggers_director": true,
  "overdue_triggers_director": true
}
```

### Example 2: TMF Tracker with Multiple Sheets

**Organization**: BioPharm Inc
**Tracker**: TMF Completeness
**Customization**: Multi-sheet workbook (Artifacts + Review Log)

**Sheet 1: TMF Artifacts**
```json
{
  "Artifact #": "artifact_number",
  "Document Name": "artifact_name",
  "Status": "status",
  "QC Reviewer": "reviewer",
  "Missing Items": "missing_documents",
  "Owner": "responsible_party",
  "Action Taken": "resolution",
  "Resolved By": "closed_by",
  "Resolved Date": "closed_date"
}
```

**Sheet 2: Review Log**
```json
{
  "ID": "item_number",
  "Type": "item_type",
  "Category": "category",
  "Description": "description",
  "Priority": "priority",
  "Status": "status",
  "Owner": "owner",
  "Due": "due_date",
  "Resolution": "resolution"
}
```

**Signal Extraction Rules:**
```json
{
  "missing_document_triggers_director": true,
  "completeness_threshold": 75,
  "days_before_milestone": 60,
  "review_log_escalation_triggers_vp": true,
  "overdue_review_items_threshold_days": 14
}
```

---

## Support

### Contact Information

- **Technical Support**: support@seleen.io
- **Account Admin Questions**: admin@seleen.io
- **API/Integration Support**: developers@seleen.io

### Documentation Links

- **API Integration Guide**: `/backend/API_INTEGRATION_GUIDE.md`
- **Dashboard User Guide**: `app.seleen.io/help/dashboard`
- **MS Project Add-in Guide**: `app.seleen.io/help/addin`
- **Video Tutorials**: `app.seleen.io/tutorials`

---

**Document Version**: 1.0
**Last Updated**: 2026-02-13
**Author**: Seleen Intelligence Layer Team
