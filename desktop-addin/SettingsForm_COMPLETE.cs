using System;
using System.Windows.Forms;

namespace IlanaPM.AddIn
{
    public partial class SettingsForm : Form
    {
        // Control declarations
        private Label lblApiUrl;
        private TextBox txtApiUrl;
        private Button btnTestConnection;
        private Label lblWebhookUrl;
        private TextBox txtWebhookUrl;
        private CheckBox chkAutoUpdate;
        private Button btnSave;
        private Button btnCancel;

        public SettingsForm()
        {
            InitializeComponent();
            LoadSettings();
        }

        private void LoadSettings()
        {
            txtApiUrl.Text = Properties.Settings.Default.ApiBaseUrl ?? "https://ilanapm.azurewebsites.net";
            txtWebhookUrl.Text = Properties.Settings.Default.TeamsWebhookUrl ?? "";
            chkAutoUpdate.Checked = Properties.Settings.Default.AutoUpdateEnabled;
        }

        private void btnSave_Click(object sender, EventArgs e)
        {
            Properties.Settings.Default.ApiBaseUrl = txtApiUrl.Text;
            Properties.Settings.Default.TeamsWebhookUrl = txtWebhookUrl.Text;
            Properties.Settings.Default.AutoUpdateEnabled = chkAutoUpdate.Checked;
            Properties.Settings.Default.Save();

            MessageBox.Show("Settings saved successfully!", "Success", MessageBoxButtons.OK, MessageBoxIcon.Information);
            this.Close();
        }

        private void btnCancel_Click(object sender, EventArgs e)
        {
            this.Close();
        }

        private void btnTestConnection_Click(object sender, EventArgs e)
        {
            try
            {
                var client = new System.Net.Http.HttpClient();
                var response = client.GetAsync(txtApiUrl.Text + "/api/v1/health").Result;

                if (response.IsSuccessStatusCode)
                {
                    MessageBox.Show("Connection successful!", "Test Connection", MessageBoxButtons.OK, MessageBoxIcon.Information);
                }
                else
                {
                    MessageBox.Show("Connection failed: " + response.StatusCode.ToString(), "Test Connection", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                }
            }
            catch (Exception ex)
            {
                MessageBox.Show("Connection error: " + ex.Message, "Test Connection", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
        }

        private void InitializeComponent()
        {
            this.lblApiUrl = new System.Windows.Forms.Label();
            this.txtApiUrl = new System.Windows.Forms.TextBox();
            this.btnTestConnection = new System.Windows.Forms.Button();
            this.lblWebhookUrl = new System.Windows.Forms.Label();
            this.txtWebhookUrl = new System.Windows.Forms.TextBox();
            this.chkAutoUpdate = new System.Windows.Forms.CheckBox();
            this.btnSave = new System.Windows.Forms.Button();
            this.btnCancel = new System.Windows.Forms.Button();
            this.SuspendLayout();

            // lblApiUrl
            this.lblApiUrl.AutoSize = true;
            this.lblApiUrl.Location = new System.Drawing.Point(20, 20);
            this.lblApiUrl.Name = "lblApiUrl";
            this.lblApiUrl.Size = new System.Drawing.Size(100, 15);
            this.lblApiUrl.TabIndex = 0;
            this.lblApiUrl.Text = "API Base URL:";

            // txtApiUrl
            this.txtApiUrl.Location = new System.Drawing.Point(20, 40);
            this.txtApiUrl.Name = "txtApiUrl";
            this.txtApiUrl.Size = new System.Drawing.Size(400, 23);
            this.txtApiUrl.TabIndex = 1;

            // btnTestConnection
            this.btnTestConnection.Location = new System.Drawing.Point(430, 40);
            this.btnTestConnection.Name = "btnTestConnection";
            this.btnTestConnection.Size = new System.Drawing.Size(100, 23);
            this.btnTestConnection.TabIndex = 2;
            this.btnTestConnection.Text = "Test Connection";
            this.btnTestConnection.UseVisualStyleBackColor = true;
            this.btnTestConnection.Click += new System.EventHandler(this.btnTestConnection_Click);

            // lblWebhookUrl
            this.lblWebhookUrl.AutoSize = true;
            this.lblWebhookUrl.Location = new System.Drawing.Point(20, 80);
            this.lblWebhookUrl.Name = "lblWebhookUrl";
            this.lblWebhookUrl.Size = new System.Drawing.Size(150, 15);
            this.lblWebhookUrl.TabIndex = 3;
            this.lblWebhookUrl.Text = "Teams Webhook URL:";

            // txtWebhookUrl
            this.txtWebhookUrl.Location = new System.Drawing.Point(20, 100);
            this.txtWebhookUrl.Name = "txtWebhookUrl";
            this.txtWebhookUrl.Size = new System.Drawing.Size(510, 23);
            this.txtWebhookUrl.TabIndex = 4;

            // chkAutoUpdate
            this.chkAutoUpdate.AutoSize = true;
            this.chkAutoUpdate.Location = new System.Drawing.Point(20, 140);
            this.chkAutoUpdate.Name = "chkAutoUpdate";
            this.chkAutoUpdate.Size = new System.Drawing.Size(200, 19);
            this.chkAutoUpdate.TabIndex = 5;
            this.chkAutoUpdate.Text = "Enable automatic update checks";
            this.chkAutoUpdate.UseVisualStyleBackColor = true;

            // btnSave
            this.btnSave.Location = new System.Drawing.Point(374, 180);
            this.btnSave.Name = "btnSave";
            this.btnSave.Size = new System.Drawing.Size(75, 23);
            this.btnSave.TabIndex = 6;
            this.btnSave.Text = "Save";
            this.btnSave.UseVisualStyleBackColor = true;
            this.btnSave.Click += new System.EventHandler(this.btnSave_Click);

            // btnCancel
            this.btnCancel.Location = new System.Drawing.Point(455, 180);
            this.btnCancel.Name = "btnCancel";
            this.btnCancel.Size = new System.Drawing.Size(75, 23);
            this.btnCancel.TabIndex = 7;
            this.btnCancel.Text = "Cancel";
            this.btnCancel.UseVisualStyleBackColor = true;
            this.btnCancel.Click += new System.EventHandler(this.btnCancel_Click);

            // SettingsForm
            this.ClientSize = new System.Drawing.Size(550, 220);
            this.Controls.Add(this.btnCancel);
            this.Controls.Add(this.btnSave);
            this.Controls.Add(this.chkAutoUpdate);
            this.Controls.Add(this.txtWebhookUrl);
            this.Controls.Add(this.lblWebhookUrl);
            this.Controls.Add(this.btnTestConnection);
            this.Controls.Add(this.txtApiUrl);
            this.Controls.Add(this.lblApiUrl);
            this.Name = "SettingsForm";
            this.StartPosition = System.Windows.Forms.FormStartPosition.CenterScreen;
            this.Text = "Ilana PM - Settings";
            this.ResumeLayout(false);
            this.PerformLayout();
        }
    }
}
