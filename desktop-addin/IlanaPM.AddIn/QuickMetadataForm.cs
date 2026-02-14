using System;
using System.Collections.Generic;
using System.Drawing;
using System.Windows.Forms;
using IlanaPM.AddIn.Models;

namespace IlanaPM.AddIn
{
    /// <summary>
    /// Quick metadata collection form - shown when study metadata is missing
    ///
    /// Simple 3-field form to collect:
    /// - Study Phase
    /// - Therapeutic Area
    /// - Primary Country
    ///
    /// Automatically saves to MS Project custom fields after collection
    /// </summary>
    public partial class QuickMetadataForm : Form
    {
        public StudyMetadata CollectedMetadata { get; private set; }

        public QuickMetadataForm()
        {
            InitializeComponent();
            LoadDropdownOptions();
            CenterToParent();
        }

        /// <summary>
        /// Load dropdown options for all fields
        /// </summary>
        private void LoadDropdownOptions()
        {
            // Study phases
            cboPhase.Items.Clear();
            cboPhase.Items.Add("Phase I");
            cboPhase.Items.Add("Phase II");
            cboPhase.Items.Add("Phase III");
            cboPhase.Items.Add("Phase IV");
            cboPhase.Items.Add("Phase I/II");
            cboPhase.Items.Add("Phase II/III");

            // Therapeutic areas (most common)
            cboTherapeuticArea.Items.Clear();
            cboTherapeuticArea.Items.Add("Oncology");
            cboTherapeuticArea.Items.Add("Cardiology");
            cboTherapeuticArea.Items.Add("Neurology");
            cboTherapeuticArea.Items.Add("Infectious Disease");
            cboTherapeuticArea.Items.Add("Metabolic Disorders");
            cboTherapeuticArea.Items.Add("Respiratory");
            cboTherapeuticArea.Items.Add("Immunology");
            cboTherapeuticArea.Items.Add("Rare Diseases");
            cboTherapeuticArea.Items.Add("Dermatology");
            cboTherapeuticArea.Items.Add("Ophthalmology");
            cboTherapeuticArea.Items.Add("Other");

            // Countries/Authorities (most common)
            cboPrimaryCountry.Items.Clear();
            cboPrimaryCountry.Items.Add("US (FDA)");
            cboPrimaryCountry.Items.Add("EU (EMA)");
            cboPrimaryCountry.Items.Add("Japan (PMDA)");
            cboPrimaryCountry.Items.Add("Canada (Health Canada)");
            cboPrimaryCountry.Items.Add("United Kingdom (MHRA)");
            cboPrimaryCountry.Items.Add("Australia (TGA)");
            cboPrimaryCountry.Items.Add("China (NMPA)");
            cboPrimaryCountry.Items.Add("South Korea (MFDS)");
            cboPrimaryCountry.Items.Add("Switzerland (Swissmedic)");
            cboPrimaryCountry.Items.Add("Other");

            // Set default selections to first item
            if (cboPhase.Items.Count > 0)
                cboPhase.SelectedIndex = 0;
            if (cboTherapeuticArea.Items.Count > 0)
                cboTherapeuticArea.SelectedIndex = 0;
            if (cboPrimaryCountry.Items.Count > 0)
                cboPrimaryCountry.SelectedIndex = 0;
        }

        /// <summary>
        /// OK button - validate and save metadata
        /// </summary>
        private void btnOK_Click(object sender, EventArgs e)
        {
            if (ValidateInputs())
            {
                CollectedMetadata = new StudyMetadata
                {
                    Phase = cboPhase.SelectedItem?.ToString(),
                    TherapeuticArea = cboTherapeuticArea.SelectedItem?.ToString(),
                    PrimaryCountry = ExtractCountryCode(cboPrimaryCountry.SelectedItem?.ToString()),
                    StudyName = Globals.ThisAddIn.Application.ActiveProject?.Name,
                    MetadataSource = "user_provided"
                };

                this.DialogResult = DialogResult.OK;
                this.Close();
            }
        }

        /// <summary>
        /// Cancel button
        /// </summary>
        private void btnCancel_Click(object sender, EventArgs e)
        {
            this.DialogResult = DialogResult.Cancel;
            this.Close();
        }

        /// <summary>
        /// Validate that all required fields are selected
        /// </summary>
        private bool ValidateInputs()
        {
            if (cboPhase.SelectedIndex < 0)
            {
                MessageBox.Show("Please select a study phase.", "Validation Error",
                    MessageBoxButtons.OK, MessageBoxIcon.Warning);
                cboPhase.Focus();
                return false;
            }

            if (cboTherapeuticArea.SelectedIndex < 0)
            {
                MessageBox.Show("Please select a therapeutic area.", "Validation Error",
                    MessageBoxButtons.OK, MessageBoxIcon.Warning);
                cboTherapeuticArea.Focus();
                return false;
            }

            if (cboPrimaryCountry.SelectedIndex < 0)
            {
                MessageBox.Show("Please select a primary country.", "Validation Error",
                    MessageBoxButtons.OK, MessageBoxIcon.Warning);
                cboPrimaryCountry.Focus();
                return false;
            }

            return true;
        }

        /// <summary>
        /// Extract country code from display string "US (FDA)" -> "US"
        /// </summary>
        private string ExtractCountryCode(string displayValue)
        {
            if (string.IsNullOrWhiteSpace(displayValue))
                return "";

            // Extract code before parenthesis
            int parenIndex = displayValue.IndexOf('(');
            if (parenIndex > 0)
            {
                return displayValue.Substring(0, parenIndex).Trim();
            }

            return displayValue.Trim();
        }
    }

    /// <summary>
    /// Designer code for QuickMetadataForm
    /// </summary>
    partial class QuickMetadataForm
    {
        private System.ComponentModel.IContainer components = null;
        private Label lblTitle;
        private Label lblDescription;
        private Label lblPhase;
        private ComboBox cboPhase;
        private Label lblTherapeuticArea;
        private ComboBox cboTherapeuticArea;
        private Label lblPrimaryCountry;
        private ComboBox cboPrimaryCountry;
        private Label lblNote;
        private Button btnOK;
        private Button btnCancel;
        private Panel panelButtons;

        /// <summary>
        /// Clean up any resources being used
        /// </summary>
        protected override void Dispose(bool disposing)
        {
            if (disposing && (components != null))
            {
                components.Dispose();
            }
            base.Dispose(disposing);
        }

        /// <summary>
        /// Initialize form components
        /// </summary>
        private void InitializeComponent()
        {
            this.components = new System.ComponentModel.Container();

            // Form
            this.Text = "Study Information Required";
            this.ClientSize = new Size(480, 340);
            this.FormBorderStyle = FormBorderStyle.FixedDialog;
            this.MaximizeBox = false;
            this.MinimizeBox = false;
            this.StartPosition = FormStartPosition.CenterParent;
            this.ShowInTaskbar = false;

            // Title
            this.lblTitle = new Label();
            this.lblTitle.Text = "Study Information Needed";
            this.lblTitle.Font = new Font("Segoe UI", 12F, FontStyle.Bold);
            this.lblTitle.Location = new Point(20, 20);
            this.lblTitle.Size = new Size(440, 25);

            // Description
            this.lblDescription = new Label();
            this.lblDescription.Text = "To provide accurate benchmarks, we need the following information:";
            this.lblDescription.Location = new Point(20, 55);
            this.lblDescription.Size = new Size(440, 20);

            // Phase label
            this.lblPhase = new Label();
            this.lblPhase.Text = "Study Phase:";
            this.lblPhase.Location = new Point(20, 95);
            this.lblPhase.Size = new Size(120, 20);

            // Phase dropdown
            this.cboPhase = new ComboBox();
            this.cboPhase.DropDownStyle = ComboBoxStyle.DropDownList;
            this.cboPhase.Location = new Point(150, 92);
            this.cboPhase.Size = new Size(310, 25);

            // Therapeutic Area label
            this.lblTherapeuticArea = new Label();
            this.lblTherapeuticArea.Text = "Therapeutic Area:";
            this.lblTherapeuticArea.Location = new Point(20, 135);
            this.lblTherapeuticArea.Size = new Size(120, 20);

            // Therapeutic Area dropdown
            this.cboTherapeuticArea = new ComboBox();
            this.cboTherapeuticArea.DropDownStyle = ComboBoxStyle.DropDownList;
            this.cboTherapeuticArea.Location = new Point(150, 132);
            this.cboTherapeuticArea.Size = new Size(310, 25);

            // Primary Country label
            this.lblPrimaryCountry = new Label();
            this.lblPrimaryCountry.Text = "Primary Country:";
            this.lblPrimaryCountry.Location = new Point(20, 175);
            this.lblPrimaryCountry.Size = new Size(120, 20);

            // Primary Country dropdown
            this.cboPrimaryCountry = new ComboBox();
            this.cboPrimaryCountry.DropDownStyle = ComboBoxStyle.DropDownList;
            this.cboPrimaryCountry.Location = new Point(150, 172);
            this.cboPrimaryCountry.Size = new Size(310, 25);

            // Note
            this.lblNote = new Label();
            this.lblNote.Text = "This information will be saved for future use.";
            this.lblNote.ForeColor = SystemColors.GrayText;
            this.lblNote.Location = new Point(20, 220);
            this.lblNote.Size = new Size(440, 20);

            // Button panel
            this.panelButtons = new Panel();
            this.panelButtons.Location = new Point(0, 265);
            this.panelButtons.Size = new Size(480, 75);
            this.panelButtons.BackColor = SystemColors.Control;

            // OK button
            this.btnOK = new Button();
            this.btnOK.Text = "Continue";
            this.btnOK.Location = new Point(280, 20);
            this.btnOK.Size = new Size(90, 30);
            this.btnOK.Click += new EventHandler(this.btnOK_Click);

            // Cancel button
            this.btnCancel = new Button();
            this.btnCancel.Text = "Cancel";
            this.btnCancel.Location = new Point(380, 20);
            this.btnCancel.Size = new Size(90, 30);
            this.btnCancel.Click += new EventHandler(this.btnCancel_Click);

            // Add buttons to panel
            this.panelButtons.Controls.Add(this.btnOK);
            this.panelButtons.Controls.Add(this.btnCancel);

            // Add all controls to form
            this.Controls.Add(this.lblTitle);
            this.Controls.Add(this.lblDescription);
            this.Controls.Add(this.lblPhase);
            this.Controls.Add(this.cboPhase);
            this.Controls.Add(this.lblTherapeuticArea);
            this.Controls.Add(this.cboTherapeuticArea);
            this.Controls.Add(this.lblPrimaryCountry);
            this.Controls.Add(this.cboPrimaryCountry);
            this.Controls.Add(this.lblNote);
            this.Controls.Add(this.panelButtons);

            this.AcceptButton = this.btnOK;
            this.CancelButton = this.btnCancel;
        }
    }
}
