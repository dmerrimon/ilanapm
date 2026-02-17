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
            this.grpReports = this.Factory.CreateRibbonGroup();

            // Group 1: 2 dropdowns + 2 standalone buttons
            this.btnMultiCountry = this.Factory.CreateRibbonButton();

            this.menuClinical = this.Factory.CreateRibbonMenu();
            this.btnClinicalProjectManager = this.Factory.CreateRibbonButton();
            this.btnEssentialDocs = this.Factory.CreateRibbonButton();

            this.menuAnalysis = this.Factory.CreateRibbonMenu();
            this.btnValidate = this.Factory.CreateRibbonButton();
            this.btnCriticalPath = this.Factory.CreateRibbonButton();
            this.btnUploadTracker = this.Factory.CreateRibbonButton();
            this.btnLeadershipDashboard = this.Factory.CreateRibbonButton();

            this.btnSettings = this.Factory.CreateRibbonButton();

            // Group 2: Reports - 2 standalone report buttons (Site Status & Site Activation REMOVED 2026-02-17)
            this.btnEssentialDocsCompliance = this.Factory.CreateRibbonButton();
            this.btnStudyTimelineStatus = this.Factory.CreateRibbonButton();

            // DEPRECATED: Keep for 1 release but hide from UI
            this.btnLoadTemplate = this.Factory.CreateRibbonButton();
            this.btnTemplateManager = this.Factory.CreateRibbonButton();
            this.btnClinicalSetup = this.Factory.CreateRibbonButton();

            this.tab1.SuspendLayout();
            this.group1.SuspendLayout();
            this.grpReports.SuspendLayout();
            this.SuspendLayout();

            //
            // tab1
            //
            this.tab1.ControlId.ControlIdType = Microsoft.Office.Tools.Ribbon.RibbonControlIdType.Office;
            this.tab1.Groups.Add(this.group1);
            this.tab1.Groups.Add(this.grpReports);
            this.tab1.Label = "TabAddIns";
            this.tab1.Name = "tab1";

            //
            // group1 - 2 dropdowns + 2 standalone buttons
            //
            this.group1.Items.Add(this.menuClinical);
            this.group1.Items.Add(this.menuAnalysis);
            this.group1.Items.Add(this.btnMultiCountry);
            this.group1.Items.Add(this.btnSettings);
            this.group1.Label = "Ilana PM";
            this.group1.Name = "group1";

            //
            // btnMultiCountry (standalone button)
            //
            this.btnMultiCountry.ControlSize = Microsoft.Office.Core.RibbonControlSize.RibbonControlSizeLarge;
            this.btnMultiCountry.Label = "Multi-Country\nCalculator";
            this.btnMultiCountry.Name = "btnMultiCountry";
            this.btnMultiCountry.ShowImage = true;
            this.btnMultiCountry.Image = Properties.Resources.multicountry;
            this.btnMultiCountry.Click += new Microsoft.Office.Tools.Ribbon.RibbonControlEventHandler(this.btnMultiCountry_Click);

            //
            // menuClinical - Updated with Clinical Project Manager
            //
            this.menuClinical.ControlSize = Microsoft.Office.Core.RibbonControlSize.RibbonControlSizeLarge;
            this.menuClinical.Items.Add(this.btnClinicalProjectManager);
            // this.menuClinical.Items.Add(this.btnEssentialDocs);  // REMOVED - not working yet
            this.menuClinical.Label = "Clinical";
            this.menuClinical.Name = "menuClinical";
            this.menuClinical.ShowImage = true;
            this.menuClinical.Image = Properties.Resources.clinical;

            //
            // btnClinicalProjectManager (NEW - Unified wizard)
            //
            this.btnClinicalProjectManager.Label = "Clinical Project Manager";
            this.btnClinicalProjectManager.Name = "btnClinicalProjectManager";
            this.btnClinicalProjectManager.ShowImage = true;
            this.btnClinicalProjectManager.OfficeImageId = "ProjectManagement";
            this.btnClinicalProjectManager.Click += new Microsoft.Office.Tools.Ribbon.RibbonControlEventHandler(this.btnClinicalProjectManager_Click);

            //
            // btnEssentialDocs (inside Clinical menu) - HIDDEN FOR NOW
            //
            this.btnEssentialDocs.Label = "Essential Documents Tracker";
            this.btnEssentialDocs.Name = "btnEssentialDocs";
            this.btnEssentialDocs.ShowImage = true;
            this.btnEssentialDocs.OfficeImageId = "FileFolderDocuments";
            this.btnEssentialDocs.Visible = false;  // HIDDEN - not working yet
            this.btnEssentialDocs.Click += new Microsoft.Office.Tools.Ribbon.RibbonControlEventHandler(this.btnEssentialDocs_Click);

            //
            // menuAnalysis
            //
            this.menuAnalysis.ControlSize = Microsoft.Office.Core.RibbonControlSize.RibbonControlSizeLarge;
            this.menuAnalysis.Items.Add(this.btnValidate);
            this.menuAnalysis.Items.Add(this.btnCriticalPath);
            this.menuAnalysis.Items.Add(this.btnUploadTracker);
            this.menuAnalysis.Items.Add(this.btnLeadershipDashboard);
            this.menuAnalysis.Label = "Analysis";
            this.menuAnalysis.Name = "menuAnalysis";
            this.menuAnalysis.ShowImage = true;
            this.menuAnalysis.Image = Properties.Resources.analysis;

            //
            // btnValidate (inside Analysis menu)
            //
            this.btnValidate.Label = "Validate Timeline";
            this.btnValidate.Name = "btnValidate";
            this.btnValidate.ShowImage = true;
            this.btnValidate.OfficeImageId = "ReviewAcceptChange";
            this.btnValidate.Click += new Microsoft.Office.Tools.Ribbon.RibbonControlEventHandler(this.btnValidate_Click);

            //
            // btnCriticalPath (inside Analysis menu)
            //
            this.btnCriticalPath.Label = "Critical Path";
            this.btnCriticalPath.Name = "btnCriticalPath";
            this.btnCriticalPath.ShowImage = true;
            this.btnCriticalPath.OfficeImageId = "DiagramTargetInsertClassic";
            this.btnCriticalPath.Click += new Microsoft.Office.Tools.Ribbon.RibbonControlEventHandler(this.btnCriticalPath_Click);

            //
            // btnUploadTracker (inside Analysis menu) - PHASE 5
            //
            this.btnUploadTracker.Label = "Upload Tracker";
            this.btnUploadTracker.Name = "btnUploadTracker";
            this.btnUploadTracker.ShowImage = true;
            this.btnUploadTracker.OfficeImageId = "ImportExcel";
            this.btnUploadTracker.Click += new Microsoft.Office.Tools.Ribbon.RibbonControlEventHandler(this.btnUploadTracker_Click);

            //
            // btnLeadershipDashboard (inside Analysis menu) - PHASE 5B
            //
            this.btnLeadershipDashboard.Label = "Leadership Dashboard";
            this.btnLeadershipDashboard.Name = "btnLeadershipDashboard";
            this.btnLeadershipDashboard.ShowImage = true;
            this.btnLeadershipDashboard.OfficeImageId = "ViewDashboard";
            this.btnLeadershipDashboard.Click += new Microsoft.Office.Tools.Ribbon.RibbonControlEventHandler(this.btnLeadershipDashboard_Click);

            //
            // grpReports - Reports Group (Site Status & Site Activation REMOVED 2026-02-17)
            //
            // All report buttons removed - focus on tracker uploads instead
            // this.grpReports.Items.Add(this.btnEssentialDocsCompliance);  // REMOVED - focus on Essential Documents Tracker instead
            // this.grpReports.Items.Add(this.btnStudyTimelineStatus);  // REMOVED - not working yet
            this.grpReports.Label = "Reports";
            this.grpReports.Name = "grpReports";

            // btnSiteStatusDashboard REMOVED 2026-02-17
            // btnSiteActivationTimeline REMOVED 2026-02-17

            //
            // btnEssentialDocsCompliance (standalone in Reports group) - HIDDEN FOR NOW
            //
            this.btnEssentialDocsCompliance.ControlSize = Microsoft.Office.Core.RibbonControlSize.RibbonControlSizeLarge;
            this.btnEssentialDocsCompliance.Label = "Essential Docs\nCompliance";
            this.btnEssentialDocsCompliance.Name = "btnEssentialDocsCompliance";
            this.btnEssentialDocsCompliance.ShowImage = true;
            this.btnEssentialDocsCompliance.OfficeImageId = "FileFolderDocuments";
            this.btnEssentialDocsCompliance.Visible = false;  // HIDDEN - focus on Essential Documents Tracker instead
            this.btnEssentialDocsCompliance.Click += new Microsoft.Office.Tools.Ribbon.RibbonControlEventHandler(this.btnEssentialDocsCompliance_Click);

            //
            // btnStudyTimelineStatus (standalone in Reports group) - HIDDEN FOR NOW
            //
            this.btnStudyTimelineStatus.ControlSize = Microsoft.Office.Core.RibbonControlSize.RibbonControlSizeLarge;
            this.btnStudyTimelineStatus.Label = "Study Timeline\nStatus";
            this.btnStudyTimelineStatus.Name = "btnStudyTimelineStatus";
            this.btnStudyTimelineStatus.ShowImage = true;
            this.btnStudyTimelineStatus.OfficeImageId = "DiagramGanttInsertClassic";
            this.btnStudyTimelineStatus.Visible = false;  // HIDDEN - not working yet
            this.btnStudyTimelineStatus.Click += new Microsoft.Office.Tools.Ribbon.RibbonControlEventHandler(this.btnStudyTimelineStatus_Click);

            //
            // btnSettings (standalone)
            //
            this.btnSettings.ControlSize = Microsoft.Office.Core.RibbonControlSize.RibbonControlSizeLarge;
            this.btnSettings.Label = "Settings";
            this.btnSettings.Name = "btnSettings";
            this.btnSettings.ShowImage = true;
            this.btnSettings.Image = Properties.Resources.settings;
            this.btnSettings.Click += new Microsoft.Office.Tools.Ribbon.RibbonControlEventHandler(this.btnSettings_Click);

            //
            // DEPRECATED buttons - hidden but kept for backward compatibility
            //
            this.btnLoadTemplate.ControlSize = Microsoft.Office.Core.RibbonControlSize.RibbonControlSizeLarge;
            this.btnLoadTemplate.Label = "Load Template (Deprecated)";
            this.btnLoadTemplate.Name = "btnLoadTemplate";
            this.btnLoadTemplate.ShowImage = true;
            this.btnLoadTemplate.OfficeImageId = "FileNewDefault";
            this.btnLoadTemplate.Visible = false;  // HIDDEN - use Clinical Project Manager instead
            this.btnLoadTemplate.Click += new Microsoft.Office.Tools.Ribbon.RibbonControlEventHandler(this.btnLoadTemplate_Click);

            this.btnTemplateManager.Label = "Template Manager (Deprecated)";
            this.btnTemplateManager.Name = "btnTemplateManager";
            this.btnTemplateManager.Visible = false;  // HIDDEN - use Clinical Project Manager instead

            this.btnClinicalSetup.Label = "Clinical Setup";
            this.btnClinicalSetup.Name = "btnClinicalSetup";
            this.btnClinicalSetup.Visible = true;  // Required for Amendments/Cohorts (Tag Task feature)

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
            this.grpReports.ResumeLayout(false);
            this.grpReports.PerformLayout();
            this.ResumeLayout(false);
        }

        #endregion

        internal Microsoft.Office.Tools.Ribbon.RibbonTab tab1;
        internal Microsoft.Office.Tools.Ribbon.RibbonGroup group1;

        // Restructured: 2 dropdowns + 2 standalone buttons
        internal Microsoft.Office.Tools.Ribbon.RibbonButton btnMultiCountry;

        internal Microsoft.Office.Tools.Ribbon.RibbonMenu menuClinical;
        internal Microsoft.Office.Tools.Ribbon.RibbonButton btnClinicalProjectManager;
        internal Microsoft.Office.Tools.Ribbon.RibbonButton btnEssentialDocs;

        internal Microsoft.Office.Tools.Ribbon.RibbonMenu menuAnalysis;
        internal Microsoft.Office.Tools.Ribbon.RibbonButton btnValidate;
        internal Microsoft.Office.Tools.Ribbon.RibbonButton btnCriticalPath;
        internal Microsoft.Office.Tools.Ribbon.RibbonButton btnUploadTracker;
        internal Microsoft.Office.Tools.Ribbon.RibbonButton btnLeadershipDashboard;

        internal Microsoft.Office.Tools.Ribbon.RibbonButton btnSettings;

        // Reports Group (Site Status & Site Activation REMOVED 2026-02-17)
        internal Microsoft.Office.Tools.Ribbon.RibbonGroup grpReports;
        internal Microsoft.Office.Tools.Ribbon.RibbonButton btnEssentialDocsCompliance;
        internal Microsoft.Office.Tools.Ribbon.RibbonButton btnStudyTimelineStatus;

        // DEPRECATED: Kept for 1 release for backward compatibility (hidden)
        internal Microsoft.Office.Tools.Ribbon.RibbonButton btnLoadTemplate;
        internal Microsoft.Office.Tools.Ribbon.RibbonButton btnTemplateManager;
        internal Microsoft.Office.Tools.Ribbon.RibbonButton btnClinicalSetup;
    }

    partial class ThisRibbonCollection
    {
        internal IlanaPMRibbon IlanaPMRibbon
        {
            get { return this.GetRibbon<IlanaPMRibbon>(); }
        }
    }
}
