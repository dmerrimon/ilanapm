using System;
using System.Collections.Generic;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Windows.Forms;

namespace IlanaPM.AddIn
{
    /// <summary>
    /// Multi-Country Calculator - Helps PMs plan multi-country trial submission strategies
    /// PHASE 3: Proactive planning tool for comparing countries and optimizing submission timing
    /// </summary>
    public class MultiCountryCalculatorForm : Form
    {
        private Label lblTitle;
        private Label lblInstructions;
        private CheckedListBox lstCountries;
        private Button btnCalculate;
        private Button btnClose;
        private TextBox txtResults;
        private Panel pnlCountries;
        private Panel pnlResults;
        private Label lblLoading;

        private List<Models.CountrySummary> allCountries;
        private Dictionary<int, Models.CountrySummary> indexToCountryMap;

        public MultiCountryCalculatorForm()
        {
            InitializeComponents();
            LoadCountriesAsync();
        }

        private void InitializeComponents()
        {
            // Form settings
            this.Text = "Multi-Country Trial Calculator";
            this.Width = 900;
            this.Height = 700;
            this.StartPosition = FormStartPosition.CenterScreen;
            this.FormBorderStyle = FormBorderStyle.Sizable;
            this.MinimumSize = new Size(800, 600);

            // Title label
            lblTitle = new Label
            {
                Text = "Multi-Country Clinical Trial Calculator",
                Left = 20,
                Top = 15,
                Width = 840,
                Height = 30,
                Font = new Font(FontFamily.GenericSansSerif, 14, FontStyle.Bold),
                ForeColor = Color.FromArgb(0, 102, 204) // Blue
            };

            // Instructions label
            lblInstructions = new Label
            {
                Text = "Select the countries where you plan to conduct your clinical trial. The calculator will compare regulatory timelines, workflow complexity, and recommend an optimal submission strategy.",
                Left = 20,
                Top = 50,
                Width = 840,
                Height = 40,
                Font = new Font(FontFamily.GenericSansSerif, 9)
            };

            // Loading label (initially visible)
            lblLoading = new Label
            {
                Text = "Loading countries from backend...",
                Left = 20,
                Top = 110,
                Width = 840,
                Height = 30,
                Font = new Font(FontFamily.GenericSansSerif, 10, FontStyle.Italic),
                ForeColor = Color.Gray
            };

            // Country selection panel
            pnlCountries = new Panel
            {
                Left = 20,
                Top = 110,
                Width = 840,
                Height = 300,
                BorderStyle = BorderStyle.FixedSingle,
                Visible = false // Hidden until countries load
            };

            // Country checklist
            lstCountries = new CheckedListBox
            {
                Dock = DockStyle.Fill,
                CheckOnClick = true,
                Font = new Font(FontFamily.GenericMonospace, 9)
            };
            pnlCountries.Controls.Add(lstCountries);

            // Calculate button
            btnCalculate = new Button
            {
                Text = "Calculate Submission Strategy",
                Left = 20,
                Top = 420,
                Width = 200,
                Height = 35,
                Font = new Font(FontFamily.GenericSansSerif, 9, FontStyle.Bold),
                BackColor = Color.FromArgb(0, 102, 204),
                ForeColor = Color.White,
                FlatStyle = FlatStyle.Flat,
                Enabled = false
            };
            btnCalculate.Click += BtnCalculate_Click;

            // Results panel
            pnlResults = new Panel
            {
                Left = 20,
                Top = 465,
                Width = 840,
                Height = 150,
                BorderStyle = BorderStyle.FixedSingle,
                Anchor = AnchorStyles.Top | AnchorStyles.Bottom | AnchorStyles.Left | AnchorStyles.Right
            };

            // Results textbox
            txtResults = new TextBox
            {
                Multiline = true,
                ScrollBars = ScrollBars.Vertical,
                Dock = DockStyle.Fill,
                Font = new Font(FontFamily.GenericMonospace, 9),
                ReadOnly = true,
                BackColor = Color.White
            };
            pnlResults.Controls.Add(txtResults);

            // Close button
            btnClose = new Button
            {
                Text = "Close",
                Left = 780,
                Top = 625,
                Width = 80,
                Height = 30,
                Anchor = AnchorStyles.Bottom | AnchorStyles.Right
            };
            btnClose.Click += (s, e) => this.Close();

            // Add controls to form
            this.Controls.Add(lblTitle);
            this.Controls.Add(lblInstructions);
            this.Controls.Add(lblLoading);
            this.Controls.Add(pnlCountries);
            this.Controls.Add(btnCalculate);
            this.Controls.Add(pnlResults);
            this.Controls.Add(btnClose);

            // Initial message in results
            txtResults.Text = "Select countries above and click 'Calculate Submission Strategy' to see analysis.";
        }

        private async void LoadCountriesAsync()
        {
            try
            {
                System.Net.ServicePointManager.SecurityProtocol = System.Net.SecurityProtocolType.Tls12;

                lblLoading.Text = "Loading countries from backend...";
                lblLoading.Visible = true;

                // Fetch countries from backend
                var apiClient = new Services.ApiClient();
                allCountries = await apiClient.GetCountriesDetailedAsync();

                if (allCountries != null && allCountries.Count > 0)
                {
                    // Sort by country name
                    allCountries = allCountries.OrderBy(c => c.name).ToList();

                    // Populate checklist
                    indexToCountryMap = new Dictionary<int, Models.CountrySummary>();
                    int index = 0;

                    foreach (var country in allCountries)
                    {
                        string displayText = FormatCountryForList(country);
                        lstCountries.Items.Add(displayText);
                        indexToCountryMap[index] = country;
                        index++;
                    }

                    // Show countries panel, hide loading
                    lblLoading.Visible = false;
                    pnlCountries.Visible = true;
                    btnCalculate.Enabled = true;

                    txtResults.Text = $"Loaded {allCountries.Count} countries. Select countries above to compare submission strategies.";
                }
                else
                {
                    lblLoading.Text = "No countries available. Check backend connection.";
                    lblLoading.ForeColor = Color.Red;
                }
            }
            catch (Exception ex)
            {
                lblLoading.Text = $"Error loading countries: {ex.Message}";
                lblLoading.ForeColor = Color.Red;

                MessageBox.Show(
                    $"Failed to load country data from backend.\n\n{ex.Message}",
                    "Connection Error",
                    MessageBoxButtons.OK,
                    MessageBoxIcon.Error
                );
            }
        }

        private string FormatCountryForList(Models.CountrySummary country)
        {
            // Format: "Kenya (KE) - 3-Layer Sequential - Complexity: 4.0 - ~60 days"
            string timeline = country.total_timeline_days.HasValue
                ? $"~{country.total_timeline_days.Value} days"
                : "Variable";

            string workflow = FormatWorkflowType(country.workflow_type);

            return $"{country.name,-25} ({country.code}) - {workflow,-20} - Complexity: {country.complexity_level:F1} - {timeline}";
        }

        private string FormatWorkflowType(string workflowType)
        {
            // Make workflow types more readable
            return workflowType
                .Replace("_", " ")
                .Replace("parallel integrated", "Integrated")
                .Replace("parallel", "Parallel")
                .Replace("sequential", "Sequential")
                .Replace("three layer", "3-Layer")
                .Replace("four layer", "4-Layer")
                .Replace("three body", "3-Body")
                .Replace("four body", "4-Body");
        }

        private void BtnCalculate_Click(object sender, EventArgs e)
        {
            // Get selected countries
            var selectedCountries = new List<Models.CountrySummary>();

            for (int i = 0; i < lstCountries.CheckedIndices.Count; i++)
            {
                int index = lstCountries.CheckedIndices[i];
                if (indexToCountryMap.ContainsKey(index))
                {
                    selectedCountries.Add(indexToCountryMap[index]);
                }
            }

            if (selectedCountries.Count == 0)
            {
                txtResults.Text = "⚠ Please select at least one country to analyze.";
                return;
            }

            // Track calculation telemetry
            try
            {
                var telemetryService = Globals.ThisAddIn.TelemetryService;
                if (telemetryService != null)
                {
                    var properties = new System.Collections.Generic.Dictionary<string, object>
                    {
                        { "country_count", selectedCountries.Count },
                        { "countries", string.Join(",", selectedCountries.Select(c => c.code)) }
                    };
                    telemetryService.TrackEvent(Models.TelemetryEventType.ButtonClicked, properties);
                }
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Telemetry error in calculation: {ex.Message}");
            }

            // Generate analysis
            StringBuilder sb = new StringBuilder();
            sb.AppendLine("══════════════════════════════════════════════════════════════════════════════");
            sb.AppendLine("               MULTI-COUNTRY SUBMISSION STRATEGY ANALYSIS                     ");
            sb.AppendLine("══════════════════════════════════════════════════════════════════════════════");
            sb.AppendLine();

            sb.AppendLine($"Countries Selected: {selectedCountries.Count}");
            sb.AppendLine();

            // Section 1: Country Comparison
            sb.AppendLine("═══ COUNTRY COMPARISON ═══");
            sb.AppendLine();

            foreach (var country in selectedCountries.OrderBy(c => c.complexity_level))
            {
                sb.AppendLine($"▸ {country.name} ({country.code})");
                sb.AppendLine($"  Workflow: {country.workflow_description ?? FormatWorkflowType(country.workflow_type)}");
                sb.AppendLine($"  Complexity: {country.complexity_level:F1}/5.0");
                sb.AppendLine($"  Timeline: {(country.total_timeline_days.HasValue ? country.total_timeline_days.Value + " days" : "Variable")}");
                sb.AppendLine($"  Regulatory: {country.regulatory_authority_name} ({country.regulatory_authority_code})");
                sb.AppendLine($"  Ethics: {country.ethics_authority_name} ({country.ethics_authority_code})");

                if (country.additional_authorities != null && country.additional_authorities.Count > 0)
                {
                    sb.AppendLine($"  Additional: {string.Join(", ", country.additional_authorities.Select(a => a.ContainsKey("name") ? a["name"] : "Unknown"))}");
                }

                if (country.has_emergency_pathway || country.has_fast_track)
                {
                    List<string> pathways = new List<string>();
                    if (country.has_emergency_pathway) pathways.Add("Emergency");
                    if (country.has_fast_track) pathways.Add("Fast-Track");
                    sb.AppendLine($"  ⚡ Expedited Pathways: {string.Join(", ", pathways)}");
                }

                sb.AppendLine();
            }

            // Section 2: Complexity Analysis
            sb.AppendLine("═══ COMPLEXITY ANALYSIS ═══");
            sb.AppendLine();

            double avgComplexity = selectedCountries.Average(c => c.complexity_level);
            var mostComplex = selectedCountries.OrderByDescending(c => c.complexity_level).First();
            var leastComplex = selectedCountries.OrderBy(c => c.complexity_level).First();

            sb.AppendLine($"Average Complexity: {avgComplexity:F2}/5.0");
            sb.AppendLine($"Most Complex: {mostComplex.name} ({mostComplex.complexity_level:F1})");
            sb.AppendLine($"Least Complex: {leastComplex.name} ({leastComplex.complexity_level:F1})");
            sb.AppendLine();

            // Section 3: Timeline Estimation
            sb.AppendLine("═══ TIMELINE ESTIMATION ═══");
            sb.AppendLine();

            var countriesWithTimelines = selectedCountries.Where(c => c.total_timeline_days.HasValue).ToList();
            if (countriesWithTimelines.Count > 0)
            {
                int maxTimeline = countriesWithTimelines.Max(c => c.total_timeline_days.Value);
                int minTimeline = countriesWithTimelines.Min(c => c.total_timeline_days.Value);
                double avgTimeline = countriesWithTimelines.Average(c => c.total_timeline_days.Value);

                sb.AppendLine($"Longest Timeline: {maxTimeline} days ({countriesWithTimelines.First(c => c.total_timeline_days == maxTimeline).name})");
                sb.AppendLine($"Shortest Timeline: {minTimeline} days ({countriesWithTimelines.First(c => c.total_timeline_days == minTimeline).name})");
                sb.AppendLine($"Average Timeline: {avgTimeline:F0} days");
                sb.AppendLine();
            }

            // Section 4: Workflow Analysis
            sb.AppendLine("═══ WORKFLOW ANALYSIS ═══");
            sb.AppendLine();

            var parallelCountries = selectedCountries.Where(c => c.workflow_type.Contains("parallel")).ToList();
            var sequentialCountries = selectedCountries.Where(c => c.workflow_type.Contains("sequential")).ToList();
            var hybridCountries = selectedCountries.Where(c => c.workflow_type.Contains("hybrid") || c.workflow_type.Contains("flexible")).ToList();

            if (parallelCountries.Count > 0)
            {
                sb.AppendLine($"✓ Parallel Workflows ({parallelCountries.Count}): {string.Join(", ", parallelCountries.Select(c => c.code))}");
                sb.AppendLine("  → Regulatory and Ethics can run simultaneously");
            }

            if (sequentialCountries.Count > 0)
            {
                sb.AppendLine($"⚠ Sequential Workflows ({sequentialCountries.Count}): {string.Join(", ", sequentialCountries.Select(c => c.code))}");
                sb.AppendLine("  → Ethics approval required BEFORE regulatory submission");
            }

            if (hybridCountries.Count > 0)
            {
                sb.AppendLine($"⚡ Flexible Workflows ({hybridCountries.Count}): {string.Join(", ", hybridCountries.Select(c => c.code))}");
                sb.AppendLine("  → Can switch between parallel and sequential based on circumstances");
            }

            sb.AppendLine();

            // Section 5: Recommendations
            sb.AppendLine("═══ SUBMISSION STRATEGY RECOMMENDATIONS ═══");
            sb.AppendLine();

            if (selectedCountries.Count == 1)
            {
                var country = selectedCountries[0];
                sb.AppendLine($"Single-Country Trial ({country.name}):");
                sb.AppendLine($"• Follow {country.workflow_description ?? FormatWorkflowType(country.workflow_type).ToLower()}");
                sb.AppendLine($"• Estimated timeline: {(country.total_timeline_days.HasValue ? country.total_timeline_days.Value + " days" : "Variable")}");
                sb.AppendLine($"• Coordinate with {country.regulatory_authority_name} and {country.ethics_authority_name}");

                if (country.has_emergency_pathway || country.has_fast_track)
                {
                    sb.AppendLine($"• Consider expedited pathways if eligible");
                }
            }
            else
            {
                sb.AppendLine("Multi-Country Trial Recommendations:");
                sb.AppendLine();

                // Recommendation 1: Start with fastest/simplest
                if (leastComplex.complexity_level < avgComplexity - 0.5)
                {
                    sb.AppendLine($"1. START EARLY with {leastComplex.name} (Complexity: {leastComplex.complexity_level:F1})");
                    sb.AppendLine("   → Lowest complexity, good for initial regulatory interactions");
                    sb.AppendLine();
                }

                // Recommendation 2: Sequence complex countries
                if (mostComplex.complexity_level > 4.0)
                {
                    sb.AppendLine($"2. SEQUENCE {mostComplex.name} carefully (Complexity: {mostComplex.complexity_level:F1})");
                    sb.AppendLine("   → High complexity requires extra planning and resources");
                    sb.AppendLine();
                }

                // Recommendation 3: Parallel opportunities
                if (parallelCountries.Count >= 2)
                {
                    sb.AppendLine($"3. PARALLEL SUBMISSIONS for: {string.Join(", ", parallelCountries.Select(c => c.name))}");
                    sb.AppendLine("   → These countries allow simultaneous regulatory and ethics reviews");
                    sb.AppendLine();
                }

                // Recommendation 4: Critical path planning
                if (countriesWithTimelines.Count > 0)
                {
                    var critical = countriesWithTimelines.OrderByDescending(c => c.total_timeline_days.Value).Take(2).ToList();
                    sb.AppendLine($"4. CRITICAL PATH countries: {string.Join(", ", critical.Select(c => c.name))}");
                    sb.AppendLine($"   → Longest timelines ({string.Join(", ", critical.Select(c => c.total_timeline_days.Value + " days"))}), start these ASAP");
                    sb.AppendLine();
                }

                // Recommendation 5: Expedited pathways
                var expeditedCountries = selectedCountries.Where(c => c.has_emergency_pathway || c.has_fast_track).ToList();
                if (expeditedCountries.Count > 0)
                {
                    sb.AppendLine($"5. EXPEDITED PATHWAYS available in: {string.Join(", ", expeditedCountries.Select(c => c.name))}");
                    sb.AppendLine("   → Consider eligibility criteria for fast-track or emergency pathways");
                    sb.AppendLine();
                }
            }

            sb.AppendLine();
            sb.AppendLine("══════════════════════════════════════════════════════════════════════════════");

            txtResults.Text = sb.ToString();
        }
    }
}
