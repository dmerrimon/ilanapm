namespace IlanaPM.AddIn
{
    partial class UnifiedTemplateManagerForm
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
            this.lblTitle = new System.Windows.Forms.Label();
            this.lblStepIndicator = new System.Windows.Forms.Label();
            this.panelStepHeaders = new System.Windows.Forms.Panel();
            this.lblStep3Title = new System.Windows.Forms.Label();
            this.lblStep2Title = new System.Windows.Forms.Label();
            this.lblStep1Title = new System.Windows.Forms.Label();
            this.panelStep1 = new System.Windows.Forms.Panel();
            this.rbAmendmentWorkflow = new System.Windows.Forms.RadioButton();
            this.rbStudyCloseout = new System.Windows.Forms.RadioButton();
            this.rbSiteCloseout = new System.Windows.Forms.RadioButton();
            this.rbSiteImplementation = new System.Windows.Forms.RadioButton();
            this.rbSiteStartup = new System.Windows.Forms.RadioButton();
            this.rbFullStudyTimeline = new System.Windows.Forms.RadioButton();
            this.lblStep1Instructions = new System.Windows.Forms.Label();
            this.panelStep2 = new System.Windows.Forms.Panel();
            this.panelFullStudyConfig = new System.Windows.Forms.Panel();
            this.cmbTherapeuticArea = new System.Windows.Forms.ComboBox();
            this.lblTherapeuticArea = new System.Windows.Forms.Label();
            this.cmbStudyPhase = new System.Windows.Forms.ComboBox();
            this.lblStudyPhase = new System.Windows.Forms.Label();
            this.cmbFullStudyCountry = new System.Windows.Forms.ComboBox();
            this.lblFullStudyCountry = new System.Windows.Forms.Label();
            this.panelSiteStartupConfig = new System.Windows.Forms.Panel();
            this.cmbSiteStartupCountry = new System.Windows.Forms.ComboBox();
            this.lblSiteStartupCountry = new System.Windows.Forms.Label();
            this.cmbSiteStartupSiteId = new System.Windows.Forms.ComboBox();
            this.lblSiteStartupSiteId = new System.Windows.Forms.Label();
            this.panelSiteCloseoutConfig = new System.Windows.Forms.Panel();
            this.cmbSiteCloseoutCountry = new System.Windows.Forms.ComboBox();
            this.lblSiteCloseoutCountry = new System.Windows.Forms.Label();
            this.cmbSiteCloseoutSiteId = new System.Windows.Forms.ComboBox();
            this.lblSiteCloseoutSiteId = new System.Windows.Forms.Label();
            this.panelStudyCloseoutConfig = new System.Windows.Forms.Panel();
            this.lblStudyCloseoutInfo = new System.Windows.Forms.Label();
            this.lblStep2Instructions = new System.Windows.Forms.Label();
            this.panelStep3 = new System.Windows.Forms.Panel();
            this.dgvTaskPreview = new System.Windows.Forms.DataGridView();
            this.colTaskName = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.colDuration = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.colCategory = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.colMandatory = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.panelFilters = new System.Windows.Forms.Panel();
            this.chkIncludeOptional = new System.Windows.Forms.CheckBox();
            this.clbCategories = new System.Windows.Forms.CheckedListBox();
            this.lblFilterCategories = new System.Windows.Forms.Label();
            this.panelPreviewInfo = new System.Windows.Forms.Panel();
            this.lblPreviewSource = new System.Windows.Forms.Label();
            this.lblPreviewSourceLabel = new System.Windows.Forms.Label();
            this.lblPreviewDuration = new System.Windows.Forms.Label();
            this.lblPreviewDurationLabel = new System.Windows.Forms.Label();
            this.lblPreviewTaskCount = new System.Windows.Forms.Label();
            this.lblPreviewTaskCountLabel = new System.Windows.Forms.Label();
            this.lblPreviewStatus = new System.Windows.Forms.Label();
            this.lblStep3Instructions = new System.Windows.Forms.Label();
            this.panelButtons = new System.Windows.Forms.Panel();
            this.btnCancel = new System.Windows.Forms.Button();
            this.btnGenerate = new System.Windows.Forms.Button();
            this.btnNext = new System.Windows.Forms.Button();
            this.btnBack = new System.Windows.Forms.Button();
            this.panelStepHeaders.SuspendLayout();
            this.panelStep1.SuspendLayout();
            this.panelStep2.SuspendLayout();
            this.panelFullStudyConfig.SuspendLayout();
            this.panelSiteStartupConfig.SuspendLayout();
            this.panelSiteCloseoutConfig.SuspendLayout();
            this.panelStudyCloseoutConfig.SuspendLayout();
            this.panelStep3.SuspendLayout();
            ((System.ComponentModel.ISupportInitialize)(this.dgvTaskPreview)).BeginInit();
            this.panelFilters.SuspendLayout();
            this.panelPreviewInfo.SuspendLayout();
            this.panelButtons.SuspendLayout();
            this.SuspendLayout();
            //
            // lblTitle
            //
            this.lblTitle.AutoSize = true;
            this.lblTitle.Font = new System.Drawing.Font("Microsoft Sans Serif", 14F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.lblTitle.Location = new System.Drawing.Point(12, 12);
            this.lblTitle.Name = "lblTitle";
            this.lblTitle.Size = new System.Drawing.Size(285, 24);
            this.lblTitle.TabIndex = 0;
            this.lblTitle.Text = "Unified Template Manager";
            //
            // lblStepIndicator
            //
            this.lblStepIndicator.AutoSize = true;
            this.lblStepIndicator.Location = new System.Drawing.Point(12, 45);
            this.lblStepIndicator.Name = "lblStepIndicator";
            this.lblStepIndicator.Size = new System.Drawing.Size(62, 13);
            this.lblStepIndicator.TabIndex = 1;
            this.lblStepIndicator.Text = "Step 1 of 3";
            //
            // panelStepHeaders
            //
            this.panelStepHeaders.BackColor = System.Drawing.SystemColors.ControlLight;
            this.panelStepHeaders.Controls.Add(this.lblStep3Title);
            this.panelStepHeaders.Controls.Add(this.lblStep2Title);
            this.panelStepHeaders.Controls.Add(this.lblStep1Title);
            this.panelStepHeaders.Location = new System.Drawing.Point(12, 70);
            this.panelStepHeaders.Name = "panelStepHeaders";
            this.panelStepHeaders.Size = new System.Drawing.Size(760, 40);
            this.panelStepHeaders.TabIndex = 2;
            //
            // lblStep3Title
            //
            this.lblStep3Title.AutoSize = true;
            this.lblStep3Title.Location = new System.Drawing.Point(520, 13);
            this.lblStep3Title.Name = "lblStep3Title";
            this.lblStep3Title.Size = new System.Drawing.Size(119, 13);
            this.lblStep3Title.TabIndex = 2;
            this.lblStep3Title.Text = "3. Preview and Filter";
            //
            // lblStep2Title
            //
            this.lblStep2Title.AutoSize = true;
            this.lblStep2Title.Location = new System.Drawing.Point(260, 13);
            this.lblStep2Title.Name = "lblStep2Title";
            this.lblStep2Title.Size = new System.Drawing.Size(77, 13);
            this.lblStep2Title.TabIndex = 1;
            this.lblStep2Title.Text = "2. Configure";
            //
            // lblStep1Title
            //
            this.lblStep1Title.AutoSize = true;
            this.lblStep1Title.Font = new System.Drawing.Font("Microsoft Sans Serif", 8.25F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.lblStep1Title.Location = new System.Drawing.Point(10, 13);
            this.lblStep1Title.Name = "lblStep1Title";
            this.lblStep1Title.Size = new System.Drawing.Size(141, 13);
            this.lblStep1Title.TabIndex = 0;
            this.lblStep1Title.Text = "1. Select Template Type";
            //
            // panelStep1
            //
            this.panelStep1.Controls.Add(this.rbAmendmentWorkflow);
            this.panelStep1.Controls.Add(this.rbStudyCloseout);
            this.panelStep1.Controls.Add(this.rbSiteCloseout);
            this.panelStep1.Controls.Add(this.rbSiteImplementation);
            this.panelStep1.Controls.Add(this.rbSiteStartup);
            this.panelStep1.Controls.Add(this.rbFullStudyTimeline);
            this.panelStep1.Controls.Add(this.lblStep1Instructions);
            this.panelStep1.Location = new System.Drawing.Point(12, 120);
            this.panelStep1.Name = "panelStep1";
            this.panelStep1.Size = new System.Drawing.Size(760, 350);
            this.panelStep1.TabIndex = 3;
            //
            // rbAmendmentWorkflow
            //
            this.rbAmendmentWorkflow.AutoSize = true;
            this.rbAmendmentWorkflow.Enabled = false;
            this.rbAmendmentWorkflow.Location = new System.Drawing.Point(30, 250);
            this.rbAmendmentWorkflow.Name = "rbAmendmentWorkflow";
            this.rbAmendmentWorkflow.Size = new System.Drawing.Size(311, 17);
            this.rbAmendmentWorkflow.TabIndex = 5;
            this.rbAmendmentWorkflow.Text = "Amendment Workflow (Phase 2 - Coming Soon)";
            this.rbAmendmentWorkflow.UseVisualStyleBackColor = true;
            //
            // rbStudyCloseout
            //
            this.rbStudyCloseout.AutoSize = true;
            this.rbStudyCloseout.Location = new System.Drawing.Point(30, 210);
            this.rbStudyCloseout.Name = "rbStudyCloseout";
            this.rbStudyCloseout.Size = new System.Drawing.Size(280, 17);
            this.rbStudyCloseout.TabIndex = 4;
            this.rbStudyCloseout.Text = "Study Closeout (Study-level closure tasks)";
            this.rbStudyCloseout.UseVisualStyleBackColor = true;
            //
            // rbSiteCloseout
            //
            this.rbSiteCloseout.AutoSize = true;
            this.rbSiteCloseout.Location = new System.Drawing.Point(30, 170);
            this.rbSiteCloseout.Name = "rbSiteCloseout";
            this.rbSiteCloseout.Size = new System.Drawing.Size(290, 17);
            this.rbSiteCloseout.TabIndex = 3;
            this.rbSiteCloseout.Text = "Site Closeout (Site shutdown tasks - 23 countries)";
            this.rbSiteCloseout.UseVisualStyleBackColor = true;
            //
            // rbSiteStartup
            //
            this.rbSiteStartup.AutoSize = true;
            this.rbSiteStartup.Location = new System.Drawing.Point(30, 110);
            this.rbSiteStartup.Name = "rbSiteStartup";
            this.rbSiteStartup.Size = new System.Drawing.Size(302, 17);
            this.rbSiteStartup.TabIndex = 2;
            this.rbSiteStartup.Text = "Site Startup (Site activation tasks - 23 countries)";
            this.rbSiteStartup.UseVisualStyleBackColor = true;
            //
            // rbSiteImplementation
            //
            this.rbSiteImplementation.AutoSize = true;
            this.rbSiteImplementation.Location = new System.Drawing.Point(30, 130);
            this.rbSiteImplementation.Name = "rbSiteImplementation";
            this.rbSiteImplementation.Size = new System.Drawing.Size(320, 17);
            this.rbSiteImplementation.TabIndex = 2;
            this.rbSiteImplementation.Text = "Site Implementation (IRB continuing review, ongoing tasks)";
            this.rbSiteImplementation.UseVisualStyleBackColor = true;
            //
            // rbFullStudyTimeline
            //
            this.rbFullStudyTimeline.AutoSize = true;
            this.rbFullStudyTimeline.Checked = true;
            this.rbFullStudyTimeline.Location = new System.Drawing.Point(30, 70);
            this.rbFullStudyTimeline.Name = "rbFullStudyTimeline";
            this.rbFullStudyTimeline.Size = new System.Drawing.Size(363, 17);
            this.rbFullStudyTimeline.TabIndex = 1;
            this.rbFullStudyTimeline.TabStop = true;
            this.rbFullStudyTimeline.Text = "Full Study Timeline (API-based, complete regulatory timeline)";
            this.rbFullStudyTimeline.UseVisualStyleBackColor = true;
            //
            // lblStep1Instructions
            //
            this.lblStep1Instructions.AutoSize = true;
            this.lblStep1Instructions.Location = new System.Drawing.Point(15, 15);
            this.lblStep1Instructions.Name = "lblStep1Instructions";
            this.lblStep1Instructions.Size = new System.Drawing.Size(314, 13);
            this.lblStep1Instructions.TabIndex = 0;
            this.lblStep1Instructions.Text = "Select the type of template you want to generate:";
            //
            // panelStep2
            //
            this.panelStep2.Controls.Add(this.panelFullStudyConfig);
            this.panelStep2.Controls.Add(this.panelSiteStartupConfig);
            this.panelStep2.Controls.Add(this.panelSiteCloseoutConfig);
            this.panelStep2.Controls.Add(this.panelStudyCloseoutConfig);
            this.panelStep2.Controls.Add(this.lblStep2Instructions);
            this.panelStep2.Location = new System.Drawing.Point(12, 120);
            this.panelStep2.Name = "panelStep2";
            this.panelStep2.Size = new System.Drawing.Size(760, 350);
            this.panelStep2.TabIndex = 4;
            this.panelStep2.Visible = false;
            //
            // panelFullStudyConfig
            //
            this.panelFullStudyConfig.Controls.Add(this.cmbTherapeuticArea);
            this.panelFullStudyConfig.Controls.Add(this.lblTherapeuticArea);
            this.panelFullStudyConfig.Controls.Add(this.cmbStudyPhase);
            this.panelFullStudyConfig.Controls.Add(this.lblStudyPhase);
            this.panelFullStudyConfig.Controls.Add(this.cmbFullStudyCountry);
            this.panelFullStudyConfig.Controls.Add(this.lblFullStudyCountry);
            this.panelFullStudyConfig.Location = new System.Drawing.Point(15, 50);
            this.panelFullStudyConfig.Name = "panelFullStudyConfig";
            this.panelFullStudyConfig.Size = new System.Drawing.Size(730, 280);
            this.panelFullStudyConfig.TabIndex = 4;
            this.panelFullStudyConfig.Visible = false;
            //
            // cmbTherapeuticArea
            //
            this.cmbTherapeuticArea.DropDownStyle = System.Windows.Forms.ComboBoxStyle.DropDownList;
            this.cmbTherapeuticArea.FormattingEnabled = true;
            this.cmbTherapeuticArea.Location = new System.Drawing.Point(150, 110);
            this.cmbTherapeuticArea.Name = "cmbTherapeuticArea";
            this.cmbTherapeuticArea.Size = new System.Drawing.Size(250, 21);
            this.cmbTherapeuticArea.TabIndex = 5;
            //
            // lblTherapeuticArea
            //
            this.lblTherapeuticArea.AutoSize = true;
            this.lblTherapeuticArea.Location = new System.Drawing.Point(15, 113);
            this.lblTherapeuticArea.Name = "lblTherapeuticArea";
            this.lblTherapeuticArea.Size = new System.Drawing.Size(99, 13);
            this.lblTherapeuticArea.TabIndex = 4;
            this.lblTherapeuticArea.Text = "Therapeutic Area:";
            //
            // cmbStudyPhase
            //
            this.cmbStudyPhase.DropDownStyle = System.Windows.Forms.ComboBoxStyle.DropDownList;
            this.cmbStudyPhase.FormattingEnabled = true;
            this.cmbStudyPhase.Location = new System.Drawing.Point(150, 70);
            this.cmbStudyPhase.Name = "cmbStudyPhase";
            this.cmbStudyPhase.Size = new System.Drawing.Size(250, 21);
            this.cmbStudyPhase.TabIndex = 3;
            //
            // lblStudyPhase
            //
            this.lblStudyPhase.AutoSize = true;
            this.lblStudyPhase.Location = new System.Drawing.Point(15, 73);
            this.lblStudyPhase.Name = "lblStudyPhase";
            this.lblStudyPhase.Size = new System.Drawing.Size(76, 13);
            this.lblStudyPhase.TabIndex = 2;
            this.lblStudyPhase.Text = "Study Phase:";
            //
            // cmbFullStudyCountry
            //
            this.cmbFullStudyCountry.DropDownStyle = System.Windows.Forms.ComboBoxStyle.DropDownList;
            this.cmbFullStudyCountry.FormattingEnabled = true;
            this.cmbFullStudyCountry.Location = new System.Drawing.Point(150, 30);
            this.cmbFullStudyCountry.Name = "cmbFullStudyCountry";
            this.cmbFullStudyCountry.Size = new System.Drawing.Size(250, 21);
            this.cmbFullStudyCountry.TabIndex = 1;
            //
            // lblFullStudyCountry
            //
            this.lblFullStudyCountry.AutoSize = true;
            this.lblFullStudyCountry.Location = new System.Drawing.Point(15, 33);
            this.lblFullStudyCountry.Name = "lblFullStudyCountry";
            this.lblFullStudyCountry.Size = new System.Drawing.Size(52, 13);
            this.lblFullStudyCountry.TabIndex = 0;
            this.lblFullStudyCountry.Text = "Country:";
            //
            // panelSiteStartupConfig
            //
            this.panelSiteStartupConfig.Controls.Add(this.cmbSiteStartupCountry);
            this.panelSiteStartupConfig.Controls.Add(this.lblSiteStartupCountry);
            this.panelSiteStartupConfig.Controls.Add(this.cmbSiteStartupSiteId);
            this.panelSiteStartupConfig.Controls.Add(this.lblSiteStartupSiteId);
            this.panelSiteStartupConfig.Location = new System.Drawing.Point(15, 50);
            this.panelSiteStartupConfig.Name = "panelSiteStartupConfig";
            this.panelSiteStartupConfig.Size = new System.Drawing.Size(730, 280);
            this.panelSiteStartupConfig.TabIndex = 3;
            this.panelSiteStartupConfig.Visible = false;
            //
            // cmbSiteStartupCountry
            //
            this.cmbSiteStartupCountry.DropDownStyle = System.Windows.Forms.ComboBoxStyle.DropDownList;
            this.cmbSiteStartupCountry.FormattingEnabled = true;
            this.cmbSiteStartupCountry.Location = new System.Drawing.Point(150, 70);
            this.cmbSiteStartupCountry.Name = "cmbSiteStartupCountry";
            this.cmbSiteStartupCountry.Size = new System.Drawing.Size(250, 21);
            this.cmbSiteStartupCountry.TabIndex = 3;
            //
            // lblSiteStartupCountry
            //
            this.lblSiteStartupCountry.AutoSize = true;
            this.lblSiteStartupCountry.Location = new System.Drawing.Point(15, 73);
            this.lblSiteStartupCountry.Name = "lblSiteStartupCountry";
            this.lblSiteStartupCountry.Size = new System.Drawing.Size(52, 13);
            this.lblSiteStartupCountry.TabIndex = 2;
            this.lblSiteStartupCountry.Text = "Country:";
            //
            // cmbSiteStartupSiteId
            //
            this.cmbSiteStartupSiteId.DropDownStyle = System.Windows.Forms.ComboBoxStyle.DropDown;
            this.cmbSiteStartupSiteId.FormattingEnabled = true;
            this.cmbSiteStartupSiteId.Location = new System.Drawing.Point(150, 30);
            this.cmbSiteStartupSiteId.Name = "cmbSiteStartupSiteId";
            this.cmbSiteStartupSiteId.Size = new System.Drawing.Size(250, 21);
            this.cmbSiteStartupSiteId.TabIndex = 1;
            this.cmbSiteStartupSiteId.Text = "SITE-001";
            this.cmbSiteStartupSiteId.SelectedIndexChanged += new System.EventHandler(this.cmbSiteStartupSiteId_SelectedIndexChanged);
            //
            // lblSiteStartupSiteId
            //
            this.lblSiteStartupSiteId.AutoSize = true;
            this.lblSiteStartupSiteId.Location = new System.Drawing.Point(15, 33);
            this.lblSiteStartupSiteId.Name = "lblSiteStartupSiteId";
            this.lblSiteStartupSiteId.Size = new System.Drawing.Size(47, 13);
            this.lblSiteStartupSiteId.TabIndex = 0;
            this.lblSiteStartupSiteId.Text = "Site ID:";
            //
            // panelSiteCloseoutConfig
            //
            this.panelSiteCloseoutConfig.Controls.Add(this.cmbSiteCloseoutCountry);
            this.panelSiteCloseoutConfig.Controls.Add(this.lblSiteCloseoutCountry);
            this.panelSiteCloseoutConfig.Controls.Add(this.cmbSiteCloseoutSiteId);
            this.panelSiteCloseoutConfig.Controls.Add(this.lblSiteCloseoutSiteId);
            this.panelSiteCloseoutConfig.Location = new System.Drawing.Point(15, 50);
            this.panelSiteCloseoutConfig.Name = "panelSiteCloseoutConfig";
            this.panelSiteCloseoutConfig.Size = new System.Drawing.Size(730, 280);
            this.panelSiteCloseoutConfig.TabIndex = 2;
            this.panelSiteCloseoutConfig.Visible = false;
            //
            // cmbSiteCloseoutCountry
            //
            this.cmbSiteCloseoutCountry.DropDownStyle = System.Windows.Forms.ComboBoxStyle.DropDownList;
            this.cmbSiteCloseoutCountry.FormattingEnabled = true;
            this.cmbSiteCloseoutCountry.Location = new System.Drawing.Point(150, 70);
            this.cmbSiteCloseoutCountry.Name = "cmbSiteCloseoutCountry";
            this.cmbSiteCloseoutCountry.Size = new System.Drawing.Size(250, 21);
            this.cmbSiteCloseoutCountry.TabIndex = 3;
            //
            // lblSiteCloseoutCountry
            //
            this.lblSiteCloseoutCountry.AutoSize = true;
            this.lblSiteCloseoutCountry.Location = new System.Drawing.Point(15, 73);
            this.lblSiteCloseoutCountry.Name = "lblSiteCloseoutCountry";
            this.lblSiteCloseoutCountry.Size = new System.Drawing.Size(52, 13);
            this.lblSiteCloseoutCountry.TabIndex = 2;
            this.lblSiteCloseoutCountry.Text = "Country:";
            //
            // cmbSiteCloseoutSiteId
            //
            this.cmbSiteCloseoutSiteId.DropDownStyle = System.Windows.Forms.ComboBoxStyle.DropDown;
            this.cmbSiteCloseoutSiteId.FormattingEnabled = true;
            this.cmbSiteCloseoutSiteId.Location = new System.Drawing.Point(150, 30);
            this.cmbSiteCloseoutSiteId.Name = "cmbSiteCloseoutSiteId";
            this.cmbSiteCloseoutSiteId.Size = new System.Drawing.Size(250, 21);
            this.cmbSiteCloseoutSiteId.TabIndex = 1;
            this.cmbSiteCloseoutSiteId.Text = "SITE-001";
            this.cmbSiteCloseoutSiteId.SelectedIndexChanged += new System.EventHandler(this.cmbSiteCloseoutSiteId_SelectedIndexChanged);
            //
            // lblSiteCloseoutSiteId
            //
            this.lblSiteCloseoutSiteId.AutoSize = true;
            this.lblSiteCloseoutSiteId.Location = new System.Drawing.Point(15, 33);
            this.lblSiteCloseoutSiteId.Name = "lblSiteCloseoutSiteId";
            this.lblSiteCloseoutSiteId.Size = new System.Drawing.Size(47, 13);
            this.lblSiteCloseoutSiteId.TabIndex = 0;
            this.lblSiteCloseoutSiteId.Text = "Site ID:";
            //
            // panelStudyCloseoutConfig
            //
            this.panelStudyCloseoutConfig.Controls.Add(this.lblStudyCloseoutInfo);
            this.panelStudyCloseoutConfig.Location = new System.Drawing.Point(15, 50);
            this.panelStudyCloseoutConfig.Name = "panelStudyCloseoutConfig";
            this.panelStudyCloseoutConfig.Size = new System.Drawing.Size(730, 280);
            this.panelStudyCloseoutConfig.TabIndex = 1;
            this.panelStudyCloseoutConfig.Visible = false;
            //
            // lblStudyCloseoutInfo
            //
            this.lblStudyCloseoutInfo.AutoSize = true;
            this.lblStudyCloseoutInfo.Location = new System.Drawing.Point(15, 30);
            this.lblStudyCloseoutInfo.Name = "lblStudyCloseoutInfo";
            this.lblStudyCloseoutInfo.Size = new System.Drawing.Size(445, 52);
            this.lblStudyCloseoutInfo.TabIndex = 0;
            this.lblStudyCloseoutInfo.Text = "Study Closeout templates include study-level closure tasks:\r\n\r\n- Database lock and finalization\r\n- Study archival\r\n- Regulatory authority notifications";
            //
            // lblStep2Instructions
            //
            this.lblStep2Instructions.AutoSize = true;
            this.lblStep2Instructions.Location = new System.Drawing.Point(15, 15);
            this.lblStep2Instructions.Name = "lblStep2Instructions";
            this.lblStep2Instructions.Size = new System.Drawing.Size(206, 13);
            this.lblStep2Instructions.TabIndex = 0;
            this.lblStep2Instructions.Text = "Configure your template settings:";
            //
            // panelStep3
            //
            this.panelStep3.Controls.Add(this.dgvTaskPreview);
            this.panelStep3.Controls.Add(this.panelFilters);
            this.panelStep3.Controls.Add(this.panelPreviewInfo);
            this.panelStep3.Controls.Add(this.lblPreviewStatus);
            this.panelStep3.Controls.Add(this.lblStep3Instructions);
            this.panelStep3.Location = new System.Drawing.Point(12, 120);
            this.panelStep3.Name = "panelStep3";
            this.panelStep3.Size = new System.Drawing.Size(760, 350);
            this.panelStep3.TabIndex = 5;
            this.panelStep3.Visible = false;
            //
            // dgvTaskPreview
            //
            this.dgvTaskPreview.AllowUserToAddRows = false;
            this.dgvTaskPreview.AllowUserToDeleteRows = false;
            this.dgvTaskPreview.ColumnHeadersHeightSizeMode = System.Windows.Forms.DataGridViewColumnHeadersHeightSizeMode.AutoSize;
            this.dgvTaskPreview.Columns.AddRange(new System.Windows.Forms.DataGridViewColumn[] {
            this.colTaskName,
            this.colDuration,
            this.colCategory,
            this.colMandatory});
            this.dgvTaskPreview.Location = new System.Drawing.Point(15, 115);
            this.dgvTaskPreview.Name = "dgvTaskPreview";
            this.dgvTaskPreview.ReadOnly = true;
            this.dgvTaskPreview.Size = new System.Drawing.Size(540, 220);
            this.dgvTaskPreview.TabIndex = 4;
            //
            // colTaskName
            //
            this.colTaskName.HeaderText = "Task Name";
            this.colTaskName.Name = "colTaskName";
            this.colTaskName.ReadOnly = true;
            this.colTaskName.Width = 250;
            //
            // colDuration
            //
            this.colDuration.HeaderText = "Duration";
            this.colDuration.Name = "colDuration";
            this.colDuration.ReadOnly = true;
            this.colDuration.Width = 80;
            //
            // colCategory
            //
            this.colCategory.HeaderText = "Category";
            this.colCategory.Name = "colCategory";
            this.colCategory.ReadOnly = true;
            //
            // colMandatory
            //
            this.colMandatory.HeaderText = "Mandatory";
            this.colMandatory.Name = "colMandatory";
            this.colMandatory.ReadOnly = true;
            this.colMandatory.Width = 80;
            //
            // panelFilters
            //
            this.panelFilters.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.panelFilters.Controls.Add(this.chkIncludeOptional);
            this.panelFilters.Controls.Add(this.clbCategories);
            this.panelFilters.Controls.Add(this.lblFilterCategories);
            this.panelFilters.Location = new System.Drawing.Point(570, 115);
            this.panelFilters.Name = "panelFilters";
            this.panelFilters.Size = new System.Drawing.Size(175, 220);
            this.panelFilters.TabIndex = 3;
            //
            // chkIncludeOptional
            //
            this.chkIncludeOptional.AutoSize = true;
            this.chkIncludeOptional.Checked = true;
            this.chkIncludeOptional.CheckState = System.Windows.Forms.CheckState.Checked;
            this.chkIncludeOptional.Location = new System.Drawing.Point(10, 190);
            this.chkIncludeOptional.Name = "chkIncludeOptional";
            this.chkIncludeOptional.Size = new System.Drawing.Size(131, 17);
            this.chkIncludeOptional.TabIndex = 2;
            this.chkIncludeOptional.Text = "Include optional tasks";
            this.chkIncludeOptional.UseVisualStyleBackColor = true;
            this.chkIncludeOptional.CheckedChanged += new System.EventHandler(this.chkIncludeOptional_CheckedChanged);
            //
            // clbCategories
            //
            this.clbCategories.CheckOnClick = true;
            this.clbCategories.FormattingEnabled = true;
            this.clbCategories.Location = new System.Drawing.Point(10, 30);
            this.clbCategories.Name = "clbCategories";
            this.clbCategories.Size = new System.Drawing.Size(150, 154);
            this.clbCategories.TabIndex = 1;
            this.clbCategories.ItemCheck += new System.Windows.Forms.ItemCheckEventHandler(this.clbCategories_ItemCheck);
            //
            // lblFilterCategories
            //
            this.lblFilterCategories.AutoSize = true;
            this.lblFilterCategories.Font = new System.Drawing.Font("Microsoft Sans Serif", 8.25F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.lblFilterCategories.Location = new System.Drawing.Point(7, 10);
            this.lblFilterCategories.Name = "lblFilterCategories";
            this.lblFilterCategories.Size = new System.Drawing.Size(59, 13);
            this.lblFilterCategories.TabIndex = 0;
            this.lblFilterCategories.Text = "Filters:";
            //
            // panelPreviewInfo
            //
            this.panelPreviewInfo.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.panelPreviewInfo.Controls.Add(this.lblPreviewSource);
            this.panelPreviewInfo.Controls.Add(this.lblPreviewSourceLabel);
            this.panelPreviewInfo.Controls.Add(this.lblPreviewDuration);
            this.panelPreviewInfo.Controls.Add(this.lblPreviewDurationLabel);
            this.panelPreviewInfo.Controls.Add(this.lblPreviewTaskCount);
            this.panelPreviewInfo.Controls.Add(this.lblPreviewTaskCountLabel);
            this.panelPreviewInfo.Location = new System.Drawing.Point(15, 50);
            this.panelPreviewInfo.Name = "panelPreviewInfo";
            this.panelPreviewInfo.Size = new System.Drawing.Size(540, 50);
            this.panelPreviewInfo.TabIndex = 2;
            //
            // lblPreviewSource
            //
            this.lblPreviewSource.AutoSize = true;
            this.lblPreviewSource.Location = new System.Drawing.Point(430, 15);
            this.lblPreviewSource.Name = "lblPreviewSource";
            this.lblPreviewSource.Size = new System.Drawing.Size(10, 13);
            this.lblPreviewSource.TabIndex = 5;
            this.lblPreviewSource.Text = "-";
            //
            // lblPreviewSourceLabel
            //
            this.lblPreviewSourceLabel.AutoSize = true;
            this.lblPreviewSourceLabel.Font = new System.Drawing.Font("Microsoft Sans Serif", 8.25F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.lblPreviewSourceLabel.Location = new System.Drawing.Point(370, 15);
            this.lblPreviewSourceLabel.Name = "lblPreviewSourceLabel";
            this.lblPreviewSourceLabel.Size = new System.Drawing.Size(52, 13);
            this.lblPreviewSourceLabel.TabIndex = 4;
            this.lblPreviewSourceLabel.Text = "Source:";
            //
            // lblPreviewDuration
            //
            this.lblPreviewDuration.AutoSize = true;
            this.lblPreviewDuration.Location = new System.Drawing.Point(245, 15);
            this.lblPreviewDuration.Name = "lblPreviewDuration";
            this.lblPreviewDuration.Size = new System.Drawing.Size(10, 13);
            this.lblPreviewDuration.TabIndex = 3;
            this.lblPreviewDuration.Text = "-";
            //
            // lblPreviewDurationLabel
            //
            this.lblPreviewDurationLabel.AutoSize = true;
            this.lblPreviewDurationLabel.Font = new System.Drawing.Font("Microsoft Sans Serif", 8.25F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.lblPreviewDurationLabel.Location = new System.Drawing.Point(180, 15);
            this.lblPreviewDurationLabel.Name = "lblPreviewDurationLabel";
            this.lblPreviewDurationLabel.Size = new System.Drawing.Size(61, 13);
            this.lblPreviewDurationLabel.TabIndex = 2;
            this.lblPreviewDurationLabel.Text = "Duration:";
            //
            // lblPreviewTaskCount
            //
            this.lblPreviewTaskCount.AutoSize = true;
            this.lblPreviewTaskCount.Location = new System.Drawing.Point(80, 15);
            this.lblPreviewTaskCount.Name = "lblPreviewTaskCount";
            this.lblPreviewTaskCount.Size = new System.Drawing.Size(10, 13);
            this.lblPreviewTaskCount.TabIndex = 1;
            this.lblPreviewTaskCount.Text = "-";
            //
            // lblPreviewTaskCountLabel
            //
            this.lblPreviewTaskCountLabel.AutoSize = true;
            this.lblPreviewTaskCountLabel.Font = new System.Drawing.Font("Microsoft Sans Serif", 8.25F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.lblPreviewTaskCountLabel.Location = new System.Drawing.Point(10, 15);
            this.lblPreviewTaskCountLabel.Name = "lblPreviewTaskCountLabel";
            this.lblPreviewTaskCountLabel.Size = new System.Drawing.Size(45, 13);
            this.lblPreviewTaskCountLabel.TabIndex = 0;
            this.lblPreviewTaskCountLabel.Text = "Tasks:";
            //
            // lblPreviewStatus
            //
            this.lblPreviewStatus.AutoSize = true;
            this.lblPreviewStatus.ForeColor = System.Drawing.SystemColors.ControlDarkDark;
            this.lblPreviewStatus.Location = new System.Drawing.Point(570, 85);
            this.lblPreviewStatus.Name = "lblPreviewStatus";
            this.lblPreviewStatus.Size = new System.Drawing.Size(99, 13);
            this.lblPreviewStatus.TabIndex = 1;
            this.lblPreviewStatus.Text = "Preview loaded";
            //
            // lblStep3Instructions
            //
            this.lblStep3Instructions.AutoSize = true;
            this.lblStep3Instructions.Location = new System.Drawing.Point(15, 15);
            this.lblStep3Instructions.Name = "lblStep3Instructions";
            this.lblStep3Instructions.Size = new System.Drawing.Size(366, 13);
            this.lblStep3Instructions.TabIndex = 0;
            this.lblStep3Instructions.Text = "Preview tasks and apply filters. Click Generate to add to your project.";
            //
            // panelButtons
            //
            this.panelButtons.Controls.Add(this.btnCancel);
            this.panelButtons.Controls.Add(this.btnGenerate);
            this.panelButtons.Controls.Add(this.btnNext);
            this.panelButtons.Controls.Add(this.btnBack);
            this.panelButtons.Location = new System.Drawing.Point(12, 480);
            this.panelButtons.Name = "panelButtons";
            this.panelButtons.Size = new System.Drawing.Size(760, 40);
            this.panelButtons.TabIndex = 6;
            //
            // btnCancel
            //
            this.btnCancel.Location = new System.Drawing.Point(10, 8);
            this.btnCancel.Name = "btnCancel";
            this.btnCancel.Size = new System.Drawing.Size(80, 25);
            this.btnCancel.TabIndex = 3;
            this.btnCancel.Text = "Cancel";
            this.btnCancel.UseVisualStyleBackColor = true;
            this.btnCancel.Click += new System.EventHandler(this.btnCancel_Click);
            //
            // btnGenerate
            //
            this.btnGenerate.Font = new System.Drawing.Font("Microsoft Sans Serif", 8.25F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.btnGenerate.Location = new System.Drawing.Point(660, 8);
            this.btnGenerate.Name = "btnGenerate";
            this.btnGenerate.Size = new System.Drawing.Size(85, 25);
            this.btnGenerate.TabIndex = 2;
            this.btnGenerate.Text = "Generate";
            this.btnGenerate.UseVisualStyleBackColor = true;
            this.btnGenerate.Visible = false;
            this.btnGenerate.Click += new System.EventHandler(this.btnGenerate_Click);
            //
            // btnNext
            //
            this.btnNext.Location = new System.Drawing.Point(660, 8);
            this.btnNext.Name = "btnNext";
            this.btnNext.Size = new System.Drawing.Size(85, 25);
            this.btnNext.TabIndex = 1;
            this.btnNext.Text = "Next >";
            this.btnNext.UseVisualStyleBackColor = true;
            this.btnNext.Click += new System.EventHandler(this.btnNext_Click);
            //
            // btnBack
            //
            this.btnBack.Enabled = false;
            this.btnBack.Location = new System.Drawing.Point(570, 8);
            this.btnBack.Name = "btnBack";
            this.btnBack.Size = new System.Drawing.Size(80, 25);
            this.btnBack.TabIndex = 0;
            this.btnBack.Text = "< Back";
            this.btnBack.UseVisualStyleBackColor = true;
            this.btnBack.Click += new System.EventHandler(this.btnBack_Click);
            //
            // UnifiedTemplateManagerForm
            //
            this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 13F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(784, 531);
            this.Controls.Add(this.panelButtons);
            this.Controls.Add(this.panelStep3);
            this.Controls.Add(this.panelStep2);
            this.Controls.Add(this.panelStep1);
            this.Controls.Add(this.panelStepHeaders);
            this.Controls.Add(this.lblStepIndicator);
            this.Controls.Add(this.lblTitle);
            this.FormBorderStyle = System.Windows.Forms.FormBorderStyle.FixedDialog;
            this.MaximizeBox = false;
            this.MinimizeBox = false;
            this.Name = "UnifiedTemplateManagerForm";
            this.StartPosition = System.Windows.Forms.FormStartPosition.CenterScreen;
            this.Text = "Unified Template Manager";
            this.panelStepHeaders.ResumeLayout(false);
            this.panelStepHeaders.PerformLayout();
            this.panelStep1.ResumeLayout(false);
            this.panelStep1.PerformLayout();
            this.panelStep2.ResumeLayout(false);
            this.panelStep2.PerformLayout();
            this.panelFullStudyConfig.ResumeLayout(false);
            this.panelFullStudyConfig.PerformLayout();
            this.panelSiteStartupConfig.ResumeLayout(false);
            this.panelSiteStartupConfig.PerformLayout();
            this.panelSiteCloseoutConfig.ResumeLayout(false);
            this.panelSiteCloseoutConfig.PerformLayout();
            this.panelStudyCloseoutConfig.ResumeLayout(false);
            this.panelStudyCloseoutConfig.PerformLayout();
            this.panelStep3.ResumeLayout(false);
            this.panelStep3.PerformLayout();
            ((System.ComponentModel.ISupportInitialize)(this.dgvTaskPreview)).EndInit();
            this.panelFilters.ResumeLayout(false);
            this.panelFilters.PerformLayout();
            this.panelPreviewInfo.ResumeLayout(false);
            this.panelPreviewInfo.PerformLayout();
            this.panelButtons.ResumeLayout(false);
            this.ResumeLayout(false);
            this.PerformLayout();

        }

        #endregion

        private System.Windows.Forms.Label lblTitle;
        private System.Windows.Forms.Label lblStepIndicator;
        private System.Windows.Forms.Panel panelStepHeaders;
        private System.Windows.Forms.Label lblStep3Title;
        private System.Windows.Forms.Label lblStep2Title;
        private System.Windows.Forms.Label lblStep1Title;
        private System.Windows.Forms.Panel panelStep1;
        private System.Windows.Forms.RadioButton rbAmendmentWorkflow;
        private System.Windows.Forms.RadioButton rbStudyCloseout;
        private System.Windows.Forms.RadioButton rbSiteCloseout;
        private System.Windows.Forms.RadioButton rbSiteImplementation;
        private System.Windows.Forms.RadioButton rbSiteStartup;
        private System.Windows.Forms.RadioButton rbFullStudyTimeline;
        private System.Windows.Forms.Label lblStep1Instructions;
        private System.Windows.Forms.Panel panelStep2;
        private System.Windows.Forms.Panel panelFullStudyConfig;
        private System.Windows.Forms.ComboBox cmbTherapeuticArea;
        private System.Windows.Forms.Label lblTherapeuticArea;
        private System.Windows.Forms.ComboBox cmbStudyPhase;
        private System.Windows.Forms.Label lblStudyPhase;
        private System.Windows.Forms.ComboBox cmbFullStudyCountry;
        private System.Windows.Forms.Label lblFullStudyCountry;
        private System.Windows.Forms.Panel panelSiteStartupConfig;
        private System.Windows.Forms.ComboBox cmbSiteStartupCountry;
        private System.Windows.Forms.Label lblSiteStartupCountry;
        private System.Windows.Forms.ComboBox cmbSiteStartupSiteId;
        private System.Windows.Forms.Label lblSiteStartupSiteId;
        private System.Windows.Forms.Panel panelSiteCloseoutConfig;
        private System.Windows.Forms.ComboBox cmbSiteCloseoutCountry;
        private System.Windows.Forms.Label lblSiteCloseoutCountry;
        private System.Windows.Forms.ComboBox cmbSiteCloseoutSiteId;
        private System.Windows.Forms.Label lblSiteCloseoutSiteId;
        private System.Windows.Forms.Panel panelStudyCloseoutConfig;
        private System.Windows.Forms.Label lblStudyCloseoutInfo;
        private System.Windows.Forms.Label lblStep2Instructions;
        private System.Windows.Forms.Panel panelStep3;
        private System.Windows.Forms.DataGridView dgvTaskPreview;
        private System.Windows.Forms.Panel panelFilters;
        private System.Windows.Forms.CheckBox chkIncludeOptional;
        private System.Windows.Forms.CheckedListBox clbCategories;
        private System.Windows.Forms.Label lblFilterCategories;
        private System.Windows.Forms.Panel panelPreviewInfo;
        private System.Windows.Forms.Label lblPreviewSource;
        private System.Windows.Forms.Label lblPreviewSourceLabel;
        private System.Windows.Forms.Label lblPreviewDuration;
        private System.Windows.Forms.Label lblPreviewDurationLabel;
        private System.Windows.Forms.Label lblPreviewTaskCount;
        private System.Windows.Forms.Label lblPreviewTaskCountLabel;
        private System.Windows.Forms.Label lblPreviewStatus;
        private System.Windows.Forms.Label lblStep3Instructions;
        private System.Windows.Forms.Panel panelButtons;
        private System.Windows.Forms.Button btnCancel;
        private System.Windows.Forms.Button btnGenerate;
        private System.Windows.Forms.Button btnNext;
        private System.Windows.Forms.Button btnBack;
        private System.Windows.Forms.DataGridViewTextBoxColumn colTaskName;
        private System.Windows.Forms.DataGridViewTextBoxColumn colDuration;
        private System.Windows.Forms.DataGridViewTextBoxColumn colCategory;
        private System.Windows.Forms.DataGridViewTextBoxColumn colMandatory;
    }
}
