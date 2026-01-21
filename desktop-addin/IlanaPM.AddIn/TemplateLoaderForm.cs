using System;
using System.Collections.Generic;
using System.Linq;
using System.Windows.Forms;

namespace IlanaPM.AddIn
{
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

        private List<Models.CountrySummary> countries;

        public string SelectedCountryCode { get; private set; }
        public string SelectedPhase { get; private set; }
        public string SelectedTherapeuticArea { get; private set; }
        public bool IncludeOptional { get; private set; }

        public TemplateLoaderForm()
        {
            InitializeComponent();
            LoadCountries();
        }

        private void InitializeComponent()
        {
            this.Text = "Load Country-Specific Timeline Template";
            this.Width = 500;
            this.Height = 400;
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

            // Load Button
            btnLoad = new Button
            {
                Text = "Load Template",
                Left = 250,
                Top = 280,
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
                Top = 280,
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
                var response = await apiClient.GetCountriesAsync();
                countries = response.countries;

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
