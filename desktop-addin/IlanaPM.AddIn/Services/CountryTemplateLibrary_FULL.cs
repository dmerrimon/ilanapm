using IlanaPM.AddIn.Models;
using System.Collections.Generic;

namespace IlanaPM.AddIn.Services
{
    /// <summary>
    /// Library of country-specific site task templates
    /// Provides starter templates for FDA, EMA (Germany), MHRA (UK), Health Canada, and PMDA (Japan)
    /// </summary>
    public static class CountryTemplateLibrary
    {
        #region USA (FDA) Site Startup Tasks

        public static SitePhaseTaskSet GetUSA_SiteStartup()
        {
            var taskSet = new SitePhaseTaskSet
            {
                phase_name = "Site Startup",
                phase_type = "Startup",
                country_code = "USA",
                country_name = "United States",
                regulatory_authority = "FDA"
            };

            // Phase 1: Essential Documents Collection (PARALLEL - Days 1-7)
            taskSet.tasks.AddRange(new List<TemplateTask>
            {
                new TemplateTask
                {
                    task_id = "USA-SS-001",
                    name = "Collect FDA Form 1572",
                    description = "Statement of Investigator",
                    duration_days = 5,
                    category = "Regulatory",
                    can_run_parallel = true,
                    execution_group = "Parallel-Essential-Docs",
                    parallel_group_id = 1,
                    required_documents = new List<string> { "FDA-1572" }
                },
                new TemplateTask
                {
                    task_id = "USA-SS-002",
                    name = "Collect PI CV and Medical License",
                    duration_days = 3,
                    category = "Regulatory",
                    can_run_parallel = true,
                    execution_group = "Parallel-Essential-Docs",
                    parallel_group_id = 1,
                    required_documents = new List<string> { "PI-CV" }
                },
                new TemplateTask
                {
                    task_id = "USA-SS-003",
                    name = "Collect Sub-Investigator CVs (IND only)",
                    duration_days = 5,
                    category = "Regulatory",
                    can_run_parallel = true,
                    execution_group = "Parallel-Essential-Docs",
                    parallel_group_id = 1,
                    required_documents = new List<string> { "SUB-INV-CV" }
                },
                new TemplateTask
                {
                    task_id = "USA-SS-004",
                    name = "Collect Financial Disclosure Forms (IND only)",
                    duration_days = 7,
                    category = "Regulatory",
                    can_run_parallel = true,
                    execution_group = "Parallel-Essential-Docs",
                    parallel_group_id = 1,
                    required_documents = new List<string> { "FIN-DISC" }
                },
                new TemplateTask
                {
                    task_id = "USA-SS-005",
                    name = "Collect Laboratory Certifications (CLIA)",
                    duration_days = 3,
                    category = "Lab",
                    can_run_parallel = true,
                    execution_group = "Parallel-Essential-Docs",
                    parallel_group_id = 1,
                    required_documents = new List<string> { "LAB-CERT" }
                },
                new TemplateTask
                {
                    task_id = "USA-SS-006",
                    name = "Collect Laboratory Reference Ranges",
                    duration_days = 2,
                    category = "Lab",
                    can_run_parallel = false,
                    execution_group = "Sequential-Lab-Docs",
                    predecessors = new List<string> { "USA-SS-005" },
                    required_documents = new List<string> { "LAB-CERT" }
                },
                new TemplateTask
                {
                    task_id = "USA-SS-007",
                    name = "Collect Protocol Signature Pages (all versions)",
                    duration_days = 3,
                    category = "Regulatory",
                    can_run_parallel = true,
                    execution_group = "Parallel-Essential-Docs",
                    parallel_group_id = 1,
                    required_documents = new List<string> { "PROTOCOL-SIG" }
                },
                new TemplateTask
                {
                    task_id = "USA-SS-008",
                    name = "Collect IBC documentation (if required)",
                    duration_days = 5,
                    category = "Regulatory",
                    can_run_parallel = true,
                    execution_group = "Parallel-Essential-Docs",
                    parallel_group_id = 1,
                    is_mandatory = false,
                    required_documents = new List<string> { "IBC-APPROVAL" }
                },
                new TemplateTask
                {
                    task_id = "USA-SS-009",
                    name = "Collect Approved Informed Consent Templates",
                    duration_days = 3,
                    category = "Regulatory",
                    can_run_parallel = true,
                    execution_group = "Parallel-Essential-Docs",
                    parallel_group_id = 1,
                    required_documents = new List<string> { "ICF-APPROVED" }
                },
                new TemplateTask
                {
                    task_id = "USA-SS-010",
                    name = "Collect Blank Approved CRFs",
                    duration_days = 2,
                    category = "Data",
                    can_run_parallel = true,
                    execution_group = "Parallel-Essential-Docs",
                    parallel_group_id = 1,
                    required_documents = new List<string> { "BLANK-CRF" }
                },
                new TemplateTask
                {
                    task_id = "USA-SS-011",
                    name = "Collect Final PSRL",
                    duration_days = 3,
                    category = "Regulatory",
                    can_run_parallel = true,
                    execution_group = "Parallel-Essential-Docs",
                    parallel_group_id = 1,
                    required_documents = new List<string> { "PSRL-FINAL" }
                },
                new TemplateTask
                {
                    task_id = "USA-SS-012",
                    name = "Review and Collect Investigator Brochure",
                    duration_days = 2,
                    category = "Regulatory",
                    can_run_parallel = true,
                    execution_group = "Parallel-Essential-Docs",
                    parallel_group_id = 1
                },
                new TemplateTask
                {
                    task_id = "USA-SS-013",
                    name = "Setup Site Regulatory Binder Structure",
                    duration_days = 1,
                    category = "Admin",
                    can_run_parallel = true,
                    execution_group = "Parallel-Essential-Docs",
                    parallel_group_id = 1
                }
            });

            // Phase 2: IRB Submission (SEQUENTIAL - Days 8-13)
            taskSet.tasks.AddRange(new List<TemplateTask>
            {
                new TemplateTask
                {
                    task_id = "USA-SS-014",
                    name = "Prepare IRB Submission Package",
                    duration_days = 5,
                    category = "Regulatory",
                    can_run_parallel = false,
                    execution_group = "Sequential-IRB-Prep",
                    predecessors = new List<string> { "USA-SS-001", "USA-SS-002", "USA-SS-007", "USA-SS-009" },
                    is_blocking = true
                },
                new TemplateTask
                {
                    task_id = "USA-SS-015",
                    name = "Internal Quality Check of IRB Package",
                    duration_days = 2,
                    category = "Regulatory",
                    can_run_parallel = false,
                    execution_group = "Sequential-IRB-Prep",
                    predecessors = new List<string> { "USA-SS-014" }
                },
                new TemplateTask
                {
                    task_id = "USA-SS-016",
                    name = "Submit Protocol to IRB",
                    duration_days = 1,
                    category = "Regulatory",
                    can_run_parallel = false,
                    execution_group = "Sequential-IRB-Review",
                    predecessors = new List<string> { "USA-SS-015" },
                    is_blocking = true,
                    requires_irb_approval = true
                },
                new TemplateTask
                {
                    task_id = "USA-SS-017",
                    name = "IRB Review and Approval",
                    duration_days = 30,
                    category = "Regulatory",
                    can_run_parallel = false,
                    execution_group = "Sequential-IRB-Review",
                    predecessors = new List<string> { "USA-SS-016" },
                    is_blocking = true,
                    requires_irb_approval = true,
                    required_documents = new List<string> { "IRB-APPROVAL" }
                }
            });

            // Phase 3: Contracts & Budget (PARALLEL with IRB - Days 8-25)
            taskSet.tasks.AddRange(new List<TemplateTask>
            {
                new TemplateTask
                {
                    task_id = "USA-SS-018",
                    name = "Draft Site Contract/CDA",
                    duration_days = 7,
                    category = "Admin",
                    can_run_parallel = true,
                    execution_group = "Parallel-Site-Prep",
                    parallel_group_id = 2
                },
                new TemplateTask
                {
                    task_id = "USA-SS-019",
                    name = "Budget Negotiation with Site",
                    duration_days = 10,
                    category = "Admin",
                    can_run_parallel = false,
                    execution_group = "Parallel-Site-Prep",
                    predecessors = new List<string> { "USA-SS-018" }
                },
                new TemplateTask
                {
                    task_id = "USA-SS-020",
                    name = "Legal Review of Contract",
                    duration_days = 5,
                    category = "Admin",
                    can_run_parallel = false,
                    execution_group = "Parallel-Site-Prep",
                    predecessors = new List<string> { "USA-SS-019" }
                },
                new TemplateTask
                {
                    task_id = "USA-SS-021",
                    name = "Site Contract Execution",
                    duration_days = 3,
                    category = "Admin",
                    can_run_parallel = false,
                    execution_group = "Parallel-Site-Prep",
                    predecessors = new List<string> { "USA-SS-020" }
                },
                new TemplateTask
                {
                    task_id = "USA-SS-022",
                    name = "Budget Approval and Upload to CTMS",
                    duration_days = 2,
                    category = "Admin",
                    can_run_parallel = false,
                    execution_group = "Parallel-Site-Prep",
                    predecessors = new List<string> { "USA-SS-021" }
                },
                new TemplateTask
                {
                    task_id = "USA-SS-023",
                    name = "Payment Milestone Setup",
                    duration_days = 1,
                    category = "Admin",
                    can_run_parallel = false,
                    execution_group = "Parallel-Site-Prep",
                    predecessors = new List<string> { "USA-SS-022" }
                },
                new TemplateTask
                {
                    task_id = "USA-SS-024",
                    name = "Purchase Order Creation (if required)",
                    duration_days = 2,
                    category = "Admin",
                    can_run_parallel = true,
                    execution_group = "Parallel-Site-Prep",
                    parallel_group_id = 2,
                    is_mandatory = false
                }
            });

            // Phase 4: Site Training Prep (PARALLEL with IRB - Days 20-35)
            taskSet.tasks.AddRange(new List<TemplateTask>
            {
                new TemplateTask
                {
                    task_id = "USA-SS-025",
                    name = "Schedule Site Initiation Visit (SIV)",
                    duration_days = 2,
                    category = "Clinical",
                    can_run_parallel = true,
                    execution_group = "Parallel-Training-Prep",
                    parallel_group_id = 3
                },
                new TemplateTask
                {
                    task_id = "USA-SS-026",
                    name = "Prepare SIV Materials and Agenda",
                    duration_days = 3,
                    category = "Clinical",
                    can_run_parallel = true,
                    execution_group = "Parallel-Training-Prep",
                    parallel_group_id = 3
                },
                new TemplateTask
                {
                    task_id = "USA-SS-027",
                    name = "Prepare Protocol Training Materials",
                    duration_days = 5,
                    category = "Clinical",
                    can_run_parallel = true,
                    execution_group = "Parallel-Training-Prep",
                    parallel_group_id = 3
                },
                new TemplateTask
                {
                    task_id = "USA-SS-028",
                    name = "Prepare eCRF Training Materials",
                    duration_days = 5,
                    category = "Data",
                    can_run_parallel = true,
                    execution_group = "Parallel-Training-Prep",
                    parallel_group_id = 3
                },
                new TemplateTask
                {
                    task_id = "USA-SS-029",
                    name = "Prepare IRT/IWRS Training Materials",
                    duration_days = 3,
                    category = "Data",
                    can_run_parallel = true,
                    execution_group = "Parallel-Training-Prep",
                    parallel_group_id = 3
                },
                new TemplateTask
                {
                    task_id = "USA-SS-030",
                    name = "Prepare AE/SAE Reporting Training Materials",
                    duration_days = 3,
                    category = "Clinical",
                    can_run_parallel = true,
                    execution_group = "Parallel-Training-Prep",
                    parallel_group_id = 3
                }
            });

            // Phase 5: Systems & Equipment Setup (PARALLEL with IRB - Days 15-35)
            taskSet.tasks.AddRange(new List<TemplateTask>
            {
                new TemplateTask
                {
                    task_id = "USA-SS-031",
                    name = "EDC User Account Creation",
                    duration_days = 1,
                    category = "Data",
                    can_run_parallel = true,
                    execution_group = "Parallel-Systems-Setup",
                    parallel_group_id = 4
                },
                new TemplateTask
                {
                    task_id = "USA-SS-032",
                    name = "IRT/IWRS User Account Creation",
                    duration_days = 1,
                    category = "Data",
                    can_run_parallel = true,
                    execution_group = "Parallel-Systems-Setup",
                    parallel_group_id = 4
                },
                new TemplateTask
                {
                    task_id = "USA-SS-033",
                    name = "CTMS User Account Creation",
                    duration_days = 1,
                    category = "Data",
                    can_run_parallel = true,
                    execution_group = "Parallel-Systems-Setup",
                    parallel_group_id = 4
                },
                new TemplateTask
                {
                    task_id = "USA-SS-034",
                    name = "Ship Equipment to Site (ECG, Centrifuge, etc.)",
                    duration_days = 5,
                    category = "Clinical",
                    can_run_parallel = true,
                    execution_group = "Parallel-Systems-Setup",
                    parallel_group_id = 4
                },
                new TemplateTask
                {
                    task_id = "USA-SS-035",
                    name = "Equipment Installation",
                    duration_days = 3,
                    category = "Clinical",
                    can_run_parallel = false,
                    execution_group = "Parallel-Systems-Setup",
                    predecessors = new List<string> { "USA-SS-034" }
                },
                new TemplateTask
                {
                    task_id = "USA-SS-036",
                    name = "Equipment Qualification (IQ/OQ)",
                    duration_days = 2,
                    category = "Clinical",
                    can_run_parallel = false,
                    execution_group = "Parallel-Systems-Setup",
                    predecessors = new List<string> { "USA-SS-035" }
                },
                new TemplateTask
                {
                    task_id = "USA-SS-037",
                    name = "Order Barcode Labels",
                    duration_days = 3,
                    category = "Clinical",
                    can_run_parallel = true,
                    execution_group = "Parallel-Systems-Setup",
                    parallel_group_id = 4
                },
                new TemplateTask
                {
                    task_id = "USA-SS-038",
                    name = "Ship Barcode Labels to Site",
                    duration_days = 5,
                    category = "Clinical",
                    can_run_parallel = false,
                    execution_group = "Parallel-Systems-Setup",
                    predecessors = new List<string> { "USA-SS-037" }
                },
                new TemplateTask
                {
                    task_id = "USA-SS-039",
                    name = "Prepare Randomization Materials",
                    duration_days = 2,
                    category = "Clinical",
                    can_run_parallel = true,
                    execution_group = "Parallel-Systems-Setup",
                    parallel_group_id = 4
                },
                new TemplateTask
                {
                    task_id = "USA-SS-040",
                    name = "ePRO Device Configuration (if applicable)",
                    duration_days = 3,
                    category = "Data",
                    can_run_parallel = true,
                    execution_group = "Parallel-Systems-Setup",
                    parallel_group_id = 4,
                    is_mandatory = false
                },
                new TemplateTask
                {
                    task_id = "USA-SS-041",
                    name = "Temperature Monitoring Device Setup",
                    duration_days = 2,
                    category = "Clinical",
                    can_run_parallel = true,
                    execution_group = "Parallel-Systems-Setup",
                    parallel_group_id = 4
                }
            });

            // Phase 6: Site Training Execution (SEQUENTIAL - after IRB - Days 45-52)
            taskSet.tasks.AddRange(new List<TemplateTask>
            {
                new TemplateTask
                {
                    task_id = "USA-SS-042",
                    name = "Conduct Site Initiation Visit (SIV)",
                    duration_days = 2,
                    category = "Clinical",
                    can_run_parallel = false,
                    execution_group = "Sequential-Training",
                    predecessors = new List<string> { "USA-SS-017" },
                    is_blocking = true
                },
                new TemplateTask
                {
                    task_id = "USA-SS-043",
                    name = "Protocol Training for PI and Staff",
                    duration_days = 1,
                    category = "Clinical",
                    can_run_parallel = false,
                    execution_group = "Sequential-Training",
                    predecessors = new List<string> { "USA-SS-042" }
                },
                new TemplateTask
                {
                    task_id = "USA-SS-044",
                    name = "GCP Refresher Training",
                    duration_days = 1,
                    category = "Clinical",
                    can_run_parallel = false,
                    execution_group = "Sequential-Training",
                    predecessors = new List<string> { "USA-SS-042" }
                },
                new TemplateTask
                {
                    task_id = "USA-SS-045",
                    name = "EDC/eCRF System Training",
                    duration_days = 1,
                    category = "Data",
                    can_run_parallel = false,
                    execution_group = "Sequential-Training",
                    predecessors = new List<string> { "USA-SS-042", "USA-SS-031" }
                },
                new TemplateTask
                {
                    task_id = "USA-SS-046",
                    name = "IRT/IWRS Randomization Training",
                    duration_days = 1,
                    category = "Data",
                    can_run_parallel = false,
                    execution_group = "Sequential-Training",
                    predecessors = new List<string> { "USA-SS-042", "USA-SS-032" }
                },
                new TemplateTask
                {
                    task_id = "USA-SS-047",
                    name = "Lab Procedures and Specimen Handling Training",
                    duration_days = 1,
                    category = "Lab",
                    can_run_parallel = false,
                    execution_group = "Sequential-Training",
                    predecessors = new List<string> { "USA-SS-042" }
                },
                new TemplateTask
                {
                    task_id = "USA-SS-048",
                    name = "AE/SAE Reporting Training",
                    duration_days = 1,
                    category = "Clinical",
                    can_run_parallel = false,
                    execution_group = "Sequential-Training",
                    predecessors = new List<string> { "USA-SS-042" }
                },
                new TemplateTask
                {
                    task_id = "USA-SS-049",
                    name = "Complete SIV Report and Action Items",
                    duration_days = 3,
                    category = "Clinical",
                    can_run_parallel = false,
                    execution_group = "Sequential-Training",
                    predecessors = new List<string> { "USA-SS-042" }
                }
            });

            // Phase 7: Site Activation (SEQUENTIAL - after training - Days 53-58)
            taskSet.tasks.AddRange(new List<TemplateTask>
            {
                new TemplateTask
                {
                    task_id = "USA-SS-050",
                    name = "Pharmacy Setup and Training",
                    duration_days = 2,
                    category = "Clinical",
                    can_run_parallel = false,
                    execution_group = "Sequential-Activation",
                    predecessors = new List<string> { "USA-SS-017" }
                },
                new TemplateTask
                {
                    task_id = "USA-SS-051",
                    name = "Ship Investigational Product to Site",
                    duration_days = 3,
                    category = "Clinical",
                    can_run_parallel = false,
                    execution_group = "Sequential-Activation",
                    predecessors = new List<string> { "USA-SS-017", "USA-SS-050" },
                    is_blocking = true
                },
                new TemplateTask
                {
                    task_id = "USA-SS-052",
                    name = "Pharmacy IP Receipt and Accountability",
                    duration_days = 1,
                    category = "Clinical",
                    can_run_parallel = false,
                    execution_group = "Sequential-Activation",
                    predecessors = new List<string> { "USA-SS-051" }
                },
                new TemplateTask
                {
                    task_id = "USA-SS-053",
                    name = "IP Temperature Monitoring Activation",
                    duration_days = 1,
                    category = "Clinical",
                    can_run_parallel = false,
                    execution_group = "Sequential-Activation",
                    predecessors = new List<string> { "USA-SS-052" }
                },
                new TemplateTask
                {
                    task_id = "USA-SS-054",
                    name = "Site Activation Readiness Checklist Review",
                    duration_days = 1,
                    category = "Clinical",
                    can_run_parallel = false,
                    execution_group = "Sequential-Activation",
                    predecessors = new List<string> { "USA-SS-049", "USA-SS-052", "USA-SS-021" }
                },
                new TemplateTask
                {
                    task_id = "USA-SS-055",
                    name = "Issue Site Activation Memo",
                    duration_days = 1,
                    category = "Admin",
                    can_run_parallel = false,
                    execution_group = "Sequential-Activation",
                    predecessors = new List<string> { "USA-SS-054" },
                    is_blocking = true
                }
            });

            taskSet.milestones.Add(new Milestone
            {
                milestone_id = "USA-MS-001",
                name = "Site Activated",
                description = "Site ready to enroll patients",
                phase = "Site Startup",
                is_study_level = false
            });

            taskSet.essential_documents = GetUSA_EssentialDocuments();

            return taskSet;
        }

        public static List<EssentialDocument> GetUSA_EssentialDocuments()
        {
            return new List<EssentialDocument>
            {
                new EssentialDocument
                {
                    document_id = "FDA-1572",
                    document_name = "FDA Form 1572 (Statement of Investigator)",
                    country_code = "USA",
                    regulatory_authority = "FDA",
                    is_mandatory = true,
                    regulatory_reference = "21 CFR 312.53(c)",
                    collection_task_id = "USA-SS-001",
                    document_category = "Investigator"
                },
                new EssentialDocument
                {
                    document_id = "PI-CV",
                    document_name = "Principal Investigator CV and Medical License",
                    country_code = "USA",
                    regulatory_authority = "FDA",
                    is_mandatory = true,
                    regulatory_reference = "21 CFR 312.62",
                    collection_task_id = "USA-SS-002",
                    document_category = "Investigator"
                },
                new EssentialDocument
                {
                    document_id = "PROTOCOL-SIG",
                    document_name = "Protocol Signature Page (all versions)",
                    country_code = "USA",
                    regulatory_authority = "FDA",
                    is_mandatory = true,
                    regulatory_reference = "ICH-GCP 8.2.2",
                    collection_task_id = "USA-SS-007",
                    document_category = "Protocol"
                },
                new EssentialDocument
                {
                    document_id = "SUB-INV-CV",
                    document_name = "Sub-Investigator CVs (IND only)",
                    country_code = "USA",
                    regulatory_authority = "FDA",
                    is_mandatory = true,
                    regulatory_reference = "21 CFR 312.53(c)(4)",
                    collection_task_id = "USA-SS-003",
                    document_category = "Investigator",
                    is_ind_specific = true
                },
                new EssentialDocument
                {
                    document_id = "FIN-DISC",
                    document_name = "Financial Disclosure Forms (IND only)",
                    country_code = "USA",
                    regulatory_authority = "FDA",
                    is_mandatory = true,
                    regulatory_reference = "21 CFR 54",
                    collection_task_id = "USA-SS-004",
                    document_category = "Investigator",
                    is_ind_specific = true
                },
                new EssentialDocument
                {
                    document_id = "IRB-APPROVAL",
                    document_name = "All IRB Submissions, Reviews, and Approvals",
                    country_code = "USA",
                    regulatory_authority = "FDA",
                    is_mandatory = true,
                    regulatory_reference = "21 CFR 56",
                    collection_task_id = "USA-SS-016",
                    document_category = "IRB"
                },
                new EssentialDocument
                {
                    document_id = "IBC-APPROVAL",
                    document_name = "IBC Submissions, Reviews, Approvals (if required)",
                    country_code = "USA",
                    regulatory_authority = "FDA",
                    is_mandatory = false,
                    regulatory_reference = "NIH Guidelines for Research Involving rDNA",
                    collection_task_id = "USA-SS-008",
                    document_category = "IRB",
                    is_ibc_specific = true
                },
                new EssentialDocument
                {
                    document_id = "ICF-APPROVED",
                    document_name = "Informed Consent (approved templates)",
                    country_code = "USA",
                    regulatory_authority = "FDA",
                    is_mandatory = true,
                    regulatory_reference = "21 CFR 50",
                    collection_task_id = "USA-SS-009",
                    document_category = "IRB"
                },
                new EssentialDocument
                {
                    document_id = "IRB-ANNUAL",
                    document_name = "IRB Reports and Annual Reviews",
                    country_code = "USA",
                    regulatory_authority = "FDA",
                    is_mandatory = true,
                    regulatory_reference = "21 CFR 56.109",
                    collection_task_id = "Ongoing",
                    document_category = "IRB"
                },
                new EssentialDocument
                {
                    document_id = "MEMOS-NTF",
                    document_name = "All Memorandums and Notes to File",
                    country_code = "USA",
                    regulatory_authority = "FDA",
                    is_mandatory = true,
                    regulatory_reference = "ICH-GCP 8.3",
                    collection_task_id = "Ongoing",
                    document_category = "Other"
                },
                new EssentialDocument
                {
                    document_id = "LAB-CERT",
                    document_name = "Laboratory Certifications, CLIA, Reference Ranges",
                    country_code = "USA",
                    regulatory_authority = "FDA",
                    is_mandatory = true,
                    regulatory_reference = "CLIA '88",
                    collection_task_id = "USA-SS-005",
                    document_category = "Lab"
                },
                new EssentialDocument
                {
                    document_id = "BLANK-CRF",
                    document_name = "Copy of Blank Approved CRFs",
                    country_code = "USA",
                    regulatory_authority = "FDA",
                    is_mandatory = true,
                    regulatory_reference = "ICH-GCP 8.3.18",
                    collection_task_id = "USA-SS-010",
                    document_category = "Protocol"
                },
                new EssentialDocument
                {
                    document_id = "PSRL-FINAL",
                    document_name = "Final PSRL (Protocol Safety Review Letter)",
                    country_code = "USA",
                    regulatory_authority = "FDA",
                    is_mandatory = true,
                    regulatory_reference = "Sponsor SOP",
                    collection_task_id = "USA-SS-011",
                    document_category = "Protocol"
                }
            };
        }

        #endregion

        #region Germany (BfArM/EMA) Site Startup Tasks

        public static SitePhaseTaskSet GetGermany_SiteStartup()
        {
            var taskSet = new SitePhaseTaskSet
            {
                phase_name = "Site Startup",
                phase_type = "Startup",
                country_code = "DEU",
                country_name = "Germany",
                regulatory_authority = "BfArM"
            };

            taskSet.tasks.AddRange(new List<TemplateTask>
            {
                new TemplateTask
                {
                    task_id = "DEU-SS-001",
                    name = "Collect Investigator of Record (IoR) Form",
                    description = "EU equivalent of FDA 1572",
                    duration_days = 5,
                    category = "Regulatory",
                    can_run_parallel = true,
                    execution_group = "Parallel-Essential-Docs",
                    parallel_group_id = 1
                },
                new TemplateTask
                {
                    task_id = "DEU-SS-002",
                    name = "Collect PI CV and Medical License (Approbation)",
                    duration_days = 3,
                    category = "Regulatory",
                    can_run_parallel = true,
                    execution_group = "Parallel-Essential-Docs",
                    parallel_group_id = 1
                },
                new TemplateTask
                {
                    task_id = "DEU-SS-003",
                    name = "Obtain EudraCT Number",
                    duration_days = 5,
                    category = "Regulatory",
                    can_run_parallel = true,
                    execution_group = "Parallel-Essential-Docs",
                    parallel_group_id = 1
                },
                new TemplateTask
                {
                    task_id = "DEU-SS-004",
                    name = "Prepare BfArM Notification Package",
                    duration_days = 7,
                    category = "Regulatory",
                    can_run_parallel = false,
                    execution_group = "Sequential-Regulatory-Prep",
                    predecessors = new List<string> { "DEU-SS-001", "DEU-SS-002", "DEU-SS-003" }
                },
                new TemplateTask
                {
                    task_id = "DEU-SS-005",
                    name = "Submit to Ethikkommission",
                    duration_days = 1,
                    category = "Regulatory",
                    can_run_parallel = false,
                    execution_group = "Sequential-Ethics-Review",
                    predecessors = new List<string> { "DEU-SS-004" },
                    is_blocking = true,
                    requires_irb_approval = true
                },
                new TemplateTask
                {
                    task_id = "DEU-SS-006",
                    name = "Ethikkommission Review and Approval",
                    duration_days = 45,
                    category = "Regulatory",
                    can_run_parallel = false,
                    execution_group = "Sequential-Ethics-Review",
                    predecessors = new List<string> { "DEU-SS-005" },
                    is_blocking = true,
                    requires_irb_approval = true
                },
                new TemplateTask
                {
                    task_id = "DEU-SS-007",
                    name = "Obtain Import License for Investigational Product (Einfuhrgenehmigung)",
                    duration_days = 14,
                    category = "Regulatory",
                    can_run_parallel = true,
                    execution_group = "Parallel-Site-Prep",
                    parallel_group_id = 2,
                    is_mandatory = true
                },
                new TemplateTask
                {
                    task_id = "DEU-SS-008",
                    name = "Conduct Site Initiation Visit (SIV)",
                    duration_days = 2,
                    category = "Clinical",
                    can_run_parallel = false,
                    execution_group = "Sequential-Activation",
                    predecessors = new List<string> { "DEU-SS-006" },
                    is_blocking = true
                },
                new TemplateTask
                {
                    task_id = "DEU-SS-009",
                    name = "Ship Investigational Product to Site",
                    duration_days = 5,
                    category = "Clinical",
                    can_run_parallel = false,
                    execution_group = "Sequential-Activation",
                    predecessors = new List<string> { "DEU-SS-006", "DEU-SS-007" },
                    is_blocking = true
                },
                new TemplateTask
                {
                    task_id = "DEU-SS-010",
                    name = "Issue Site Activation Memo",
                    duration_days = 1,
                    category = "Admin",
                    can_run_parallel = false,
                    execution_group = "Sequential-Activation",
                    predecessors = new List<string> { "DEU-SS-008", "DEU-SS-009" },
                    is_blocking = true
                }
            });

            taskSet.milestones.Add(new Milestone
            {
                milestone_id = "DEU-MS-001",
                name = "Site Activated",
                phase = "Site Startup",
                is_study_level = false
            });

            taskSet.essential_documents = GetGermany_EssentialDocuments();

            return taskSet;
        }

        public static List<EssentialDocument> GetGermany_EssentialDocuments()
        {
            return new List<EssentialDocument>
            {
                new EssentialDocument
                {
                    document_id = "IOR-FORM",
                    document_name = "Investigator of Record (IoR) Form",
                    country_code = "DEU",
                    regulatory_authority = "BfArM",
                    is_mandatory = true,
                    regulatory_reference = "EU GCP Directive 2001/20/EC",
                    document_category = "Investigator"
                },
                new EssentialDocument
                {
                    document_id = "EUDRACT",
                    document_name = "EudraCT Number",
                    country_code = "DEU",
                    regulatory_authority = "EMA",
                    is_mandatory = true,
                    regulatory_reference = "Regulation (EU) No 536/2014",
                    document_category = "Regulatory"
                },
                new EssentialDocument
                {
                    document_id = "IMPORT-LICENSE",
                    document_name = "Import License (Einfuhrgenehmigung)",
                    country_code = "DEU",
                    regulatory_authority = "BfArM",
                    is_mandatory = true,
                    regulatory_reference = "AMG §73",
                    document_category = "Regulatory"
                },
                new EssentialDocument
                {
                    document_id = "ETHICS-APPROVAL",
                    document_name = "Ethikkommission Approval",
                    country_code = "DEU",
                    regulatory_authority = "Ethikkommission",
                    is_mandatory = true,
                    regulatory_reference = "EU GCP Article 6",
                    document_category = "IRB"
                }
            };
        }

        #endregion

        #region UK (MHRA) Site Startup Tasks

        public static SitePhaseTaskSet GetUK_SiteStartup()
        {
            var taskSet = new SitePhaseTaskSet
            {
                phase_name = "Site Startup",
                phase_type = "Startup",
                country_code = "GBR",
                country_name = "United Kingdom",
                regulatory_authority = "MHRA"
            };

            taskSet.tasks.AddRange(new List<TemplateTask>
            {
                new TemplateTask
                {
                    task_id = "GBR-SS-001",
                    name = "Collect Investigator Site File Documents",
                    duration_days = 5,
                    category = "Regulatory",
                    can_run_parallel = true,
                    execution_group = "Parallel-Essential-Docs",
                    parallel_group_id = 1,
                    is_mandatory = true
                },
                new TemplateTask
                {
                    task_id = "GBR-SS-002",
                    name = "Collect PI CV and GMC Registration",
                    description = "General Medical Council registration required",
                    duration_days = 3,
                    category = "Regulatory",
                    can_run_parallel = true,
                    execution_group = "Parallel-Essential-Docs",
                    parallel_group_id = 1,
                    is_mandatory = true
                },
                new TemplateTask
                {
                    task_id = "GBR-SS-003",
                    name = "Collect GCP Certificates (all staff)",
                    duration_days = 3,
                    category = "Regulatory",
                    can_run_parallel = true,
                    execution_group = "Parallel-Essential-Docs",
                    parallel_group_id = 1,
                    is_mandatory = true
                },
                new TemplateTask
                {
                    task_id = "GBR-SS-004",
                    name = "Prepare IRAS Application",
                    description = "Integrated Research Application System",
                    duration_days = 7,
                    category = "Regulatory",
                    can_run_parallel = false,
                    execution_group = "Sequential-REC-Prep",
                    predecessors = new List<string> { "GBR-SS-001", "GBR-SS-002", "GBR-SS-003" },
                    is_blocking = true,
                    is_mandatory = true
                },
                new TemplateTask
                {
                    task_id = "GBR-SS-005",
                    name = "Submit to Research Ethics Committee (REC)",
                    duration_days = 2,
                    category = "Regulatory",
                    can_run_parallel = false,
                    execution_group = "Sequential-REC-Review",
                    predecessors = new List<string> { "GBR-SS-004" },
                    is_blocking = true,
                    requires_irb_approval = true,
                    is_mandatory = true
                },
                new TemplateTask
                {
                    task_id = "GBR-SS-006",
                    name = "REC Review Period",
                    description = "Up to 60 days for favourable opinion",
                    duration_days = 60,
                    category = "Regulatory",
                    can_run_parallel = false,
                    execution_group = "Sequential-REC-Review",
                    predecessors = new List<string> { "GBR-SS-005" },
                    is_blocking = true,
                    requires_irb_approval = true,
                    is_mandatory = true
                },
                new TemplateTask
                {
                    task_id = "GBR-SS-007",
                    name = "Obtain NHS R&D Approval",
                    description = "NHS Research & Development approval",
                    duration_days = 30,
                    category = "Regulatory",
                    can_run_parallel = true,
                    execution_group = "Parallel-NHS-Approval",
                    parallel_group_id = 2,
                    predecessors = new List<string> { "GBR-SS-005" },
                    is_blocking = true,
                    is_mandatory = true
                },
                new TemplateTask
                {
                    task_id = "GBR-SS-008",
                    name = "Submit MHRA Clinical Trial Application (if CTIMP)",
                    description = "Clinical Trial of an Investigational Medicinal Product",
                    duration_days = 5,
                    category = "Regulatory",
                    can_run_parallel = true,
                    execution_group = "Parallel-MHRA",
                    parallel_group_id = 3,
                    is_mandatory = false
                },
                new TemplateTask
                {
                    task_id = "GBR-SS-009",
                    name = "MHRA Assessment Period (30 days)",
                    duration_days = 30,
                    category = "Regulatory",
                    can_run_parallel = false,
                    execution_group = "Parallel-MHRA",
                    predecessors = new List<string> { "GBR-SS-008" },
                    is_mandatory = false
                },
                new TemplateTask
                {
                    task_id = "GBR-SS-010",
                    name = "Pharmacy Setup (MHRA-Licensed)",
                    description = "Pharmacy must be MHRA licensed for IMP storage",
                    duration_days = 14,
                    category = "Clinical",
                    can_run_parallel = true,
                    execution_group = "Parallel-Site-Prep",
                    parallel_group_id = 4,
                    is_mandatory = true
                },
                new TemplateTask
                {
                    task_id = "GBR-SS-011",
                    name = "Site Initiation Visit",
                    duration_days = 2,
                    category = "Clinical",
                    can_run_parallel = false,
                    execution_group = "Sequential-Training",
                    predecessors = new List<string> { "GBR-SS-006", "GBR-SS-007", "GBR-SS-010" },
                    is_blocking = true,
                    is_mandatory = true
                },
                new TemplateTask
                {
                    task_id = "GBR-SS-012",
                    name = "GCP Training (ICH-GCP)",
                    duration_days = 1,
                    category = "Clinical",
                    can_run_parallel = false,
                    execution_group = "Sequential-Training",
                    predecessors = new List<string> { "GBR-SS-011" },
                    is_mandatory = true
                },
                new TemplateTask
                {
                    task_id = "GBR-SS-013",
                    name = "Ship Investigational Product to Site",
                    duration_days = 3,
                    category = "Clinical",
                    can_run_parallel = false,
                    execution_group = "Sequential-Activation",
                    predecessors = new List<string> { "GBR-SS-006", "GBR-SS-010" },
                    is_blocking = true,
                    is_mandatory = true
                },
                new TemplateTask
                {
                    task_id = "GBR-SS-014",
                    name = "Issue Site Activation Memo",
                    duration_days = 1,
                    category = "Admin",
                    can_run_parallel = false,
                    execution_group = "Sequential-Activation",
                    predecessors = new List<string> { "GBR-SS-012", "GBR-SS-013" },
                    is_blocking = true,
                    is_mandatory = true
                }
            });

            taskSet.milestones.Add(new Milestone
            {
                milestone_id = "GBR-MS-001",
                name = "Site Activated",
                phase = "Site Startup",
                is_study_level = false
            });

            taskSet.essential_documents = GetUK_EssentialDocuments();

            return taskSet;
        }

        public static List<EssentialDocument> GetUK_EssentialDocuments()
        {
            return new List<EssentialDocument>
            {
                new EssentialDocument
                {
                    document_id = "GMC-REG",
                    document_name = "GMC Registration Certificate",
                    country_code = "GBR",
                    regulatory_authority = "GMC",
                    is_mandatory = true,
                    regulatory_reference = "UK GCP",
                    document_category = "Investigator"
                },
                new EssentialDocument
                {
                    document_id = "REC-APPROVAL",
                    document_name = "REC Favourable Opinion",
                    country_code = "GBR",
                    regulatory_authority = "HRA",
                    is_mandatory = true,
                    regulatory_reference = "HRA Guidelines",
                    document_category = "IRB"
                },
                new EssentialDocument
                {
                    document_id = "NHS-RD",
                    document_name = "NHS R&D Approval",
                    country_code = "GBR",
                    regulatory_authority = "NHS",
                    is_mandatory = true,
                    regulatory_reference = "NHS R&D Framework",
                    document_category = "Regulatory"
                },
                new EssentialDocument
                {
                    document_id = "MHRA-CTA",
                    document_name = "MHRA Clinical Trial Authorization (CTIMP only)",
                    country_code = "GBR",
                    regulatory_authority = "MHRA",
                    is_mandatory = false,
                    regulatory_reference = "SI 2004/1031",
                    document_category = "Regulatory"
                },
                new EssentialDocument
                {
                    document_id = "IRAS-APP",
                    document_name = "IRAS Application",
                    country_code = "GBR",
                    regulatory_authority = "HRA",
                    is_mandatory = true,
                    regulatory_reference = "HRA Guidelines",
                    document_category = "Regulatory"
                }
            };
        }

        #endregion

        #region Canada (Health Canada) Site Startup Tasks

        public static SitePhaseTaskSet GetCanada_SiteStartup()
        {
            var taskSet = new SitePhaseTaskSet
            {
                phase_name = "Site Startup",
                phase_type = "Startup",
                country_code = "CAN",
                country_name = "Canada",
                regulatory_authority = "Health Canada"
            };

            taskSet.tasks.AddRange(new List<TemplateTask>
            {
                new TemplateTask
                {
                    task_id = "CAN-SS-001",
                    name = "Collect Investigator Agreement",
                    duration_days = 5,
                    category = "Regulatory",
                    can_run_parallel = true,
                    execution_group = "Parallel-Essential-Docs",
                    parallel_group_id = 1,
                    is_mandatory = true
                },
                new TemplateTask
                {
                    task_id = "CAN-SS-002",
                    name = "Collect PI CV and Medical License",
                    description = "Provincial medical license required",
                    duration_days = 3,
                    category = "Regulatory",
                    can_run_parallel = true,
                    execution_group = "Parallel-Essential-Docs",
                    parallel_group_id = 1,
                    is_mandatory = true
                },
                new TemplateTask
                {
                    task_id = "CAN-SS-003",
                    name = "Collect Conflict of Interest Declarations",
                    duration_days = 3,
                    category = "Regulatory",
                    can_run_parallel = true,
                    execution_group = "Parallel-Essential-Docs",
                    parallel_group_id = 1,
                    is_mandatory = true
                },
                new TemplateTask
                {
                    task_id = "CAN-SS-004",
                    name = "Collect Laboratory Certifications",
                    duration_days = 3,
                    category = "Lab",
                    can_run_parallel = true,
                    execution_group = "Parallel-Essential-Docs",
                    parallel_group_id = 1,
                    is_mandatory = true
                },
                new TemplateTask
                {
                    task_id = "CAN-SS-005",
                    name = "Prepare Health Canada CTA Submission",
                    description = "Clinical Trial Application to Health Canada",
                    duration_days = 10,
                    category = "Regulatory",
                    can_run_parallel = false,
                    execution_group = "Sequential-HC-Prep",
                    predecessors = new List<string> { "CAN-SS-001", "CAN-SS-002" },
                    is_blocking = true,
                    is_mandatory = true
                },
                new TemplateTask
                {
                    task_id = "CAN-SS-006",
                    name = "Submit Health Canada CTA",
                    duration_days = 1,
                    category = "Regulatory",
                    can_run_parallel = false,
                    execution_group = "Sequential-HC-Review",
                    predecessors = new List<string> { "CAN-SS-005" },
                    is_blocking = true,
                    is_mandatory = true
                },
                new TemplateTask
                {
                    task_id = "CAN-SS-007",
                    name = "Health Canada CTA Review Period (30 days)",
                    description = "No objection letter from Health Canada",
                    duration_days = 30,
                    category = "Regulatory",
                    can_run_parallel = false,
                    execution_group = "Sequential-HC-Review",
                    predecessors = new List<string> { "CAN-SS-006" },
                    is_blocking = true,
                    is_mandatory = true
                },
                new TemplateTask
                {
                    task_id = "CAN-SS-008",
                    name = "Prepare REB Submission Package",
                    description = "Research Ethics Board submission",
                    duration_days = 7,
                    category = "Regulatory",
                    can_run_parallel = true,
                    execution_group = "Parallel-REB-Prep",
                    parallel_group_id = 2,
                    predecessors = new List<string> { "CAN-SS-001", "CAN-SS-002", "CAN-SS-003" },
                    is_blocking = true,
                    is_mandatory = true
                },
                new TemplateTask
                {
                    task_id = "CAN-SS-009",
                    name = "Submit to Research Ethics Board (REB)",
                    duration_days = 2,
                    category = "Regulatory",
                    can_run_parallel = false,
                    execution_group = "Sequential-REB-Review",
                    predecessors = new List<string> { "CAN-SS-008" },
                    is_blocking = true,
                    requires_irb_approval = true,
                    is_mandatory = true
                },
                new TemplateTask
                {
                    task_id = "CAN-SS-010",
                    name = "REB Review Period",
                    description = "Ethics board review - typically 35 days",
                    duration_days = 35,
                    category = "Regulatory",
                    can_run_parallel = false,
                    execution_group = "Sequential-REB-Review",
                    predecessors = new List<string> { "CAN-SS-009" },
                    is_blocking = true,
                    requires_irb_approval = true,
                    is_mandatory = true
                },
                new TemplateTask
                {
                    task_id = "CAN-SS-011",
                    name = "Pharmacy Setup and IP Storage",
                    duration_days = 10,
                    category = "Clinical",
                    can_run_parallel = true,
                    execution_group = "Parallel-Site-Prep",
                    parallel_group_id = 3,
                    is_mandatory = true
                },
                new TemplateTask
                {
                    task_id = "CAN-SS-012",
                    name = "Site Initiation Visit",
                    duration_days = 2,
                    category = "Clinical",
                    can_run_parallel = false,
                    execution_group = "Sequential-Training",
                    predecessors = new List<string> { "CAN-SS-007", "CAN-SS-010", "CAN-SS-011" },
                    is_blocking = true,
                    is_mandatory = true
                },
                new TemplateTask
                {
                    task_id = "CAN-SS-013",
                    name = "ICH-GCP Training",
                    duration_days = 1,
                    category = "Clinical",
                    can_run_parallel = false,
                    execution_group = "Sequential-Training",
                    predecessors = new List<string> { "CAN-SS-012" },
                    is_mandatory = true
                },
                new TemplateTask
                {
                    task_id = "CAN-SS-014",
                    name = "Ship Investigational Product to Site",
                    duration_days = 3,
                    category = "Clinical",
                    can_run_parallel = false,
                    execution_group = "Sequential-Activation",
                    predecessors = new List<string> { "CAN-SS-007", "CAN-SS-011" },
                    is_blocking = true,
                    is_mandatory = true
                },
                new TemplateTask
                {
                    task_id = "CAN-SS-015",
                    name = "Issue Site Activation Memo",
                    duration_days = 1,
                    category = "Admin",
                    can_run_parallel = false,
                    execution_group = "Sequential-Activation",
                    predecessors = new List<string> { "CAN-SS-013", "CAN-SS-014" },
                    is_blocking = true,
                    is_mandatory = true
                }
            });

            taskSet.milestones.Add(new Milestone
            {
                milestone_id = "CAN-MS-001",
                name = "Site Activated",
                phase = "Site Startup",
                is_study_level = false
            });

            taskSet.essential_documents = GetCanada_EssentialDocuments();

            return taskSet;
        }

        public static List<EssentialDocument> GetCanada_EssentialDocuments()
        {
            return new List<EssentialDocument>
            {
                new EssentialDocument
                {
                    document_id = "HC-CTA",
                    document_name = "Health Canada Clinical Trial Application",
                    country_code = "CAN",
                    regulatory_authority = "Health Canada",
                    is_mandatory = true,
                    regulatory_reference = "C.05.005 Food and Drug Regulations",
                    document_category = "Regulatory"
                },
                new EssentialDocument
                {
                    document_id = "REB-APPROVAL",
                    document_name = "REB Approval Letter",
                    country_code = "CAN",
                    regulatory_authority = "REB",
                    is_mandatory = true,
                    regulatory_reference = "ICH-GCP / TCPS2",
                    document_category = "IRB"
                },
                new EssentialDocument
                {
                    document_id = "PI-LICENSE",
                    document_name = "Provincial Medical License",
                    country_code = "CAN",
                    regulatory_authority = "Provincial College",
                    is_mandatory = true,
                    regulatory_reference = "Provincial Regulations",
                    document_category = "Investigator"
                },
                new EssentialDocument
                {
                    document_id = "COI-DECL",
                    document_name = "Conflict of Interest Declaration",
                    country_code = "CAN",
                    regulatory_authority = "REB",
                    is_mandatory = true,
                    regulatory_reference = "TCPS2",
                    document_category = "Investigator"
                }
            };
        }

        #endregion

        #region Japan (PMDA) Site Startup Tasks

        public static SitePhaseTaskSet GetJapan_SiteStartup()
        {
            var taskSet = new SitePhaseTaskSet
            {
                phase_name = "Site Startup",
                phase_type = "Startup",
                country_code = "JPN",
                country_name = "Japan",
                regulatory_authority = "PMDA"
            };

            taskSet.tasks.AddRange(new List<TemplateTask>
            {
                new TemplateTask
                {
                    task_id = "JPN-SS-001",
                    name = "Translate Protocol to Japanese",
                    description = "PMDA requires Japanese translation",
                    duration_days = 14,
                    category = "Translation",
                    can_run_parallel = true,
                    execution_group = "Parallel-Translation",
                    parallel_group_id = 1,
                    is_blocking = true,
                    is_mandatory = true
                },
                new TemplateTask
                {
                    task_id = "JPN-SS-002",
                    name = "Translate Informed Consent Form to Japanese",
                    duration_days = 10,
                    category = "Translation",
                    can_run_parallel = true,
                    execution_group = "Parallel-Translation",
                    parallel_group_id = 1,
                    is_mandatory = true
                },
                new TemplateTask
                {
                    task_id = "JPN-SS-003",
                    name = "Collect Investigator Agreement (Japanese)",
                    duration_days = 7,
                    category = "Regulatory",
                    can_run_parallel = true,
                    execution_group = "Parallel-Essential-Docs",
                    parallel_group_id = 2,
                    is_mandatory = true
                },
                new TemplateTask
                {
                    task_id = "JPN-SS-004",
                    name = "Collect PI CV and Medical License (Japanese)",
                    description = "Japanese medical license required",
                    duration_days = 5,
                    category = "Regulatory",
                    can_run_parallel = true,
                    execution_group = "Parallel-Essential-Docs",
                    parallel_group_id = 2,
                    is_mandatory = true
                },
                new TemplateTask
                {
                    task_id = "JPN-SS-005",
                    name = "Assign Clinical Research Coordinator (CRC)",
                    description = "Dedicated CRC required in Japan",
                    duration_days = 7,
                    category = "Clinical",
                    can_run_parallel = true,
                    execution_group = "Parallel-Site-Prep",
                    parallel_group_id = 3,
                    is_mandatory = true
                },
                new TemplateTask
                {
                    task_id = "JPN-SS-006",
                    name = "Prepare PMDA Clinical Trial Notification",
                    description = "jRCT registration required",
                    duration_days = 10,
                    category = "Regulatory",
                    can_run_parallel = false,
                    execution_group = "Sequential-PMDA-Prep",
                    predecessors = new List<string> { "JPN-SS-001", "JPN-SS-003", "JPN-SS-004" },
                    is_blocking = true,
                    is_mandatory = true
                },
                new TemplateTask
                {
                    task_id = "JPN-SS-007",
                    name = "Submit PMDA Notification (jRCT)",
                    description = "Japan Registry of Clinical Trials",
                    duration_days = 2,
                    category = "Regulatory",
                    can_run_parallel = false,
                    execution_group = "Sequential-PMDA-Review",
                    predecessors = new List<string> { "JPN-SS-006" },
                    is_blocking = true,
                    is_mandatory = true
                },
                new TemplateTask
                {
                    task_id = "JPN-SS-008",
                    name = "PMDA Review Period (30 days)",
                    description = "PMDA assessment period",
                    duration_days = 30,
                    category = "Regulatory",
                    can_run_parallel = false,
                    execution_group = "Sequential-PMDA-Review",
                    predecessors = new List<string> { "JPN-SS-007" },
                    is_blocking = true,
                    is_mandatory = true
                },
                new TemplateTask
                {
                    task_id = "JPN-SS-009",
                    name = "Prepare IRB Submission (Japanese)",
                    duration_days = 7,
                    category = "Regulatory",
                    can_run_parallel = true,
                    execution_group = "Parallel-IRB-Prep",
                    parallel_group_id = 4,
                    predecessors = new List<string> { "JPN-SS-001", "JPN-SS-002" },
                    is_blocking = true,
                    is_mandatory = true
                },
                new TemplateTask
                {
                    task_id = "JPN-SS-010",
                    name = "Submit to IRB",
                    duration_days = 2,
                    category = "Regulatory",
                    can_run_parallel = false,
                    execution_group = "Sequential-IRB-Review",
                    predecessors = new List<string> { "JPN-SS-009" },
                    is_blocking = true,
                    requires_irb_approval = true,
                    is_mandatory = true
                },
                new TemplateTask
                {
                    task_id = "JPN-SS-011",
                    name = "IRB Review Period",
                    description = "Japanese IRB review - typically 30 days",
                    duration_days = 30,
                    category = "Regulatory",
                    can_run_parallel = false,
                    execution_group = "Sequential-IRB-Review",
                    predecessors = new List<string> { "JPN-SS-010" },
                    is_blocking = true,
                    requires_irb_approval = true,
                    is_mandatory = true
                },
                new TemplateTask
                {
                    task_id = "JPN-SS-012",
                    name = "Hospital Pharmacy Setup",
                    description = "Hospital pharmacy must be certified",
                    duration_days = 14,
                    category = "Clinical",
                    can_run_parallel = true,
                    execution_group = "Parallel-Site-Prep",
                    parallel_group_id = 5,
                    is_mandatory = true
                },
                new TemplateTask
                {
                    task_id = "JPN-SS-013",
                    name = "Site Initiation Visit (with Translator)",
                    description = "Japanese-English translator required",
                    duration_days = 2,
                    category = "Clinical",
                    can_run_parallel = false,
                    execution_group = "Sequential-Training",
                    predecessors = new List<string> { "JPN-SS-008", "JPN-SS-011", "JPN-SS-012", "JPN-SS-005" },
                    is_blocking = true,
                    is_mandatory = true
                },
                new TemplateTask
                {
                    task_id = "JPN-SS-014",
                    name = "J-GCP Training (Japanese GCP)",
                    description = "Japanese version of GCP training required",
                    duration_days = 1,
                    category = "Clinical",
                    can_run_parallel = false,
                    execution_group = "Sequential-Training",
                    predecessors = new List<string> { "JPN-SS-013" },
                    is_mandatory = true
                },
                new TemplateTask
                {
                    task_id = "JPN-SS-015",
                    name = "CRC Protocol Training (Japanese)",
                    duration_days = 1,
                    category = "Clinical",
                    can_run_parallel = false,
                    execution_group = "Sequential-Training",
                    predecessors = new List<string> { "JPN-SS-013" },
                    is_mandatory = true
                },
                new TemplateTask
                {
                    task_id = "JPN-SS-016",
                    name = "Ship Investigational Product to Site",
                    description = "Import documentation required",
                    duration_days = 5,
                    category = "Clinical",
                    can_run_parallel = false,
                    execution_group = "Sequential-Activation",
                    predecessors = new List<string> { "JPN-SS-008", "JPN-SS-012" },
                    is_blocking = true,
                    is_mandatory = true
                },
                new TemplateTask
                {
                    task_id = "JPN-SS-017",
                    name = "Issue Site Activation Memo",
                    duration_days = 1,
                    category = "Admin",
                    can_run_parallel = false,
                    execution_group = "Sequential-Activation",
                    predecessors = new List<string> { "JPN-SS-014", "JPN-SS-015", "JPN-SS-016" },
                    is_blocking = true,
                    is_mandatory = true
                }
            });

            taskSet.milestones.Add(new Milestone
            {
                milestone_id = "JPN-MS-001",
                name = "Site Activated",
                phase = "Site Startup",
                is_study_level = false
            });

            taskSet.essential_documents = GetJapan_EssentialDocuments();

            return taskSet;
        }

        public static List<EssentialDocument> GetJapan_EssentialDocuments()
        {
            return new List<EssentialDocument>
            {
                new EssentialDocument
                {
                    document_id = "JRCT-REG",
                    document_name = "jRCT Registration",
                    country_code = "JPN",
                    regulatory_authority = "PMDA",
                    is_mandatory = true,
                    regulatory_reference = "Clinical Trials Act (2018)",
                    document_category = "Regulatory"
                },
                new EssentialDocument
                {
                    document_id = "PMDA-NOTIF",
                    document_name = "PMDA Clinical Trial Notification",
                    country_code = "JPN",
                    regulatory_authority = "PMDA",
                    is_mandatory = true,
                    regulatory_reference = "Pharmaceutical Affairs Law",
                    document_category = "Regulatory"
                },
                new EssentialDocument
                {
                    document_id = "PROTOCOL-JP",
                    document_name = "Protocol (Japanese Translation)",
                    country_code = "JPN",
                    regulatory_authority = "PMDA",
                    is_mandatory = true,
                    regulatory_reference = "J-GCP",
                    document_category = "Protocol"
                },
                new EssentialDocument
                {
                    document_id = "ICF-JP",
                    document_name = "Informed Consent Form (Japanese)",
                    country_code = "JPN",
                    regulatory_authority = "IRB",
                    is_mandatory = true,
                    regulatory_reference = "J-GCP Article 53",
                    document_category = "IRB"
                },
                new EssentialDocument
                {
                    document_id = "PI-LICENSE-JP",
                    document_name = "Japanese Medical License",
                    country_code = "JPN",
                    regulatory_authority = "MHLW",
                    is_mandatory = true,
                    regulatory_reference = "Medical Practitioners' Law",
                    document_category = "Investigator"
                },
                new EssentialDocument
                {
                    document_id = "CRC-ASSIGNMENT",
                    document_name = "Clinical Research Coordinator Assignment",
                    country_code = "JPN",
                    regulatory_authority = "Hospital",
                    is_mandatory = true,
                    regulatory_reference = "J-GCP",
                    document_category = "Other"
                }
            };
        }

        #endregion

        public static SitePhaseTaskSet GetSiteStartupByCountry(string countryCode)
        {
            switch (countryCode.ToUpper())
            {
                case "USA":
                    return GetUSA_SiteStartup();
                case "DEU":
                case "GERMANY":
                    return GetGermany_SiteStartup();
                case "GBR":
                case "UK":
                    return GetUK_SiteStartup();
                case "CAN":
                case "CANADA":
                    return GetCanada_SiteStartup();
                case "JPN":
                case "JAPAN":
                    return GetJapan_SiteStartup();
                default:
                    return GetUSA_SiteStartup();
            }
        }
    }
}
