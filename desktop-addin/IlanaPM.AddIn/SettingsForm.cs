using System;
using System.Windows.Forms;

namespace IlanaPM.AddIn
{
    public partial class SettingsForm : Form
    {
        // Control field declarations
        private Label lblTitle;
        private GroupBox grpLicense;
        private Label lblEmail;
        private Label lblOrganization;
        private Label lblTier;
        private Label lblSeats;
        private Label lblExpiry;
        private Label lblStatus;
        private Button btnManageBilling;
        private Button btnReactivate;
        private Button btnClose;
        private ProgressBar progressBar;

        // Telemetry controls REMOVED in Phase 1C (deferred to future release)

        public SettingsForm()
        {
            InitializeComponent();
            LoadLicenseInfo();
        }

        private async void LoadLicenseInfo()
        {
            try
            {
                // Check if token exists
                bool hasToken = Services.SecureStorage.HasToken();

                if (!hasToken)
                {
                    ShowNotActivated();
                    return;
                }

                // Get stored info
                string email = Services.SecureStorage.ReadUserEmail();
                string tier = Services.SecureStorage.ReadTier();

                // Try to fetch fresh license info from API
                try
                {
                    progressBar.Visible = true;
                    var apiClient = new Services.ApiClient();
                    var licenseInfo = await apiClient.GetLicenseInfoAsync();

                    // Display license info
                    lblEmail.Text = $"Email: {licenseInfo.user_email}";
                    lblOrganization.Text = $"Organization: {licenseInfo.org_name}";
                    lblTier.Text = $"Tier: {(licenseInfo.tier == "professional" ? "Professional" : "Enterprise")}";
                    lblSeats.Text = $"Seats: {licenseInfo.seats_used}/{licenseInfo.seats_purchased}";
                    lblExpiry.Text = $"Valid until: {licenseInfo.subscription_end}";

                    // Status indicator
                    if (licenseInfo.status == "active")
                    {
                        lblStatus.Text = "Status: ✓ Active";
                        lblStatus.ForeColor = System.Drawing.Color.Green;
                        btnManageBilling.Enabled = true;
                    }
                    else
                    {
                        lblStatus.Text = $"Status: {licenseInfo.status}";
                        lblStatus.ForeColor = System.Drawing.Color.Red;
                        btnManageBilling.Enabled = false;
                    }

                    progressBar.Visible = false;
                }
                catch (Models.UnauthorizedException)
                {
                    // Token expired - show reactivation needed
                    ShowExpired();
                }
                catch (Exception ex)
                {
                    // Network error - show cached info
                    System.Diagnostics.Debug.WriteLine($"Failed to fetch license info: {ex.Message}");
                    lblEmail.Text = $"Email: {email ?? "Unknown"}";
                    lblOrganization.Text = "Organization: (Offline)";
                    lblTier.Text = $"Tier: {(tier == "professional" ? "Professional" : tier == "enterprise" ? "Enterprise" : "Unknown")}";
                    lblSeats.Text = "Seats: (Offline)";
                    lblExpiry.Text = "Valid until: (Offline)";
                    lblStatus.Text = "Status: Cannot verify (network error)";
                    lblStatus.ForeColor = System.Drawing.Color.Orange;
                    btnManageBilling.Enabled = false;
                    progressBar.Visible = false;
                }
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Error loading license info: {ex.Message}");
                ShowNotActivated();
            }
        }

        private void ShowNotActivated()
        {
            lblEmail.Text = "Email: Not activated";
            lblOrganization.Text = "Organization: -";
            lblTier.Text = "Tier: -";
            lblSeats.Text = "Seats: -";
            lblExpiry.Text = "Valid until: -";
            lblStatus.Text = "Status: ⚠ No license";
            lblStatus.ForeColor = System.Drawing.Color.Red;
            btnManageBilling.Enabled = false;
            btnReactivate.Text = "Activate License";
            progressBar.Visible = false;
        }

        private void ShowExpired()
        {
            string email = Services.SecureStorage.ReadUserEmail();
            lblEmail.Text = $"Email: {email ?? "Unknown"}";
            lblOrganization.Text = "Organization: -";
            lblTier.Text = "Tier: -";
            lblSeats.Text = "Seats: -";
            lblExpiry.Text = "Valid until: Expired";
            lblStatus.Text = "Status: ⚠ Expired or Invalid";
            lblStatus.ForeColor = System.Drawing.Color.Red;
            btnManageBilling.Enabled = false;
            btnReactivate.Text = "Reactivate License";
            progressBar.Visible = false;
        }

        private async void btnManageBilling_Click(object sender, EventArgs e)
        {
            try
            {
                btnManageBilling.Enabled = false;
                btnManageBilling.Text = "Opening...";
                progressBar.Visible = true;

                var apiClient = new Services.ApiClient();
                string portalUrl = await apiClient.GetBillingPortalUrlAsync();

                // Open billing portal in default browser
                System.Diagnostics.Process.Start(portalUrl);

                MessageBox.Show(
                    "Billing portal opened in your browser.\n\n" +
                    "You can:\n" +
                    "• Cancel your subscription\n" +
                    "• Update payment method\n" +
                    "• View invoices\n" +
                    "• Update billing information",
                    "Billing Portal",
                    MessageBoxButtons.OK,
                    MessageBoxIcon.Information
                );

                btnManageBilling.Text = "Manage Billing";
                btnManageBilling.Enabled = true;
                progressBar.Visible = false;
            }
            catch (Models.UnauthorizedException)
            {
                MessageBox.Show(
                    "Your license has expired. Please reactivate your license.",
                    "License Expired",
                    MessageBoxButtons.OK,
                    MessageBoxIcon.Warning
                );
                ShowExpired();
                btnManageBilling.Text = "Manage Billing";
                btnManageBilling.Enabled = false;
                progressBar.Visible = false;
            }
            catch (Exception ex)
            {
                MessageBox.Show(
                    $"Failed to open billing portal:\n\n{ex.Message}\n\n" +
                    "Please try again or contact support@ilanaimmersive.com",
                    "Error",
                    MessageBoxButtons.OK,
                    MessageBoxIcon.Error
                );
                btnManageBilling.Text = "Manage Billing";
                btnManageBilling.Enabled = true;
                progressBar.Visible = false;
            }
        }

        private void btnReactivate_Click(object sender, EventArgs e)
        {
            var activationForm = new LicenseActivationForm();
            if (activationForm.ShowDialog() == DialogResult.OK)
            {
                // Reload license info after successful activation
                LoadLicenseInfo();
            }
        }

        private void btnClose_Click(object sender, EventArgs e)
        {
            this.Close();
        }

        private void InitializeComponent()
        {
            this.lblTitle = new System.Windows.Forms.Label();
            this.grpLicense = new System.Windows.Forms.GroupBox();
            this.lblEmail = new System.Windows.Forms.Label();
            this.lblOrganization = new System.Windows.Forms.Label();
            this.lblTier = new System.Windows.Forms.Label();
            this.lblSeats = new System.Windows.Forms.Label();
            this.lblExpiry = new System.Windows.Forms.Label();
            this.lblStatus = new System.Windows.Forms.Label();
            this.btnManageBilling = new System.Windows.Forms.Button();
            this.btnReactivate = new System.Windows.Forms.Button();
            this.btnClose = new System.Windows.Forms.Button();
            this.progressBar = new System.Windows.Forms.ProgressBar();

            // Telemetry controls
            this.grpTelemetry = new System.Windows.Forms.GroupBox();
            this.chkTelemetryConsent = new System.Windows.Forms.CheckBox();
            this.lblTelemetryInfo = new System.Windows.Forms.Label();
            this.lnkPrivacyPolicy = new System.Windows.Forms.LinkLabel();

            this.SuspendLayout();

            //
            // lblTitle
            //
            this.lblTitle.AutoSize = true;
            this.lblTitle.Font = new System.Drawing.Font("Segoe UI", 12F, System.Drawing.FontStyle.Bold);
            this.lblTitle.Location = new System.Drawing.Point(20, 20);
            this.lblTitle.Name = "lblTitle";
            this.lblTitle.Size = new System.Drawing.Size(150, 21);
            this.lblTitle.TabIndex = 0;
            this.lblTitle.Text = "License Information";

            //
            // grpLicense
            //
            this.grpLicense.Location = new System.Drawing.Point(20, 55);
            this.grpLicense.Name = "grpLicense";
            this.grpLicense.Size = new System.Drawing.Size(510, 220);
            this.grpLicense.TabIndex = 1;
            this.grpLicense.TabStop = false;
            this.grpLicense.Text = "License Details";

            //
            // lblStatus
            //
            this.lblStatus.AutoSize = true;
            this.lblStatus.Font = new System.Drawing.Font("Segoe UI", 9F, System.Drawing.FontStyle.Bold);
            this.lblStatus.Location = new System.Drawing.Point(15, 25);
            this.lblStatus.Name = "lblStatus";
            this.lblStatus.Size = new System.Drawing.Size(100, 15);
            this.lblStatus.TabIndex = 0;
            this.lblStatus.Text = "Status: Loading...";
            this.grpLicense.Controls.Add(this.lblStatus);

            //
            // lblEmail
            //
            this.lblEmail.AutoSize = true;
            this.lblEmail.Font = new System.Drawing.Font("Segoe UI", 9F);
            this.lblEmail.Location = new System.Drawing.Point(15, 55);
            this.lblEmail.Name = "lblEmail";
            this.lblEmail.Size = new System.Drawing.Size(150, 15);
            this.lblEmail.TabIndex = 1;
            this.lblEmail.Text = "Email: Loading...";
            this.grpLicense.Controls.Add(this.lblEmail);

            //
            // lblOrganization
            //
            this.lblOrganization.AutoSize = true;
            this.lblOrganization.Font = new System.Drawing.Font("Segoe UI", 9F);
            this.lblOrganization.Location = new System.Drawing.Point(15, 80);
            this.lblOrganization.Name = "lblOrganization";
            this.lblOrganization.Size = new System.Drawing.Size(150, 15);
            this.lblOrganization.TabIndex = 2;
            this.lblOrganization.Text = "Organization: Loading...";
            this.grpLicense.Controls.Add(this.lblOrganization);

            //
            // lblTier
            //
            this.lblTier.AutoSize = true;
            this.lblTier.Font = new System.Drawing.Font("Segoe UI", 9F);
            this.lblTier.Location = new System.Drawing.Point(15, 105);
            this.lblTier.Name = "lblTier";
            this.lblTier.Size = new System.Drawing.Size(100, 15);
            this.lblTier.TabIndex = 3;
            this.lblTier.Text = "Tier: Loading...";
            this.grpLicense.Controls.Add(this.lblTier);

            //
            // lblSeats
            //
            this.lblSeats.AutoSize = true;
            this.lblSeats.Font = new System.Drawing.Font("Segoe UI", 9F);
            this.lblSeats.Location = new System.Drawing.Point(15, 130);
            this.lblSeats.Name = "lblSeats";
            this.lblSeats.Size = new System.Drawing.Size(100, 15);
            this.lblSeats.TabIndex = 4;
            this.lblSeats.Text = "Seats: Loading...";
            this.grpLicense.Controls.Add(this.lblSeats);

            //
            // lblExpiry
            //
            this.lblExpiry.AutoSize = true;
            this.lblExpiry.Font = new System.Drawing.Font("Segoe UI", 9F);
            this.lblExpiry.Location = new System.Drawing.Point(15, 155);
            this.lblExpiry.Name = "lblExpiry";
            this.lblExpiry.Size = new System.Drawing.Size(150, 15);
            this.lblExpiry.TabIndex = 5;
            this.lblExpiry.Text = "Valid until: Loading...";
            this.grpLicense.Controls.Add(this.lblExpiry);

            //
            // btnManageBilling
            //
            this.btnManageBilling.Location = new System.Drawing.Point(15, 185);
            this.btnManageBilling.Name = "btnManageBilling";
            this.btnManageBilling.Size = new System.Drawing.Size(150, 30);
            this.btnManageBilling.TabIndex = 6;
            this.btnManageBilling.Text = "Manage Billing";
            this.btnManageBilling.UseVisualStyleBackColor = true;
            this.btnManageBilling.Click += new System.EventHandler(this.btnManageBilling_Click);
            this.grpLicense.Controls.Add(this.btnManageBilling);

            //
            // btnReactivate
            //
            this.btnReactivate.Location = new System.Drawing.Point(175, 185);
            this.btnReactivate.Name = "btnReactivate";
            this.btnReactivate.Size = new System.Drawing.Size(150, 30);
            this.btnReactivate.TabIndex = 7;
            this.btnReactivate.Text = "Reactivate License";
            this.btnReactivate.UseVisualStyleBackColor = true;
            this.btnReactivate.Click += new System.EventHandler(this.btnReactivate_Click);
            this.grpLicense.Controls.Add(this.btnReactivate);

            //
            // progressBar
            //
            this.progressBar.Location = new System.Drawing.Point(20, 285);
            this.progressBar.Name = "progressBar";
            this.progressBar.Size = new System.Drawing.Size(510, 10);
            this.progressBar.Style = System.Windows.Forms.ProgressBarStyle.Marquee;
            this.progressBar.TabIndex = 2;
            this.progressBar.Visible = false;

            // Telemetry controls REMOVED in Phase 1C

            //
            // btnClose
            //
            this.btnClose.Location = new System.Drawing.Point(455, 310);
            this.btnClose.Name = "btnClose";
            this.btnClose.Size = new System.Drawing.Size(75, 30);
            this.btnClose.TabIndex = 5;
            this.btnClose.Text = "Close";
            this.btnClose.UseVisualStyleBackColor = true;
            this.btnClose.Click += new System.EventHandler(this.btnClose_Click);

            //
            // SettingsForm
            //
            this.ClientSize = new System.Drawing.Size(550, 360);
            this.Controls.Add(this.btnClose);
            this.Controls.Add(this.progressBar);
            this.Controls.Add(this.grpLicense);
            this.Controls.Add(this.lblTitle);
            this.FormBorderStyle = System.Windows.Forms.FormBorderStyle.FixedDialog;
            this.MaximizeBox = false;
            this.MinimizeBox = false;
            this.Name = "SettingsForm";
            this.StartPosition = System.Windows.Forms.FormStartPosition.CenterScreen;
            this.Text = "Ilana PM - Settings";
            this.ResumeLayout(false);
            this.PerformLayout();
        }
    }
}
