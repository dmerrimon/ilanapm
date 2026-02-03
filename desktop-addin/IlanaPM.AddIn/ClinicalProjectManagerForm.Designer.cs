using System.Windows.Forms;
using System.Drawing;

namespace IlanaPM.AddIn
{
    partial class ClinicalProjectManagerForm
    {
        private System.ComponentModel.IContainer components = null;

        protected override void Dispose(bool disposing)
        {
            if (disposing && (components != null))
            {
                components.Dispose();
            }
            base.Dispose(disposing);
        }

        #region Windows Form Designer generated code

        private void InitializeComponent()
        {
            // Form-level controls
            this.lblTitle = new Label();
            this.lblStepIndicator = new Label();
            this.pnlButtons = new Panel();
            this.btnBack = new Button();
            this.btnNext = new Button();
            this.btnGenerate = new Button();
            this.btnCancel = new Button();

            // Step panels (only one visible at a time)
            this.pnlStep1 = new Panel();
            this.pnlStep2 = new Panel();
            this.pnlStep3 = new Panel();
            this.pnlStep4 = new Panel();
            this.pnlStep5 = new Panel();

            // STEP 1: Study Configuration
            this.lblStep1Title = new Label();
            this.lblStudyName = new Label();
            this.txtStudyName = new TextBox();
            this.lblStudyPhase = new Label();
            this.cmbStudyPhase = new ComboBox();
            this.lblTherapeuticArea = new Label();
            this.cmbTherapeuticArea = new ComboBox();
            this.lblCountries = new Label();
            this.lstCountries = new CheckedListBox();

            // STEP 2: Site Management
            this.lblStep2Title = new Label();
            this.dgvSites = new DataGridView();
            this.btnAddSite = new Button();
            this.btnEditSite = new Button();
            this.btnRemoveSite = new Button();
            this.btnImportSites = new Button();

            // STEP 3: Template Selection
            this.lblStep3Title = new Label();
            this.chkFullStudyTimeline = new CheckBox();
            this.chkSiteStartup = new CheckBox();
            this.chkSiteImplementation = new CheckBox();
            this.chkSiteCloseout = new CheckBox();
            this.chkStudyCloseout = new CheckBox();

            // STEP 4: Configuration
            this.lblStep4Title = new Label();
            this.grpSiteStartup = new GroupBox();
            this.clbSitesForStartup = new CheckedListBox();
            this.grpSiteImplementation = new GroupBox();
            this.clbSitesForImplementation = new CheckedListBox();
            this.grpSiteCloseout = new GroupBox();
            this.clbSitesForCloseout = new CheckedListBox();
            this.grpFilters = new GroupBox();
            this.chkIncludeOptional = new CheckBox();

            // STEP 5: Preview
            this.lblStep5Title = new Label();
            this.lblTaskCount = new Label();
            this.dgvPreview = new DataGridView();
            this.lblFilterPreview = new Label();
            this.cmbFilterSite = new ComboBox();
            this.cmbFilterStage = new ComboBox();

            // Suspend layouts
            this.pnlButtons.SuspendLayout();
            this.pnlStep1.SuspendLayout();
            this.pnlStep2.SuspendLayout();
            ((System.ComponentModel.ISupportInitialize)(this.dgvSites)).BeginInit();
            this.pnlStep3.SuspendLayout();
            this.pnlStep4.SuspendLayout();
            this.grpSiteStartup.SuspendLayout();
            this.grpSiteImplementation.SuspendLayout();
            this.grpSiteCloseout.SuspendLayout();
            this.grpFilters.SuspendLayout();
            this.pnlStep5.SuspendLayout();
            ((System.ComponentModel.ISupportInitialize)(this.dgvPreview)).BeginInit();
            this.SuspendLayout();

            //
            // lblTitle
            //
            this.lblTitle.AutoSize = false;
            this.lblTitle.Font = new Font("Segoe UI", 14F, FontStyle.Bold);
            this.lblTitle.Location = new Point(20, 20);
            this.lblTitle.Size = new Size(560, 30);
            this.lblTitle.Text = "Clinical Project Manager";

            //
            // lblStepIndicator
            //
            this.lblStepIndicator.AutoSize = false;
            this.lblStepIndicator.Font = new Font("Segoe UI", 10F);
            this.lblStepIndicator.ForeColor = Color.Gray;
            this.lblStepIndicator.Location = new Point(20, 55);
            this.lblStepIndicator.Size = new Size(560, 20);
            this.lblStepIndicator.Text = "Step 1 of 5: Study Configuration";

            //
            // pnlButtons
            //
            this.pnlButtons.Controls.Add(this.btnBack);
            this.pnlButtons.Controls.Add(this.btnNext);
            this.pnlButtons.Controls.Add(this.btnGenerate);
            this.pnlButtons.Controls.Add(this.btnCancel);
            this.pnlButtons.Location = new Point(0, 510);
            this.pnlButtons.Size = new Size(600, 50);

            //
            // btnBack
            //
            this.btnBack.Location = new Point(200, 10);
            this.btnBack.Size = new Size(90, 30);
            this.btnBack.Text = "< Back";
            this.btnBack.Enabled = false;
            this.btnBack.Click += new System.EventHandler(this.btnBack_Click);

            //
            // btnNext
            //
            this.btnNext.Location = new Point(300, 10);
            this.btnNext.Size = new Size(90, 30);
            this.btnNext.Text = "Next >";
            this.btnNext.Click += new System.EventHandler(this.btnNext_Click);

            //
            // btnGenerate
            //
            this.btnGenerate.Location = new Point(300, 10);
            this.btnGenerate.Size = new Size(90, 30);
            this.btnGenerate.Text = "Generate";
            this.btnGenerate.Visible = false;
            this.btnGenerate.Click += new System.EventHandler(this.btnGenerate_Click);

            //
            // btnCancel
            //
            this.btnCancel.Location = new Point(400, 10);
            this.btnCancel.Size = new Size(90, 30);
            this.btnCancel.Text = "Cancel";
            this.btnCancel.Click += new System.EventHandler(this.btnCancel_Click);

            // Initialize all step panels
            InitializeStep1();
            InitializeStep2();
            InitializeStep3();
            InitializeStep4();
            InitializeStep5();

            //
            // ClinicalProjectManagerForm
            //
            this.ClientSize = new Size(600, 560);
            this.Controls.Add(this.lblTitle);
            this.Controls.Add(this.lblStepIndicator);
            this.Controls.Add(this.pnlStep1);
            this.Controls.Add(this.pnlStep2);
            this.Controls.Add(this.pnlStep3);
            this.Controls.Add(this.pnlStep4);
            this.Controls.Add(this.pnlStep5);
            this.Controls.Add(this.pnlButtons);
            this.FormBorderStyle = FormBorderStyle.FixedDialog;
            this.MaximizeBox = false;
            this.MinimizeBox = false;
            this.Name = "ClinicalProjectManagerForm";
            this.StartPosition = FormStartPosition.CenterScreen;
            this.Text = "Clinical Project Manager - Unified Wizard";
            this.Load += new System.EventHandler(this.ClinicalProjectManagerForm_Load);

            // Resume layouts
            this.pnlButtons.ResumeLayout(false);
            this.pnlStep1.ResumeLayout(false);
            this.pnlStep2.ResumeLayout(false);
            ((System.ComponentModel.ISupportInitialize)(this.dgvSites)).EndInit();
            this.pnlStep3.ResumeLayout(false);
            this.pnlStep4.ResumeLayout(false);
            this.grpSiteStartup.ResumeLayout(false);
            this.grpSiteImplementation.ResumeLayout(false);
            this.grpSiteCloseout.ResumeLayout(false);
            this.grpFilters.ResumeLayout(false);
            this.pnlStep5.ResumeLayout(false);
            ((System.ComponentModel.ISupportInitialize)(this.dgvPreview)).EndInit();
            this.ResumeLayout(false);
        }

        private void InitializeStep1()
        {
            // pnlStep1
            this.pnlStep1.Location = new Point(20, 85);
            this.pnlStep1.Size = new Size(560, 410);
            this.pnlStep1.Visible = true;
            this.pnlStep1.Controls.Add(this.lblStep1Title);
            this.pnlStep1.Controls.Add(this.lblStudyName);
            this.pnlStep1.Controls.Add(this.txtStudyName);
            this.pnlStep1.Controls.Add(this.lblStudyPhase);
            this.pnlStep1.Controls.Add(this.cmbStudyPhase);
            this.pnlStep1.Controls.Add(this.lblTherapeuticArea);
            this.pnlStep1.Controls.Add(this.cmbTherapeuticArea);
            this.pnlStep1.Controls.Add(this.lblCountries);
            this.pnlStep1.Controls.Add(this.lstCountries);

            // lblStep1Title
            this.lblStep1Title.Font = new Font("Segoe UI", 11F, FontStyle.Bold);
            this.lblStep1Title.Location = new Point(0, 0);
            this.lblStep1Title.Size = new Size(560, 25);
            this.lblStep1Title.Text = "Study Configuration";

            // lblStudyName
            this.lblStudyName.Location = new Point(0, 40);
            this.lblStudyName.Size = new Size(200, 20);
            this.lblStudyName.Text = "Study Name / Identifier:";

            // txtStudyName
            this.txtStudyName.Location = new Point(0, 65);
            this.txtStudyName.Size = new Size(350, 25);
            this.txtStudyName.Font = new Font("Segoe UI", 9F);

            // lblStudyPhase
            this.lblStudyPhase.Location = new Point(0, 100);
            this.lblStudyPhase.Size = new Size(150, 20);
            this.lblStudyPhase.Text = "Study Phase:";

            // cmbStudyPhase
            this.cmbStudyPhase.DropDownStyle = ComboBoxStyle.DropDownList;
            this.cmbStudyPhase.Location = new Point(0, 125);
            this.cmbStudyPhase.Size = new Size(200, 25);
            this.cmbStudyPhase.Items.AddRange(new object[] { "Phase I", "Phase II", "Phase III", "Phase IV", "Phase I/II" });

            // lblTherapeuticArea
            this.lblTherapeuticArea.Location = new Point(0, 160);
            this.lblTherapeuticArea.Size = new Size(150, 20);
            this.lblTherapeuticArea.Text = "Therapeutic Area:";

            // cmbTherapeuticArea
            this.cmbTherapeuticArea.DropDownStyle = ComboBoxStyle.DropDownList;
            this.cmbTherapeuticArea.Location = new Point(0, 185);
            this.cmbTherapeuticArea.Size = new Size(250, 25);
            this.cmbTherapeuticArea.Items.AddRange(new object[] {
                "Oncology",
                "Infectious Disease",
                "Cardiology",
                "Neurology",
                "Immunology",
                "Rare Disease",
                "Other"
            });

            // lblCountries
            this.lblCountries.Location = new Point(0, 220);
            this.lblCountries.Size = new Size(350, 20);
            this.lblCountries.Text = "Countries (select all that apply):";

            // lstCountries
            this.lstCountries.CheckOnClick = true;
            this.lstCountries.Location = new Point(0, 245);
            this.lstCountries.Size = new Size(350, 150);
            this.lstCountries.Items.AddRange(new object[] {
                "USA", "Canada", "United Kingdom", "Germany", "France",
                "Spain", "Italy", "Netherlands", "Belgium", "Switzerland",
                "Japan", "Australia", "China", "India", "Brazil"
            });
        }

        private void InitializeStep2()
        {
            // pnlStep2
            this.pnlStep2.Location = new Point(20, 85);
            this.pnlStep2.Size = new Size(560, 410);
            this.pnlStep2.Visible = false;
            this.pnlStep2.Controls.Add(this.lblStep2Title);
            this.pnlStep2.Controls.Add(this.dgvSites);
            this.pnlStep2.Controls.Add(this.btnAddSite);
            this.pnlStep2.Controls.Add(this.btnEditSite);
            this.pnlStep2.Controls.Add(this.btnRemoveSite);
            this.pnlStep2.Controls.Add(this.btnImportSites);

            // lblStep2Title
            this.lblStep2Title.Font = new Font("Segoe UI", 11F, FontStyle.Bold);
            this.lblStep2Title.Location = new Point(0, 0);
            this.lblStep2Title.Size = new Size(560, 25);
            this.lblStep2Title.Text = "Site Management";

            // dgvSites
            this.dgvSites.AllowUserToAddRows = false;
            this.dgvSites.AllowUserToDeleteRows = false;
            this.dgvSites.AutoSizeColumnsMode = DataGridViewAutoSizeColumnsMode.Fill;
            this.dgvSites.Location = new Point(0, 35);
            this.dgvSites.MultiSelect = false;
            this.dgvSites.SelectionMode = DataGridViewSelectionMode.FullRowSelect;
            this.dgvSites.Size = new Size(560, 320);

            // btnAddSite
            this.btnAddSite.Location = new Point(0, 365);
            this.btnAddSite.Size = new Size(100, 30);
            this.btnAddSite.Text = "Add Site";
            this.btnAddSite.Click += new System.EventHandler(this.btnAddSite_Click);

            // btnEditSite
            this.btnEditSite.Location = new Point(110, 365);
            this.btnEditSite.Size = new Size(100, 30);
            this.btnEditSite.Text = "Edit Site";
            this.btnEditSite.Click += new System.EventHandler(this.btnEditSite_Click);

            // btnRemoveSite
            this.btnRemoveSite.Location = new Point(220, 365);
            this.btnRemoveSite.Size = new Size(100, 30);
            this.btnRemoveSite.Text = "Remove Site";
            this.btnRemoveSite.Click += new System.EventHandler(this.btnRemoveSite_Click);

            // btnImportSites
            this.btnImportSites.Location = new Point(380, 365);
            this.btnImportSites.Size = new Size(180, 30);
            this.btnImportSites.Text = "Import from Clinical Setup";
            this.btnImportSites.Click += new System.EventHandler(this.btnImportSites_Click);
        }

        private void InitializeStep3()
        {
            // pnlStep3
            this.pnlStep3.Location = new Point(20, 85);
            this.pnlStep3.Size = new Size(560, 410);
            this.pnlStep3.Visible = false;
            this.pnlStep3.Controls.Add(this.lblStep3Title);
            this.pnlStep3.Controls.Add(this.chkFullStudyTimeline);
            this.pnlStep3.Controls.Add(this.chkSiteStartup);
            this.pnlStep3.Controls.Add(this.chkSiteImplementation);
            this.pnlStep3.Controls.Add(this.chkSiteCloseout);
            this.pnlStep3.Controls.Add(this.chkStudyCloseout);

            // lblStep3Title
            this.lblStep3Title.Font = new Font("Segoe UI", 11F, FontStyle.Bold);
            this.lblStep3Title.Location = new Point(0, 0);
            this.lblStep3Title.Size = new Size(560, 25);
            this.lblStep3Title.Text = "Template Selection";

            // Template checkboxes
            this.chkFullStudyTimeline.Location = new Point(20, 50);
            this.chkFullStudyTimeline.Size = new Size(500, 60);
            this.chkFullStudyTimeline.Font = new Font("Segoe UI", 10F, FontStyle.Bold);
            this.chkFullStudyTimeline.Text = "Full Study Timeline\n(Regulatory phases from API - all countries supported)";
            this.chkFullStudyTimeline.CheckedChanged += new System.EventHandler(this.TemplateCheckbox_CheckedChanged);

            this.chkSiteStartup.Location = new Point(20, 120);
            this.chkSiteStartup.Size = new Size(500, 60);
            this.chkSiteStartup.Font = new Font("Segoe UI", 10F, FontStyle.Bold);
            this.chkSiteStartup.Text = "Site Startup\n(Site activation tasks from library - 23 countries)";
            this.chkSiteStartup.CheckedChanged += new System.EventHandler(this.TemplateCheckbox_CheckedChanged);

            this.chkSiteImplementation.Location = new Point(20, 190);
            this.chkSiteImplementation.Size = new Size(500, 60);
            this.chkSiteImplementation.Font = new Font("Segoe UI", 10F, FontStyle.Bold);
            this.chkSiteImplementation.Text = "Site Implementation\n(Ongoing tasks like IRB continuing review)";
            this.chkSiteImplementation.CheckedChanged += new System.EventHandler(this.TemplateCheckbox_CheckedChanged);

            this.chkSiteCloseout.Location = new Point(20, 260);
            this.chkSiteCloseout.Size = new Size(500, 60);
            this.chkSiteCloseout.Font = new Font("Segoe UI", 10F, FontStyle.Bold);
            this.chkSiteCloseout.Text = "Site Closeout\n(Site shutdown tasks from library)";
            this.chkSiteCloseout.CheckedChanged += new System.EventHandler(this.TemplateCheckbox_CheckedChanged);

            this.chkStudyCloseout.Location = new Point(20, 330);
            this.chkStudyCloseout.Size = new Size(500, 60);
            this.chkStudyCloseout.Font = new Font("Segoe UI", 10F, FontStyle.Bold);
            this.chkStudyCloseout.Text = "Study Closeout\n(Study-level closure - no site-specific tasks)";
            this.chkStudyCloseout.CheckedChanged += new System.EventHandler(this.TemplateCheckbox_CheckedChanged);
        }

        private void InitializeStep4()
        {
            // pnlStep4
            this.pnlStep4.Location = new Point(20, 85);
            this.pnlStep4.Size = new Size(560, 410);
            this.pnlStep4.Visible = false;
            this.pnlStep4.Controls.Add(this.lblStep4Title);
            this.pnlStep4.Controls.Add(this.grpSiteStartup);
            this.pnlStep4.Controls.Add(this.grpSiteImplementation);
            this.pnlStep4.Controls.Add(this.grpSiteCloseout);
            this.pnlStep4.Controls.Add(this.grpFilters);

            // lblStep4Title
            this.lblStep4Title.Font = new Font("Segoe UI", 11F, FontStyle.Bold);
            this.lblStep4Title.Location = new Point(0, 0);
            this.lblStep4Title.Size = new Size(560, 25);
            this.lblStep4Title.Text = "Configuration & Filters";

            // grpSiteStartup
            this.grpSiteStartup.Location = new Point(0, 35);
            this.grpSiteStartup.Size = new Size(270, 150);
            this.grpSiteStartup.Text = "Sites for Startup";
            this.grpSiteStartup.Visible = false;
            this.grpSiteStartup.Controls.Add(this.clbSitesForStartup);

            this.clbSitesForStartup.CheckOnClick = true;
            this.clbSitesForStartup.Dock = DockStyle.Fill;

            // grpSiteImplementation
            this.grpSiteImplementation.Location = new Point(285, 35);
            this.grpSiteImplementation.Size = new Size(270, 150);
            this.grpSiteImplementation.Text = "Sites for Implementation";
            this.grpSiteImplementation.Visible = false;
            this.grpSiteImplementation.Controls.Add(this.clbSitesForImplementation);

            this.clbSitesForImplementation.CheckOnClick = true;
            this.clbSitesForImplementation.Dock = DockStyle.Fill;

            // grpSiteCloseout
            this.grpSiteCloseout.Location = new Point(0, 195);
            this.grpSiteCloseout.Size = new Size(270, 150);
            this.grpSiteCloseout.Text = "Sites for Closeout";
            this.grpSiteCloseout.Visible = false;
            this.grpSiteCloseout.Controls.Add(this.clbSitesForCloseout);

            this.clbSitesForCloseout.CheckOnClick = true;
            this.clbSitesForCloseout.Dock = DockStyle.Fill;

            // grpFilters
            this.grpFilters.Location = new Point(285, 195);
            this.grpFilters.Size = new Size(270, 150);
            this.grpFilters.Text = "Filter Options";
            this.grpFilters.Controls.Add(this.chkIncludeOptional);

            this.chkIncludeOptional.Location = new Point(10, 25);
            this.chkIncludeOptional.Size = new Size(250, 25);
            this.chkIncludeOptional.Text = "Include optional (non-mandatory) tasks";
            this.chkIncludeOptional.Checked = true;
        }

        private void InitializeStep5()
        {
            // pnlStep5
            this.pnlStep5.Location = new Point(20, 85);
            this.pnlStep5.Size = new Size(560, 410);
            this.pnlStep5.Visible = false;
            this.pnlStep5.Controls.Add(this.lblStep5Title);
            this.pnlStep5.Controls.Add(this.lblTaskCount);
            this.pnlStep5.Controls.Add(this.lblFilterPreview);
            this.pnlStep5.Controls.Add(this.cmbFilterSite);
            this.pnlStep5.Controls.Add(this.cmbFilterStage);
            this.pnlStep5.Controls.Add(this.dgvPreview);

            // lblStep5Title
            this.lblStep5Title.Font = new Font("Segoe UI", 11F, FontStyle.Bold);
            this.lblStep5Title.Location = new Point(0, 0);
            this.lblStep5Title.Size = new Size(560, 25);
            this.lblStep5Title.Text = "Preview & Generate";

            // lblTaskCount
            this.lblTaskCount.Font = new Font("Segoe UI", 10F, FontStyle.Bold);
            this.lblTaskCount.ForeColor = Color.DarkGreen;
            this.lblTaskCount.Location = new Point(0, 30);
            this.lblTaskCount.Size = new Size(560, 25);
            this.lblTaskCount.Text = "0 tasks will be generated";

            // lblFilterPreview
            this.lblFilterPreview.Location = new Point(0, 60);
            this.lblFilterPreview.Size = new Size(80, 20);
            this.lblFilterPreview.Text = "Filter by:";

            // cmbFilterSite
            this.cmbFilterSite.DropDownStyle = ComboBoxStyle.DropDownList;
            this.cmbFilterSite.Location = new Point(80, 57);
            this.cmbFilterSite.Size = new Size(150, 25);
            this.cmbFilterSite.SelectedIndexChanged += new System.EventHandler(this.PreviewFilter_Changed);

            // cmbFilterStage
            this.cmbFilterStage.DropDownStyle = ComboBoxStyle.DropDownList;
            this.cmbFilterStage.Location = new Point(240, 57);
            this.cmbFilterStage.Size = new Size(180, 25);
            this.cmbFilterStage.SelectedIndexChanged += new System.EventHandler(this.PreviewFilter_Changed);

            // dgvPreview
            this.dgvPreview.AllowUserToAddRows = false;
            this.dgvPreview.AllowUserToDeleteRows = false;
            this.dgvPreview.AutoSizeColumnsMode = DataGridViewAutoSizeColumnsMode.AllCells;
            this.dgvPreview.Location = new Point(0, 90);
            this.dgvPreview.MultiSelect = false;
            this.dgvPreview.ReadOnly = true;
            this.dgvPreview.SelectionMode = DataGridViewSelectionMode.FullRowSelect;
            this.dgvPreview.Size = new Size(560, 310);
        }

        #endregion

        // Form-level controls
        private Label lblTitle;
        private Label lblStepIndicator;
        private Panel pnlButtons;
        private Button btnBack;
        private Button btnNext;
        private Button btnGenerate;
        private Button btnCancel;

        // Step panels
        private Panel pnlStep1;
        private Panel pnlStep2;
        private Panel pnlStep3;
        private Panel pnlStep4;
        private Panel pnlStep5;

        // Step 1 controls
        private Label lblStep1Title;
        private Label lblStudyName;
        private TextBox txtStudyName;
        private Label lblStudyPhase;
        private ComboBox cmbStudyPhase;
        private Label lblTherapeuticArea;
        private ComboBox cmbTherapeuticArea;
        private Label lblCountries;
        private CheckedListBox lstCountries;

        // Step 2 controls
        private Label lblStep2Title;
        private DataGridView dgvSites;
        private Button btnAddSite;
        private Button btnEditSite;
        private Button btnRemoveSite;
        private Button btnImportSites;

        // Step 3 controls
        private Label lblStep3Title;
        private CheckBox chkFullStudyTimeline;
        private CheckBox chkSiteStartup;
        private CheckBox chkSiteImplementation;
        private CheckBox chkSiteCloseout;
        private CheckBox chkStudyCloseout;

        // Step 4 controls
        private Label lblStep4Title;
        private GroupBox grpSiteStartup;
        private CheckedListBox clbSitesForStartup;
        private GroupBox grpSiteImplementation;
        private CheckedListBox clbSitesForImplementation;
        private GroupBox grpSiteCloseout;
        private CheckedListBox clbSitesForCloseout;
        private GroupBox grpFilters;
        private CheckBox chkIncludeOptional;

        // Step 5 controls
        private Label lblStep5Title;
        private Label lblTaskCount;
        private Label lblFilterPreview;
        private ComboBox cmbFilterSite;
        private ComboBox cmbFilterStage;
        private DataGridView dgvPreview;
    }
}
