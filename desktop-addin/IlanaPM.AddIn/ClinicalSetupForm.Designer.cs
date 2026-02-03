namespace IlanaPM.AddIn
{
    partial class ClinicalSetupForm
    {
        /// <summary>
        /// Required designer variable.
        /// </summary>
        private System.ComponentModel.IContainer components = null;

        /// <summary>
        /// Clean up any resources being used.
        /// </summary>
        /// <param name="disposing">true if managed resources should be disposed; otherwise, false.</param>
        protected override void Dispose(bool disposing)
        {
            if (disposing && (components != null))
            {
                components.Dispose();
            }
            base.Dispose(disposing);
        }

        #region Windows Form Designer generated code

        /// <summary>
        /// Required method for Designer support - do not modify
        /// the contents of this method with the code editor.
        /// </summary>
        private void InitializeComponent()
        {
            this.tabControl1 = new System.Windows.Forms.TabControl();
            this.tabSites = new System.Windows.Forms.TabPage();
            this.btnDeleteSite = new System.Windows.Forms.Button();
            this.btnAddSite = new System.Windows.Forms.Button();
            this.dgvSites = new System.Windows.Forms.DataGridView();
            this.colSiteId = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.colSiteName = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.colCountry = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.colStatus = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.colIRBDate = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.colPI = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.tabAmendments = new System.Windows.Forms.TabPage();
            this.btnEditAffectedSites = new System.Windows.Forms.Button();
            this.btnDeleteAmendment = new System.Windows.Forms.Button();
            this.btnAddAmendment = new System.Windows.Forms.Button();
            this.dgvAmendments = new System.Windows.Forms.DataGridView();
            this.colAmendmentId = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.colNumber = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.colDate = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.colDescription = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.colAffectedSites = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.colAmendmentType = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.tabCohorts = new System.Windows.Forms.TabPage();
            this.btnEditParticipatingSites = new System.Windows.Forms.Button();
            this.btnDeleteCohort = new System.Windows.Forms.Button();
            this.btnAddCohort = new System.Windows.Forms.Button();
            this.dgvCohorts = new System.Windows.Forms.DataGridView();
            this.colCohortId = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.colCohortName = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.colEnrollmentTarget = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.colPrerequisites = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.colParticipatingSites = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.btnSave = new System.Windows.Forms.Button();
            this.btnCancel = new System.Windows.Forms.Button();
            this.tabControl1.SuspendLayout();
            this.tabSites.SuspendLayout();
            ((System.ComponentModel.ISupportInitialize)(this.dgvSites)).BeginInit();
            this.tabAmendments.SuspendLayout();
            ((System.ComponentModel.ISupportInitialize)(this.dgvAmendments)).BeginInit();
            this.tabCohorts.SuspendLayout();
            ((System.ComponentModel.ISupportInitialize)(this.dgvCohorts)).BeginInit();
            this.SuspendLayout();
            //
            // tabControl1
            //
            this.tabControl1.Controls.Add(this.tabSites);
            this.tabControl1.Controls.Add(this.tabAmendments);
            this.tabControl1.Controls.Add(this.tabCohorts);
            this.tabControl1.Location = new System.Drawing.Point(12, 12);
            this.tabControl1.Name = "tabControl1";
            this.tabControl1.SelectedIndex = 0;
            this.tabControl1.Size = new System.Drawing.Size(760, 400);
            this.tabControl1.TabIndex = 0;
            //
            // tabSites
            //
            this.tabSites.Controls.Add(this.btnDeleteSite);
            this.tabSites.Controls.Add(this.btnAddSite);
            this.tabSites.Controls.Add(this.dgvSites);
            this.tabSites.Location = new System.Drawing.Point(4, 22);
            this.tabSites.Name = "tabSites";
            this.tabSites.Padding = new System.Windows.Forms.Padding(3);
            this.tabSites.Size = new System.Drawing.Size(752, 374);
            this.tabSites.TabIndex = 0;
            this.tabSites.Text = "Sites";
            this.tabSites.UseVisualStyleBackColor = true;
            //
            // btnDeleteSite
            //
            this.btnDeleteSite.Location = new System.Drawing.Point(120, 335);
            this.btnDeleteSite.Name = "btnDeleteSite";
            this.btnDeleteSite.Size = new System.Drawing.Size(100, 30);
            this.btnDeleteSite.TabIndex = 2;
            this.btnDeleteSite.Text = "Delete";
            this.btnDeleteSite.UseVisualStyleBackColor = true;
            this.btnDeleteSite.Click += new System.EventHandler(this.btnDeleteSite_Click);
            //
            // btnAddSite
            //
            this.btnAddSite.Location = new System.Drawing.Point(10, 335);
            this.btnAddSite.Name = "btnAddSite";
            this.btnAddSite.Size = new System.Drawing.Size(100, 30);
            this.btnAddSite.TabIndex = 1;
            this.btnAddSite.Text = "Add Site";
            this.btnAddSite.UseVisualStyleBackColor = true;
            this.btnAddSite.Click += new System.EventHandler(this.btnAddSite_Click);
            //
            // dgvSites
            //
            this.dgvSites.ColumnHeadersHeightSizeMode = System.Windows.Forms.DataGridViewColumnHeadersHeightSizeMode.AutoSize;
            this.dgvSites.Columns.AddRange(new System.Windows.Forms.DataGridViewColumn[] {
            this.colSiteId,
            this.colSiteName,
            this.colCountry,
            this.colStatus,
            this.colIRBDate,
            this.colPI});
            this.dgvSites.Location = new System.Drawing.Point(10, 10);
            this.dgvSites.Name = "dgvSites";
            this.dgvSites.Size = new System.Drawing.Size(730, 315);
            this.dgvSites.TabIndex = 0;
            this.dgvSites.CellEndEdit += new System.Windows.Forms.DataGridViewCellEventHandler(this.dgvSites_CellEndEdit);
            //
            // colSiteId
            //
            this.colSiteId.HeaderText = "ID";
            this.colSiteId.Name = "colSiteId";
            this.colSiteId.Width = 80;
            //
            // colSiteName
            //
            this.colSiteName.HeaderText = "Name";
            this.colSiteName.Name = "colSiteName";
            this.colSiteName.Width = 200;
            //
            // colCountry
            //
            this.colCountry.HeaderText = "Country";
            this.colCountry.Name = "colCountry";
            this.colCountry.Width = 80;
            //
            // colStatus
            //
            this.colStatus.HeaderText = "Status";
            this.colStatus.Name = "colStatus";
            this.colStatus.Width = 80;
            //
            // colIRBDate
            //
            this.colIRBDate.HeaderText = "IRB Approval Date";
            this.colIRBDate.Name = "colIRBDate";
            this.colIRBDate.Width = 120;
            //
            // colPI
            //
            this.colPI.HeaderText = "Principal Investigator";
            this.colPI.Name = "colPI";
            this.colPI.Width = 150;
            //
            // tabAmendments
            //
            this.tabAmendments.Controls.Add(this.btnEditAffectedSites);
            this.tabAmendments.Controls.Add(this.btnDeleteAmendment);
            this.tabAmendments.Controls.Add(this.btnAddAmendment);
            this.tabAmendments.Controls.Add(this.dgvAmendments);
            this.tabAmendments.Location = new System.Drawing.Point(4, 22);
            this.tabAmendments.Name = "tabAmendments";
            this.tabAmendments.Padding = new System.Windows.Forms.Padding(3);
            this.tabAmendments.Size = new System.Drawing.Size(752, 374);
            this.tabAmendments.TabIndex = 1;
            this.tabAmendments.Text = "Amendments";
            this.tabAmendments.UseVisualStyleBackColor = true;
            //
            // btnEditAffectedSites
            //
            this.btnEditAffectedSites.Location = new System.Drawing.Point(230, 335);
            this.btnEditAffectedSites.Name = "btnEditAffectedSites";
            this.btnEditAffectedSites.Size = new System.Drawing.Size(130, 30);
            this.btnEditAffectedSites.TabIndex = 3;
            this.btnEditAffectedSites.Text = "Edit Affected Sites";
            this.btnEditAffectedSites.UseVisualStyleBackColor = true;
            this.btnEditAffectedSites.Click += new System.EventHandler(this.btnEditAffectedSites_Click);
            //
            // btnDeleteAmendment
            //
            this.btnDeleteAmendment.Location = new System.Drawing.Point(120, 335);
            this.btnDeleteAmendment.Name = "btnDeleteAmendment";
            this.btnDeleteAmendment.Size = new System.Drawing.Size(100, 30);
            this.btnDeleteAmendment.TabIndex = 2;
            this.btnDeleteAmendment.Text = "Delete";
            this.btnDeleteAmendment.UseVisualStyleBackColor = true;
            this.btnDeleteAmendment.Click += new System.EventHandler(this.btnDeleteAmendment_Click);
            //
            // btnAddAmendment
            //
            this.btnAddAmendment.Location = new System.Drawing.Point(10, 335);
            this.btnAddAmendment.Name = "btnAddAmendment";
            this.btnAddAmendment.Size = new System.Drawing.Size(100, 30);
            this.btnAddAmendment.TabIndex = 1;
            this.btnAddAmendment.Text = "Add Amendment";
            this.btnAddAmendment.UseVisualStyleBackColor = true;
            this.btnAddAmendment.Click += new System.EventHandler(this.btnAddAmendment_Click);
            //
            // dgvAmendments
            //
            this.dgvAmendments.ColumnHeadersHeightSizeMode = System.Windows.Forms.DataGridViewColumnHeadersHeightSizeMode.AutoSize;
            this.dgvAmendments.Columns.AddRange(new System.Windows.Forms.DataGridViewColumn[] {
            this.colAmendmentId,
            this.colNumber,
            this.colDate,
            this.colDescription,
            this.colAffectedSites,
            this.colAmendmentType});
            this.dgvAmendments.Location = new System.Drawing.Point(10, 10);
            this.dgvAmendments.Name = "dgvAmendments";
            this.dgvAmendments.Size = new System.Drawing.Size(730, 315);
            this.dgvAmendments.TabIndex = 0;
            this.dgvAmendments.CellEndEdit += new System.Windows.Forms.DataGridViewCellEventHandler(this.dgvAmendments_CellEndEdit);
            //
            // colAmendmentId
            //
            this.colAmendmentId.HeaderText = "ID";
            this.colAmendmentId.Name = "colAmendmentId";
            this.colAmendmentId.Width = 80;
            //
            // colNumber
            //
            this.colNumber.HeaderText = "Number";
            this.colNumber.Name = "colNumber";
            this.colNumber.Width = 100;
            //
            // colDate
            //
            this.colDate.HeaderText = "Date";
            this.colDate.Name = "colDate";
            this.colDate.Width = 100;
            //
            // colDescription
            //
            this.colDescription.HeaderText = "Description";
            this.colDescription.Name = "colDescription";
            this.colDescription.Width = 200;
            //
            // colAffectedSites
            //
            this.colAffectedSites.HeaderText = "Affected Sites";
            this.colAffectedSites.Name = "colAffectedSites";
            this.colAffectedSites.Width = 150;
            //
            // colAmendmentType
            //
            this.colAmendmentType.HeaderText = "Type";
            this.colAmendmentType.Name = "colAmendmentType";
            this.colAmendmentType.Width = 80;
            //
            // tabCohorts
            //
            this.tabCohorts.Controls.Add(this.btnEditParticipatingSites);
            this.tabCohorts.Controls.Add(this.btnDeleteCohort);
            this.tabCohorts.Controls.Add(this.btnAddCohort);
            this.tabCohorts.Controls.Add(this.dgvCohorts);
            this.tabCohorts.Location = new System.Drawing.Point(4, 22);
            this.tabCohorts.Name = "tabCohorts";
            this.tabCohorts.Size = new System.Drawing.Size(752, 374);
            this.tabCohorts.TabIndex = 2;
            this.tabCohorts.Text = "Cohorts";
            this.tabCohorts.UseVisualStyleBackColor = true;
            //
            // btnEditParticipatingSites
            //
            this.btnEditParticipatingSites.Location = new System.Drawing.Point(230, 335);
            this.btnEditParticipatingSites.Name = "btnEditParticipatingSites";
            this.btnEditParticipatingSites.Size = new System.Drawing.Size(160, 30);
            this.btnEditParticipatingSites.TabIndex = 3;
            this.btnEditParticipatingSites.Text = "Edit Participating Sites";
            this.btnEditParticipatingSites.UseVisualStyleBackColor = true;
            this.btnEditParticipatingSites.Click += new System.EventHandler(this.btnEditParticipatingSites_Click);
            //
            // btnDeleteCohort
            //
            this.btnDeleteCohort.Location = new System.Drawing.Point(120, 335);
            this.btnDeleteCohort.Name = "btnDeleteCohort";
            this.btnDeleteCohort.Size = new System.Drawing.Size(100, 30);
            this.btnDeleteCohort.TabIndex = 2;
            this.btnDeleteCohort.Text = "Delete";
            this.btnDeleteCohort.UseVisualStyleBackColor = true;
            this.btnDeleteCohort.Click += new System.EventHandler(this.btnDeleteCohort_Click);
            //
            // btnAddCohort
            //
            this.btnAddCohort.Location = new System.Drawing.Point(10, 335);
            this.btnAddCohort.Name = "btnAddCohort";
            this.btnAddCohort.Size = new System.Drawing.Size(100, 30);
            this.btnAddCohort.TabIndex = 1;
            this.btnAddCohort.Text = "Add Cohort";
            this.btnAddCohort.UseVisualStyleBackColor = true;
            this.btnAddCohort.Click += new System.EventHandler(this.btnAddCohort_Click);
            //
            // dgvCohorts
            //
            this.dgvCohorts.ColumnHeadersHeightSizeMode = System.Windows.Forms.DataGridViewColumnHeadersHeightSizeMode.AutoSize;
            this.dgvCohorts.Columns.AddRange(new System.Windows.Forms.DataGridViewColumn[] {
            this.colCohortId,
            this.colCohortName,
            this.colEnrollmentTarget,
            this.colPrerequisites,
            this.colParticipatingSites});
            this.dgvCohorts.Location = new System.Drawing.Point(10, 10);
            this.dgvCohorts.Name = "dgvCohorts";
            this.dgvCohorts.Size = new System.Drawing.Size(730, 315);
            this.dgvCohorts.TabIndex = 0;
            this.dgvCohorts.CellEndEdit += new System.Windows.Forms.DataGridViewCellEventHandler(this.dgvCohorts_CellEndEdit);
            //
            // colCohortId
            //
            this.colCohortId.HeaderText = "ID";
            this.colCohortId.Name = "colCohortId";
            this.colCohortId.Width = 80;
            //
            // colCohortName
            //
            this.colCohortName.HeaderText = "Name";
            this.colCohortName.Name = "colCohortName";
            this.colCohortName.Width = 200;
            //
            // colEnrollmentTarget
            //
            this.colEnrollmentTarget.HeaderText = "Enrollment Target";
            this.colEnrollmentTarget.Name = "colEnrollmentTarget";
            this.colEnrollmentTarget.Width = 100;
            //
            // colPrerequisites
            //
            this.colPrerequisites.HeaderText = "Prerequisites";
            this.colPrerequisites.Name = "colPrerequisites";
            this.colPrerequisites.Width = 150;
            //
            // colParticipatingSites
            //
            this.colParticipatingSites.HeaderText = "Participating Sites";
            this.colParticipatingSites.Name = "colParticipatingSites";
            this.colParticipatingSites.Width = 180;
            //
            // btnSave
            //
            this.btnSave.Font = new System.Drawing.Font("Microsoft Sans Serif", 9F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.btnSave.Location = new System.Drawing.Point(550, 425);
            this.btnSave.Name = "btnSave";
            this.btnSave.Size = new System.Drawing.Size(110, 35);
            this.btnSave.TabIndex = 1;
            this.btnSave.Text = "Save";
            this.btnSave.UseVisualStyleBackColor = true;
            this.btnSave.Click += new System.EventHandler(this.btnSave_Click);
            //
            // btnCancel
            //
            this.btnCancel.Location = new System.Drawing.Point(670, 425);
            this.btnCancel.Name = "btnCancel";
            this.btnCancel.Size = new System.Drawing.Size(110, 35);
            this.btnCancel.TabIndex = 2;
            this.btnCancel.Text = "Cancel";
            this.btnCancel.UseVisualStyleBackColor = true;
            this.btnCancel.Click += new System.EventHandler(this.btnCancel_Click);
            //
            // ClinicalSetupForm
            //
            this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 13F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(784, 471);
            this.Controls.Add(this.btnCancel);
            this.Controls.Add(this.btnSave);
            this.Controls.Add(this.tabControl1);
            this.FormBorderStyle = System.Windows.Forms.FormBorderStyle.FixedDialog;
            this.MaximizeBox = false;
            this.MinimizeBox = false;
            this.Name = "ClinicalSetupForm";
            this.StartPosition = System.Windows.Forms.FormStartPosition.CenterScreen;
            this.Text = "Clinical Entity Setup";
            this.Load += new System.EventHandler(this.ClinicalSetupForm_Load);
            this.tabControl1.ResumeLayout(false);
            this.tabSites.ResumeLayout(false);
            ((System.ComponentModel.ISupportInitialize)(this.dgvSites)).EndInit();
            this.tabAmendments.ResumeLayout(false);
            ((System.ComponentModel.ISupportInitialize)(this.dgvAmendments)).EndInit();
            this.tabCohorts.ResumeLayout(false);
            ((System.ComponentModel.ISupportInitialize)(this.dgvCohorts)).EndInit();
            this.ResumeLayout(false);

        }

        #endregion

        private System.Windows.Forms.TabControl tabControl1;
        private System.Windows.Forms.TabPage tabSites;
        private System.Windows.Forms.TabPage tabAmendments;
        private System.Windows.Forms.TabPage tabCohorts;
        private System.Windows.Forms.DataGridView dgvSites;
        private System.Windows.Forms.Button btnAddSite;
        private System.Windows.Forms.Button btnDeleteSite;
        private System.Windows.Forms.DataGridView dgvAmendments;
        private System.Windows.Forms.Button btnAddAmendment;
        private System.Windows.Forms.Button btnDeleteAmendment;
        private System.Windows.Forms.DataGridView dgvCohorts;
        private System.Windows.Forms.Button btnAddCohort;
        private System.Windows.Forms.Button btnDeleteCohort;
        private System.Windows.Forms.Button btnSave;
        private System.Windows.Forms.Button btnCancel;
        private System.Windows.Forms.DataGridViewTextBoxColumn colSiteId;
        private System.Windows.Forms.DataGridViewTextBoxColumn colSiteName;
        private System.Windows.Forms.DataGridViewTextBoxColumn colCountry;
        private System.Windows.Forms.DataGridViewTextBoxColumn colStatus;
        private System.Windows.Forms.DataGridViewTextBoxColumn colIRBDate;
        private System.Windows.Forms.DataGridViewTextBoxColumn colPI;
        private System.Windows.Forms.DataGridViewTextBoxColumn colAmendmentId;
        private System.Windows.Forms.DataGridViewTextBoxColumn colNumber;
        private System.Windows.Forms.DataGridViewTextBoxColumn colDate;
        private System.Windows.Forms.DataGridViewTextBoxColumn colDescription;
        private System.Windows.Forms.DataGridViewTextBoxColumn colAffectedSites;
        private System.Windows.Forms.DataGridViewTextBoxColumn colAmendmentType;
        private System.Windows.Forms.Button btnEditAffectedSites;
        private System.Windows.Forms.Button btnEditParticipatingSites;
        private System.Windows.Forms.DataGridViewTextBoxColumn colCohortId;
        private System.Windows.Forms.DataGridViewTextBoxColumn colCohortName;
        private System.Windows.Forms.DataGridViewTextBoxColumn colEnrollmentTarget;
        private System.Windows.Forms.DataGridViewTextBoxColumn colPrerequisites;
        private System.Windows.Forms.DataGridViewTextBoxColumn colParticipatingSites;
    }
}
