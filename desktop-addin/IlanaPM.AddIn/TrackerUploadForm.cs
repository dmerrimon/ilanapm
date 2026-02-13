using System;
using System.IO;
using System.Windows.Forms;

namespace IlanaPM.AddIn
{
    /// <summary>
    /// Form for uploading tracker files (Risk Log, TMF, Budget, Vendor)
    /// Phase 5: Core Tracker Upload workflow
    /// </summary>
    public partial class TrackerUploadForm : Form
    {
        private string _orgId;
        private string _projectId;
        private string _selectedFilePath;

        public string SelectedTrackerType { get; private set; }
        public Models.TrackerUploadResult UploadResult { get; private set; }

        public TrackerUploadForm(string orgId, string projectId)
        {
            _orgId = orgId;
            _projectId = projectId;
            InitializeComponent();
            PopulateTrackerTypes();
        }

        private void PopulateTrackerTypes()
        {
            cboTrackerType.Items.Add("Risk Log");
            cboTrackerType.Items.Add("TMF Completeness Tracker");
            cboTrackerType.Items.Add("Budget Tracker");
            cboTrackerType.Items.Add("Vendor Management Tracker");
            cboTrackerType.SelectedIndex = 0;
        }

        private void BtnBrowse_Click(object sender, EventArgs e)
        {
            using (var openDialog = new OpenFileDialog())
            {
                openDialog.Filter = "Excel files (*.xlsx;*.xls)|*.xlsx;*.xls|CSV files (*.csv)|*.csv|All files (*.*)|*.*";
                openDialog.Title = "Select Tracker File";
                openDialog.CheckFileExists = true;

                if (openDialog.ShowDialog() == DialogResult.OK)
                {
                    _selectedFilePath = openDialog.FileName;
                    txtFilePath.Text = _selectedFilePath;
                    btnUpload.Enabled = true;
                    lblStatus.Text = "";
                }
            }
        }

        private async void BtnUpload_Click(object sender, EventArgs e)
        {
            if (string.IsNullOrEmpty(_selectedFilePath))
            {
                MessageBox.Show("Please select a file to upload.", "File Required",
                    MessageBoxButtons.OK, MessageBoxIcon.Warning);
                return;
            }

            if (!File.Exists(_selectedFilePath))
            {
                MessageBox.Show("Selected file does not exist.", "File Not Found",
                    MessageBoxButtons.OK, MessageBoxIcon.Error);
                return;
            }

            try
            {
                // Disable UI during upload
                btnBrowse.Enabled = false;
                btnUpload.Enabled = false;
                cboTrackerType.Enabled = false;
                progressBar.Visible = true;
                progressBar.Style = ProgressBarStyle.Marquee;
                lblStatus.Text = "Uploading...";
                lblStatus.ForeColor = System.Drawing.Color.Blue;

                // Read file bytes
                byte[] fileBytes = File.ReadAllBytes(_selectedFilePath);
                string fileName = Path.GetFileName(_selectedFilePath);

                // Map tracker type to API value
                string trackerType = MapTrackerType(cboTrackerType.SelectedItem.ToString());
                SelectedTrackerType = trackerType;

                System.Diagnostics.Debug.WriteLine($"Uploading tracker: {fileName}, Type: {trackerType}, Size: {fileBytes.Length} bytes");

                // Upload to API
                var apiClient = new Services.ApiClient();
                UploadResult = await apiClient.UploadTrackerAsync(
                    _orgId,
                    _projectId,
                    trackerType,
                    fileBytes,
                    fileName
                );

                if (UploadResult.success)
                {
                    // Success
                    progressBar.Style = ProgressBarStyle.Continuous;
                    progressBar.Value = 100;
                    lblStatus.Text = $"✓ Upload complete!\n" +
                                    $"{UploadResult.rows_processed} rows processed, " +
                                    $"{UploadResult.signals_extracted} signals extracted";
                    lblStatus.ForeColor = System.Drawing.Color.DarkGreen;

                    System.Diagnostics.Debug.WriteLine($"Upload successful: {UploadResult.rows_processed} rows, " +
                                                       $"{UploadResult.signals_extracted} signals, " +
                                                       $"{UploadResult.escalations_detected} escalations");

                    // Wait a moment to show success message
                    await System.Threading.Tasks.Task.Delay(1000);

                    DialogResult = DialogResult.OK;
                    Close();
                }
                else
                {
                    // Upload failed
                    progressBar.Visible = false;
                    ShowUploadError(UploadResult);

                    // Re-enable UI
                    btnBrowse.Enabled = true;
                    btnUpload.Enabled = true;
                    cboTrackerType.Enabled = true;
                }
            }
            catch (Models.UnauthorizedException ex)
            {
                progressBar.Visible = false;
                lblStatus.Text = "";
                MessageBox.Show(ex.Message, "License Required",
                    MessageBoxButtons.OK, MessageBoxIcon.Warning);

                // Close form and let ribbon handler show activation form
                DialogResult = DialogResult.Cancel;
                Close();
            }
            catch (Exception ex)
            {
                progressBar.Visible = false;
                lblStatus.Text = $"✗ Upload failed: {ex.Message}";
                lblStatus.ForeColor = System.Drawing.Color.Red;

                System.Diagnostics.Debug.WriteLine($"Upload error: {ex.Message}");

                MessageBox.Show(
                    $"Error uploading file:\n\n{ex.Message}",
                    "Upload Error",
                    MessageBoxButtons.OK,
                    MessageBoxIcon.Error
                );

                // Re-enable UI
                btnBrowse.Enabled = true;
                btnUpload.Enabled = true;
                cboTrackerType.Enabled = true;
            }
        }

        private void ShowUploadError(Models.TrackerUploadResult result)
        {
            string errorMsg = result.error_message ?? "Upload failed";
            lblStatus.Text = $"✗ {errorMsg}";
            lblStatus.ForeColor = System.Drawing.Color.Red;

            // Build detailed error message
            string detailedMessage = errorMsg;

            if (result.error_type == "column_mismatch")
            {
                detailedMessage += "\n\nThis tracker type has not been configured for your organization.\n" +
                                  "Please contact your Account Administrator to set up column mappings.";
            }
            else if (result.error_type == "not_configured")
            {
                detailedMessage += "\n\nPlease ask your Account Administrator to configure this tracker type " +
                                  "in the Seleen web portal (Account Management → Tracker Configuration).";
            }
            else if (result.validation_errors != null && result.validation_errors.Count > 0)
            {
                detailedMessage += "\n\nValidation errors found:\n";

                int errorCount = Math.Min(5, result.validation_errors.Count);
                for (int i = 0; i < errorCount; i++)
                {
                    var err = result.validation_errors[i];
                    detailedMessage += $"• Row {err.row_number}: {err.error_message}\n";
                }

                if (result.validation_errors.Count > 5)
                {
                    detailedMessage += $"\n...and {result.validation_errors.Count - 5} more errors.";
                }

                detailedMessage += "\n\nPlease fix these errors in your tracker file and try again.";
            }

            MessageBox.Show(detailedMessage, "Upload Failed",
                MessageBoxButtons.OK, MessageBoxIcon.Error);
        }

        private string MapTrackerType(string displayName)
        {
            switch (displayName)
            {
                case "Risk Log":
                    return "risk_log";
                case "TMF Completeness Tracker":
                    return "tmf_tracker";
                case "Budget Tracker":
                    return "budget_tracker";
                case "Vendor Management Tracker":
                    return "vendor_tracker";
                default:
                    return "risk_log";
            }
        }
    }
}
