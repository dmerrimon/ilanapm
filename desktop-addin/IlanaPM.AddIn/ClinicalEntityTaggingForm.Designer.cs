namespace IlanaPM.AddIn
{
    partial class ClinicalEntityTaggingForm
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
            this.lblTaskCount = new System.Windows.Forms.Label();
            this.groupBox1 = new System.Windows.Forms.GroupBox();
            this.clbSites = new System.Windows.Forms.CheckedListBox();
            this.groupBox2 = new System.Windows.Forms.GroupBox();
            this.clbAmendments = new System.Windows.Forms.CheckedListBox();
            this.groupBox3 = new System.Windows.Forms.GroupBox();
            this.clbCohorts = new System.Windows.Forms.CheckedListBox();
            this.btnApplyTags = new System.Windows.Forms.Button();
            this.btnCancel = new System.Windows.Forms.Button();
            this.groupBox1.SuspendLayout();
            this.groupBox2.SuspendLayout();
            this.groupBox3.SuspendLayout();
            this.SuspendLayout();
            //
            // lblTaskCount
            //
            this.lblTaskCount.AutoSize = true;
            this.lblTaskCount.Font = new System.Drawing.Font("Microsoft Sans Serif", 9F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.lblTaskCount.Location = new System.Drawing.Point(12, 15);
            this.lblTaskCount.Name = "lblTaskCount";
            this.lblTaskCount.Size = new System.Drawing.Size(150, 15);
            this.lblTaskCount.TabIndex = 0;
            this.lblTaskCount.Text = "Tagging selected tasks";
            //
            // groupBox1
            //
            this.groupBox1.Controls.Add(this.clbSites);
            this.groupBox1.Location = new System.Drawing.Point(15, 45);
            this.groupBox1.Name = "groupBox1";
            this.groupBox1.Size = new System.Drawing.Size(450, 120);
            this.groupBox1.TabIndex = 1;
            this.groupBox1.TabStop = false;
            this.groupBox1.Text = "Sites";
            //
            // clbSites
            //
            this.clbSites.CheckOnClick = true;
            this.clbSites.Dock = System.Windows.Forms.DockStyle.Fill;
            this.clbSites.FormattingEnabled = true;
            this.clbSites.Location = new System.Drawing.Point(3, 16);
            this.clbSites.Name = "clbSites";
            this.clbSites.Size = new System.Drawing.Size(444, 101);
            this.clbSites.TabIndex = 0;
            //
            // groupBox2
            //
            this.groupBox2.Controls.Add(this.clbAmendments);
            this.groupBox2.Location = new System.Drawing.Point(15, 175);
            this.groupBox2.Name = "groupBox2";
            this.groupBox2.Size = new System.Drawing.Size(450, 120);
            this.groupBox2.TabIndex = 2;
            this.groupBox2.TabStop = false;
            this.groupBox2.Text = "Amendments";
            //
            // clbAmendments
            //
            this.clbAmendments.CheckOnClick = true;
            this.clbAmendments.Dock = System.Windows.Forms.DockStyle.Fill;
            this.clbAmendments.FormattingEnabled = true;
            this.clbAmendments.Location = new System.Drawing.Point(3, 16);
            this.clbAmendments.Name = "clbAmendments";
            this.clbAmendments.Size = new System.Drawing.Size(444, 101);
            this.clbAmendments.TabIndex = 0;
            //
            // groupBox3
            //
            this.groupBox3.Controls.Add(this.clbCohorts);
            this.groupBox3.Location = new System.Drawing.Point(15, 305);
            this.groupBox3.Name = "groupBox3";
            this.groupBox3.Size = new System.Drawing.Size(450, 120);
            this.groupBox3.TabIndex = 3;
            this.groupBox3.TabStop = false;
            this.groupBox3.Text = "Cohorts";
            //
            // clbCohorts
            //
            this.clbCohorts.CheckOnClick = true;
            this.clbCohorts.Dock = System.Windows.Forms.DockStyle.Fill;
            this.clbCohorts.FormattingEnabled = true;
            this.clbCohorts.Location = new System.Drawing.Point(3, 16);
            this.clbCohorts.Name = "clbCohorts";
            this.clbCohorts.Size = new System.Drawing.Size(444, 101);
            this.clbCohorts.TabIndex = 0;
            //
            // btnApplyTags
            //
            this.btnApplyTags.Font = new System.Drawing.Font("Microsoft Sans Serif", 9F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.btnApplyTags.Location = new System.Drawing.Point(270, 440);
            this.btnApplyTags.Name = "btnApplyTags";
            this.btnApplyTags.Size = new System.Drawing.Size(120, 35);
            this.btnApplyTags.TabIndex = 4;
            this.btnApplyTags.Text = "Apply Tags";
            this.btnApplyTags.UseVisualStyleBackColor = true;
            this.btnApplyTags.Click += new System.EventHandler(this.btnApplyTags_Click);
            //
            // btnCancel
            //
            this.btnCancel.Location = new System.Drawing.Point(145, 440);
            this.btnCancel.Name = "btnCancel";
            this.btnCancel.Size = new System.Drawing.Size(120, 35);
            this.btnCancel.TabIndex = 5;
            this.btnCancel.Text = "Cancel";
            this.btnCancel.UseVisualStyleBackColor = true;
            this.btnCancel.Click += new System.EventHandler(this.btnCancel_Click);
            //
            // ClinicalEntityTaggingForm
            //
            this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 13F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(484, 491);
            this.Controls.Add(this.btnCancel);
            this.Controls.Add(this.btnApplyTags);
            this.Controls.Add(this.groupBox3);
            this.Controls.Add(this.groupBox2);
            this.Controls.Add(this.groupBox1);
            this.Controls.Add(this.lblTaskCount);
            this.FormBorderStyle = System.Windows.Forms.FormBorderStyle.FixedDialog;
            this.MaximizeBox = false;
            this.MinimizeBox = false;
            this.Name = "ClinicalEntityTaggingForm";
            this.StartPosition = System.Windows.Forms.FormStartPosition.CenterScreen;
            this.Text = "Tag Tasks with Clinical Entities";
            this.groupBox1.ResumeLayout(false);
            this.groupBox2.ResumeLayout(false);
            this.groupBox3.ResumeLayout(false);
            this.ResumeLayout(false);
            this.PerformLayout();

        }

        #endregion

        private System.Windows.Forms.Label lblTaskCount;
        private System.Windows.Forms.GroupBox groupBox1;
        private System.Windows.Forms.CheckedListBox clbSites;
        private System.Windows.Forms.GroupBox groupBox2;
        private System.Windows.Forms.CheckedListBox clbAmendments;
        private System.Windows.Forms.GroupBox groupBox3;
        private System.Windows.Forms.CheckedListBox clbCohorts;
        private System.Windows.Forms.Button btnApplyTags;
        private System.Windows.Forms.Button btnCancel;
    }
}
