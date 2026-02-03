namespace IlanaPM.AddIn
{
    partial class SettingsForm
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
            this.lblApiUrl = new System.Windows.Forms.Label();
            this.txtApiUrl = new System.Windows.Forms.TextBox();
            this.btnTestConnection = new System.Windows.Forms.Button();
            this.lblWebhookUrl = new System.Windows.Forms.Label();
            this.txtWebhookUrl = new System.Windows.Forms.TextBox();
            this.chkAutoUpdate = new System.Windows.Forms.CheckBox();
            this.btnSave = new System.Windows.Forms.Button();
            this.btnCancel = new System.Windows.Forms.Button();
            this.SuspendLayout();
            //
            // lblApiUrl
            //
            this.lblApiUrl.AutoSize = true;
            this.lblApiUrl.Location = new System.Drawing.Point(20, 20);
            this.lblApiUrl.Name = "lblApiUrl";
            this.lblApiUrl.Size = new System.Drawing.Size(100, 15);
            this.lblApiUrl.TabIndex = 0;
            this.lblApiUrl.Text = "API Base URL:";
            //
            // txtApiUrl
            //
            this.txtApiUrl.Location = new System.Drawing.Point(20, 40);
            this.txtApiUrl.Name = "txtApiUrl";
            this.txtApiUrl.Size = new System.Drawing.Size(400, 23);
            this.txtApiUrl.TabIndex = 1;
            //
            // btnTestConnection
            //
            this.btnTestConnection.Location = new System.Drawing.Point(430, 40);
            this.btnTestConnection.Name = "btnTestConnection";
            this.btnTestConnection.Size = new System.Drawing.Size(100, 23);
            this.btnTestConnection.TabIndex = 2;
            this.btnTestConnection.Text = "Test Connection";
            this.btnTestConnection.UseVisualStyleBackColor = true;
            this.btnTestConnection.Click += new System.EventHandler(this.btnTestConnection_Click);
            //
            // lblWebhookUrl
            //
            this.lblWebhookUrl.AutoSize = true;
            this.lblWebhookUrl.Location = new System.Drawing.Point(20, 80);
            this.lblWebhookUrl.Name = "lblWebhookUrl";
            this.lblWebhookUrl.Size = new System.Drawing.Size(150, 15);
            this.lblWebhookUrl.TabIndex = 3;
            this.lblWebhookUrl.Text = "Teams Webhook URL:";
            //
            // txtWebhookUrl
            //
            this.txtWebhookUrl.Location = new System.Drawing.Point(20, 100);
            this.txtWebhookUrl.Name = "txtWebhookUrl";
            this.txtWebhookUrl.Size = new System.Drawing.Size(510, 23);
            this.txtWebhookUrl.TabIndex = 4;
            //
            // chkAutoUpdate
            //
            this.chkAutoUpdate.AutoSize = true;
            this.chkAutoUpdate.Location = new System.Drawing.Point(20, 140);
            this.chkAutoUpdate.Name = "chkAutoUpdate";
            this.chkAutoUpdate.Size = new System.Drawing.Size(200, 19);
            this.chkAutoUpdate.TabIndex = 5;
            this.chkAutoUpdate.Text = "Enable automatic update checks";
            this.chkAutoUpdate.UseVisualStyleBackColor = true;
            //
            // btnSave
            //
            this.btnSave.Location = new System.Drawing.Point(374, 180);
            this.btnSave.Name = "btnSave";
            this.btnSave.Size = new System.Drawing.Size(75, 23);
            this.btnSave.TabIndex = 6;
            this.btnSave.Text = "Save";
            this.btnSave.UseVisualStyleBackColor = true;
            this.btnSave.Click += new System.EventHandler(this.btnSave_Click);
            //
            // btnCancel
            //
            this.btnCancel.Location = new System.Drawing.Point(455, 180);
            this.btnCancel.Name = "btnCancel";
            this.btnCancel.Size = new System.Drawing.Size(75, 23);
            this.btnCancel.TabIndex = 7;
            this.btnCancel.Text = "Cancel";
            this.btnCancel.UseVisualStyleBackColor = true;
            this.btnCancel.Click += new System.EventHandler(this.btnCancel_Click);
            //
            // SettingsForm
            //
            this.ClientSize = new System.Drawing.Size(550, 220);
            this.Controls.Add(this.btnCancel);
            this.Controls.Add(this.btnSave);
            this.Controls.Add(this.chkAutoUpdate);
            this.Controls.Add(this.txtWebhookUrl);
            this.Controls.Add(this.lblWebhookUrl);
            this.Controls.Add(this.btnTestConnection);
            this.Controls.Add(this.txtApiUrl);
            this.Controls.Add(this.lblApiUrl);
            this.Name = "SettingsForm";
            this.StartPosition = System.Windows.Forms.FormStartPosition.CenterScreen;
            this.Text = "Ilana PM - Settings";
            this.ResumeLayout(false);
            this.PerformLayout();
        }

        #endregion

        private System.Windows.Forms.Label lblApiUrl;
        private System.Windows.Forms.TextBox txtApiUrl;
        private System.Windows.Forms.Button btnTestConnection;
        private System.Windows.Forms.Label lblWebhookUrl;
        private System.Windows.Forms.TextBox txtWebhookUrl;
        private System.Windows.Forms.CheckBox chkAutoUpdate;
        private System.Windows.Forms.Button btnSave;
        private System.Windows.Forms.Button btnCancel;
    }
}
