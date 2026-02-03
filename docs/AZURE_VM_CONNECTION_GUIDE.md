# Azure Windows Development VM - Connection Guide

**Created:** 2026-01-15
**Purpose:** Windows development environment for Microsoft Project VSTO add-in

---

## VM Details

| Property | Value |
|----------|-------|
| **Name** | ilana-dev-vm |
| **Location** | East US |
| **Size** | Standard_B2ms (2 vCPU, 8GB RAM) |
| **OS** | Windows 11 Pro (23H2) |
| **Public IP** | `20.51.190.180` |
| **Status** | Running |

---

## Connection Credentials

**Username:** `ilanaadmin`
**Password:** `IlanaPM2026!Secure#Dev`

⚠️ **IMPORTANT:** Change this password after first login!

---

## How to Connect from Mac

### Option 1: Microsoft Remote Desktop (Recommended)

1. **Download Microsoft Remote Desktop from Mac App Store:**
   - Open App Store
   - Search for "Microsoft Remote Desktop"
   - Download and install (it's free)

2. **Add PC Connection:**
   - Open Microsoft Remote Desktop
   - Click **"+"** button → **"Add PC"**
   - **PC Name:** `20.51.190.180`
   - **User account:** Click "Add User Account"
     - **Username:** `ilanaadmin`
     - **Password:** `IlanaPM2026!Secure#Dev`
   - Click **"Add"**

3. **Connect:**
   - Double-click the connection
   - Accept certificate warning (first time only)
   - You'll see Windows 11 desktop

### Option 2: Command Line (Quick Test)

```bash
# Install rdesktop via Homebrew
brew install freerdp

# Connect
xfreerdp /u:ilanaadmin /p:IlanaPM2026!Secure#Dev /v:20.51.190.180
```

---

## First Time Setup on Windows VM

Once connected, follow these steps:

### 1. Change Password (Recommended)

```powershell
# Press Ctrl+Alt+End (Mac: Fn+Ctrl+Option+Delete)
# Select "Change a password"
```

### 2. Install Visual Studio 2022 Community

1. Open Edge browser
2. Go to: https://visualstudio.microsoft.com/downloads/
3. Download **Visual Studio 2022 Community** (free)
4. Run installer
5. **Workloads to select:**
   - ✅ .NET desktop development
   - ✅ Office/SharePoint development
   - ✅ ASP.NET and web development (optional)
6. Click **Install** (takes ~30-60 minutes)

### 3. Install Microsoft Project (Trial)

1. Go to: https://www.microsoft.com/en-us/microsoft-365/project/project-plan-1
2. Click **"Try for free"** (30-day trial)
3. Sign in with Microsoft account
4. Download and install Project

**Alternative:** If you have a Microsoft 365 subscription with Project, use that instead.

### 4. Install Git for Windows

1. Go to: https://git-scm.com/download/win
2. Download and install Git
3. Accept all defaults

### 5. Clone Your Ilana PM Repository

```powershell
# Open PowerShell
cd C:\Users\ilanaadmin\Documents
git clone https://github.com/dmerrimon/ilanapm.git
cd ilanapm
```

### 6. Install .NET Framework 4.8

1. Go to: https://dotnet.microsoft.com/en-us/download/dotnet-framework/net48
2. Download and install
3. Restart VM if prompted

---

## Cost Management

**Current Cost:** ~$40/month

### Save Money by Stopping VM When Not Using

**To Stop VM (from your Mac):**
```bash
az vm stop --resource-group ilana-pm-rg --name ilana-dev-vm
```

**To Start VM (when you need it):**
```bash
az vm start --resource-group ilana-pm-rg --name ilana-dev-vm
```

**To Check Status:**
```bash
az vm show --resource-group ilana-pm-rg --name ilana-dev-vm --show-details --query powerState
```

**Cost Breakdown:**
- **Running:** ~$0.067/hour = ~$1.60/day
- **Stopped (deallocated):** $0/hour (only pay for storage ~$0.16/day)
- **Storage (always charged):** ~$5/month for OS disk

💡 **Tip:** Stop the VM every night to save ~$1.60/day = ~$48/month

---

## Accessing Your Production API from VM

Your Ilana PM backend API is accessible from the VM:

**Production API:** https://ilanapm.azurewebsites.net

**Test from VM PowerShell:**
```powershell
Invoke-RestMethod -Uri "https://ilanapm.azurewebsites.net/api/v1/health"
```

---

## Troubleshooting

### Can't Connect?

**Check if VM is running:**
```bash
az vm show --resource-group ilana-pm-rg --name ilana-dev-vm --show-details --query powerState
```

**If stopped, start it:**
```bash
az vm start --resource-group ilana-pm-rg --name ilana-dev-vm
```

**Check public IP (in case it changed):**
```bash
az vm show --resource-group ilana-pm-rg --name ilana-dev-vm --show-details --query publicIps -o tsv
```

### Remote Desktop Certificate Warning

This is normal for first connection. Click **"Continue"** or **"Yes"**.

### Slow Performance?

The B2ms size (2 CPU, 8GB RAM) is adequate for development. If you need more power:

```bash
# Upgrade to B4ms (4 CPU, 16GB RAM) - ~$120/month
az vm resize --resource-group ilana-pm-rg --name ilana-dev-vm --size Standard_B4ms
```

---

## Next Steps

1. ✅ Connect to VM
2. ✅ Install Visual Studio 2022 Community
3. ✅ Install Microsoft Project (trial)
4. ✅ Clone ilanapm repository
5. 🚀 Start building VSTO add-in

---

## Security Notes

- ⚠️ **Change default password** after first login
- 🔒 VM is accessible from internet (RDP port 3389 open)
- 💡 Consider restricting RDP to your IP only:
  ```bash
  az vm open-port --resource-group ilana-pm-rg --name ilana-dev-vm --port 3389 --priority 1000 --source-address-prefix YOUR_IP_ADDRESS
  ```
- 🔐 Enable Windows Firewall on the VM
- 📝 Regular Windows Updates recommended

---

## Quick Reference Card

| Action | Command |
|--------|---------|
| Start VM | `az vm start --resource-group ilana-pm-rg --name ilana-dev-vm` |
| Stop VM | `az vm stop --resource-group ilana-pm-rg --name ilana-dev-vm` |
| Check Status | `az vm show --resource-group ilana-pm-rg --name ilana-dev-vm --show-details --query powerState` |
| Get IP | `az vm show --resource-group ilana-pm-rg --name ilana-dev-vm --show-details --query publicIps -o tsv` |
| Restart VM | `az vm restart --resource-group ilana-pm-rg --name ilana-dev-vm` |

---

**Ready to connect!** 🎉

Use Microsoft Remote Desktop to connect to: `20.51.190.180`
