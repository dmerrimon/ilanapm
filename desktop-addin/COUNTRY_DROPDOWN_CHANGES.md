# Country Dropdown Implementation

## Changes Made

### 1. Add Site Dialog - Country Input Changed to Dropdown

**File:** `ClinicalProjectManagerForm.cs`

**Changed from:** Text input for country
**Changed to:** Dropdown (ComboBox) with 22 country ISO codes

### Changes:

#### A. Dialog Control (Line ~763-775)
**Before:**
```csharp
var lblCountry = new Label { Text = "Country:", ... };
var txtCountry = new TextBox { Name = "txtCountry", ... Text = "USA" };
```

**After:**
```csharp
var lblCountry = new Label { Text = "Country Code:", ... };
var cmbCountry = new ComboBox { Name = "cmbCountry", ... DropDownStyle = ComboBoxStyle.DropDownList };
cmbCountry.Items.AddRange(new object[] {
    "US", "CA", "MX", "PE",           // Americas
    "GB",                              // Europe
    "ZA", "KE", "UG", "TZ", "ZW",     // Africa 1
    "MW", "LR", "ML", "SL", "GN", "CD", // Africa 2
    "AU", "BD", "CN", "IN", "TH", "VN" // Asia-Pacific
});
cmbCountry.SelectedItem = existingSite?.CountryCode ?? "US";
```

#### B. Add Site Handler (Line ~648-666)
**Before:**
```csharp
var country = dialog.Controls["txtCountry"].Text;
...
CountryCode = country,
CountryName = country,
```

**After:**
```csharp
var countryCode = ((ComboBox)dialog.Controls["cmbCountry"]).SelectedItem?.ToString() ?? "US";
...
CountryCode = countryCode,
CountryName = ConvertISOCodeToCountryName(countryCode),
```

#### C. Edit Site Handler (Line ~692-696)
**Before:**
```csharp
site.CountryCode = dialog.Controls["txtCountry"].Text;
site.CountryName = dialog.Controls["txtCountry"].Text;
```

**After:**
```csharp
site.CountryCode = ((ComboBox)dialog.Controls["cmbCountry"]).SelectedItem?.ToString() ?? "US";
site.CountryName = ConvertISOCodeToCountryName(site.CountryCode);
```

## Benefits

1. **Data Validation:** Users can only select valid country codes
2. **User Experience:** No need to memorize or type ISO codes
3. **Consistency:** Matches the 22 countries supported by the backend ontology
4. **Data Integrity:** Prevents typos and invalid country codes

## Country Codes Available (22 total)

### Americas (4)
- US - United States
- CA - Canada
- MX - Mexico
- PE - Peru

### Europe (1)
- GB - United Kingdom

### Africa (11)
- ZA - South Africa
- KE - Kenya
- **UG - Uganda**
- TZ - Tanzania
- ZW - Zimbabwe
- MW - Malawi
- LR - Liberia
- ML - Mali
- SL - Sierra Leone
- GN - Guinea
- CD - DRC (Democratic Republic of the Congo)

### Asia-Pacific (6)
- AU - Australia
- BD - Bangladesh
- CN - China
- IN - India
- TH - Thailand
- VN - Vietnam

## How It Works

1. **Add Site:** User clicks "Add Site" button
2. **Dialog Opens:** Shows dropdown with all 22 country codes
3. **Select Country:** User selects from dropdown (e.g., "UG" for Uganda)
4. **Site Created:** CountryCode saves as "UG", CountryName saves as "Uganda"
5. **Template Generation:** Uses "UG" to fetch Uganda-specific tasks from API
6. **Authority-Specific Tasks:** Templates show NDA, UNCST, EC for Uganda

## Related Changes

This complements the earlier changes where we:
1. Added all 22 countries to the main wizard's country checklist
2. Updated ConvertCountryNameToISOCode() mapping
3. Updated ConvertISOCodeToCountryName() reverse mapping
4. Implemented authority-specific template generation in backend

## Testing Checklist

- [ ] Open Add Site dialog - verify dropdown appears
- [ ] Verify dropdown shows all 22 country codes
- [ ] Select "UG" - verify site saves with CountryCode="UG"
- [ ] Check site grid - verify CountryName displays as "Uganda"
- [ ] Edit existing site - verify country dropdown pre-selects correct code
- [ ] Generate Site Startup template for Uganda site
- [ ] Verify template shows "Submit to National Drug Authority (NDA)"
- [ ] Verify template shows "Obtain UNCST Research Permit"
