# Study Metadata Requirement - Implementation Guide

## Overview

As of this update, **study metadata is REQUIRED** for all intelligence features. This ensures accurate benchmark matching by comparing timelines to the correct industry standards.

## Why Metadata is Critical

Benchmarks vary dramatically by:
- **Phase**: Phase I timelines ≠ Phase III timelines (e.g., IRB: 30 days vs 90 days)
- **Therapeutic Area**: Oncology ≠ Cardiology timelines (different approval processes)
- **Country/Authority**: US/FDA ≠ EU/EMA ≠ Japan/PMDA (different regulatory requirements)

Without this context, Seleen would be comparing apples to oranges.

## Required Fields

All intelligence API calls now require:

```json
{
  "study_metadata": {
    "phase": "Phase I | Phase II | Phase III | Phase IV",
    "therapeutic_area": "Oncology | Cardiology | Neurology | ...",
    "primary_country": "US | EU | JP | CA | GB | ..."
  }
}
```

Optional fields:
- `additional_countries`: Array of additional countries
- `study_name`: Friendly name for the study
- `study_id`: Internal study identifier
- `metadata_source`: "user_provided" | "inferred" | "project_profile"

## API Changes

### 1. New Endpoint: Validate Metadata

**Before uploading timelines**, validate that we have benchmarks:

```bash
POST /api/v1/intelligence/validate-metadata
Content-Type: application/json

{
  "phase": "Phase III",
  "therapeutic_area": "Oncology",
  "primary_country": "US"
}
```

**Response**:
```json
{
  "is_valid": true,
  "coverage_percent": 87.5,
  "benchmarks_available": 78,
  "total_task_categories": 92,
  "missing_benchmarks": ["enrollment_projection", "safety_monitoring"],
  "warnings": [],
  "recommendations": ["Excellent benchmark coverage (87.5%) for this study type!"]
}
```

**Use this to**:
- Show users upfront if we have good benchmark coverage
- Warn if coverage is low (<50%)
- Guide users to better metadata choices

### 2. Updated Endpoint: Intelligence Validation

**Before**:
```json
POST /api/v1/intelligence/validate-core
{
  "timeline": {...},
  "org_id": "org_123",
  "tier": "core"
}
```

**After** (metadata required):
```json
POST /api/v1/intelligence/validate-core
{
  "timeline": {...},
  "org_id": "org_123",
  "tier": "core",
  "study_metadata": {
    "phase": "Phase III",
    "therapeutic_area": "Oncology",
    "primary_country": "US",
    "study_name": "CART-01 Phase III Trial"
  }
}
```

**Error if metadata missing**:
```json
HTTP 422 Unprocessable Entity
{
  "error": "Study metadata required",
  "message": "Study metadata (phase, therapeutic_area, primary_country) is required for accurate benchmarking",
  "help": "Provide study_metadata with phase, therapeutic_area, and primary_country"
}
```

## Frontend Integration

### Customer Portal (React/Next.js)

**Option 1: Metadata Form Before Upload**
```typescript
// pages/intelligence/new.tsx
const [studyMetadata, setStudyMetadata] = useState({
  phase: '',
  therapeutic_area: '',
  primary_country: ''
});

// Step 1: Collect metadata
<MetadataForm
  metadata={studyMetadata}
  onChange={setStudyMetadata}
  onValidate={async () => {
    const result = await validateMetadata(studyMetadata);
    if (result.coverage_percent < 50) {
      showWarning(`Low benchmark coverage: ${result.coverage_percent}%`);
    }
  }}
/>

// Step 2: Upload timeline (only after metadata collected)
<TimelineUpload
  metadata={studyMetadata}
  onUpload={async (file) => {
    await analyzeTimeline(file, studyMetadata);
  }}
/>
```

**Option 2: Organization Defaults**
```typescript
// Settings page - set default metadata
const orgDefaults = {
  primary_therapeutic_areas: ['Oncology', 'Cardiology'],
  typical_phases: ['Phase II', 'Phase III'],
  primary_countries: ['US', 'EU'],
  default_country: 'US'
};

// On upload, use defaults but allow override
const metadata = {
  phase: selectedPhase || orgDefaults.typical_phases[0],
  therapeutic_area: selectedArea || orgDefaults.primary_therapeutic_areas[0],
  primary_country: selectedCountry || orgDefaults.default_country
};
```

### MS Project Add-In (C#)

**Show metadata form before validation**:

```csharp
private void ValidateButton_Click(object sender, EventArgs e)
{
    // Check if project has metadata
    var metadata = GetProjectMetadata();

    if (!metadata.IsValid())
    {
        // Show metadata collection form
        using (var form = new StudyMetadataForm())
        {
            if (form.ShowDialog() == DialogResult.OK)
            {
                metadata = form.GetMetadata();
                SaveMetadataToProject(metadata);
            }
            else
            {
                return; // User cancelled
            }
        }
    }

    // Now validate with metadata
    var request = new IntelligenceValidationRequest
    {
        Timeline = ExtractTimeline(),
        OrgId = this.orgId,
        Tier = this.tier,
        StudyMetadata = metadata
    };

    var result = await apiClient.ValidateTimeline(request);
    DisplayResults(result);
}
```

## Database Changes

### Organization Defaults

Store default metadata in `organizations` table:

```sql
ALTER TABLE organizations
ADD COLUMN organization_defaults JSONB DEFAULT '{
  "primary_therapeutic_areas": [],
  "typical_phases": [],
  "primary_countries": [],
  "default_country": null
}'::jsonb;
```

### Project Profiles

Enhanced `project_profiles` table (already exists):

```sql
-- These fields are now REQUIRED
ALTER TABLE project_profiles
ADD CONSTRAINT require_core_metadata
CHECK (
  therapeutic_area IS NOT NULL AND
  phase IS NOT NULL AND
  primary_country IS NOT NULL
);
```

## Configuration Models

```python
class StudyMetadata(BaseModel):
    """Required metadata for accurate benchmark matching"""
    phase: str  # Required
    therapeutic_area: str  # Required
    primary_country: str  # Required
    additional_countries: Optional[List[str]] = None
    study_name: Optional[str] = None
    study_id: Optional[str] = None
    metadata_source: str = "user_provided"

    def validate_required_fields(self) -> bool:
        """Validate that critical fields are populated"""
        return bool(self.phase and self.therapeutic_area and self.primary_country)
```

## Testing

Run metadata requirement tests:

```bash
cd backend
source venv/bin/activate
python tests/test_metadata_requirement.py
```

**Expected output**: 6/6 tests passing
- ✅ Metadata endpoint exists
- ✅ Valid metadata accepted
- ✅ Missing phase rejected (422)
- ✅ Missing therapeutic area rejected (422)
- ✅ Missing country rejected (422)
- ✅ Model validation works

## Migration Guide

### For Existing API Clients

**Step 1**: Add metadata to all validation calls

```diff
  {
    "timeline": {...},
    "org_id": "org_123",
-   "tier": "core"
+   "tier": "core",
+   "study_metadata": {
+     "phase": "Phase III",
+     "therapeutic_area": "Oncology",
+     "primary_country": "US"
+   }
  }
```

**Step 2**: Add metadata validation before upload

```javascript
// Check benchmark coverage before uploading
const coverage = await fetch('/api/v1/intelligence/validate-metadata', {
  method: 'POST',
  body: JSON.stringify(studyMetadata)
});

if (coverage.coverage_percent < 50) {
  alert(`Warning: Low benchmark coverage (${coverage.coverage_percent}%)`);
}
```

**Step 3**: Store metadata in project profiles

```javascript
// Create project profile with metadata
await fetch('/api/v1/intelligence/project-profiles', {
  method: 'POST',
  body: JSON.stringify({
    project_name: "CART-01 Trial",
    phase: "Phase III",
    therapeutic_area: "Oncology",
    primary_country: "US"
  })
});
```

## Benefits of This Approach

✅ **Accurate Benchmarking**: Compare timelines to relevant industry standards
✅ **Transparency**: Users know exactly what's being compared
✅ **Quality Control**: Catch missing metadata before wasting API calls
✅ **Better UX**: Show benchmark coverage upfront, set expectations
✅ **Data Quality**: Force structured metadata collection
✅ **Professional**: Demonstrates sophistication to CROs

## Next Steps

1. ✅ **API updated** to require metadata (DONE)
2. ⏳ **Update MS Project Add-In** to collect metadata
3. ⏳ **Update Customer Portal** with metadata forms
4. ⏳ **Add organization defaults** to Settings page
5. ⏳ **Build onboarding wizard** for new customers

## Questions?

See the implementation in:
- Models: `/backend/intelligence/models.py`
- API: `/backend/api/intelligence.py`
- Tests: `/backend/tests/test_metadata_requirement.py`
