namespace IlanaPM.AddIn
{
    partial class IlanaPMRibbon : Microsoft.Office.Tools.Ribbon.RibbonBase
    {
        private System.ComponentModel.IContainer components = null;

        public IlanaPMRibbon()
            : base(Globals.Factory.GetRibbonFactory())
        {
            InitializeComponent();
        }

        protected override void Dispose(bool disposing)
        {
            if (disposing && (components != null))
            {
                components.Dispose();
            }
            base.Dispose(disposing);
        }

        #region Component Designer generated code                                                    

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

            this.tab1.ControlId.ControlIdType =
Microsoft.Office.Tools.Ribbon.RibbonControlIdType.Office;
            this.tab1.Groups.Add(this.group1);
            this.tab1.Label = "TabAddIns";
            this.tab1.Name = "tab1";

            this.group1.Items.Add(this.btnValidate);
            this.group1.Items.Add(this.btnMLAdvisory);
            this.group1.Items.Add(this.btnExportTeams);
            this.group1.Items.Add(this.btnViewReport);
            this.group1.Items.Add(this.btnSettings);
            this.group1.Label = "Ilana PM";
            this.group1.Name = "group1";

            this.btnValidate.ControlSize =
Microsoft.Office.Core.RibbonControlSize.RibbonControlSizeLarge;
            this.btnValidate.Label = "Validate Timeline";
            this.btnValidate.Name = "btnValidate";
            this.btnValidate.ShowImage = true;
            this.btnValidate.OfficeImageId = "ReviewAcceptChange";
            this.btnValidate.Click += new
Microsoft.Office.Tools.Ribbon.RibbonControlEventHandler(this.btnValidate_Click);

            this.btnMLAdvisory.ControlSize =
Microsoft.Office.Core.RibbonControlSize.RibbonControlSizeLarge;
            this.btnMLAdvisory.Label = "ML Advisory";
            this.btnMLAdvisory.Name = "btnMLAdvisory";
            this.btnMLAdvisory.ShowImage = true;
            this.btnMLAdvisory.OfficeImageId = "ChartInsert";
            this.btnMLAdvisory.Click += new
Microsoft.Office.Tools.Ribbon.RibbonControlEventHandler(this.btnMLAdvisory_Click);

            this.btnExportTeams.ControlSize =
Microsoft.Office.Core.RibbonControlSize.RibbonControlSizeLarge;
            this.btnExportTeams.Label = "Export to Teams";
            this.btnExportTeams.Name = "btnExportTeams";
            this.btnExportTeams.ShowImage = true;
            this.btnExportTeams.OfficeImageId = "ExportExcel";
            this.btnExportTeams.Click += new
Microsoft.Office.Tools.Ribbon.RibbonControlEventHandler(this.btnExportTeams_Click);

            this.btnViewReport.ControlSize =
Microsoft.Office.Core.RibbonControlSize.RibbonControlSizeLarge;
            this.btnViewReport.Label = "View Report";
            this.btnViewReport.Name = "btnViewReport";
            this.btnViewReport.ShowImage = true;
            this.btnViewReport.OfficeImageId = "TableOfContentsGallery";
            this.btnViewReport.Click += new
Microsoft.Office.Tools.Ribbon.RibbonControlEventHandler(this.btnViewReport_Click);

            this.btnSettings.ControlSize =
Microsoft.Office.Core.RibbonControlSize.RibbonControlSizeLarge;
            this.btnSettings.Label = "Settings";
            this.btnSettings.Name = "btnSettings";
            this.btnSettings.ShowImage = true;
            this.btnSettings.OfficeImageId = "ApplicationOptionsDialog";
            this.btnSettings.Click += new
Microsoft.Office.Tools.Ribbon.RibbonControlEventHandler(this.btnSettings_Click);

            this.Name = "IlanaPMRibbon";
            this.RibbonType = "Microsoft.Project.Project";
            this.Tabs.Add(this.tab1);
            this.Load += new
Microsoft.Office.Tools.Ribbon.RibbonUIEventHandler(this.IlanaPMRibbon_Load);
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