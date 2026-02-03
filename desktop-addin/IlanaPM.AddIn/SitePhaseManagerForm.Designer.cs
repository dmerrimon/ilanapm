namespace IlanaPM.AddIn
{
    partial class SitePhaseManagerForm
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
            this.lblSelectPhase = new System.Windows.Forms.Label();
            this.cboPhase = new System.Windows.Forms.ComboBox();
            this.lblSelectSite = new System.Windows.Forms.Label();
            this.cboSite = new System.Windows.Forms.ComboBox();
            this.groupSiteInfo = new System.Windows.Forms.GroupBox();
            this.lblPI = new System.Windows.Forms.Label();
            this.lblStatus = new System.Windows.Forms.Label();
            this.lblCurrentPhase = new System.Windows.Forms.Label();
            this.lblCountry = new System.Windows.Forms.Label();
            this.lblSiteName = new System.Windows.Forms.Label();
            this.groupTemplates = new System.Windows.Forms.GroupBox();
            this.txtTemplateDetails = new System.Windows.Forms.TextBox();
            this.lblAvailableTemplates = new System.Windows.Forms.Label();
            this.lstTemplates = new System.Windows.Forms.ListBox();
            this.btnGenerateStartupTasks = new System.Windows.Forms.Button();
            this.btnPreview = new System.Windows.Forms.Button();
            this.btnClose = new System.Windows.Forms.Button();
            this.groupSiteInfo.SuspendLayout();
            this.groupTemplates.SuspendLayout();
            this.SuspendLayout();
            //
            // lblTitle
            //
            this.lblTitle.AutoSize = true;
            this.lblTitle.Font = new System.Drawing.Font("Microsoft Sans Serif", 14F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.lblTitle.Location = new System.Drawing.Point(12, 15);
            this.lblTitle.Name = "lblTitle";
            this.lblTitle.Size = new System.Drawing.Size(194, 24);
            this.lblTitle.TabIndex = 0;
            this.lblTitle.Text = "Site Phase Manager";
            //
            // lblSelectPhase
            //
            this.lblSelectPhase.AutoSize = true;
            this.lblSelectPhase.Location = new System.Drawing.Point(12, 55);
            this.lblSelectPhase.Name = "lblSelectPhase";
            this.lblSelectPhase.Size = new System.Drawing.Size(75, 13);
            this.lblSelectPhase.TabIndex = 1;
            this.lblSelectPhase.Text = "Select Phase:";
            //
            // cboPhase
            //
            this.cboPhase.DropDownStyle = System.Windows.Forms.ComboBoxStyle.DropDownList;
            this.cboPhase.FormattingEnabled = true;
            this.cboPhase.Items.AddRange(new object[] {
            "Site Startup",
            "Site Closeout",
            "Study Closeout"});
            this.cboPhase.Location = new System.Drawing.Point(93, 52);
            this.cboPhase.Name = "cboPhase";
            this.cboPhase.Size = new System.Drawing.Size(200, 21);
            this.cboPhase.TabIndex = 2;
            this.cboPhase.SelectedIndexChanged += new System.EventHandler(this.cboPhase_SelectedIndexChanged);
            //
            // lblSelectSite
            //
            this.lblSelectSite.AutoSize = true;
            this.lblSelectSite.Location = new System.Drawing.Point(12, 85);
            this.lblSelectSite.Name = "lblSelectSite";
            this.lblSelectSite.Size = new System.Drawing.Size(64, 13);
            this.lblSelectSite.TabIndex = 3;
            this.lblSelectSite.Text = "Select Site:";
            //
            // cboSite
            //
            this.cboSite.DisplayMember = "DisplayName";
            this.cboSite.DropDownStyle = System.Windows.Forms.ComboBoxStyle.DropDownList;
            this.cboSite.FormattingEnabled = true;
            this.cboSite.Location = new System.Drawing.Point(82, 82);
            this.cboSite.Name = "cboSite";
            this.cboSite.Size = new System.Drawing.Size(400, 21);
            this.cboSite.TabIndex = 4;
            this.cboSite.SelectedIndexChanged += new System.EventHandler(this.cboSite_SelectedIndexChanged);
            //
            // groupSiteInfo
            //
            this.groupSiteInfo.Controls.Add(this.lblPI);
            this.groupSiteInfo.Controls.Add(this.lblStatus);
            this.groupSiteInfo.Controls.Add(this.lblCurrentPhase);
            this.groupSiteInfo.Controls.Add(this.lblCountry);
            this.groupSiteInfo.Controls.Add(this.lblSiteName);
            this.groupSiteInfo.Location = new System.Drawing.Point(15, 120);
            this.groupSiteInfo.Name = "groupSiteInfo";
            this.groupSiteInfo.Size = new System.Drawing.Size(467, 140);
            this.groupSiteInfo.TabIndex = 5;
            this.groupSiteInfo.TabStop = false;
            this.groupSiteInfo.Text = "Site Information";
            //
            // lblPI
            //
            this.lblPI.AutoSize = true;
            this.lblPI.Location = new System.Drawing.Point(15, 105);
            this.lblPI.Name = "lblPI";
            this.lblPI.Size = new System.Drawing.Size(18, 13);
            this.lblPI.TabIndex = 4;
            this.lblPI.Text = "PI:";
            //
            // lblStatus
            //
            this.lblStatus.AutoSize = true;
            this.lblStatus.Location = new System.Drawing.Point(15, 80);
            this.lblStatus.Name = "lblStatus";
            this.lblStatus.Size = new System.Drawing.Size(40, 13);
            this.lblStatus.TabIndex = 3;
            this.lblStatus.Text = "Status:";
            //
            // lblCurrentPhase
            //
            this.lblCurrentPhase.AutoSize = true;
            this.lblCurrentPhase.Font = new System.Drawing.Font("Microsoft Sans Serif", 9F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.lblCurrentPhase.Location = new System.Drawing.Point(15, 55);
            this.lblCurrentPhase.Name = "lblCurrentPhase";
            this.lblCurrentPhase.Size = new System.Drawing.Size(107, 15);
            this.lblCurrentPhase.TabIndex = 2;
            this.lblCurrentPhase.Text = "Current Phase:";
            //
            // lblCountry
            //
            this.lblCountry.AutoSize = true;
            this.lblCountry.Location = new System.Drawing.Point(15, 35);
            this.lblCountry.Name = "lblCountry";
            this.lblCountry.Size = new System.Drawing.Size(46, 13);
            this.lblCountry.TabIndex = 1;
            this.lblCountry.Text = "Country:";
            //
            // lblSiteName
            //
            this.lblSiteName.AutoSize = true;
            this.lblSiteName.Font = new System.Drawing.Font("Microsoft Sans Serif", 10F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.lblSiteName.Location = new System.Drawing.Point(15, 20);
            this.lblSiteName.Name = "lblSiteName";
            this.lblSiteName.Size = new System.Drawing.Size(41, 17);
            this.lblSiteName.TabIndex = 0;
            this.lblSiteName.Text = "Site:";
            //
            // groupTemplates
            //
            this.groupTemplates.Controls.Add(this.txtTemplateDetails);
            this.groupTemplates.Controls.Add(this.lblAvailableTemplates);
            this.groupTemplates.Controls.Add(this.lstTemplates);
            this.groupTemplates.Location = new System.Drawing.Point(15, 275);
            this.groupTemplates.Name = "groupTemplates";
            this.groupTemplates.Size = new System.Drawing.Size(467, 280);
            this.groupTemplates.TabIndex = 6;
            this.groupTemplates.TabStop = false;
            this.groupTemplates.Text = "Available Templates";
            //
            // txtTemplateDetails
            //
            this.txtTemplateDetails.Font = new System.Drawing.Font("Consolas", 8.25F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.txtTemplateDetails.Location = new System.Drawing.Point(18, 120);
            this.txtTemplateDetails.Multiline = true;
            this.txtTemplateDetails.Name = "txtTemplateDetails";
            this.txtTemplateDetails.ReadOnly = true;
            this.txtTemplateDetails.ScrollBars = System.Windows.Forms.ScrollBars.Vertical;
            this.txtTemplateDetails.Size = new System.Drawing.Size(430, 145);
            this.txtTemplateDetails.TabIndex = 2;
            //
            // lblAvailableTemplates
            //
            this.lblAvailableTemplates.AutoSize = true;
            this.lblAvailableTemplates.Location = new System.Drawing.Point(15, 25);
            this.lblAvailableTemplates.Name = "lblAvailableTemplates";
            this.lblAvailableTemplates.Size = new System.Drawing.Size(104, 13);
            this.lblAvailableTemplates.TabIndex = 1;
            this.lblAvailableTemplates.Text = "Available Templates:";
            //
            // lstTemplates
            //
            this.lstTemplates.FormattingEnabled = true;
            this.lstTemplates.Location = new System.Drawing.Point(18, 45);
            this.lstTemplates.Name = "lstTemplates";
            this.lstTemplates.Size = new System.Drawing.Size(430, 56);
            this.lstTemplates.TabIndex = 0;
            //
            // btnGenerateStartupTasks
            //
            this.btnGenerateStartupTasks.Font = new System.Drawing.Font("Microsoft Sans Serif", 9F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.btnGenerateStartupTasks.Location = new System.Drawing.Point(15, 570);
            this.btnGenerateStartupTasks.Name = "btnGenerateStartupTasks";
            this.btnGenerateStartupTasks.Size = new System.Drawing.Size(180, 35);
            this.btnGenerateStartupTasks.TabIndex = 7;
            this.btnGenerateStartupTasks.Text = "Generate Tasks";
            this.btnGenerateStartupTasks.UseVisualStyleBackColor = true;
            this.btnGenerateStartupTasks.Click += new System.EventHandler(this.btnGenerateStartupTasks_Click);
            //
            // btnPreview
            //
            this.btnPreview.Location = new System.Drawing.Point(205, 570);
            this.btnPreview.Name = "btnPreview";
            this.btnPreview.Size = new System.Drawing.Size(120, 35);
            this.btnPreview.TabIndex = 8;
            this.btnPreview.Text = "Preview Tasks";
            this.btnPreview.UseVisualStyleBackColor = true;
            this.btnPreview.Click += new System.EventHandler(this.btnPreview_Click);
            //
            // btnClose
            //
            this.btnClose.Location = new System.Drawing.Point(377, 570);
            this.btnClose.Name = "btnClose";
            this.btnClose.Size = new System.Drawing.Size(105, 35);
            this.btnClose.TabIndex = 9;
            this.btnClose.Text = "Close";
            this.btnClose.UseVisualStyleBackColor = true;
            this.btnClose.Click += new System.EventHandler(this.btnClose_Click);
            //
            // SitePhaseManagerForm
            //
            this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 13F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(504, 621);
            this.Controls.Add(this.btnClose);
            this.Controls.Add(this.btnPreview);
            this.Controls.Add(this.btnGenerateStartupTasks);
            this.Controls.Add(this.groupTemplates);
            this.Controls.Add(this.groupSiteInfo);
            this.Controls.Add(this.cboSite);
            this.Controls.Add(this.lblSelectSite);
            this.Controls.Add(this.cboPhase);
            this.Controls.Add(this.lblSelectPhase);
            this.Controls.Add(this.lblTitle);
            this.FormBorderStyle = System.Windows.Forms.FormBorderStyle.FixedDialog;
            this.MaximizeBox = false;
            this.MinimizeBox = false;
            this.Name = "SitePhaseManagerForm";
            this.StartPosition = System.Windows.Forms.FormStartPosition.CenterScreen;
            this.Text = "Site Phase Manager - Ilana PM";
            this.Load += new System.EventHandler(this.SitePhaseManagerForm_Load);
            this.groupSiteInfo.ResumeLayout(false);
            this.groupSiteInfo.PerformLayout();
            this.groupTemplates.ResumeLayout(false);
            this.groupTemplates.PerformLayout();
            this.ResumeLayout(false);
            this.PerformLayout();

        }

        #endregion

        private System.Windows.Forms.Label lblTitle;
        private System.Windows.Forms.Label lblSelectPhase;
        private System.Windows.Forms.ComboBox cboPhase;
        private System.Windows.Forms.Label lblSelectSite;
        private System.Windows.Forms.ComboBox cboSite;
        private System.Windows.Forms.GroupBox groupSiteInfo;
        private System.Windows.Forms.Label lblSiteName;
        private System.Windows.Forms.Label lblCountry;
        private System.Windows.Forms.Label lblCurrentPhase;
        private System.Windows.Forms.Label lblStatus;
        private System.Windows.Forms.Label lblPI;
        private System.Windows.Forms.GroupBox groupTemplates;
        private System.Windows.Forms.ListBox lstTemplates;
        private System.Windows.Forms.Label lblAvailableTemplates;
        private System.Windows.Forms.TextBox txtTemplateDetails;
        private System.Windows.Forms.Button btnGenerateStartupTasks;
        private System.Windows.Forms.Button btnPreview;
        private System.Windows.Forms.Button btnClose;
    }
}
