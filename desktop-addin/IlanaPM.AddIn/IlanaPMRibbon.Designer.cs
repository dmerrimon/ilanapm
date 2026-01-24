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
            this.btnCriticalPath = this.Factory.CreateRibbonButton();
            this.btnLoadTemplate = this.Factory.CreateRibbonButton();
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
            this.group1.Items.Add(this.btnCriticalPath);
            this.group1.Items.Add(this.btnLoadTemplate);
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
            this.btnValidate.OfficeImageId = "ReviewAcceptChange";
            this.btnValidate.Click += new Microsoft.Office.Tools.Ribbon.RibbonControlEventHandler(this.btnValidate_Click);

            //
            // btnCriticalPath
            //
            this.btnCriticalPath.ControlSize = Microsoft.Office.Core.RibbonControlSize.RibbonControlSizeLarge;
            this.btnCriticalPath.Label = "Critical Path";
            this.btnCriticalPath.Name = "btnCriticalPath";
            this.btnCriticalPath.ShowImage = true;
            this.btnCriticalPath.OfficeImageId = "DiagramTargetInsertClassic";
            this.btnCriticalPath.Click += new Microsoft.Office.Tools.Ribbon.RibbonControlEventHandler(this.btnCriticalPath_Click);

            //
            // btnLoadTemplate
            //
            this.btnLoadTemplate.ControlSize = Microsoft.Office.Core.RibbonControlSize.RibbonControlSizeLarge;
            this.btnLoadTemplate.Label = "Load Template";
            this.btnLoadTemplate.Name = "btnLoadTemplate";
            this.btnLoadTemplate.ShowImage = true;
            this.btnLoadTemplate.OfficeImageId = "FileNewDefault";
            this.btnLoadTemplate.Click += new Microsoft.Office.Tools.Ribbon.RibbonControlEventHandler(this.btnLoadTemplate_Click);

            //
            // btnSettings
            //
            this.btnSettings.ControlSize = Microsoft.Office.Core.RibbonControlSize.RibbonControlSizeLarge;
            this.btnSettings.Label = "Settings";
            this.btnSettings.Name = "btnSettings";
            this.btnSettings.ShowImage = true;
            this.btnSettings.OfficeImageId = "ApplicationOptionsDialog";
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
        internal Microsoft.Office.Tools.Ribbon.RibbonButton btnCriticalPath;
        internal Microsoft.Office.Tools.Ribbon.RibbonButton btnLoadTemplate;
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
