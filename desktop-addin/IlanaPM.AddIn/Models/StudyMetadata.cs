using System;
using System.Collections.Generic;

namespace IlanaPM.AddIn.Models
{
    /// <summary>
    /// Study-level metadata required for accurate intelligence benchmarking
    ///
    /// CRITICAL: Benchmarks vary dramatically by phase, therapeutic area, and country:
    /// - Phase I timelines ≠ Phase III timelines (e.g., IRB: 30 days vs 90 days)
    /// - Oncology ≠ Cardiology timelines (different approval processes)
    /// - US/FDA ≠ EU/EMA ≠ Japan/PMDA (different regulatory requirements)
    ///
    /// This metadata is:
    /// - Collected during template generation (automatically saved)
    /// - Required for intelligence validation (automatically loaded)
    /// - Stored in MS Project custom fields (Text1-3 in ProjectSummaryTask)
    /// - Sent to backend API for benchmark matching
    /// </summary>
    public class StudyMetadata
    {
        /// <summary>
        /// Study phase: "Phase I", "Phase II", "Phase III", "Phase IV"
        /// Stored in: ProjectSummaryTask.Text1
        /// </summary>
        public string Phase { get; set; }

        /// <summary>
        /// Therapeutic area: "Oncology", "Cardiology", "Neurology", etc.
        /// Stored in: ProjectSummaryTask.Text2
        /// </summary>
        public string TherapeuticArea { get; set; }

        /// <summary>
        /// Primary country/authority: "US", "EU", "JP", "CA", "GB", etc.
        /// Stored in: ProjectSummaryTask.Text3
        /// </summary>
        public string PrimaryCountry { get; set; }

        /// <summary>
        /// Additional countries (optional)
        /// Stored in: ProjectSummaryTask.Text4 as comma-separated string
        /// </summary>
        public List<string> AdditionalCountries { get; set; }

        /// <summary>
        /// Study name (optional, uses project name if not specified)
        /// </summary>
        public string StudyName { get; set; }

        /// <summary>
        /// Study ID (optional)
        /// </summary>
        public string StudyId { get; set; }

        /// <summary>
        /// Source of metadata: "user_provided", "template_wizard", "project_file"
        /// </summary>
        public string MetadataSource { get; set; }

        public StudyMetadata()
        {
            AdditionalCountries = new List<string>();
            MetadataSource = "user_provided";
        }

        /// <summary>
        /// Validate that all required fields are populated
        /// </summary>
        /// <returns>True if Phase, TherapeuticArea, and PrimaryCountry are all populated</returns>
        public bool IsValid()
        {
            return !string.IsNullOrWhiteSpace(Phase) &&
                   !string.IsNullOrWhiteSpace(TherapeuticArea) &&
                   !string.IsNullOrWhiteSpace(PrimaryCountry);
        }

        /// <summary>
        /// Get validation error message if metadata is invalid
        /// </summary>
        /// <returns>Error message or null if valid</returns>
        public string GetValidationError()
        {
            if (string.IsNullOrWhiteSpace(Phase))
                return "Study phase is required";
            if (string.IsNullOrWhiteSpace(TherapeuticArea))
                return "Therapeutic area is required";
            if (string.IsNullOrWhiteSpace(PrimaryCountry))
                return "Primary country is required";
            return null;
        }

        /// <summary>
        /// Display string for UI
        /// </summary>
        /// <returns>Formatted string like "Phase III Oncology (US)"</returns>
        public override string ToString()
        {
            if (!IsValid())
                return "Incomplete metadata";

            string additional = AdditionalCountries != null && AdditionalCountries.Count > 0
                ? $" + {string.Join(", ", AdditionalCountries)}"
                : "";

            return $"{Phase} {TherapeuticArea} ({PrimaryCountry}{additional})";
        }
    }

    /// <summary>
    /// Request model for intelligence validation API
    /// Maps to backend POST /api/v1/intelligence/validate-core
    /// IMPORTANT: Uses snake_case to match Python backend API
    /// </summary>
    public class IntelligenceValidationRequest
    {
        public object timeline { get; set; }  // Extracted timeline data
        public string org_id { get; set; }
        public string tier { get; set; }
        public StudyMetadataDTO study_metadata { get; set; }  // Required for accurate benchmarking

        public IntelligenceValidationRequest()
        {
            tier = "core";  // Default tier
        }
    }

    /// <summary>
    /// DTO (Data Transfer Object) for sending study metadata to API
    /// Matches backend StudyMetadata model
    /// </summary>
    public class StudyMetadataDTO
    {
        public string phase { get; set; }
        public string therapeutic_area { get; set; }
        public string primary_country { get; set; }
        public List<string> additional_countries { get; set; }
        public string study_name { get; set; }
        public string study_id { get; set; }
        public string metadata_source { get; set; }

        /// <summary>
        /// Create DTO from StudyMetadata model
        /// </summary>
        public static StudyMetadataDTO FromModel(StudyMetadata metadata)
        {
            return new StudyMetadataDTO
            {
                phase = metadata.Phase,
                therapeutic_area = metadata.TherapeuticArea,
                primary_country = metadata.PrimaryCountry,
                additional_countries = metadata.AdditionalCountries,
                study_name = metadata.StudyName,
                study_id = metadata.StudyId,
                metadata_source = metadata.MetadataSource
            };
        }
    }

    /// <summary>
    /// Response from metadata validation API
    /// Maps to backend MetadataValidationResult model
    /// </summary>
    public class MetadataValidationResult
    {
        public bool is_valid { get; set; }
        public double coverage_percent { get; set; }
        public int benchmarks_available { get; set; }
        public int total_task_categories { get; set; }
        public List<string> missing_benchmarks { get; set; }
        public List<string> warnings { get; set; }
        public List<string> recommendations { get; set; }

        public MetadataValidationResult()
        {
            missing_benchmarks = new List<string>();
            warnings = new List<string>();
            recommendations = new List<string>();
        }
    }

    // ========================================================================
    // Intelligence Models - Variance Detection
    // Maps to backend intelligence/models.py
    // ========================================================================

    /// <summary>
    /// Industry benchmark data for a task
    /// </summary>
    public class BenchmarkData
    {
        public string task_id { get; set; }
        public string task_name { get; set; }
        public string category { get; set; }
        public int median_days { get; set; }
        public int p25_days { get; set; }
        public int p75_days { get; set; }
        public int typical_duration_days { get; set; }
        public int? sample_size { get; set; }
        public string source { get; set; }  // "WCG", "Emmes", "Tufts CSDD", etc.
        public string confidence { get; set; }  // "high", "medium", "low"
        public string data_quality { get; set; }
        public string last_updated { get; set; }
        public string country_code { get; set; }
        public string authority { get; set; }
        public string phase { get; set; }
        public string therapeutic_area { get; set; }
    }

    /// <summary>
    /// Variance metrics for a single task
    /// </summary>
    public class VarianceMetrics
    {
        public int absolute_days { get; set; }  // Difference in days (actual - benchmark)
        public double percentage { get; set; }  // Variance percentage
        public string severity { get; set; }  // "acceptable", "warning", "critical"
        public string classification { get; set; }  // "overestimate", "underestimate", "on_target"
    }

    /// <summary>
    /// Individual variance signal for a task
    /// </summary>
    public class VarianceSignal
    {
        public string task_id { get; set; }
        public string task_name { get; set; }
        public int customer_duration_days { get; set; }
        public BenchmarkData benchmark { get; set; }
        public VarianceMetrics variance { get; set; }
        public double financial_impact_usd { get; set; }
        public string explanation { get; set; }
        public List<string> recommendations { get; set; }

        public VarianceSignal()
        {
            recommendations = new List<string>();
        }
    }

    /// <summary>
    /// Summary statistics for variance report
    /// </summary>
    public class VarianceSummary
    {
        public int total_tasks_analyzed { get; set; }
        public int tasks_with_benchmarks { get; set; }
        public double benchmark_coverage_percent { get; set; }
        public int warning_count { get; set; }
        public int critical_count { get; set; }
        public int acceptable_count { get; set; }
        public double total_financial_impact_usd { get; set; }
        public double avg_variance_percent { get; set; }
        public int overestimate_count { get; set; }
        public int underestimate_count { get; set; }
    }

    /// <summary>
    /// Benchmark coverage statistics
    /// </summary>
    public class BenchmarkCoverage
    {
        public int tasks_matched { get; set; }
        public int tasks_unmatched { get; set; }
        public double coverage_percent { get; set; }
        public List<string> unmatched_task_names { get; set; }
        public Dictionary<string, int> match_quality { get; set; }  // {"exact": 10, "fuzzy": 5}

        public BenchmarkCoverage()
        {
            unmatched_task_names = new List<string>();
            match_quality = new Dictionary<string, int>();
        }
    }

    /// <summary>
    /// Complete variance detection report from intelligence API
    /// </summary>
    public class VarianceReport
    {
        public string tier { get; set; }  // "core", "calibrated", "enterprise"
        public string org_id { get; set; }
        public string analysis_timestamp { get; set; }
        public List<VarianceSignal> variance_signals { get; set; }
        public VarianceSummary summary { get; set; }
        public BenchmarkCoverage benchmark_coverage { get; set; }
        public Dictionary<string, object> configuration { get; set; }

        public VarianceReport()
        {
            variance_signals = new List<VarianceSignal>();
            summary = new VarianceSummary();
            benchmark_coverage = new BenchmarkCoverage();
            configuration = new Dictionary<string, object>();
        }
    }
}
