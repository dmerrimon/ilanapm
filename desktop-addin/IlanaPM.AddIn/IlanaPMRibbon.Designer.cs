namespace IlanaPM.AddIn
{
    partial class IlanaPMRibbon : Microsoft.Office.Tools.Ribbon.RibbonBase
    {
        /// <summary>                                                                                                                                                                                             
        /// Required designer variable.                                                                                                                                                                           
        /// </summary>                                                                                                                                                                                            
        private System.ComponentModel.IContainer components = null;

        public IlanaPMRibbon()
            : base(Globals.Factory.GetRibbonFactory())
        {
            InitializeComponent();
        }

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

        #region Component Designer generated code                                                                                                                                                                 

        /// <summary>                                                                                                                                                                                             
        /// Required method for Designer support - do not modify                                                                                                                                                  
        /// the contents of this method with the code editor.                                                                                                                                                     
        /// </summary>                                                                                                                                                                                            
        private void InitializeComponent()
        {
            this.tab1 = this.Factory.CreateRibbonTab();
            this.group1 = this.Factory.CreateRibbonGroup();
            this.btnValidate = this.Factory.CreateRibbonButton();
            this.btnMLAdvisory = this.Factory.CreateRibbonButton();
            this.btnExportTeams = this.Factory.CreateRibbonButton();
            this.btnViewReport = this.Factory.CreateRibbonButton();
            this.btnSettings = this.Factory.CreateRibbonButton();
            this.tab1.SuspendLayout();
            this.group1.SuspendLayout();
            this.SuspendLayout();
            //                                                                                                                                                                                                    
            // tab1                                                                                                                                                                                               
            //                                                                                                                                                                                                    
            this.tab1.ControlId.ControlIdType = Microsoft.Office.Tools.Ribbon.RibbonControlIdType.Office;
            this.tab1.Groups.Add(this.group1);
            this.tab1.Label = "TabAddIns";
            this.tab1.Name = "tab1";
            //                                                                                                                                                                                                    
            // group1                                                                                                                                                                                             
            //                                                                                                                                                                                                    
            this.group1.Items.Add(this.btnValidate);
            this.group1.Items.Add(this.btnMLAdvisory);
            this.group1.Items.Add(this.btnExportTeams);
            this.group1.Items.Add(this.btnViewReport);
            this.group1.Items.Add(this.btnSettings);
            this.group1.Label = "Ilana PM";
            this.group1.Name = "group1";
            //                                                                                                                                                                                                    
            // btnValidate                                                                                                                                                                                        
            //                                                                                                                                                                                                    
            this.btnValidate.ControlSize = Microsoft.Office.Core.RibbonControlSize.RibbonControlSizeLarge;
            this.btnValidate.Label = "Validate Timeline";
            this.btnValidate.Name = "btnValidate";
            this.btnValidate.ShowImage = true;
            this.btnValidate.Click += new Microsoft.Office.Tools.Ribbon.RibbonControlEventHandler(this.btnValidate_Click);
            //                                                                                                                                                                                                    
            // btnMLAdvisory                                                                                                                                                                                      
            //                                                                                                                                                                                                    
            this.btnMLAdvisory.ControlSize = Microsoft.Office.Core.RibbonControlSize.RibbonControlSizeLarge;
            this.btnMLAdvisory.Label = "ML Advisory";
            this.btnMLAdvisory.Name = "btnMLAdvisory";
            this.btnMLAdvisory.ShowImage = true;
            this.btnMLAdvisory.Click += new Microsoft.Office.Tools.Ribbon.RibbonControlEventHandler(this.btnMLAdvisory_Click);
            //                                                                                                                                                                                                    
            // btnExportTeams                                                                                                                                                                                     
            //                                                                                                                                                                                                    
            this.btnExportTeams.ControlSize = Microsoft.Office.Core.RibbonControlSize.RibbonControlSizeLarge;
            this.btnExportTeams.Label = "Export to Teams";
            this.btnExportTeams.Name = "btnExportTeams";
            this.btnExportTeams.ShowImage = true;
            this.btnExportTeams.Click += new Microsoft.Office.Tools.Ribbon.RibbonControlEventHandler(this.btnExportTeams_Click);
            //                                                                                                                                                                                                    
            // btnViewReport                                                                                                                                                                                      
            //                                                                                                                                                                                                    
            this.btnViewReport.ControlSize = Microsoft.Office.Core.RibbonControlSize.RibbonControlSizeLarge;
            this.btnViewReport.Label = "View Report";
            this.btnViewReport.Name = "btnViewReport";
            this.btnViewReport.ShowImage = true;
            this.btnViewReport.Click += new Microsoft.Office.Tools.Ribbon.RibbonControlEventHandler(this.btnViewReport_Click);
            //                                                                                                                                                                                                    
            // btnSettings                                                                                                                                                                                        
            //                                                                                                                                                                                                    
            this.btnSettings.ControlSize = Microsoft.Office.Core.RibbonControlSize.RibbonControlSizeLarge;
            this.btnSettings.Label = "Settings";
            this.btnSettings.Name = "btnSettings";
            this.btnSettings.ShowImage = true;
            this.btnSettings.Click += new Microsoft.Office.Tools.Ribbon.RibbonControlEventHandler(this.btnSettings_Click);
            //                                                                                                                                                                                                    
            // IlanaPMRibbon                                                                                                                                                                                      
            //                                                                                                                                                                                                    
            this.Name = "IlanaPMRibbon";
            this.RibbonType = "Microsoft.Project.Project";
            this.Tabs.Add(this.tab1);
            this.Load += new Microsoft.Office.Tools.Ribbon.RibbonUIEventHandler(this.IlanaPMRibbon_Load);
            this.tab1.ResumeLayout(false);
            this.tab1.PerformLayout();
            this.group1.ResumeLayout(false);
            this.group1.PerformLayout();
            this.ResumeLayout(false);

        }

        #endregion

        internal Microsoft.Office.Tools.Ribbon.RibbonTab tab1;
        internal Microsoft.Office.Tools.Ribbon.RibbonGroup group1;
        internal Microsoft.Office.Tools.Ribbon.RibbonButton btnValidate;
        internal Microsoft.Office.Tools.Ribbon.RibbonButton btnMLAdvisory;
        internal Microsoft.Office.Tools.Ribbon.RibbonButton btnExportTeams;
        internal Microsoft.Office.Tools.Ribbon.RibbonButton btnViewReport;
        internal Microsoft.Office.Tools.Ribbon.RibbonButton btnSettings;
    }

    partial class ThisRibbonCollection
    {
        internal IlanaPMRibbon IlanaPMRibbon
        {
            get { return this.GetRibbon<IlanaPMRibbon>(); }
        }
    }
}