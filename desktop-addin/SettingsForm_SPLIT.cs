// ============================================================================
// SettingsForm.cs - BUSINESS LOGIC ONLY
// ============================================================================
// This goes in SettingsForm.cs
// Delete everything in SettingsForm.cs and replace with this code
// ============================================================================

using System;
using System.Windows.Forms;

namespace IlanaPM.AddIn
{
    public partial class SettingsForm : Form
    {
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
    }
}
