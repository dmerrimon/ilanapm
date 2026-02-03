using System;
using System.Collections.Generic;
using System.Linq;
using System.Windows.Forms;

namespace IlanaPM.AddIn
{
    /// <summary>
    /// DEPRECATED: Use UnifiedTemplateManagerForm instead.
    /// This form is kept for backward compatibility until the next major release.
    /// The Template Manager provides a unified interface for all template types.
    /// </summary>
    [Obsolete("Use UnifiedTemplateManagerForm instead. This form will be removed in the next major release.", false)]
    public partial class TemplateLoaderForm : Form
    {
        private ComboBox cboCountry;
        private ComboBox cboPhase;
        private ComboBox cboTherapeuticArea;
        private CheckBox chkIncludeOptional;
        private Button btnLoad;
        private Button btnCancel;
        private Label lblCountry;
        private Label lblPhase;
        private Label lblArea;
        private Label lblCountryInfo;
        private GroupBox grpCustomColumns;
        private TextBox txtCustomText5;
        private TextBox txtCustomText6;
        private TextBox txtCustomText7;
        private Label lblCustomText5;
        private Label lblCustomText6;
        private Label lblCustomText7;

        private List<Models.CountrySummary> countries;

        public string SelectedCountryCode { get; private set; }
        public string SelectedPhase { get; private set; }
        public string SelectedTherapeuticArea { get; private set; }
        public bool IncludeOptional { get; private set; }
        public Dictionary<string, string> CustomColumnNames { get; private set; }

        public TemplateLoaderForm()
        {
            InitializeComponent();
            LoadCountries();
        }

        private void InitializeComponent()
        {
            this.Text = "Load Country-Specific Timeline Template";
            this.Width = 500;
            this.Height = 550; // Increased height for custom columns section
            this.StartPosition = FormStartPosition.CenterScreen;
            this.FormBorderStyle = FormBorderStyle.FixedDialog;
            this.MaximizeBox = false;
            this.MinimizeBox = false;

            // Country Label
            lblCountry = new Label
            {
                Text = "Country:",
                Left = 20,
                Top = 20,
                Width = 120
            };
            this.Controls.Add(lblCountry);

            // Country ComboBox
            cboCountry = new ComboBox
            {
                Left = 150,
                Top = 20,
                Width = 300,
                DropDownStyle = ComboBoxStyle.DropDownList
            };
            cboCountry.SelectedIndexChanged += CboCountry_SelectedIndexChanged;
            this.Controls.Add(cboCountry);

            // Country Info Label
            lblCountryInfo = new Label
            {
                Left = 150,
                Top = 45,
                Width = 300,
                Height = 40,
                ForeColor = System.Drawing.Color.DarkGray,
                Font = new System.Drawing.Font("Arial", 8)
            };
            this.Controls.Add(lblCountryInfo);

            // Phase Label
            lblPhase = new Label
            {
                Text = "Study Phase:",
                Left = 20,
                Top = 95,
                Width = 120
            };
            this.Controls.Add(lblPhase);

            // Phase ComboBox
            cboPhase = new ComboBox
            {
                Left = 150,
                Top = 95,
                Width = 300,
                DropDownStyle = ComboBoxStyle.DropDownList
            };
            cboPhase.Items.AddRange(new object[] { "Phase I", "Phase II", "Phase III", "Phase IV" });
            cboPhase.SelectedIndex = 2; // Default to Phase III
            this.Controls.Add(cboPhase);

            // Therapeutic Area Label
            lblArea = new Label
            {
                Text = "Therapeutic Area:",
                Left = 20,
                Top = 135,
                Width = 120
            };
            this.Controls.Add(lblArea);

            // Therapeutic Area ComboBox
            cboTherapeuticArea = new ComboBox
            {
                Left = 150,
                Top = 135,
                Width = 300,
                DropDownStyle = ComboBoxStyle.DropDownList
            };
            cboTherapeuticArea.Items.AddRange(new object[] {
                "Oncology",
                "Infectious Disease",
                "Cardiovascular",
                "Neurology",
                "Respiratory",
                "Metabolic",
                "Immunology",
                "Rare Disease"
            });
            cboTherapeuticArea.SelectedIndex = 1; // Default to Infectious Disease
            this.Controls.Add(cboTherapeuticArea);

            // Include Optional Tasks Checkbox
            chkIncludeOptional = new CheckBox
            {
                Text = "Include optional tasks",
                Left = 150,
                Top = 180,
                Width = 300,
                Checked = true
            };
            this.Controls.Add(chkIncludeOptional);

            // NOTE: All 92 tasks from task_ontology.yaml are now included by default
            // Removed checkbox for "Include Emmes timelines" - no longer needed

            // Custom Columns GroupBox
            grpCustomColumns = new GroupBox
            {
                Text = "Custom Columns (Optional)",
                Left = 20,
                Top = 215,
                Width = 440,
                Height = 150
            };
            this.Controls.Add(grpCustomColumns);

            // Custom Column 1: Text5
            lblCustomText5 = new Label
            {
                Text = "Text5 Column:",
                Left = 10,
                Top = 25,
                Width = 100
            };
            grpCustomColumns.Controls.Add(lblCustomText5);

            txtCustomText5 = new TextBox
            {
                Left = 120,
                Top = 23,
                Width = 300
                // PlaceholderText not available in .NET Framework 4.7.2
            };
            grpCustomColumns.Controls.Add(txtCustomText5);

            // Custom Column 2: Text6
            lblCustomText6 = new Label
            {
                Text = "Text6 Column:",
                Left = 10,
                Top = 60,
                Width = 100
            };
            grpCustomColumns.Controls.Add(lblCustomText6);

            txtCustomText6 = new TextBox
            {
                Left = 120,
                Top = 58,
                Width = 300
                // PlaceholderText not available in .NET Framework 4.7.2
            };
            grpCustomColumns.Controls.Add(txtCustomText6);

            // Custom Column 3: Text7
            lblCustomText7 = new Label
            {
                Text = "Text7 Column:",
                Left = 10,
                Top = 95,
                Width = 100
            };
            grpCustomColumns.Controls.Add(lblCustomText7);

            txtCustomText7 = new TextBox
            {
                Left = 120,
                Top = 93,
                Width = 300
                // PlaceholderText not available in .NET Framework 4.7.2
            };
            grpCustomColumns.Controls.Add(txtCustomText7);

            // Info Label
            Label lblCustomInfo = new Label
            {
                Text = "Custom column names will appear in MS Project views. Leave blank to skip.",
                Left = 10,
                Top = 123,
                Width = 420,
                Height = 20,
                ForeColor = System.Drawing.Color.Gray,
                Font = new System.Drawing.Font("Arial", 7)
            };
            grpCustomColumns.Controls.Add(lblCustomInfo);

            // Load Button
            btnLoad = new Button
            {
                Text = "Load Template",
                Left = 250,
                Top = 430, // Moved down to accommodate custom columns
                Width = 100,
                Height = 30
            };
            btnLoad.Click += BtnLoad_Click;
            this.Controls.Add(btnLoad);

            // Cancel Button
            btnCancel = new Button
            {
                Text = "Cancel",
                Left = 360,
                Top = 430, // Moved down to match Load button
                Width = 100,
                Height = 30
            };
            btnCancel.Click += BtnCancel_Click;
            this.Controls.Add(btnCancel);

            // Accept/Cancel buttons
            this.AcceptButton = btnLoad;
            this.CancelButton = btnCancel;
        }

        private async void LoadCountries()
        {
            try
            {
                var apiClient = new Services.ApiClient();
                countries = await apiClient.GetCountriesAsync();

                // Sort countries by name
                var sortedCountries = countries.OrderBy(c => c.name).ToList();

                cboCountry.DisplayMember = "name";
                cboCountry.ValueMember = "code";
                cboCountry.DataSource = sortedCountries;
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Error loading countries: {ex.Message}\n\nPlease check your internet connection and try again.",
                    "Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
        }

        private void CboCountry_SelectedIndexChanged(object sender, EventArgs e)
        {
            if (cboCountry.SelectedItem is Models.CountrySummary country)
            {
                // Show country info
                lblCountryInfo.Text = $"{country.workflow_type.Replace("_", " ")} workflow | " +
                                     $"Complexity: {country.complexity_level} | " +
                                     $"~{country.total_timeline_days ?? 0} days";
            }
        }

        private void BtnLoad_Click(object sender, EventArgs e)
        {
            // Validate selections
            if (cboCountry.SelectedItem == null)
            {
                MessageBox.Show("Please select a country.", "Validation Error",
                    MessageBoxButtons.OK, MessageBoxIcon.Warning);
                return;
            }

            if (cboPhase.SelectedItem == null)
            {
                MessageBox.Show("Please select a study phase.", "Validation Error",
                    MessageBoxButtons.OK, MessageBoxIcon.Warning);
                return;
            }

            if (cboTherapeuticArea.SelectedItem == null)
            {
                MessageBox.Show("Please select a therapeutic area.", "Validation Error",
                    MessageBoxButtons.OK, MessageBoxIcon.Warning);
                return;
            }

            // Set selected values
            var country = (Models.CountrySummary)cboCountry.SelectedItem;
            SelectedCountryCode = country.code;
            SelectedPhase = cboPhase.SelectedItem.ToString();
            SelectedTherapeuticArea = cboTherapeuticArea.SelectedItem.ToString();
            IncludeOptional = chkIncludeOptional.Checked;

            // Capture custom column names
            CustomColumnNames = new Dictionary<string, string>();
            if (!string.IsNullOrWhiteSpace(txtCustomText5.Text))
                CustomColumnNames["Text5"] = txtCustomText5.Text.Trim();
            if (!string.IsNullOrWhiteSpace(txtCustomText6.Text))
                CustomColumnNames["Text6"] = txtCustomText6.Text.Trim();
            if (!string.IsNullOrWhiteSpace(txtCustomText7.Text))
                CustomColumnNames["Text7"] = txtCustomText7.Text.Trim();

            this.DialogResult = DialogResult.OK;
            this.Close();
        }

        private void BtnCancel_Click(object sender, EventArgs e)
        {
            this.DialogResult = DialogResult.Cancel;
            this.Close();
        }
    }
}
