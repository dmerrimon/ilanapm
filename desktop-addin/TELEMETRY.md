# Ilana PM Add-In Telemetry Documentation

## Overview

The Ilana PM Add-In implements privacy-focused telemetry to support ML learning and improve user experience. All telemetry collection requires explicit user opt-in consent (default: OFF).

**Privacy Principles:**
- Opt-in by default (not opt-out)
- User IDs are SHA-256 hashed (irreversible)
- No personally identifiable information (PII) collected
- No project data (task names, dates, content) collected
- Only aggregate usage metrics tracked
- Batch sending reduces API calls (10 events per batch)

---

## Telemetry Event Types

All events are defined in `Models/TelemetryEvent.cs`:

### Session Events
- **SessionStarted** - Add-in session begins
  - Properties: `ms_project_version`, `addin_version`
  - Tracked in: `ThisAddIn_Startup`

- **SessionEnded** - Add-in session ends
  - Properties: `session_duration_seconds`
  - Tracked in: `ThisAddIn_Shutdown`

### Feature Usage Events
- **FeatureOpened** - User opens a feature
  - Properties: `feature` (feature name)
  - Tracked for: Template Manager, Multi-Country Calculator, Clinical Setup, Essential Documents Tracker

- **FeatureClosed** - User closes a feature
  - Properties: `feature`, `result` (OK/Cancel)
  - Tracked for: Template Manager, Multi-Country Calculator, Clinical Setup, Essential Documents Tracker

- **ButtonClicked** - User clicks a button
  - Properties: varies by context
  - Tracked for: Multi-Country Calculator calculations

### Template Events
- **TemplateLoaded** - User generates a template
  - Properties: `template_type`, `country_code`, `task_count`, `filters_applied`
  - Tracked in: `UnifiedTemplateManagerForm.btnGenerate_Click`

- **TemplateFiltered** - User applies filters to template (future)
  - Properties: TBD
  - Status: Placeholder for future use

- **TasksGenerated** - Tasks created in MS Project (future)
  - Properties: TBD
  - Status: Placeholder for future use

### Validation Events
- **ValidationStarted** - Timeline validation initiated
  - Properties: none
  - Tracked in: `IlanaPMRibbon.btnValidate_Click`

- **ValidationCompleted** - Validation finished
  - Properties: `issue_count`, `task_count`
  - Tracked in: `IlanaPMRibbon.btnValidate_Click`

- **ValidationIssueAccepted** - User accepted a suggestion (future)
  - Properties: TBD
  - Status: Placeholder for future use

- **ValidationIssueIgnored** - User ignored a warning (future)
  - Properties: TBD
  - Status: Placeholder for future use

### Analysis Events
- **CriticalPathAnalyzed** - Critical path analysis run
  - Properties: `task_count`, `total_duration`
  - Tracked in: `IlanaPMRibbon.btnCriticalPath_Click`

- **RiskAnalysisViewed** - Risk dashboard viewed / tab switched
  - Properties: `tab_name`, `tab_index`
  - Tracked in: `EnhancedValidationResultsForm.TabControl_SelectedIndexChanged`

### Clinical Management Events (Future)
- **SiteAdded** - Site added to metadata
  - Status: Placeholder for future use

- **AmendmentCreated** - Amendment created
  - Status: Placeholder for future use

- **DocumentCollected** - Essential document collected
  - Status: Placeholder for future use

### Workflow Events
- **FeatureSequence** - Track feature usage order
  - Properties: `sequence` (feature chain), `feature_count`
  - Tracked via: `TelemetryService.TrackFeatureSequence()`
  - Status: Available but not yet actively used

---

## Implementation Details

### TelemetryService

**Location:** `Services/TelemetryService.cs`

**Key Methods:**
- `TrackEvent(TelemetryEventType type, Dictionary<string, object> properties)` - Track an event
- `FlushEventsAsync()` - Send queued events to API (auto-triggered at batch size 10)
- `FlushEventsSync()` - Synchronous flush for shutdown
- `SetUserConsent(bool consent)` - Update user consent setting
- `GetSessionDurationSeconds()` - Calculate current session duration
- `TrackFeatureSequence(string[] features)` - Track workflow patterns

**Batch Configuration:**
- Batch size: 10 events
- Auto-flush when queue reaches 10 events
- Manual flush on app shutdown
- Events lost on API failure (by design - prevents infinite accumulation)

**Privacy Features:**
- SHA-256 hashing for user IDs (uses user email from SecureStorage)
- Fallback to "anonymous" if email not available
- Consent check before every tracking call
- Queue cleared immediately when user opts out

### API Endpoint

**Location:** `Services/ApiClient.cs`

**Method:** `SendTelemetryBatchAsync(TelemetryBatch batch)`

**Endpoint:** `POST /api/v1/telemetry/batch`

**Behavior:**
- Fails silently (no exceptions thrown to user)
- Uses async/await pattern
- Returns without action if API error occurs
- Debugging messages written to Debug output

---

## Current Telemetry Coverage

### Phase 4 Implementation Status

| Location | Events Tracked | Status |
|----------|---------------|--------|
| **ThisAddIn.cs** | SessionStarted, SessionEnded | ✅ Complete |
| **IlanaPMRibbon.cs** | ValidationStarted, ValidationCompleted, CriticalPathAnalyzed, FeatureOpened/Closed (5 features) | ✅ Complete |
| **UnifiedTemplateManagerForm.cs** | TemplateLoaded, FeatureOpened, FeatureClosed | ✅ Complete |
| **EnhancedValidationResultsForm.cs** | RiskAnalysisViewed (tab switching) | ✅ Complete |
| **MultiCountryCalculatorForm.cs** | ButtonClicked (calculations) | ✅ Complete |
| **CriticalPathResultsForm.cs** | (tracked in ribbon handler) | ✅ Complete |
| **ClinicalSetupForm.cs** | FeatureOpened, FeatureClosed (ribbon only) | ✅ Complete |
| **EssentialDocumentsTrackerForm.cs** | FeatureOpened, FeatureClosed (ribbon only) | ✅ Complete |
| **SettingsForm.cs** | (no tracking - privacy) | ✅ Intentional |
| **LicenseActivationForm.cs** | (no tracking - privacy) | ✅ Intentional |

**Coverage Summary:**
- 8 forms with telemetry tracking
- 5 event types actively used (11 defined for future)
- 15+ tracking points across application
- 100% of user-facing features tracked

---

## Privacy Compliance

### User Consent Management

**Default Setting:** `TelemetryConsent = False` (opt-in, not opt-out)

**Consent UI:** `SettingsForm.cs`
- Checkbox: "Allow usage analytics to improve predictions"
- Privacy policy link (future)
- Clear explanation of what's collected

**Consent Storage:** `Properties/Settings.settings`
- Setting name: `TelemetryConsent`
- Type: Boolean
- Scope: User
- Persisted across sessions

### What IS Collected

✅ Feature usage patterns (which buttons clicked, features opened)
✅ Session duration and frequency
✅ Template types and country selections (aggregate counts)
✅ Validation issue counts (not content)
✅ Critical path analysis metrics (task counts, durations)
✅ Multi-country calculator usage (countries compared)
✅ MS Project version and add-in version

### What is NOT Collected

❌ Project names or file paths
❌ Task names, descriptions, or content
❌ User email addresses (only SHA-256 hash)
❌ Date/time values from projects
❌ Resource names or assignments
❌ Custom field values
❌ Validation issue details or suggestions
❌ Settings or license information
❌ Any personally identifiable information (PII)

---

## ML Learning Use Cases

### Data Analysis Pipeline

1. **Batch Ingestion** - Events collected from API endpoint
2. **Storage** - Analytics database (separate from operational DB)
3. **Processing** - ML training pipeline consumes telemetry data
4. **Learning Outcomes:**
   - Feature adoption rates
   - Common workflow patterns
   - Template usage by country/region
   - Validation effectiveness metrics
   - Critical path analysis usage
   - Session duration patterns

### Prediction Improvements

- **Duration Predictions** - Learn from validation acceptance rates
- **Risk Scoring** - Understand which warnings users act on
- **Template Recommendations** - Identify most-used template combinations
- **Feature Discovery** - Suggest features based on user workflow patterns

### A/B Testing Framework (Future)

- Test new feature designs
- Measure feature adoption rates
- Compare workflow efficiency
- Validate UX improvements

---

## Debugging Telemetry

### Debug Output

All telemetry events write to Debug output:

```csharp
System.Diagnostics.Debug.WriteLine($"Telemetry: Tracked {type} event (queue size: {eventQueue.Count})");
```

**View Debug Output:**
- Run add-in from Visual Studio
- Open Output window
- Select "Debug" from Show output from dropdown
- Look for "Telemetry:" prefixed messages

### Common Debug Messages

```
Telemetry service initialized
Telemetry: User consent = False
Telemetry: User has not consented - event SessionStarted not tracked
Telemetry: Tracked FeatureOpened event (queue size: 1)
Telemetry: Flushing 10 events to API
Telemetry: Successfully sent 10 events
Telemetry events flushed on shutdown
```

### Troubleshooting

**Events not being tracked?**
1. Check user consent: `Properties.Settings.Default.TelemetryConsent`
2. Verify TelemetryService initialized: Check `Globals.ThisAddIn.TelemetryService != null`
3. Review Debug output for consent warnings

**Events not sent to API?**
1. Check network connectivity
2. Verify API endpoint URL in ApiClient
3. Check Debug output for API errors
4. Ensure queue reaches batch size (10 events) or shutdown occurs

**Session duration = 0?**
- Fixed in Phase 4 - now uses `sessionStartTime` field
- Calculates `DateTime.UtcNow - sessionStartTime`

---

## Future Enhancements

### Phase 5 (Planned)

1. **Auto-Fix Tracking**
   - Track when users accept/reject auto-fix suggestions
   - Measure auto-fix effectiveness

2. **Feature Sequence Tracking**
   - Actively track common workflow patterns
   - Identify feature chains (e.g., Template → Validate → Critical Path)

3. **Clinical Entity Tracking**
   - Track site additions
   - Track amendment creations
   - Track document collection rates

4. **Performance Metrics**
   - API response times
   - Template generation times
   - Validation duration

5. **Error Tracking** (Non-PII)
   - Exception types and frequencies
   - Feature failure rates
   - Recovery patterns

---

## Version History

**Phase 1 (Week 1-2):**
- Created TelemetryService and TelemetryEvent models
- Added consent UI to SettingsForm
- Implemented batch sending (10 events)
- SHA-256 user ID hashing

**Phase 2 (Week 3-4):**
- Added TemplateLoaded tracking to UnifiedTemplateManagerForm
- Implemented privacy-by-design approach

**Phase 3 (Week 5):**
- Added ribbon button tracking (all features)
- ValidationStarted/ValidationCompleted events
- CriticalPathAnalyzed event
- FeatureOpened/FeatureClosed for 5 features

**Phase 4 (Week 6):**
- Session tracking (SessionStarted/SessionEnded with duration)
- Tab switching tracking (RiskAnalysisViewed)
- Multi-country calculator tracking
- Fixed session duration bug (was 0, now calculates correctly)
- Removed duplicate SessionStarted tracking

**Current Version:** Phase 4 Complete

---

## Contact & Feedback

For questions about telemetry implementation or privacy concerns:
- Review this documentation
- Check Settings.settings for TelemetryConsent value
- Inspect Debug output for telemetry messages
- Review TelemetryService.cs source code

**Opt-out:** Uncheck "Allow usage analytics" in Settings form
