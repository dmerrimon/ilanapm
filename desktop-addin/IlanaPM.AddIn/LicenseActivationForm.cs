using System;
using System.Windows.Forms;
using System.Drawing;

namespace IlanaPM.AddIn
{
    public partial class LicenseActivationForm : Form
    {
        private Label lblTitle;
        private Label lblLicenseKey;
        private TextBox txtLicenseKey;
        private Label lblEmail;
        private TextBox txtEmail;
        private Button btnActivate;
        private Button btnCancel;
        private Label lblInstructions;
        private ProgressBar progressBar;
        private Label lblStatus;

        public LicenseActivationForm()
        {
            InitializeComponent();
        }

        private async void btnActivate_Click(object sender, EventArgs e)
        {
            // Validate inputs
            if (string.IsNullOrWhiteSpace(txtLicenseKey.Text))
            {
                MessageBox.Show("Please enter your license key.", "License Key Required",
                    MessageBoxButtons.OK, MessageBoxIcon.Warning);
                txtLicenseKey.Focus();
                return;
            }

            if (string.IsNullOrWhiteSpace(txtEmail.Text))
            {
                MessageBox.Show("Please enter your email address.", "Email Required",
                    MessageBoxButtons.OK, MessageBoxIcon.Warning);
                txtEmail.Focus();
                return;
            }

            // Basic email validation
            if (!txtEmail.Text.Contains("@") || !txtEmail.Text.Contains("."))
            {
                MessageBox.Show("Please enter a valid email address.", "Invalid Email",
                    MessageBoxButtons.OK, MessageBoxIcon.Warning);
                txtEmail.Focus();
                return;
            }

            // Disable form during activation
            SetFormEnabled(false);
            progressBar.Visible = true;
            lblStatus.Visible = true;
            lblStatus.Text = "Activating license...";

            try
            {
                string licenseKey = txtLicenseKey.Text.Trim();
                string email = txtEmail.Text.Trim().ToLower();
                string deviceId = Services.SecureStorage.GetDeviceId();

                // Create activation request
                var request = new Models.ActivationRequest
                {
                    license_key = licenseKey,
                    user_email = email,
                    device_id = deviceId
                };

                lblStatus.Text = "Contacting server...";
                Application.DoEvents();

                // Call backend API
                var apiClient = new Services.ApiClient();
                var response = await apiClient.ActivateLicenseAsync(request);

                lblStatus.Text = "Saving activation...";
                Application.DoEvents();

                // Store activation token and user info securely
                Services.SecureStorage.SaveToken(response.activation_token);
                Services.SecureStorage.SaveUserEmail(email);
                Services.SecureStorage.SaveOrgId(response.org_id);
                Services.SecureStorage.SaveTier(response.tier);

                lblStatus.Text = "Success!";
                progressBar.Visible = false;

                // Show success message
                string tierDisplay = response.tier == "professional" ? "Professional" : "Enterprise";
                MessageBox.Show(
                    $"License activated successfully!\n\n" +
                    $"Organization: {response.org_name}\n" +
                    $"Tier: {tierDisplay}\n" +
                    $"Seats: {response.seats_used}/{response.seats_purchased}\n" +
                    $"Valid until: {response.subscription_end}\n\n" +
                    $"{response.message}",
                    "Activation Successful",
                    MessageBoxButtons.OK,
                    MessageBoxIcon.Information
                );

                this.DialogResult = DialogResult.OK;
                this.Close();
            }
            catch (Models.LicenseException ex)
            {
                // License-specific errors
                progressBar.Visible = false;
                lblStatus.Visible = false;
                SetFormEnabled(true);

                MessageBox.Show(
                    $"License activation failed:\n\n{ex.Message}\n\n" +
                    $"Please check your license key and email address.\n\n" +
                    $"If you continue to have issues, contact support@ilanaimmersive.com",
                    "Activation Failed",
                    MessageBoxButtons.OK,
                    MessageBoxIcon.Error
                );
            }
            catch (Exception ex)
            {
                // General errors (network, API down, etc.)
                progressBar.Visible = false;
                lblStatus.Visible = false;
                SetFormEnabled(true);

                string errorMessage = ex.Message;
                if (ex.InnerException != null)
                {
                    errorMessage += "\n\nDetails: " + ex.InnerException.Message;
                }

                MessageBox.Show(
                    $"Activation error:\n\n{errorMessage}\n\n" +
                    $"Please check your internet connection and try again.\n\n" +
                    $"If the problem persists, contact support@ilanaimmersive.com",
                    "Error",
                    MessageBoxButtons.OK,
                    MessageBoxIcon.Error
                );

                System.Diagnostics.Debug.WriteLine($"Activation error: {ex}");
            }
        }

        private void btnCancel_Click(object sender, EventArgs e)
        {
            this.DialogResult = DialogResult.Cancel;
            this.Close();
        }

        private void SetFormEnabled(bool enabled)
        {
            txtLicenseKey.Enabled = enabled;
            txtEmail.Enabled = enabled;
            btnActivate.Enabled = enabled;
            btnCancel.Enabled = enabled;
        }

        private void InitializeComponent()
        {
            this.lblTitle = new System.Windows.Forms.Label();
            this.lblLicenseKey = new System.Windows.Forms.Label();
            this.txtLicenseKey = new System.Windows.Forms.TextBox();
            this.lblEmail = new System.Windows.Forms.Label();
            this.txtEmail = new System.Windows.Forms.TextBox();
            this.btnActivate = new System.Windows.Forms.Button();
            this.btnCancel = new System.Windows.Forms.Button();
            this.lblInstructions = new System.Windows.Forms.Label();
            this.progressBar = new System.Windows.Forms.ProgressBar();
            this.lblStatus = new System.Windows.Forms.Label();

            this.SuspendLayout();

            //
            // lblTitle
            //
            this.lblTitle.AutoSize = true;
            this.lblTitle.Font = new System.Drawing.Font("Segoe UI", 12F, System.Drawing.FontStyle.Bold);
            this.lblTitle.Location = new System.Drawing.Point(20, 20);
            this.lblTitle.Name = "lblTitle";
            this.lblTitle.Size = new System.Drawing.Size(250, 21);
            this.lblTitle.TabIndex = 0;
            this.lblTitle.Text = "Activate Ilana PM License";

            //
            // lblInstructions
            //
            this.lblInstructions.Location = new System.Drawing.Point(20, 50);
            this.lblInstructions.Name = "lblInstructions";
            this.lblInstructions.Size = new System.Drawing.Size(510, 40);
            this.lblInstructions.TabIndex = 1;
            this.lblInstructions.Text = "Enter your license key and email address to activate Ilana PM. You can find your license key in the welcome email or from your organization's admin.";

            //
            // lblLicenseKey
            //
            this.lblLicenseKey.AutoSize = true;
            this.lblLicenseKey.Font = new System.Drawing.Font("Segoe UI", 9F, System.Drawing.FontStyle.Regular);
            this.lblLicenseKey.Location = new System.Drawing.Point(20, 100);
            this.lblLicenseKey.Name = "lblLicenseKey";
            this.lblLicenseKey.Size = new System.Drawing.Size(75, 15);
            this.lblLicenseKey.TabIndex = 2;
            this.lblLicenseKey.Text = "License Key:";

            //
            // txtLicenseKey
            //
            this.txtLicenseKey.Font = new System.Drawing.Font("Consolas", 10F);
            this.txtLicenseKey.Location = new System.Drawing.Point(20, 120);
            this.txtLicenseKey.Name = "txtLicenseKey";
            this.txtLicenseKey.Size = new System.Drawing.Size(510, 23);
            this.txtLicenseKey.TabIndex = 3;
            // PlaceholderText not available in .NET Framework 4.7.2

            //
            // lblEmail
            //
            this.lblEmail.AutoSize = true;
            this.lblEmail.Font = new System.Drawing.Font("Segoe UI", 9F, System.Drawing.FontStyle.Regular);
            this.lblEmail.Location = new System.Drawing.Point(20, 160);
            this.lblEmail.Name = "lblEmail";
            this.lblEmail.Size = new System.Drawing.Size(84, 15);
            this.lblEmail.TabIndex = 4;
            this.lblEmail.Text = "Email Address:";

            //
            // txtEmail
            //
            this.txtEmail.Font = new System.Drawing.Font("Segoe UI", 10F);
            this.txtEmail.Location = new System.Drawing.Point(20, 180);
            this.txtEmail.Name = "txtEmail";
            this.txtEmail.Size = new System.Drawing.Size(510, 25);
            this.txtEmail.TabIndex = 5;
            // PlaceholderText not available in .NET Framework 4.7.2

            //
            // progressBar
            //
            this.progressBar.Location = new System.Drawing.Point(20, 220);
            this.progressBar.Name = "progressBar";
            this.progressBar.Size = new System.Drawing.Size(510, 23);
            this.progressBar.Style = System.Windows.Forms.ProgressBarStyle.Marquee;
            this.progressBar.TabIndex = 6;
            this.progressBar.Visible = false;

            //
            // lblStatus
            //
            this.lblStatus.AutoSize = true;
            this.lblStatus.Font = new System.Drawing.Font("Segoe UI", 9F, System.Drawing.FontStyle.Italic);
            this.lblStatus.ForeColor = System.Drawing.Color.FromArgb(0, 120, 212);
            this.lblStatus.Location = new System.Drawing.Point(20, 250);
            this.lblStatus.Name = "lblStatus";
            this.lblStatus.Size = new System.Drawing.Size(120, 15);
            this.lblStatus.TabIndex = 7;
            this.lblStatus.Text = "Activating license...";
            this.lblStatus.Visible = false;

            //
            // btnActivate
            //
            this.btnActivate.BackColor = System.Drawing.Color.FromArgb(0, 120, 212);
            this.btnActivate.FlatStyle = System.Windows.Forms.FlatStyle.Flat;
            this.btnActivate.Font = new System.Drawing.Font("Segoe UI", 9F, System.Drawing.FontStyle.Bold);
            this.btnActivate.ForeColor = System.Drawing.Color.White;
            this.btnActivate.Location = new System.Drawing.Point(350, 280);
            this.btnActivate.Name = "btnActivate";
            this.btnActivate.Size = new System.Drawing.Size(90, 35);
            this.btnActivate.TabIndex = 8;
            this.btnActivate.Text = "Activate";
            this.btnActivate.UseVisualStyleBackColor = false;
            this.btnActivate.Click += new System.EventHandler(this.btnActivate_Click);

            //
            // btnCancel
            //
            this.btnCancel.Location = new System.Drawing.Point(450, 280);
            this.btnCancel.Name = "btnCancel";
            this.btnCancel.Size = new System.Drawing.Size(80, 35);
            this.btnCancel.TabIndex = 9;
            this.btnCancel.Text = "Cancel";
            this.btnCancel.UseVisualStyleBackColor = true;
            this.btnCancel.Click += new System.EventHandler(this.btnCancel_Click);

            //
            // LicenseActivationForm
            //
            this.ClientSize = new System.Drawing.Size(550, 340);
            this.Controls.Add(this.btnCancel);
            this.Controls.Add(this.btnActivate);
            this.Controls.Add(this.lblStatus);
            this.Controls.Add(this.progressBar);
            this.Controls.Add(this.txtEmail);
            this.Controls.Add(this.lblEmail);
            this.Controls.Add(this.txtLicenseKey);
            this.Controls.Add(this.lblLicenseKey);
            this.Controls.Add(this.lblInstructions);
            this.Controls.Add(this.lblTitle);
            this.FormBorderStyle = System.Windows.Forms.FormBorderStyle.FixedDialog;
            this.MaximizeBox = false;
            this.MinimizeBox = false;
            this.Name = "LicenseActivationForm";
            this.StartPosition = System.Windows.Forms.FormStartPosition.CenterScreen;
            this.Text = "Ilana PM - License Activation";
            this.ResumeLayout(false);
            this.PerformLayout();
        }
    }
}
