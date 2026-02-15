-- Migration 017: Add Task Descriptions to Study Start-Up Template
-- Created: 2026-02-15
-- Description: Add descriptions/notes from Study Start-Up Guidance Document CSV
--              to template_tasks for TPL_001 (Study Start-Up)
-- This migration is idempotent - safe to run multiple times

-- ============================================================================
-- UPDATE TEMPLATE_TASKS WITH DESCRIPTIONS
-- Total updates: 82 tasks
-- ============================================================================

-- STARTUP_003: US CT.gov ▪ Registration
UPDATE template_tasks
SET description = 'Prerequisite: None | FPI',
    updated_at = datetime('now')
WHERE task_id = 'STARTUP_003';

-- STARTUP_004: Master Service Agreement (MSA)
UPDATE template_tasks
SET description = 'Prerequisite: Study Award',
    updated_at = datetime('now')
WHERE task_id = 'STARTUP_004';

-- STARTUP_005: Start-up Agreement (SUA) or full work order with Roles and Responsibilities
UPDATE template_tasks
SET description = 'Prerequisite: Study Award | SUA or full WO to be fully executed prior to start up activities taking place.',
    updated_at = datetime('now')
WHERE task_id = 'STARTUP_005';

-- STARTUP_006: Review study contract/budget for understanding on FTE allocation ▪ What roles ar
UPDATE template_tasks
SET description = 'Prerequisite: Full Execution of contract | KOM',
    updated_at = datetime('now')
WHERE task_id = 'STARTUP_006';

-- STARTUP_007: Financial tracking tools ▪ Contract/budget tracking ▪ Study/site payment trackin
UPDATE template_tasks
SET description = 'Prerequisite: Full Execution of contract',
    updated_at = datetime('now')
WHERE task_id = 'STARTUP_007';

-- STARTUP_008: Confidentiality Disclosure Agreement (CDA) for vendors - Template available? - E
UPDATE template_tasks
SET description = 'Prerequisite: Vendor Selection',
    updated_at = datetime('now')
WHERE task_id = 'STARTUP_008';

-- STARTUP_009: Site budget/contract Sites Contract/Budget Template ▪ Submit protcol and milesto
UPDATE template_tasks
SET description = 'Prerequisite: Final Protocol, timelines for study, Schedule of Assessments, Site Selection (for site specific B&C)',
    updated_at = datetime('now')
WHERE task_id = 'STARTUP_009';

-- STARTUP_010: Invoice approvel: -nvoice Review -Tracking >Ensure all items are being checked a
UPDATE template_tasks
SET description = 'Prerequisite: Contracts must be final, Accounts Payable must have all necessary items to make payments',
    updated_at = datetime('now')
WHERE task_id = 'STARTUP_010';

-- STARTUP_011: Financial Oversight (Revenue, Forcast, Billing) ▪Finance to schedule monthly rev
UPDATE template_tasks
SET description = 'Prerequisite: Contract Final and loaded into Tempo (by FA) | Monthly task, prompted by emails from Finance with due dates for FLs and PMs',
    updated_at = datetime('now')
WHERE task_id = 'STARTUP_011';

-- STARTUP_012: Core Team Meetings (aka Internal Team Meeting) see FAQ 3 for more details ▪Discu
UPDATE template_tasks
SET description = 'Prerequisite: Internal Transition Meeting | This is based on your budget.  It is however recommended to start having these at least 1 month prior to your KOM so the team has time to review the protocol, discuss the study set up and prepare for the KOM appropriately.',
    updated_at = datetime('now')
WHERE task_id = 'STARTUP_012';

-- STARTUP_013: Project Team/Sponsor Meetings (See FAQ 4 for more details) ▪Confirm attendee(s) 
UPDATE template_tasks
SET description = 'Prerequisite: KOM | See Study Budget/Contract for frequency',
    updated_at = datetime('now')
WHERE task_id = 'STARTUP_013';

-- STARTUP_014: Kick-Off Meeting (KOM) ▪ Review budget for allocated resources ▪ Sched KOM ***Co
UPDATE template_tasks
SET description = 'Prerequisite: Study Award/Internal Transition Meeting, Final Protocol | Start preparing for the KOM at least a month in advance if possible.  Slides, Agendas and minutes will be required. PM will ensure the study team is tailoring their presentations to study scope.  

Checklist for KOM planning
- Who? Study Chair attendance: confirm this directly with the Study Chair with their admin in copy and specifically which portions they will be attending; Sponsor attendance and for which portions.
- When? Ensure enough timing is planned for review of slides with Sponsor/internal

-Invite the Regulatory Manager to the KOM; Check to see if any other managers require attendance

*Study Team review of all available study documents will be needed prior to sponsor KOM.*',
    updated_at = datetime('now')
WHERE task_id = 'STARTUP_014';

-- STARTUP_015: Investigator Meeting, if scoped ▪ Schedule after site selection
UPDATE template_tasks
SET description = 'Prerequisite: KOM, Final Site List (all sites selected and in process of being activated or are open) | These may occur at the beginning of the study or following dose escalation to kick-off expansion enrollment and site participation, discuss the IP, administration process, and IP benefits, protocol, etc.',
    updated_at = datetime('now')
WHERE task_id = 'STARTUP_015';

-- STARTUP_016: PM 1:1 Meetings ▪Schedule with Sponsor Counterpart (consider including CTL if ap
UPDATE template_tasks
SET description = 'Prerequisite: KOM | Refer to budget for frequency and attendees with Sponsor.  For PM/CTL/CPA touch bases, best to ensure availability; may not be included in contract since this is just an internal process',
    updated_at = datetime('now')
WHERE task_id = 'STARTUP_016';

-- STARTUP_017: Study Start Up Plan
UPDATE template_tasks
SET description = 'Prior to First Site being Selected',
    updated_at = datetime('now')
WHERE task_id = 'STARTUP_017';

-- STARTUP_018: Project Management Plan (PMP)
UPDATE template_tasks
SET description = 'Prerequisite: Internal Transition Meeting, Final Protocol, Final Vendor Selection as applicable. | FPI',
    updated_at = datetime('now')
WHERE task_id = 'STARTUP_018';

-- STARTUP_019: Timelines (MS Project)
UPDATE template_tasks
SET description = 'Prerequisite: Internal Transition Meeting, Final Protocol | KOM',
    updated_at = datetime('now')
WHERE task_id = 'STARTUP_019';

-- STARTUP_020: Risk Log
UPDATE template_tasks
SET description = 'Prerequisite: Internal Transition Meeting',
    updated_at = datetime('now')
WHERE task_id = 'STARTUP_020';

-- STARTUP_021: Action Item and Decision Log (AID Log)
UPDATE template_tasks
SET description = 'KOM',
    updated_at = datetime('now')
WHERE task_id = 'STARTUP_021';

-- STARTUP_022: Project Team Training Tracker (PT3/PTTT)
UPDATE template_tasks
SET description = 'Prerequisite: KOM | To be finalized within 15 Business Days following KOM',
    updated_at = datetime('now')
WHERE task_id = 'STARTUP_022';

-- STARTUP_023: Risk Management Plan (RMP)
UPDATE template_tasks
SET description = 'FPI',
    updated_at = datetime('now')
WHERE task_id = 'STARTUP_023';

-- STARTUP_024: Trial Master File Plan
UPDATE template_tasks
SET description = 'Prior to filing TMF Docs',
    updated_at = datetime('now')
WHERE task_id = 'STARTUP_024';

-- STARTUP_025: eTMF Structure Checklist
UPDATE template_tasks
SET description = 'Prior to filing TMF Docs',
    updated_at = datetime('now')
WHERE task_id = 'STARTUP_025';

-- STARTUP_026: Clinical Management Plan
UPDATE template_tasks
SET description = 'PSV or SIV',
    updated_at = datetime('now')
WHERE task_id = 'STARTUP_026';

-- STARTUP_027: Monitoring Plan
UPDATE template_tasks
SET description = 'FPI',
    updated_at = datetime('now')
WHERE task_id = 'STARTUP_027';

-- STARTUP_028: Enrollment Management Plan (EMP)
UPDATE template_tasks
SET description = 'Prior to First Subject Enrollment',
    updated_at = datetime('now')
WHERE task_id = 'STARTUP_028';

-- STARTUP_029: Protocol Deviation Management Plan
UPDATE template_tasks
SET description = 'First SIV',
    updated_at = datetime('now')
WHERE task_id = 'STARTUP_029';

-- STARTUP_030: SIV Training Slides
UPDATE template_tasks
SET description = 'Prior to First SIV',
    updated_at = datetime('now')
WHERE task_id = 'STARTUP_030';

-- STARTUP_031: Study Reference Manual
UPDATE template_tasks
SET description = 'Prerequisite: Ensure all documents listed in Study Reference Document list are finalized prior to creating binders | First SIV',
    updated_at = datetime('now')
WHERE task_id = 'STARTUP_031';

-- STARTUP_032: Lab Manual
UPDATE template_tasks
SET description = 'First SIV',
    updated_at = datetime('now')
WHERE task_id = 'STARTUP_032';

-- STARTUP_033: Pharmacy Manual/Dosing Instructions
UPDATE template_tasks
SET description = 'First SIV',
    updated_at = datetime('now')
WHERE task_id = 'STARTUP_033';

-- STARTUP_034: Data Management Plan (DMP)
UPDATE template_tasks
SET description = 'Database Go-Live',
    updated_at = datetime('now')
WHERE task_id = 'STARTUP_034';

-- STARTUP_035: CRF Completion Guidelines
UPDATE template_tasks
SET description = 'Database Go-Live',
    updated_at = datetime('now')
WHERE task_id = 'STARTUP_035';

-- STARTUP_036: Safety Monitoring Plan (SMP)
UPDATE template_tasks
SET description = 'FPI',
    updated_at = datetime('now')
WHERE task_id = 'STARTUP_036';

-- STARTUP_037: Statistical Analysis Plan (SAP)
UPDATE template_tasks
SET description = 'Formal analysis or unblinding of treatment assignments',
    updated_at = datetime('now')
WHERE task_id = 'STARTUP_037';

-- STARTUP_038: Medical Monitoring Plan
UPDATE template_tasks
SET description = 'SIV',
    updated_at = datetime('now')
WHERE task_id = 'STARTUP_038';

-- STARTUP_039: Subject Enrollment Form (SEF)
UPDATE template_tasks
SET description = 'SIV',
    updated_at = datetime('now')
WHERE task_id = 'STARTUP_039';

-- STARTUP_041: Site Feasibility Questionnaire (SFQ)
UPDATE template_tasks
SET description = 'Prerequisite: KOM',
    updated_at = datetime('now')
WHERE task_id = 'STARTUP_041';

-- STARTUP_042: CTMS and eTMF setup ▪PM Submit Study Setup Request for ▪ TMF structure checklist
UPDATE template_tasks
SET description = 'Prerequisite: Study Award, Internal Transition Meeting',
    updated_at = datetime('now')
WHERE task_id = 'STARTUP_042';

-- STARTUP_043: Review & setup milestones in Veeva
UPDATE template_tasks
SET description = 'Prerequisite: SUA, Final Budget/Contract, Initial Timelines, Study',
    updated_at = datetime('now')
WHERE task_id = 'STARTUP_043';

-- STARTUP_044: Protocol/ICF development ▪ Tracking tools ▪ Review and feedback
UPDATE template_tasks
SET description = 'Prerequisite: Final Protocol required for ICF creation',
    updated_at = datetime('now')
WHERE task_id = 'STARTUP_044';

-- STARTUP_045: Project Dashboard ▪ Initiate dashboard with original study specifications
UPDATE template_tasks
SET description = 'Prerequisite: KOM | Completed Monthly based on Sponsor request',
    updated_at = datetime('now')
WHERE task_id = 'STARTUP_045';

-- STARTUP_046: Establish process/format for study reports to be shared/sent to sponsor ▪ Web po
UPDATE template_tasks
SET description = 'Prerequisite: KOM',
    updated_at = datetime('now')
WHERE task_id = 'STARTUP_046';

-- STARTUP_047: EDC Set up/ Account Access ▪ Initial Account Set up ▪ User Access Requests
UPDATE template_tasks
SET description = 'Prior to first site activated',
    updated_at = datetime('now')
WHERE task_id = 'STARTUP_047';

-- STARTUP_048: IP contact information ▪ Sponsor ▪ Vendor
UPDATE template_tasks
SET description = 'Prerequisite: Final Study Budget & Contract | First SIV',
    updated_at = datetime('now')
WHERE task_id = 'STARTUP_048';

-- STARTUP_049: Establish drug release process
UPDATE template_tasks
SET description = 'Prerequisite: Final Study Budget & Contract | First SIV',
    updated_at = datetime('now')
WHERE task_id = 'STARTUP_049';

-- STARTUP_050: IP distribution
UPDATE template_tasks
SET description = 'Prerequisite: Final Study Budget & Contract | First SIV',
    updated_at = datetime('now')
WHERE task_id = 'STARTUP_050';

-- STARTUP_051: Labeling ▪ who is responsible
UPDATE template_tasks
SET description = 'Prerequisite: Final Study Budget & Contract | First SIV',
    updated_at = datetime('now')
WHERE task_id = 'STARTUP_051';

-- STARTUP_052: International ▪ Labeling ▪ commercial availability
UPDATE template_tasks
SET description = 'Prerequisite: Final Study Budget & Contract | First SIV',
    updated_at = datetime('now')
WHERE task_id = 'STARTUP_052';

-- STARTUP_053: Generic substitution acceptable?
UPDATE template_tasks
SET description = 'Prerequisite: Final Study Budget & Contract | First SIV',
    updated_at = datetime('now')
WHERE task_id = 'STARTUP_053';

-- STARTUP_054: Service Providers ▪ Number of Vendors to be used
UPDATE template_tasks
SET description = 'Prerequisite: Final Study Budget & Contract',
    updated_at = datetime('now')
WHERE task_id = 'STARTUP_054';

-- STARTUP_055: Vendor identification ▪ Do vendors need to be identified? ▪ IP Depot ▪ Central l
UPDATE template_tasks
SET description = 'Prerequisite: Final Study Budget & Contract',
    updated_at = datetime('now')
WHERE task_id = 'STARTUP_055';

-- STARTUP_056: Vendor model, e.g. ▪Contracts/manages? ▪ Sponsor contracts/manages? ▪ Sponsor co
UPDATE template_tasks
SET description = 'Prerequisite: Final Study Budget & Contract',
    updated_at = datetime('now')
WHERE task_id = 'STARTUP_056';

-- STARTUP_057: Vendor(s) setup ▪ manual ▪ UAT required? ▪ Budget/contracts for vendors setup ▪ 
UPDATE template_tasks
SET description = 'Prerequisite: Final Study Budget & Contract',
    updated_at = datetime('now')
WHERE task_id = 'STARTUP_057';

-- STARTUP_058: Central IRB ▪ Name of IRB ▪ Which sites will use
UPDATE template_tasks
SET description = 'Prerequisite: Full execution of contract, Site selection',
    updated_at = datetime('now')
WHERE task_id = 'STARTUP_058';

-- STARTUP_059: Country Level Reg Submission
UPDATE template_tasks
SET description = 'Prerequisite: Final Study Budget & Contract',
    updated_at = datetime('now')
WHERE task_id = 'STARTUP_059';

-- STARTUP_061: Onboarding See FAQ 14 ▪ Add/Update PT3 tracker ▪ Training slides (sponsor?) - Co
UPDATE template_tasks
SET description = 'Prerequisite: Final Protocol, Team Assignments | Training is completed by project team members within 15 business days of being assigned to the study or the training, as required due to transition timelines, or as study documents are approved.',
    updated_at = datetime('now')
WHERE task_id = 'STARTUP_061';

-- STARTUP_062: SOPs need to be shared with sponsor?
UPDATE template_tasks
SET description = 'Prerequisite: Study Budget and Contract Finalized',
    updated_at = datetime('now')
WHERE task_id = 'STARTUP_062';

-- STARTUP_063: Obtain any sponsor-required SOPs
UPDATE template_tasks
SET description = 'Prerequisite: Study Budget and Contract Finalized',
    updated_at = datetime('now')
WHERE task_id = 'STARTUP_063';

-- STARTUP_064: CRA Study Planning using CRA resourcing form
UPDATE template_tasks
SET description = 'Prerequisite: projected enrollment rate (patients/month) and FPI date',
    updated_at = datetime('now')
WHERE task_id = 'STARTUP_064';

-- STARTUP_065: Laboratory sample tracker (as needed)
UPDATE template_tasks
SET description = 'Prerequisite: Lab Manual, Third Party Vendors and process defined',
    updated_at = datetime('now')
WHERE task_id = 'STARTUP_065';

-- STARTUP_066: Slot Management Tracker
UPDATE template_tasks
SET description = 'Prerequisite: EMP Plan Finalized | Prior to First subject identified',
    updated_at = datetime('now')
WHERE task_id = 'STARTUP_066';

-- STARTUP_067: Site List Request
UPDATE template_tasks
SET description = 'Prerequisite: Internal Transition Meeting',
    updated_at = datetime('now')
WHERE task_id = 'STARTUP_067';

-- STARTUP_068: Sharepoint folder setup
UPDATE template_tasks
SET description = 'Prerequisite: Internal Transition Meeting | Request this to be set up as soon as possible',
    updated_at = datetime('now')
WHERE task_id = 'STARTUP_068';

-- STARTUP_069: Electronic mailbox setup (PM)
UPDATE template_tasks
SET description = 'Prerequisite: Internal Transition Meeting | Request this to be set up as soon as possible',
    updated_at = datetime('now')
WHERE task_id = 'STARTUP_069';

-- STARTUP_070: Site Essential Document Review
UPDATE template_tasks
SET description = 'Must be done prior to activating the site',
    updated_at = datetime('now')
WHERE task_id = 'STARTUP_070';

-- STARTUP_071: Startup Tracking (Start-up is responsible) ▪ Site selection/final site list ▪ Si
UPDATE template_tasks
SET description = 'Prerequisite: Final Protocol, possibly KOM depending on timing',
    updated_at = datetime('now')
WHERE task_id = 'STARTUP_071';

-- STARTUP_072: 1572
UPDATE template_tasks
SET description = 'Prerequisite: Final Protocol Title | Prior to IND submission/in parallel to final protocol',
    updated_at = datetime('now')
WHERE task_id = 'STARTUP_072';

-- STARTUP_073: Country/site feasibility (Start-up is responsible) ▪ Country selection ▪ Site ID
UPDATE template_tasks
SET description = 'Prerequisite: Final Protocol, possibly KOM depending on timing',
    updated_at = datetime('now')
WHERE task_id = 'STARTUP_073';

-- STARTUP_074: Central and Local IRB submission completed?
UPDATE template_tasks
SET description = 'Prerequisite: IND Submission',
    updated_at = datetime('now')
WHERE task_id = 'STARTUP_074';

-- STARTUP_075: Ensure Innovations CVs current and filed
UPDATE template_tasks
SET description = 'Prerequisite: Internal Transition Meeting, Team Assignment',
    updated_at = datetime('now')
WHERE task_id = 'STARTUP_075';

-- STARTUP_076: Database build timelines sent to you? ▪ Ensure scheduling or timelines are estab
UPDATE template_tasks
SET description = 'Prerequisite: Internal Transition Meeting, Final Protocol | FPI',
    updated_at = datetime('now')
WHERE task_id = 'STARTUP_076';

-- STARTUP_077: Program for patient profiles Program for derived data sets
UPDATE template_tasks
SET description = 'Prerequisite: Database Build | FPI',
    updated_at = datetime('now')
WHERE task_id = 'STARTUP_077';

-- STARTUP_078: Case Report Form (CRF) started?
UPDATE template_tasks
SET description = 'Prerequisite: Internal Transition Meeting, Final Protocol | FPI',
    updated_at = datetime('now')
WHERE task_id = 'STARTUP_078';

-- STARTUP_079: CRF Completion Guidelines started?
UPDATE template_tasks
SET description = 'Database Go-Live',
    updated_at = datetime('now')
WHERE task_id = 'STARTUP_079';

-- STARTUP_080: Data Transfer Agreement(s) (DTA)
UPDATE template_tasks
SET description = 'Prerequisite: Vendors contracted with, Lab Manual finalized | Prior to any data transfers',
    updated_at = datetime('now')
WHERE task_id = 'STARTUP_080';

-- STARTUP_081: Argus Database Build Initiated
UPDATE template_tasks
SET description = 'Prerequisite: Study Award | Prior to FPI',
    updated_at = datetime('now')
WHERE task_id = 'STARTUP_081';

-- STARTUP_082: SAE form created?
UPDATE template_tasks
SET description = 'Prerequisite: Database Build | Prior to FPI',
    updated_at = datetime('now')
WHERE task_id = 'STARTUP_082';

-- STARTUP_083: Pregnancy Form created?
UPDATE template_tasks
SET description = 'Prerequisite: Database Build | Prior to FPI',
    updated_at = datetime('now')
WHERE task_id = 'STARTUP_083';

-- STARTUP_084: Protocol Writing/Finalization
UPDATE template_tasks
SET description = 'Prerequisite: Study Award',
    updated_at = datetime('now')
WHERE task_id = 'STARTUP_084';

-- STARTUP_085: Investigator Brochure (IB) writing
UPDATE template_tasks
SET description = 'Prerequisite: Study Award',
    updated_at = datetime('now')
WHERE task_id = 'STARTUP_085';

-- STARTUP_086: Informed Consent Form (ICF) writing
UPDATE template_tasks
SET description = 'Prerequisite: Final Protocol',
    updated_at = datetime('now')
WHERE task_id = 'STARTUP_086';
