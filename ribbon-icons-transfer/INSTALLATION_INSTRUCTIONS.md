# Ribbon Icons Installation Instructions

## Files Included
- `criticalpath.png` - Critical Path button icon
- `loadtemplate.png` - Load Template button icon
- `multicountry.png` - Multi-Country button icon
- `settings.png` - Settings button icon
- `validatetimeline.png` - Validate Timeline button icon
- `viewreport.png` - View Report button icon

## Installation Steps (Windows VM - Visual Studio)

### Step 1: Copy Icon Files to Project
1. Open Windows VM
2. Copy all 6 PNG files from this folder
3. Navigate to: `desktop-addin\IlanaPM.AddIn\Resources\`
4. Paste the 6 PNG files into the Resources folder

### Step 2: Add Icons to Visual Studio Project
1. Open `IlanaPM.AddIn.sln` in Visual Studio
2. In Solution Explorer, right-click on `Resources` folder
3. Select "Add" → "Existing Item..."
4. Select all 6 PNG files
5. Click "Add"

### Step 3: Set File Properties
For **each of the 6 PNG files**:
1. Right-click the file in Solution Explorer
2. Select "Properties"
3. Set **Build Action**: `Embedded Resource`
4. Set **Copy to Output Directory**: `Copy if newer`

### Step 4: Add Icons to Resources.resx
1. In Solution Explorer, open `Properties\Resources.resx`
2. In the Resources designer toolbar, click the **"+"** button (Add Resource)
3. Select "Add Existing File..." from the menu
4. Browse to the Resources folder and select all 6 PNG files
5. Click "Open" to add them
6. **IMPORTANT**: Rename each resource (remove the .png extension):
   - Rename `validatetimeline.png` → `validatetimeline`
   - Rename `criticalpath.png` → `criticalpath`
   - Rename `loadtemplate.png` → `loadtemplate`
   - Rename `multicountry.png` → `multicountry`
   - Rename `viewreport.png` → `viewreport`
   - Rename `settings.png` → `settings`
7. Save Resources.resx (Ctrl+S)

### Step 5: Update Ribbon Designer

**Option A: Using Ribbon Designer (Recommended)**

Open `IlanaPMRibbon.Designer.cs` and set the Image property for each button:

```csharp
// In InitializeComponent() method, add these lines:

this.btnValidate.Image = global::IlanaPM.AddIn.Properties.Resources.validatetimeline;
this.btnCriticalPath.Image = global::IlanaPM.AddIn.Properties.Resources.criticalpath;
this.btnLoadTemplate.Image = global::IlanaPM.AddIn.Properties.Resources.loadtemplate;
this.btnMultiCountry.Image = global::IlanaPM.AddIn.Properties.Resources.multicountry;
this.btnViewReport.Image = global::IlanaPM.AddIn.Properties.Resources.viewreport;
this.btnSettings.Image = global::IlanaPM.AddIn.Properties.Resources.settings;
```

**Option B: Using Ribbon XML (if applicable)**

If using Ribbon XML, add a `GetButtonImage` method in `IlanaPMRibbon.cs`:

```csharp
public System.Drawing.Bitmap GetButtonImage(Office.IRibbonControl control)
{
    switch (control.Id)
    {
        case "btnValidate":
            return Properties.Resources.validatetimeline;
        case "btnCriticalPath":
            return Properties.Resources.criticalpath;
        case "btnLoadTemplate":
            return Properties.Resources.loadtemplate;
        case "btnMultiCountry":
            return Properties.Resources.multicountry;
        case "btnViewReport":
            return Properties.Resources.viewreport;
        case "btnSettings":
            return Properties.Resources.settings;
        default:
            return null;
    }
}
```

And in your Ribbon XML, add `getImage` callback:
```xml
<button id="btnValidate" label="Validate Timeline" getImage="GetButtonImage" onAction="btnValidate_Click" />
```

### Step 6: Build and Test
1. Build the solution (Build → Build Solution)
2. Fix any compilation errors
3. Open MS Project
4. Verify all 6 ribbon buttons display their custom icons
5. Verify icons are clear and visible at ribbon sizes (16x16 or 32x32)

## Troubleshooting

### Icons not showing:
- Verify Build Action is set to "Embedded Resource"
- Verify Resources.resx has the correct resource names (no file extensions)
- Rebuild the solution completely (Build → Rebuild Solution)

### Build errors:
- Check that all icon files are in the Resources folder
- Verify the resource names in code match the resource names in Resources.resx
- Ensure using statements include: `using IlanaPM.AddIn.Properties;`

## Expected Result
All 6 buttons in the Ilana PM ribbon should display their custom icons:
- ✅ Validate Timeline (checkmark/validation icon)
- ✅ Critical Path (network/path icon)
- ✅ Load Template (document/template icon)
- ✅ Multi-Country (globe/world icon)
- ✅ View Report (report/chart icon)
- ✅ Settings (gear icon)
