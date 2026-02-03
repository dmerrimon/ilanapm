namespace IlanaPM.AddIn
{
    partial class EssentialDocumentsTrackerForm
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
            this.lblSite = new System.Windows.Forms.Label();
            this.cboSite = new System.Windows.Forms.ComboBox();
            this.dgvDocuments = new System.Windows.Forms.DataGridView();
            this.colDocumentName = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.colRegulatoryRef = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.colStatus = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.colDateCollected = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.colCollectedBy = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.colVersion = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.colMandatory = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.lblSiteInfo = new System.Windows.Forms.Label();
            this.lblCompletion = new System.Windows.Forms.Label();
            this.lblOverallStats = new System.Windows.Forms.Label();
            this.btnMarkCollected = new System.Windows.Forms.Button();
            this.btnMarkVerified = new System.Windows.Forms.Button();
            this.btnMarkFiled = new System.Windows.Forms.Button();
            this.btnExportChecklist = new System.Windows.Forms.Button();
            this.btnClose = new System.Windows.Forms.Button();
            ((System.ComponentModel.ISupportInitialize)(this.dgvDocuments)).BeginInit();
            this.SuspendLayout();
            //
            // lblTitle
            //
            this.lblTitle.AutoSize = true;
            this.lblTitle.Font = new System.Drawing.Font("Microsoft Sans Serif", 12F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.lblTitle.Location = new System.Drawing.Point(12, 15);
            this.lblTitle.Name = "lblTitle";
            this.lblTitle.Size = new System.Drawing.Size(259, 20);
            this.lblTitle.TabIndex = 0;
            this.lblTitle.Text = "Essential Documents Tracker";
            //
            // lblSite
            //
            this.lblSite.AutoSize = true;
            this.lblSite.Location = new System.Drawing.Point(12, 50);
            this.lblSite.Name = "lblSite";
            this.lblSite.Size = new System.Drawing.Size(64, 13);
            this.lblSite.TabIndex = 1;
            this.lblSite.Text = "Select Site:";
            //
            // cboSite
            //
            this.cboSite.DisplayMember = "DisplayName";
            this.cboSite.DropDownStyle = System.Windows.Forms.ComboBoxStyle.DropDownList;
            this.cboSite.FormattingEnabled = true;
            this.cboSite.Location = new System.Drawing.Point(82, 47);
            this.cboSite.Name = "cboSite";
            this.cboSite.Size = new System.Drawing.Size(350, 21);
            this.cboSite.TabIndex = 2;
            this.cboSite.SelectedIndexChanged += new System.EventHandler(this.cboSite_SelectedIndexChanged);
            //
            // dgvDocuments
            //
            this.dgvDocuments.AllowUserToAddRows = false;
            this.dgvDocuments.AllowUserToDeleteRows = false;
            this.dgvDocuments.ColumnHeadersHeightSizeMode = System.Windows.Forms.DataGridViewColumnHeadersHeightSizeMode.AutoSize;
            this.dgvDocuments.Columns.AddRange(new System.Windows.Forms.DataGridViewColumn[] {
            this.colDocumentName,
            this.colRegulatoryRef,
            this.colStatus,
            this.colDateCollected,
            this.colCollectedBy,
            this.colVersion,
            this.colMandatory});
            this.dgvDocuments.Location = new System.Drawing.Point(15, 120);
            this.dgvDocuments.Name = "dgvDocuments";
            this.dgvDocuments.ReadOnly = true;
            this.dgvDocuments.SelectionMode = System.Windows.Forms.DataGridViewSelectionMode.FullRowSelect;
            this.dgvDocuments.Size = new System.Drawing.Size(950, 380);
            this.dgvDocuments.TabIndex = 3;
            //
            // colDocumentName
            //
            this.colDocumentName.HeaderText = "Document Name";
            this.colDocumentName.Name = "colDocumentName";
            this.colDocumentName.ReadOnly = true;
            this.colDocumentName.Width = 280;
            //
            // colRegulatoryRef
            //
            this.colRegulatoryRef.HeaderText = "Regulatory Reference";
            this.colRegulatoryRef.Name = "colRegulatoryRef";
            this.colRegulatoryRef.ReadOnly = true;
            this.colRegulatoryRef.Width = 150;
            //
            // colStatus
            //
            this.colStatus.HeaderText = "Status";
            this.colStatus.Name = "colStatus";
            this.colStatus.ReadOnly = true;
            this.colStatus.Width = 120;
            //
            // colDateCollected
            //
            this.colDateCollected.HeaderText = "Date Collected";
            this.colDateCollected.Name = "colDateCollected";
            this.colDateCollected.ReadOnly = true;
            this.colDateCollected.Width = 100;
            //
            // colCollectedBy
            //
            this.colCollectedBy.HeaderText = "Collected By";
            this.colCollectedBy.Name = "colCollectedBy";
            this.colCollectedBy.ReadOnly = true;
            this.colCollectedBy.Width = 120;
            //
            // colVersion
            //
            this.colVersion.HeaderText = "Version";
            this.colVersion.Name = "colVersion";
            this.colVersion.ReadOnly = true;
            this.colVersion.Width = 80;
            //
            // colMandatory
            //
            this.colMandatory.HeaderText = "Mandatory";
            this.colMandatory.Name = "colMandatory";
            this.colMandatory.ReadOnly = true;
            this.colMandatory.Width = 80;
            //
            // lblSiteInfo
            //
            this.lblSiteInfo.AutoSize = true;
            this.lblSiteInfo.Font = new System.Drawing.Font("Microsoft Sans Serif", 9F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.lblSiteInfo.Location = new System.Drawing.Point(15, 90);
            this.lblSiteInfo.Name = "lblSiteInfo";
            this.lblSiteInfo.Size = new System.Drawing.Size(79, 15);
            this.lblSiteInfo.TabIndex = 4;
            this.lblSiteInfo.Text = "Site: (none)";
            //
            // lblCompletion
            //
            this.lblCompletion.AutoSize = true;
            this.lblCompletion.Font = new System.Drawing.Font("Microsoft Sans Serif", 9F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.lblCompletion.Location = new System.Drawing.Point(550, 90);
            this.lblCompletion.Name = "lblCompletion";
            this.lblCompletion.Size = new System.Drawing.Size(103, 15);
            this.lblCompletion.TabIndex = 5;
            this.lblCompletion.Text = "Completion: 0%";
            //
            // lblOverallStats
            //
            this.lblOverallStats.AutoSize = true;
            this.lblOverallStats.Location = new System.Drawing.Point(450, 50);
            this.lblOverallStats.Name = "lblOverallStats";
            this.lblOverallStats.Size = new System.Drawing.Size(145, 13);
            this.lblOverallStats.TabIndex = 6;
            this.lblOverallStats.Text = "Overall: 0/0 documents collected";
            //
            // btnMarkCollected
            //
            this.btnMarkCollected.Location = new System.Drawing.Point(15, 515);
            this.btnMarkCollected.Name = "btnMarkCollected";
            this.btnMarkCollected.Size = new System.Drawing.Size(150, 30);
            this.btnMarkCollected.TabIndex = 7;
            this.btnMarkCollected.Text = "Mark as Collected";
            this.btnMarkCollected.UseVisualStyleBackColor = true;
            this.btnMarkCollected.Click += new System.EventHandler(this.btnMarkCollected_Click);
            //
            // btnMarkVerified
            //
            this.btnMarkVerified.Location = new System.Drawing.Point(175, 515);
            this.btnMarkVerified.Name = "btnMarkVerified";
            this.btnMarkVerified.Size = new System.Drawing.Size(150, 30);
            this.btnMarkVerified.TabIndex = 8;
            this.btnMarkVerified.Text = "Mark as Verified";
            this.btnMarkVerified.UseVisualStyleBackColor = true;
            this.btnMarkVerified.Click += new System.EventHandler(this.btnMarkVerified_Click);
            //
            // btnMarkFiled
            //
            this.btnMarkFiled.Location = new System.Drawing.Point(335, 515);
            this.btnMarkFiled.Name = "btnMarkFiled";
            this.btnMarkFiled.Size = new System.Drawing.Size(150, 30);
            this.btnMarkFiled.TabIndex = 9;
            this.btnMarkFiled.Text = "Mark as Filed";
            this.btnMarkFiled.UseVisualStyleBackColor = true;
            this.btnMarkFiled.Click += new System.EventHandler(this.btnMarkFiled_Click);
            //
            // btnExportChecklist
            //
            this.btnExportChecklist.Font = new System.Drawing.Font("Microsoft Sans Serif", 9F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.btnExportChecklist.Location = new System.Drawing.Point(730, 515);
            this.btnExportChecklist.Name = "btnExportChecklist";
            this.btnExportChecklist.Size = new System.Drawing.Size(120, 30);
            this.btnExportChecklist.TabIndex = 10;
            this.btnExportChecklist.Text = "Export to CSV";
            this.btnExportChecklist.UseVisualStyleBackColor = true;
            this.btnExportChecklist.Click += new System.EventHandler(this.btnExportChecklist_Click);
            //
            // btnClose
            //
            this.btnClose.Location = new System.Drawing.Point(860, 515);
            this.btnClose.Name = "btnClose";
            this.btnClose.Size = new System.Drawing.Size(105, 30);
            this.btnClose.TabIndex = 11;
            this.btnClose.Text = "Close";
            this.btnClose.UseVisualStyleBackColor = true;
            this.btnClose.Click += new System.EventHandler(this.btnClose_Click);
            //
            // EssentialDocumentsTrackerForm
            //
            this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 13F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(984, 561);
            this.Controls.Add(this.btnClose);
            this.Controls.Add(this.btnExportChecklist);
            this.Controls.Add(this.btnMarkFiled);
            this.Controls.Add(this.btnMarkVerified);
            this.Controls.Add(this.btnMarkCollected);
            this.Controls.Add(this.lblOverallStats);
            this.Controls.Add(this.lblCompletion);
            this.Controls.Add(this.lblSiteInfo);
            this.Controls.Add(this.dgvDocuments);
            this.Controls.Add(this.cboSite);
            this.Controls.Add(this.lblSite);
            this.Controls.Add(this.lblTitle);
            this.FormBorderStyle = System.Windows.Forms.FormBorderStyle.FixedDialog;
            this.MaximizeBox = false;
            this.MinimizeBox = false;
            this.Name = "EssentialDocumentsTrackerForm";
            this.StartPosition = System.Windows.Forms.FormStartPosition.CenterScreen;
            this.Text = "Essential Documents Tracker";
            this.Load += new System.EventHandler(this.EssentialDocumentsTrackerForm_Load);
            ((System.ComponentModel.ISupportInitialize)(this.dgvDocuments)).EndInit();
            this.ResumeLayout(false);
            this.PerformLayout();

        }

        #endregion

        private System.Windows.Forms.Label lblTitle;
        private System.Windows.Forms.Label lblSite;
        private System.Windows.Forms.ComboBox cboSite;
        private System.Windows.Forms.DataGridView dgvDocuments;
        private System.Windows.Forms.DataGridViewTextBoxColumn colDocumentName;
        private System.Windows.Forms.DataGridViewTextBoxColumn colRegulatoryRef;
        private System.Windows.Forms.DataGridViewTextBoxColumn colStatus;
        private System.Windows.Forms.DataGridViewTextBoxColumn colDateCollected;
        private System.Windows.Forms.DataGridViewTextBoxColumn colCollectedBy;
        private System.Windows.Forms.DataGridViewTextBoxColumn colVersion;
        private System.Windows.Forms.DataGridViewTextBoxColumn colMandatory;
        private System.Windows.Forms.Label lblSiteInfo;
        private System.Windows.Forms.Label lblCompletion;
        private System.Windows.Forms.Label lblOverallStats;
        private System.Windows.Forms.Button btnMarkCollected;
        private System.Windows.Forms.Button btnMarkVerified;
        private System.Windows.Forms.Button btnMarkFiled;
        private System.Windows.Forms.Button btnExportChecklist;
        private System.Windows.Forms.Button btnClose;
    }
}
