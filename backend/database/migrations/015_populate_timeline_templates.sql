-- Migration 015: Populate Timeline Template Data
-- Created: 2026-02-14
-- Description: Seed database with 6 system templates (291 tasks, 75 dependencies)
-- This migration is idempotent - safe to run multiple times

-- ============================================================================
-- 1. DELETE EXISTING DATA (to handle re-runs cleanly)
-- ============================================================================

DELETE FROM template_dependencies WHERE template_id LIKE 'TPL_%';
DELETE FROM template_tasks WHERE template_id LIKE 'TPL_%';
DELETE FROM timeline_templates WHERE template_id LIKE 'TPL_%';

-- ============================================================================
-- 2. INSERT TIMELINE TEMPLATES (6 templates)
-- ============================================================================

INSERT INTO timeline_templates (
    template_id, template_name, template_type, version, description,
    total_task_count, estimated_duration_days,
    applicable_phases, applicable_authorities, org_id,
    created_at, updated_at
) VALUES
('TPL_001', 'Study Start-Up', 'study_startup', '1.0',
 'Study startup activities from Study Award to FPI',
 86, 180, NULL, NULL, NULL,
 NOW(), NOW()),

('TPL_002', 'Study Implementation/Active Enrollment', 'implementation', '1.0',
 'Study conduct milestones (FPI → LPLV) with recurring activities',
 10, 730, NULL, NULL, NULL,
 NOW(), NOW()),

('TPL_003', 'Study Closeout', 'closeout', '1.0',
 'Study closeout from LPLV to FDA CSR submission',
 23, 300, NULL, NULL, NULL,
 NOW(), NOW()),

('TPL_004', 'Site Activation', 'site_activation', '1.0',
 'Site activation checklist from site selection to site activated',
 34, 90, NULL, NULL, NULL,
 NOW(), NOW()),

('TPL_005', 'Site Closeout', 'site_closeout', '1.0',
 'Site closeout activities by category',
 19, 30, NULL, NULL, NULL,
 NOW(), NOW()),

('TPL_006', 'Full Study Timeline', 'full_study', '1.0',
 'Complete study timeline: Startup + Implementation + Closeout',
 119, 1260, NULL, NULL, NULL,
 NOW(), NOW());

-- ============================================================================
-- 3. INSERT TEMPLATE TASKS (291 tasks)
-- Note: Using Python script to generate this section
-- ============================================================================

-- Template Tasks (291 tasks)

INSERT INTO template_tasks (
    task_id, template_id, task_name, task_code, category,
    typical_duration_days, min_duration_days, max_duration_days, p25_duration_days, p75_duration_days,
    is_milestone, is_critical_path, is_recurring, recurrence_interval_days,
    description, responsible_role, notes,
    parent_task_id, sort_order, outline_level,
    created_at, updated_at
) VALUES
('STARTUP_001', 'TPL_001', 'Internal Transition Meeting
- Confirm date and PM prep tasks, 
- Follow-up on any unassigned resources', NULL, 'Initiation', 1, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 1, 1, NOW(), NOW()),
('STARTUP_002', 'TPL_001', 'Data Visualization Tool (DVT)                           -', NULL, 'Initiation', 1, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 2, 1, NOW(), NOW()),
('STARTUP_003', 'TPL_001', 'US CT.gov
▪ Registration', NULL, 'Study Information', 90, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 3, 1, NOW(), NOW()),
('STARTUP_004', 'TPL_001', 'Master Service Agreement (MSA)', NULL, 'Legal and Finance', 1, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 4, 1, NOW(), NOW()),
('STARTUP_005', 'TPL_001', 'Start-up Agreement (SUA) or full work order with Roles and Responsibilities', NULL, 'Legal and Finance', 14, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 5, 1, NOW(), NOW()),
('STARTUP_006', 'TPL_001', 'Review study contract/budget for understanding on FTE allocation
▪ What roles are assigned to the study?
▪ What tasks are delegated to Innovations?
▪ Functional Lead(s) to review and provide questions/feedback on budget', NULL, 'Legal and Finance', 30, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 6, 1, NOW(), NOW()),
('STARTUP_007', 'TPL_001', 'Financial tracking tools 
▪ Contract/budget tracking
▪ Study/site payment tracking
▪ Vendor payment tracking
▪ Pass-thru tracking', NULL, 'Legal and Finance', 1, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 7, 1, NOW(), NOW()),
('STARTUP_008', 'TPL_001', 'Confidentiality Disclosure Agreement (CDA) for vendors
- Template available?
- Executed?', NULL, 'Legal and Finance', 1, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 8, 1, NOW(), NOW()),
('STARTUP_009', 'TPL_001', 'Site budget/contract 
Sites Contract/Budget Template
▪ Submit protcol and milestones to Finance to initiate draft
▪ Process for review/signatures                                ▪ Required to use CRO template with in-network sites', NULL, 'Legal and Finance', 1, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 9, 1, NOW(), NOW()),
('STARTUP_010', 'TPL_001', 'Invoice approvel:
   -nvoice Review
   -Tracking
>Ensure all items are being checked against EDC, Site Contract', NULL, 'Legal and Finance', 1, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 10, 1, NOW(), NOW()),
('STARTUP_011', 'TPL_001', 'Financial Oversight (Revenue, Forcast, Billing)
▪Finance to schedule monthly review meetings to occur shortly after deadline for PM approval of revenue and forecasting. 
▪Review budget with functional leads
▪Initiate Trackers
   ▪Contract/Budget
   ▪Study Payments w/ Mid-Study Changes
   ▪Site Payments w/Pass-Thru & Screen Failures
   ▪Vendor Payments', NULL, 'Legal and Finance', 30, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 11, 1, NOW(), NOW()),
('STARTUP_012', 'TPL_001', 'Core Team Meetings (aka Internal  Team Meeting)
see FAQ 3 for more details
▪Discuss mandatory/optional attendees 
▪Sends out meeting invite
▪Creates agenda/minutes template for PM review', NULL, 'Meetings', 30, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 12, 1, NOW(), NOW()),
('STARTUP_013', 'TPL_001', 'Project Team/Sponsor Meetings
(See FAQ 4 for more details)
▪Confirm attendee(s)
▪Schedule', NULL, 'Meetings', 14, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 13, 1, NOW(), NOW()),
('STARTUP_014', 'TPL_001', 'Kick-Off Meeting (KOM)
▪ Review budget for allocated resources
▪ Sched KOM
***Confirm availability for Sponsors and SMEs first.
▪ Sched KOM Prep Meeting with internal team', NULL, 'Meetings', 1, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, 'Start preparing for the KOM at least a month in advance if possible.  Slides, Agendas and minutes will be required. PM will ensure the study team is tailoring their presentations to study scope.  

Checklist for KOM planning
- Who? Study Chair attendance: confirm this directly with the Study Chair with their admin in copy and specifically which portions they will be attending; Sponsor attendance and for which portions.
- When? Ensure enough timing is planned for review of slides with Sponsor/internal

-Invite the Regulatory Manager to the KOM; Check to see if any other managers require attendance

*Study Team review of all available study documents will be needed prior to sponsor KOM.*', NULL, 14, 1, NOW(), NOW()),
('STARTUP_015', 'TPL_001', 'Investigator Meeting, if scoped
▪ Schedule after site selection', NULL, 'Meetings', 1, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, 'These may occur at the beginning of the study or following dose escalation to kick-off expansion enrollment and site participation, discuss the IP, administration process, and IP benefits, protocol, etc.', NULL, 15, 1, NOW(), NOW()),
('STARTUP_016', 'TPL_001', 'PM 1:1 Meetings
▪Schedule with Sponsor Counterpart (consider including CTL if appropriate)
▪Schedule with CTL and CPA or separately', NULL, 'Meetings', 1, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, 'Refer to budget for frequency and attendees with Sponsor.  For PM/CTL/CPA touch bases, best to ensure availability; may not be included in contract since this is just an internal process', NULL, 16, 1, NOW(), NOW()),
('STARTUP_017', 'TPL_001', 'Study Start Up Plan', NULL, 'Meetings', 90, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 17, 1, NOW(), NOW()),
('STARTUP_018', 'TPL_001', 'Project Management Plan (PMP)', NULL, 'Meetings', 90, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 18, 1, NOW(), NOW()),
('STARTUP_019', 'TPL_001', 'Timelines (MS Project)', NULL, 'Meetings', 30, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 19, 1, NOW(), NOW()),
('STARTUP_020', 'TPL_001', 'Risk Log', NULL, 'Meetings', 1, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 20, 1, NOW(), NOW()),
('STARTUP_021', 'TPL_001', 'Action Item and Decision Log (AID Log)', NULL, 'Meetings', 30, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 21, 1, NOW(), NOW()),
('STARTUP_022', 'TPL_001', 'Project Team Training Tracker (PT3/PTTT)', NULL, 'Meetings', 30, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 22, 1, NOW(), NOW()),
('STARTUP_023', 'TPL_001', 'Risk Management Plan (RMP)', NULL, 'Meetings', 90, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 23, 1, NOW(), NOW()),
('STARTUP_024', 'TPL_001', 'Trial Master File Plan', NULL, 'Meetings', 7, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 24, 1, NOW(), NOW()),
('STARTUP_025', 'TPL_001', 'eTMF Structure Checklist', NULL, 'Meetings', 7, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 25, 1, NOW(), NOW()),
('STARTUP_026', 'TPL_001', 'Clinical Management Plan', NULL, 'Meetings', 60, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 26, 1, NOW(), NOW()),
('STARTUP_027', 'TPL_001', 'Monitoring Plan', NULL, 'Meetings', 1, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 27, 1, NOW(), NOW()),
('STARTUP_028', 'TPL_001', 'Enrollment Management Plan (EMP)', NULL, 'Meetings', 90, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 28, 1, NOW(), NOW()),
('STARTUP_029', 'TPL_001', 'Protocol Deviation Management Plan', NULL, 'Meetings', 90, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 29, 1, NOW(), NOW()),
('STARTUP_030', 'TPL_001', 'SIV Training Slides', NULL, 'Meetings', 90, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 30, 1, NOW(), NOW()),
('STARTUP_031', 'TPL_001', 'Study Reference Manual', NULL, 'Meetings', 90, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 31, 1, NOW(), NOW()),
('STARTUP_032', 'TPL_001', 'Lab Manual', NULL, 'Meetings', 90, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 32, 1, NOW(), NOW()),
('STARTUP_033', 'TPL_001', 'Pharmacy Manual/Dosing Instructions', NULL, 'Meetings', 90, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 33, 1, NOW(), NOW()),
('STARTUP_034', 'TPL_001', 'Data Management Plan (DMP)', NULL, 'Meetings', 45, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 34, 1, NOW(), NOW()),
('STARTUP_035', 'TPL_001', 'CRF Completion Guidelines', NULL, 'Meetings', 45, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 35, 1, NOW(), NOW()),
('STARTUP_036', 'TPL_001', 'Safety Monitoring Plan (SMP)', NULL, 'Meetings', 90, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 36, 1, NOW(), NOW()),
('STARTUP_037', 'TPL_001', 'Statistical Analysis Plan (SAP)', NULL, 'Meetings', 14, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 37, 1, NOW(), NOW()),
('STARTUP_038', 'TPL_001', 'Medical Monitoring Plan', NULL, 'Meetings', 60, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 38, 1, NOW(), NOW()),
('STARTUP_039', 'TPL_001', 'Subject Enrollment Form (SEF)', NULL, 'Meetings', 60, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 39, 1, NOW(), NOW()),
('STARTUP_040', 'TPL_001', 'Quality Management Plan', NULL, 'Meetings', 1, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 40, 1, NOW(), NOW()),
('STARTUP_041', 'TPL_001', 'Site Feasibility Questionnaire (SFQ)', NULL, 'Meetings', 1, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 41, 1, NOW(), NOW()),
('STARTUP_042', 'TPL_001', 'CTMS and eTMF setup
▪PM Submit Study Setup Request for ▪ TMF structure checklist sign-off
▪ Sponsor requirements
  ◦ Review of documents/TMF
  ◦ Document submission requirements
  ◦ Verify creation of files (check SOP for timeline)', NULL, 'Infrastructural/Systems Setup', 1, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 42, 1, NOW(), NOW()),
('STARTUP_043', 'TPL_001', 'Review & setup milestones in Veeva', NULL, 'Infrastructural/Systems Setup', 1, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 43, 1, NOW(), NOW()),
('STARTUP_044', 'TPL_001', 'Protocol/ICF development
▪ Tracking tools
▪ Review and feedback', NULL, 'Infrastructural/Systems Setup', 1, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 44, 1, NOW(), NOW()),
('STARTUP_045', 'TPL_001', 'Project Dashboard
▪ Initiate dashboard with original study specifications', NULL, 'Infrastructural/Systems Setup', 30, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 45, 1, NOW(), NOW()),
('STARTUP_046', 'TPL_001', 'Establish process/format for study reports to be shared/sent to sponsor
▪  Web portal
▪  Access/training if needed', NULL, 'Infrastructural/Systems Setup', 1, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 46, 1, NOW(), NOW()),
('STARTUP_047', 'TPL_001', 'EDC Set up/ Account Access                                                                   ▪ Initial Account Set up                                                ▪ User Access Requests', NULL, 'Infrastructural/Systems Setup', 7, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 47, 1, NOW(), NOW()),
('STARTUP_048', 'TPL_001', 'IP contact information
▪ Sponsor
▪ Vendor', NULL, 'Drug Supply Chain', 90, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 48, 1, NOW(), NOW()),
('STARTUP_049', 'TPL_001', 'Establish drug release process', NULL, 'Drug Supply Chain', 90, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 49, 1, NOW(), NOW()),
('STARTUP_050', 'TPL_001', 'IP distribution', NULL, 'Drug Supply Chain', 90, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 50, 1, NOW(), NOW());

INSERT INTO template_tasks (
    task_id, template_id, task_name, task_code, category,
    typical_duration_days, min_duration_days, max_duration_days, p25_duration_days, p75_duration_days,
    is_milestone, is_critical_path, is_recurring, recurrence_interval_days,
    description, responsible_role, notes,
    parent_task_id, sort_order, outline_level,
    created_at, updated_at
) VALUES
('STARTUP_051', 'TPL_001', 'Labeling
▪  who is responsible', NULL, 'Drug Supply Chain', 90, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 51, 1, NOW(), NOW()),
('STARTUP_052', 'TPL_001', 'International
▪ Labeling
▪ commercial availability', NULL, 'Drug Supply Chain', 90, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 52, 1, NOW(), NOW()),
('STARTUP_053', 'TPL_001', 'Generic substitution acceptable?', NULL, 'Drug Supply Chain', 90, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 53, 1, NOW(), NOW()),
('STARTUP_054', 'TPL_001', 'Service Providers

▪ Number of Vendors to be used', NULL, 'Vendors', 1, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 54, 1, NOW(), NOW()),
('STARTUP_055', 'TPL_001', 'Vendor identification
▪ Do vendors need to be identified?
▪ IP Depot
▪ Central labs
▪ Central imaging
▪ Other "study specific" central lab
▪ IVRS?
▪ Impact on any other functional areas', NULL, 'Vendors', 1, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 55, 1, NOW(), NOW()),
('STARTUP_056', 'TPL_001', 'Vendor model, e.g.
▪Contracts/manages?
▪ Sponsor contracts/manages?
▪ Sponsor contracts and Innovations manages?', NULL, 'Vendors', 1, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 56, 1, NOW(), NOW()),
('STARTUP_057', 'TPL_001', 'Vendor(s) setup
▪ manual
▪ UAT required?
▪ Budget/contracts for vendors setup
▪ Access for vendor systems requested', NULL, 'Vendors', 1, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 57, 1, NOW(), NOW()),
('STARTUP_058', 'TPL_001', 'Central IRB
▪ Name of IRB
▪ Which sites will use', NULL, 'Vendors', 1, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 58, 1, NOW(), NOW()),
('STARTUP_059', 'TPL_001', 'Country Level Reg Submission', NULL, 'Vendors', 1, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 59, 1, NOW(), NOW()),
('STARTUP_060', 'TPL_001', 'International:
▪  Import/export license requirement', NULL, 'Vendors', 1, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 60, 1, NOW(), NOW()),
('STARTUP_061', 'TPL_001', 'Onboarding
See FAQ 14
▪ Add/Update PT3 tracker
▪ Training slides (sponsor?)
 - Conduct/schedule team training
▪ Protocol
▪ Therapeutic training with Medical Monitor
▪ Investigator''s Brochure (IB)
▪ SIV
▪ EDC
▪ Study plans/procedures
▪ Guidelines
▪ Study SOPs/Sponosr SOPs', NULL, 'Training', 14, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 61, 1, NOW(), NOW()),
('STARTUP_062', 'TPL_001', 'SOPs need to be shared with sponsor?', NULL, 'Training', 1, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 62, 1, NOW(), NOW()),
('STARTUP_063', 'TPL_001', 'Obtain any sponsor-required SOPs', NULL, 'Training', 1, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 63, 1, NOW(), NOW()),
('STARTUP_064', 'TPL_001', 'CRA Study Planning using CRA resourcing form', NULL, 'Training', 1, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 64, 1, NOW(), NOW()),
('STARTUP_065', 'TPL_001', 'Laboratory sample tracker (as needed)', NULL, 'Delegated:  Clinical/Regulatory Affairs', 1, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 65, 1, NOW(), NOW()),
('STARTUP_066', 'TPL_001', 'Slot Management Tracker', NULL, 'Delegated:  Clinical/Regulatory Affairs', 90, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 66, 1, NOW(), NOW()),
('STARTUP_067', 'TPL_001', 'Site List Request', NULL, 'Delegated:  Clinical/Regulatory Affairs', 1, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 67, 1, NOW(), NOW()),
('STARTUP_068', 'TPL_001', 'Sharepoint folder setup', NULL, 'Delegated:  Clinical/Regulatory Affairs', 14, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 68, 1, NOW(), NOW()),
('STARTUP_069', 'TPL_001', 'Electronic mailbox setup (PM)', NULL, 'Delegated:  Clinical/Regulatory Affairs', 14, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 69, 1, NOW(), NOW()),
('STARTUP_070', 'TPL_001', 'Site Essential Document Review', NULL, 'Delegated:  Clinical/Regulatory Affairs', 14, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 70, 1, NOW(), NOW()),
('STARTUP_071', 'TPL_001', 'Startup Tracking (Start-up is responsible)
▪ Site selection/final site list
▪ Site activation projection tracker                      ▪ Feasibility tracker', NULL, 'Delegated:  Clinical/Regulatory Affairs', 1, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 71, 1, NOW(), NOW()),
('STARTUP_072', 'TPL_001', '1572', NULL, 'Delegated:  Clinical/Regulatory Affairs', 7, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 72, 1, NOW(), NOW()),
('STARTUP_073', 'TPL_001', 'Country/site feasibility (Start-up is responsible)
▪ Country selection
▪ Site ID
▪ Site selection', NULL, 'Delegated:  Clinical/Regulatory Affairs', 1, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 73, 1, NOW(), NOW()),
('STARTUP_074', 'TPL_001', 'Central and Local IRB submission completed?', NULL, 'Delegated:  Clinical/Regulatory Affairs', 1, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 74, 1, NOW(), NOW()),
('STARTUP_075', 'TPL_001', 'Ensure Innovations CVs current and filed', NULL, 'Delegated:  Clinical/Regulatory Affairs', 1, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 75, 1, NOW(), NOW()),
('STARTUP_076', 'TPL_001', 'Database build timelines sent to you?
▪ Ensure scheduling or timelines are established for periodic database cuts and lock', NULL, 'Delegated:  Clinical/Regulatory Affairs', 90, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 76, 1, NOW(), NOW()),
('STARTUP_077', 'TPL_001', 'Program for patient profiles
Program for derived data sets', NULL, 'Delegated:  Data Management/Biostistics', 90, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 77, 1, NOW(), NOW()),
('STARTUP_078', 'TPL_001', 'Case Report Form (CRF) started?', NULL, 'Delegated:  Data Management/Biostistics', 90, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 78, 1, NOW(), NOW()),
('STARTUP_079', 'TPL_001', 'CRF Completion Guidelines started?', NULL, 'Delegated:  Data Management/Biostistics', 90, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 79, 1, NOW(), NOW()),
('STARTUP_080', 'TPL_001', 'Data Transfer Agreement(s) (DTA)', NULL, 'Delegated:  Data Management/Biostistics', 7, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 80, 1, NOW(), NOW()),
('STARTUP_081', 'TPL_001', 'Argus Database Build Initiated', NULL, 'Delegated:  Data Management/Biostistics', 90, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 81, 1, NOW(), NOW()),
('STARTUP_082', 'TPL_001', 'SAE form created?', NULL, 'Delegated:  Safety', 90, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 82, 1, NOW(), NOW()),
('STARTUP_083', 'TPL_001', 'Pregnancy Form created?', NULL, 'Delegated:  Safety', 90, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 83, 1, NOW(), NOW()),
('STARTUP_084', 'TPL_001', 'Protocol Writing/Finalization', NULL, 'Delegated:  Medical Writing', 1, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 84, 1, NOW(), NOW()),
('STARTUP_085', 'TPL_001', 'Investigator Brochure (IB) writing', NULL, 'Delegated:  Medical Writing', 1, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 85, 1, NOW(), NOW()),
('STARTUP_086', 'TPL_001', 'Informed Consent Form (ICF) writing', NULL, 'Delegated:  Medical Writing', 1, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 86, 1, NOW(), NOW()),
('IMPL_001', 'TPL_002', 'First Person In (FPI)', 'FPI', 'Study Conduct', 1, NULL, NULL, NULL, NULL, 1, 0, 0, NULL, 'First participant enrolled in the study', NULL, NULL, NULL, 1, 1, NOW(), NOW()),
('IMPL_002', 'TPL_002', 'First Person Dosed (FPD)', 'FPD', 'Study Conduct', 1, NULL, NULL, NULL, NULL, 1, 0, 0, NULL, 'First participant receives study intervention/drug', NULL, NULL, NULL, 2, 1, NOW(), NOW()),
('IMPL_003', 'TPL_002', 'First Cohort Review (FCR)', 'FCR', 'Study Conduct', 1, NULL, NULL, NULL, NULL, 1, 0, 0, NULL, 'Review of first cohort data before proceeding (if applicable)', NULL, NULL, NULL, 3, 1, NOW(), NOW()),
('IMPL_004', 'TPL_002', 'Last Patient In (LPI)', 'LPI', 'Study Conduct', 1, NULL, NULL, NULL, NULL, 1, 0, 0, NULL, 'Last participant enrolled in the study', NULL, NULL, NULL, 4, 1, NOW(), NOW()),
('IMPL_005', 'TPL_002', 'Last Person Dosed (LPD)', 'LPD', 'Study Conduct', 1, NULL, NULL, NULL, NULL, 1, 0, 0, NULL, 'Last participant receives final dose of study intervention', NULL, NULL, NULL, 5, 1, NOW(), NOW()),
('IMPL_006', 'TPL_002', 'Last Participant Last Visit (LPLV)', 'LPLV', 'Study Conduct', 1, NULL, NULL, NULL, NULL, 1, 0, 0, NULL, 'Last participant completes final study visit', NULL, NULL, NULL, 6, 1, NOW(), NOW()),
('IMPL_007', 'TPL_002', 'Last Specimen Collection', 'LSC', 'Study Conduct', 1, NULL, NULL, NULL, NULL, 1, 0, 0, NULL, 'Final biological specimen collected from last participant', NULL, NULL, NULL, 7, 1, NOW(), NOW()),
('IMPL_008', 'TPL_002', 'Follow Up', 'FOLLOW_UP', 'Study Conduct', 1, NULL, NULL, NULL, NULL, 1, 0, 0, NULL, 'Post-study follow-up period', NULL, NULL, NULL, 8, 1, NOW(), NOW()),
('IMPL_009', 'TPL_002', 'IRB Continuing Review', 'IRB_REVIEW', 'Study Conduct', 1, NULL, NULL, NULL, NULL, 0, 0, 1, 365, 'Ongoing throughout study conduct', NULL, NULL, NULL, 9, 1, NOW(), NOW()),
('IMPL_010', 'TPL_002', 'FDA Annual Report', 'FDA_ANNUAL', 'Study Conduct', 1, NULL, NULL, NULL, NULL, 0, 0, 1, 365, 'Submit 60 days within anniversary date the IND went into effect (if sponsor of IND)', NULL, NULL, NULL, 10, 1, NOW(), NOW()),
('CDB_001', 'TPL_003', 'Clinical data entry completed', 'CDB_001', 'Data Management', 4, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, '4 days after last subject, last visit', NULL, NULL, NULL, 1, 1, NOW(), NOW()),
('CDB_002', 'TPL_003', 'Data cleaning and querying', 'CDB_002', 'Data Management', 14, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, '2 weeks after data entry completion', NULL, NULL, NULL, 2, 1, NOW(), NOW()),
('CDB_003', 'TPL_003', 'Serious Adverse Event reconciliation', 'CDB_003', 'Safety', 21, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, '3 weeks after data entry completion', NULL, NULL, NULL, 3, 1, NOW(), NOW()),
('CDB_004', 'TPL_003', 'Final monitoring visit', 'CDB_004', 'Monitoring', 35, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, '5 weeks after last subject, last visit', NULL, NULL, NULL, 4, 1, NOW(), NOW());

INSERT INTO template_tasks (
    task_id, template_id, task_name, task_code, category,
    typical_duration_days, min_duration_days, max_duration_days, p25_duration_days, p75_duration_days,
    is_milestone, is_critical_path, is_recurring, recurrence_interval_days,
    description, responsible_role, notes,
    parent_task_id, sort_order, outline_level,
    created_at, updated_at
) VALUES
('CDB_005', 'TPL_003', 'Resolution of all data management and monitoring queries', 'CDB_005', 'Data Management', 1, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, '1 day after final monitoring visit', NULL, NULL, NULL, 5, 1, NOW(), NOW()),
('CDB_006', 'TPL_003', 'Clinical database lock', 'CDB_006', 'Data Management', 1, NULL, NULL, NULL, NULL, 1, 0, 0, NULL, '1 day after resolution of all queries', NULL, NULL, NULL, 6, 1, NOW(), NOW()),
('LDB_001', 'TPL_003', 'Assay completion and transfer of laboratory data', 'LDB_001', 'Laboratory', 84, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, '12 weeks after last specimen collection', NULL, NULL, NULL, 7, 1, NOW(), NOW()),
('LDB_002', 'TPL_003', 'QC of laboratory data and distribution of queries', 'LDB_002', 'Laboratory', 4, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, '4 days after receipt of laboratory data', NULL, NULL, NULL, 8, 1, NOW(), NOW()),
('LDB_003', 'TPL_003', 'Resolution of laboratory queries', 'LDB_003', 'Laboratory', 7, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, '1 week after distribution of queries', NULL, NULL, NULL, 9, 1, NOW(), NOW()),
('LDB_004', 'TPL_003', 'Laboratory database lock', 'LDB_004', 'Laboratory', 1, NULL, NULL, NULL, NULL, 1, 0, 0, NULL, '1 day after resolution of lab queries', NULL, NULL, NULL, 10, 1, NOW(), NOW()),
('CSR_001', 'TPL_003', 'Preparation of draft Interim CSR', 'CSR_001', 'Regulatory', 84, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, '12 weeks after clinical AND laboratory database lock', NULL, NULL, NULL, 11, 1, NOW(), NOW()),
('CSR_002', 'TPL_003', 'PVG provides SAE narratives', 'CSR_002', 'Safety', 30, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, '30 days after clinical database lock', NULL, NULL, NULL, 12, 1, NOW(), NOW()),
('CSR_003', 'TPL_003', 'Distribute draft Interim CSR to PI for review', 'CSR_003', 'Regulatory', 1, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, '1 day after draft CSR complete', NULL, NULL, NULL, 13, 1, NOW(), NOW()),
('CSR_004', 'TPL_003', 'PI reviews and completes designated sections of CSR', 'CSR_004', 'Regulatory', 35, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, '4-6 weeks after distribution of draft CSR', NULL, NULL, NULL, 14, 1, NOW(), NOW()),
('CSR_005', 'TPL_003', 'Incorporate PI text, address comments, format CSR', 'CSR_005', 'Regulatory', 7, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, '1 week after receiving draft CSR from PI', NULL, NULL, NULL, 15, 1, NOW(), NOW()),
('CSR_006', 'TPL_003', 'Distribute draft CSR to DMID and PI for review', 'CSR_006', 'Regulatory', 1, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, '1 day after draft CSR complete', NULL, NULL, NULL, 16, 1, NOW(), NOW()),
('CSR_007', 'TPL_003', 'DMID reviews draft CSR and provides comments', 'CSR_007', 'Regulatory', 28, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, '4 weeks after distribution to DMID', NULL, NULL, NULL, 17, 1, NOW(), NOW()),
('CSR_008', 'TPL_003', 'Incorporate DMID comments and prepare final draft CSR', 'CSR_008', 'Regulatory', 7, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, '1 week after receipt of DMID comments', NULL, NULL, NULL, 18, 1, NOW(), NOW()),
('CSR_009', 'TPL_003', 'Receive DMID and PI approval to finalize CSR', 'CSR_009', 'Regulatory', 3, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, '3 days after final draft distributed', NULL, NULL, NULL, 19, 1, NOW(), NOW()),
('CSR_010', 'TPL_003', 'Prepare approved CSR per regulatory requirements', 'CSR_010', 'Regulatory', 3, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, '3 days after approval to finalize', NULL, NULL, NULL, 20, 1, NOW(), NOW()),
('CSR_011', 'TPL_003', 'Lead PI signs signature page and returns', 'CSR_011', 'Regulatory', 3, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, '3 days after notification of approved CSR', NULL, NULL, NULL, 21, 1, NOW(), NOW()),
('CSR_012', 'TPL_003', 'Distribute approved CSR to CROMS portals', 'CSR_012', 'Regulatory', 1, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, '1 day after receipt of PI signature', NULL, NULL, NULL, 22, 1, NOW(), NOW()),
('CSR_013', 'TPL_003', 'RAS submits final, signed CSR to FDA', 'CSR_013', 'Regulatory', 17, NULL, NULL, NULL, NULL, 1, 0, 0, NULL, '2-3 weeks after signature page posted', NULL, NULL, NULL, 23, 1, NOW(), NOW()),
('SITEACT_001', 'TPL_004', 'Site essential documents (including IRB approvals) collected and uploaded', NULL, 'Documents, Training and Funding', 3, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 1, 1, NOW(), NOW()),
('SITEACT_002', 'TPL_004', 'Investigator Brochure(s) (IB)/Package Insert', NULL, 'Documents, Training and Funding', 3, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '1', NULL, 2, 1, NOW(), NOW()),
('SITEACT_003', 'TPL_004', 'Final PSRL for activation purposes', NULL, 'Documents, Training and Funding', 3, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 3, 1, NOW(), NOW()),
('SITEACT_004', 'TPL_004', 'Site staff HSP and GCP training received and current (see PSRL for staff list)', NULL, 'Documents, Training and Funding', 3, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 4, 1, NOW(), NOW()),
('SITEACT_005', 'TPL_004', 'Attestation from site PI of site staff Sponsor training received and current (see PSRL for staff list)', NULL, 'Documents, Training and Funding', 3, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 5, 1, NOW(), NOW()),
('SITEACT_006', 'TPL_004', 'Individual site staff training documentation', NULL, 'Documents, Training and Funding', 3, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '1) Good Clinical Practice (GCP)
2) Human Subjects Protection (HSP)	
3) Sponsor and/or CRO training modules
4) Protocol training
5) Any additional relevant training (ex., laboratory, database, drug preparation and accountability, regulatory, etc.)', NULL, 6, 1, NOW(), NOW()),
('SITEACT_007', 'TPL_004', 'Study Product Management Plan (SPMP)/protocol specific SPMP in place', NULL, 'Clinical Quality Management Plan (CQMP)/protocol specific CQMP in place (i.e., reviewed within the past year)', 3, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, 'Site Pharmacist to confirm the SPMP applies to the current study product. If the current plan does not cover the needs of the study, the pharmacist will update the SPMP as needed and submit to Sponsor or CRO for approval.', NULL, 7, 1, NOW(), NOW()),
('SITEACT_008', 'TPL_004', 'Site visits conducted:', NULL, 'Clinical Quality Management Plan (CQMP)/protocol specific CQMP in place (i.e., reviewed within the past year)', 3, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 8, 1, NOW(), NOW()),
('SITEACT_009', 'TPL_004', 'SIV (refresher) training (>30 days before activated) If applicable', NULL, 'Clinical Quality Management Plan (CQMP)/protocol specific CQMP in place (i.e., reviewed within the past year)', 3, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 9, 1, NOW(), NOW()),
('SITEACT_010', 'TPL_004', 'Safety oversight: DSMB/SMC organizational meeting held', NULL, 'Clinical Quality Management Plan (CQMP)/protocol specific CQMP in place (i.e., reviewed within the past year)', 3, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 10, 1, NOW(), NOW()),
('SITEACT_011', 'TPL_004', 'Manual of Procedures (with version and date) (Draft is acceptable for training; v1.0 is needed for activation)', NULL, 'Data Management', 3, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, 'Version:', NULL, 11, 1, NOW(), NOW()),
('SITEACT_012', 'TPL_004', 'Confirmation from SDCC that all required database training is complete', NULL, 'Data Management', 3, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 12, 1, NOW(), NOW()),
('SITEACT_013', 'TPL_004', 'eCRFs are programmed for Direct Data Entry (DDE)', NULL, 'Data Management', 3, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, 'If applicable', NULL, 13, 1, NOW(), NOW()),
('SITEACT_014', 'TPL_004', 'Site PI has appropriate access in the database and has delegated data entry capabilities to study staff', NULL, 'Data Management', 3, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 14, 1, NOW(), NOW()),
('SITEACT_015', 'TPL_004', 'Paper DCFs/CRFs accessible to sites (back-ups if using DDE)', NULL, 'Data Management', 3, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 15, 1, NOW(), NOW()),
('SITEACT_016', 'TPL_004', 'Data Management training completed', NULL, 'Data Management', 3, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 16, 1, NOW(), NOW()),
('SITEACT_017', 'TPL_004', 'Database deployed', NULL, 'Data Management', 3, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 17, 1, NOW(), NOW()),
('SITEACT_018', 'TPL_004', 'Draft Statistical Analysis Plan is in place or appropriate statistical section of protocol.', NULL, 'Data Management', 3, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 18, 1, NOW(), NOW()),
('SITEACT_019', 'TPL_004', 'List of blinded and unblinded site pharmacist(s) on the PSRL with documented training. Email pharmacist names, Blinded vs. Unblinded, email addresses, & site name to the Data Manager with the CPM cc’ed for database access (only applicable to interventional trials)', NULL, 'Pharmacy', 3, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 19, 1, NOW(), NOW()),
('SITEACT_020', 'TPL_004', 'Randomization process (codes) (and unblinding table) complete and at site as confirmed by Data Manager', NULL, 'Pharmacy', 3, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 20, 1, NOW(), NOW()),
('SITEACT_021', 'TPL_004', 'Lab Specimens/Assay table & Central Assay Plan (CAP) completed', NULL, 'Laboratory', 3, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 21, 1, NOW(), NOW()),
('SITEACT_022', 'TPL_004', 'Sites have LDMS installed, and equipment tested for sample tracking (SCHARP only)', NULL, 'Laboratory', 3, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 22, 1, NOW(), NOW()),
('SITEACT_023', 'TPL_004', 'Sites have the necessary bar code scanner/software to utilize GlobalTrace tracking system for specimens collected and have necessary labels (Emmes only)', NULL, 'Laboratory', 3, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 23, 1, NOW(), NOW()),
('SITEACT_024', 'TPL_004', 'Clinical Trial Agreement (CTA) or Memo of Understanding (MOU) executed (as applicable)', NULL, 'To be discussed with CPM', 3, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 24, 1, NOW(), NOW()),
('SITEACT_025', 'TPL_004', 'National Library of Medicine (NLM) submission for clinicaltrials.gov (NCT # assigned).', NULL, 'To be discussed with CPM', 3, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, 'CPM to complete.
Not required for activation; to be submitted no later than 21 days after enrollment of first subject (21 CFR 11.24)', NULL, 25, 1, NOW(), NOW()),
('SITEACT_026', 'TPL_004', 'Study product available for distribution *location of product may vary per protocol', NULL, 'To be discussed with CPM', 3, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 26, 1, NOW(), NOW()),
('SITEACT_027', 'TPL_004', 'Clinical Monitoring Plan in place
(CPM’s verbal confirmation is acceptable.)', NULL, 'To be discussed with CPM', 3, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 27, 1, NOW(), NOW()),
('SITEACT_028', 'TPL_004', 'If conducted under IND, date of initial submission to FDA', NULL, 'To be discussed with CPM', 3, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 28, 1, NOW(), NOW()),
('SITEACT_029', 'TPL_004', 'Sites have necessary lab and clinical supplies onsite', NULL, 'To confirm with sites (may not be required for activation)', 3, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 29, 1, NOW(), NOW()),
('SITEACT_030', 'TPL_004', 'Sites have participant reimbursement cards or other mechanisms available for compensation', NULL, 'To confirm with sites (may not be required for activation)', 3, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 30, 1, NOW(), NOW()),
('SITEACT_031', 'TPL_004', 'Site funding / budget in place', NULL, 'Approvals', 3, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 31, 1, NOW(), NOW());

INSERT INTO template_tasks (
    task_id, template_id, task_name, task_code, category,
    typical_duration_days, min_duration_days, max_duration_days, p25_duration_days, p75_duration_days,
    is_milestone, is_critical_path, is_recurring, recurrence_interval_days,
    description, responsible_role, notes,
    parent_task_id, sort_order, outline_level,
    created_at, updated_at
) VALUES
('SITEACT_032', 'TPL_004', 'No outstanding major issues from SAV or SIV', NULL, 'Approvals', 3, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 32, 1, NOW(), NOW()),
('SITEACT_033', 'TPL_004', 'Confirmation of lab readiness.', NULL, 'Approvals', 3, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 33, 1, NOW(), NOW()),
('SITEACT_034', 'TPL_004', 'Confirmation from that all required agreements (MTAs, DTAs, etc) are in place', NULL, 'Approvals', 3, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, 'MTAs involving international sites, particularly if they relate to transfer of materials out of the country, may need to be approved by the in-country regulatory authority.', NULL, 34, 1, NOW(), NOW()),
('SITECLOSE_001', 'TPL_005', 'Determine IRB close-out reporting requirements', NULL, 'Regulatory', 3, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL, 1, 1, NOW(), NOW()),
('SITECLOSE_002', 'TPL_005', 'Submit final IRB report to PS', NULL, 'Regulatory', 2, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL, 2, 1, NOW(), NOW()),
('SITECLOSE_003', 'TPL_005', 'Complete regulatory binder with all essential documents', NULL, 'Regulatory', 5, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL, 3, 1, NOW(), NOW()),
('SITECLOSE_004', 'TPL_005', 'Report all protocol deviations, unblinding, and SAEs to DMID', NULL, 'Regulatory', 3, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL, 4, 1, NOW(), NOW()),
('SITECLOSE_005', 'TPL_005', 'Provide final study personnel log to FHI360', NULL, 'Regulatory', 1, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL, 5, 1, NOW(), NOW()),
('SITECLOSE_006', 'TPL_005', 'Verify all consent forms on file', NULL, 'Human Subjects', 2, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL, 6, 1, NOW(), NOW()),
('SITECLOSE_007', 'TPL_005', 'Confirm post-study specimen storage consent list', NULL, 'Human Subjects', 2, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL, 7, 1, NOW(), NOW()),
('SITECLOSE_008', 'TPL_005', 'Contact participants with ongoing AEs', NULL, 'Human Subjects', 14, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL, 8, 1, NOW(), NOW()),
('SITECLOSE_009', 'TPL_005', 'Resolve all AE queries', NULL, 'Human Subjects', 7, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL, 9, 1, NOW(), NOW()),
('SITECLOSE_010', 'TPL_005', 'Dispose of remaining study product with monitor present', NULL, 'Study Product', 1, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL, 10, 1, NOW(), NOW()),
('SITECLOSE_011', 'TPL_005', 'Facilitate site close-out visit', NULL, 'Close-out Monitoring', 1, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL, 11, 1, NOW(), NOW()),
('SITECLOSE_012', 'TPL_005', 'Resolve all monitoring issues', NULL, 'Close-out Monitoring', 7, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL, 12, 1, NOW(), NOW()),
('SITECLOSE_013', 'TPL_005', 'Download and save all participant data', NULL, 'Close-out Monitoring', 1, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL, 13, 1, NOW(), NOW()),
('SITECLOSE_014', 'TPL_005', 'Complete all paper and electronic CRFs', NULL, 'Data Management', 3, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL, 14, 1, NOW(), NOW()),
('SITECLOSE_015', 'TPL_005', 'Resolve all outstanding queries', NULL, 'Data Management', 7, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL, 15, 1, NOW(), NOW()),
('SITECLOSE_016', 'TPL_005', 'Verify all specimens sent to labs', NULL, 'Laboratory Specimens', 2, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL, 16, 1, NOW(), NOW()),
('SITECLOSE_017', 'TPL_005', 'Confirm specimen retention/disposal per consent', NULL, 'Laboratory Specimens', 3, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL, 17, 1, NOW(), NOW()),
('SITECLOSE_018', 'TPL_005', 'Plan long-term storage per protocol', NULL, 'Record Retention', 2, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL, 18, 1, NOW(), NOW()),
('SITECLOSE_019', 'TPL_005', 'Obtain authorization from COU and DMID', NULL, 'Record Retention', 5, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, NULL, NULL, 19, 1, NOW(), NOW()),
('FULL_001', 'TPL_006', 'Internal Transition Meeting
- Confirm date and PM prep tasks, 
- Follow-up on any unassigned resources', NULL, 'Initiation', 1, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 1, 1, NOW(), NOW()),
('FULL_002', 'TPL_006', 'Data Visualization Tool (DVT)                           -', NULL, 'Initiation', 1, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 2, 1, NOW(), NOW()),
('FULL_003', 'TPL_006', 'US CT.gov
▪ Registration', NULL, 'Study Information', 90, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 3, 1, NOW(), NOW()),
('FULL_004', 'TPL_006', 'Master Service Agreement (MSA)', NULL, 'Legal and Finance', 1, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 4, 1, NOW(), NOW()),
('FULL_005', 'TPL_006', 'Start-up Agreement (SUA) or full work order with Roles and Responsibilities', NULL, 'Legal and Finance', 14, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 5, 1, NOW(), NOW()),
('FULL_006', 'TPL_006', 'Review study contract/budget for understanding on FTE allocation
▪ What roles are assigned to the study?
▪ What tasks are delegated to Innovations?
▪ Functional Lead(s) to review and provide questions/feedback on budget', NULL, 'Legal and Finance', 30, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 6, 1, NOW(), NOW()),
('FULL_007', 'TPL_006', 'Financial tracking tools 
▪ Contract/budget tracking
▪ Study/site payment tracking
▪ Vendor payment tracking
▪ Pass-thru tracking', NULL, 'Legal and Finance', 1, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 7, 1, NOW(), NOW()),
('FULL_008', 'TPL_006', 'Confidentiality Disclosure Agreement (CDA) for vendors
- Template available?
- Executed?', NULL, 'Legal and Finance', 1, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 8, 1, NOW(), NOW()),
('FULL_009', 'TPL_006', 'Site budget/contract 
Sites Contract/Budget Template
▪ Submit protcol and milestones to Finance to initiate draft
▪ Process for review/signatures                                ▪ Required to use CRO template with in-network sites', NULL, 'Legal and Finance', 1, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 9, 1, NOW(), NOW()),
('FULL_010', 'TPL_006', 'Invoice approvel:
   -nvoice Review
   -Tracking
>Ensure all items are being checked against EDC, Site Contract', NULL, 'Legal and Finance', 1, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 10, 1, NOW(), NOW()),
('FULL_011', 'TPL_006', 'Financial Oversight (Revenue, Forcast, Billing)
▪Finance to schedule monthly review meetings to occur shortly after deadline for PM approval of revenue and forecasting. 
▪Review budget with functional leads
▪Initiate Trackers
   ▪Contract/Budget
   ▪Study Payments w/ Mid-Study Changes
   ▪Site Payments w/Pass-Thru & Screen Failures
   ▪Vendor Payments', NULL, 'Legal and Finance', 30, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 11, 1, NOW(), NOW()),
('FULL_012', 'TPL_006', 'Core Team Meetings (aka Internal  Team Meeting)
see FAQ 3 for more details
▪Discuss mandatory/optional attendees 
▪Sends out meeting invite
▪Creates agenda/minutes template for PM review', NULL, 'Meetings', 30, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 12, 1, NOW(), NOW()),
('FULL_013', 'TPL_006', 'Project Team/Sponsor Meetings
(See FAQ 4 for more details)
▪Confirm attendee(s)
▪Schedule', NULL, 'Meetings', 14, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 13, 1, NOW(), NOW()),
('FULL_014', 'TPL_006', 'Kick-Off Meeting (KOM)
▪ Review budget for allocated resources
▪ Sched KOM
***Confirm availability for Sponsors and SMEs first.
▪ Sched KOM Prep Meeting with internal team', NULL, 'Meetings', 1, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, 'Start preparing for the KOM at least a month in advance if possible.  Slides, Agendas and minutes will be required. PM will ensure the study team is tailoring their presentations to study scope.  

Checklist for KOM planning
- Who? Study Chair attendance: confirm this directly with the Study Chair with their admin in copy and specifically which portions they will be attending; Sponsor attendance and for which portions.
- When? Ensure enough timing is planned for review of slides with Sponsor/internal

-Invite the Regulatory Manager to the KOM; Check to see if any other managers require attendance

*Study Team review of all available study documents will be needed prior to sponsor KOM.*', NULL, 14, 1, NOW(), NOW()),
('FULL_015', 'TPL_006', 'Investigator Meeting, if scoped
▪ Schedule after site selection', NULL, 'Meetings', 1, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, 'These may occur at the beginning of the study or following dose escalation to kick-off expansion enrollment and site participation, discuss the IP, administration process, and IP benefits, protocol, etc.', NULL, 15, 1, NOW(), NOW()),
('FULL_016', 'TPL_006', 'PM 1:1 Meetings
▪Schedule with Sponsor Counterpart (consider including CTL if appropriate)
▪Schedule with CTL and CPA or separately', NULL, 'Meetings', 1, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, 'Refer to budget for frequency and attendees with Sponsor.  For PM/CTL/CPA touch bases, best to ensure availability; may not be included in contract since this is just an internal process', NULL, 16, 1, NOW(), NOW()),
('FULL_017', 'TPL_006', 'Study Start Up Plan', NULL, 'Meetings', 90, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 17, 1, NOW(), NOW()),
('FULL_018', 'TPL_006', 'Project Management Plan (PMP)', NULL, 'Meetings', 90, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 18, 1, NOW(), NOW()),
('FULL_019', 'TPL_006', 'Timelines (MS Project)', NULL, 'Meetings', 30, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 19, 1, NOW(), NOW()),
('FULL_020', 'TPL_006', 'Risk Log', NULL, 'Meetings', 1, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 20, 1, NOW(), NOW()),
('FULL_021', 'TPL_006', 'Action Item and Decision Log (AID Log)', NULL, 'Meetings', 30, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 21, 1, NOW(), NOW()),
('FULL_022', 'TPL_006', 'Project Team Training Tracker (PT3/PTTT)', NULL, 'Meetings', 30, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 22, 1, NOW(), NOW()),
('FULL_023', 'TPL_006', 'Risk Management Plan (RMP)', NULL, 'Meetings', 90, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 23, 1, NOW(), NOW()),
('FULL_024', 'TPL_006', 'Trial Master File Plan', NULL, 'Meetings', 7, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 24, 1, NOW(), NOW()),
('FULL_025', 'TPL_006', 'eTMF Structure Checklist', NULL, 'Meetings', 7, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 25, 1, NOW(), NOW()),
('FULL_026', 'TPL_006', 'Clinical Management Plan', NULL, 'Meetings', 60, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 26, 1, NOW(), NOW()),
('FULL_027', 'TPL_006', 'Monitoring Plan', NULL, 'Meetings', 1, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 27, 1, NOW(), NOW()),
('FULL_028', 'TPL_006', 'Enrollment Management Plan (EMP)', NULL, 'Meetings', 90, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 28, 1, NOW(), NOW());

INSERT INTO template_tasks (
    task_id, template_id, task_name, task_code, category,
    typical_duration_days, min_duration_days, max_duration_days, p25_duration_days, p75_duration_days,
    is_milestone, is_critical_path, is_recurring, recurrence_interval_days,
    description, responsible_role, notes,
    parent_task_id, sort_order, outline_level,
    created_at, updated_at
) VALUES
('FULL_029', 'TPL_006', 'Protocol Deviation Management Plan', NULL, 'Meetings', 90, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 29, 1, NOW(), NOW()),
('FULL_030', 'TPL_006', 'SIV Training Slides', NULL, 'Meetings', 90, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 30, 1, NOW(), NOW()),
('FULL_031', 'TPL_006', 'Study Reference Manual', NULL, 'Meetings', 90, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 31, 1, NOW(), NOW()),
('FULL_032', 'TPL_006', 'Lab Manual', NULL, 'Meetings', 90, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 32, 1, NOW(), NOW()),
('FULL_033', 'TPL_006', 'Pharmacy Manual/Dosing Instructions', NULL, 'Meetings', 90, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 33, 1, NOW(), NOW()),
('FULL_034', 'TPL_006', 'Data Management Plan (DMP)', NULL, 'Meetings', 45, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 34, 1, NOW(), NOW()),
('FULL_035', 'TPL_006', 'CRF Completion Guidelines', NULL, 'Meetings', 45, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 35, 1, NOW(), NOW()),
('FULL_036', 'TPL_006', 'Safety Monitoring Plan (SMP)', NULL, 'Meetings', 90, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 36, 1, NOW(), NOW()),
('FULL_037', 'TPL_006', 'Statistical Analysis Plan (SAP)', NULL, 'Meetings', 14, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 37, 1, NOW(), NOW()),
('FULL_038', 'TPL_006', 'Medical Monitoring Plan', NULL, 'Meetings', 60, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 38, 1, NOW(), NOW()),
('FULL_039', 'TPL_006', 'Subject Enrollment Form (SEF)', NULL, 'Meetings', 60, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 39, 1, NOW(), NOW()),
('FULL_040', 'TPL_006', 'Quality Management Plan', NULL, 'Meetings', 1, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 40, 1, NOW(), NOW()),
('FULL_041', 'TPL_006', 'Site Feasibility Questionnaire (SFQ)', NULL, 'Meetings', 1, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 41, 1, NOW(), NOW()),
('FULL_042', 'TPL_006', 'CTMS and eTMF setup
▪PM Submit Study Setup Request for ▪ TMF structure checklist sign-off
▪ Sponsor requirements
  ◦ Review of documents/TMF
  ◦ Document submission requirements
  ◦ Verify creation of files (check SOP for timeline)', NULL, 'Infrastructural/Systems Setup', 1, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 42, 1, NOW(), NOW()),
('FULL_043', 'TPL_006', 'Review & setup milestones in Veeva', NULL, 'Infrastructural/Systems Setup', 1, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 43, 1, NOW(), NOW()),
('FULL_044', 'TPL_006', 'Protocol/ICF development
▪ Tracking tools
▪ Review and feedback', NULL, 'Infrastructural/Systems Setup', 1, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 44, 1, NOW(), NOW()),
('FULL_045', 'TPL_006', 'Project Dashboard
▪ Initiate dashboard with original study specifications', NULL, 'Infrastructural/Systems Setup', 30, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 45, 1, NOW(), NOW()),
('FULL_046', 'TPL_006', 'Establish process/format for study reports to be shared/sent to sponsor
▪  Web portal
▪  Access/training if needed', NULL, 'Infrastructural/Systems Setup', 1, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 46, 1, NOW(), NOW()),
('FULL_047', 'TPL_006', 'EDC Set up/ Account Access                                                                   ▪ Initial Account Set up                                                ▪ User Access Requests', NULL, 'Infrastructural/Systems Setup', 7, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 47, 1, NOW(), NOW()),
('FULL_048', 'TPL_006', 'IP contact information
▪ Sponsor
▪ Vendor', NULL, 'Drug Supply Chain', 90, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 48, 1, NOW(), NOW()),
('FULL_049', 'TPL_006', 'Establish drug release process', NULL, 'Drug Supply Chain', 90, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 49, 1, NOW(), NOW()),
('FULL_050', 'TPL_006', 'IP distribution', NULL, 'Drug Supply Chain', 90, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 50, 1, NOW(), NOW()),
('FULL_051', 'TPL_006', 'Labeling
▪  who is responsible', NULL, 'Drug Supply Chain', 90, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 51, 1, NOW(), NOW()),
('FULL_052', 'TPL_006', 'International
▪ Labeling
▪ commercial availability', NULL, 'Drug Supply Chain', 90, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 52, 1, NOW(), NOW()),
('FULL_053', 'TPL_006', 'Generic substitution acceptable?', NULL, 'Drug Supply Chain', 90, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 53, 1, NOW(), NOW()),
('FULL_054', 'TPL_006', 'Service Providers

▪ Number of Vendors to be used', NULL, 'Vendors', 1, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 54, 1, NOW(), NOW()),
('FULL_055', 'TPL_006', 'Vendor identification
▪ Do vendors need to be identified?
▪ IP Depot
▪ Central labs
▪ Central imaging
▪ Other "study specific" central lab
▪ IVRS?
▪ Impact on any other functional areas', NULL, 'Vendors', 1, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 55, 1, NOW(), NOW()),
('FULL_056', 'TPL_006', 'Vendor model, e.g.
▪Contracts/manages?
▪ Sponsor contracts/manages?
▪ Sponsor contracts and Innovations manages?', NULL, 'Vendors', 1, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 56, 1, NOW(), NOW()),
('FULL_057', 'TPL_006', 'Vendor(s) setup
▪ manual
▪ UAT required?
▪ Budget/contracts for vendors setup
▪ Access for vendor systems requested', NULL, 'Vendors', 1, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 57, 1, NOW(), NOW()),
('FULL_058', 'TPL_006', 'Central IRB
▪ Name of IRB
▪ Which sites will use', NULL, 'Vendors', 1, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 58, 1, NOW(), NOW()),
('FULL_059', 'TPL_006', 'Country Level Reg Submission', NULL, 'Vendors', 1, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 59, 1, NOW(), NOW()),
('FULL_060', 'TPL_006', 'International:
▪  Import/export license requirement', NULL, 'Vendors', 1, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 60, 1, NOW(), NOW()),
('FULL_061', 'TPL_006', 'Onboarding
See FAQ 14
▪ Add/Update PT3 tracker
▪ Training slides (sponsor?)
 - Conduct/schedule team training
▪ Protocol
▪ Therapeutic training with Medical Monitor
▪ Investigator''s Brochure (IB)
▪ SIV
▪ EDC
▪ Study plans/procedures
▪ Guidelines
▪ Study SOPs/Sponosr SOPs', NULL, 'Training', 14, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 61, 1, NOW(), NOW()),
('FULL_062', 'TPL_006', 'SOPs need to be shared with sponsor?', NULL, 'Training', 1, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 62, 1, NOW(), NOW()),
('FULL_063', 'TPL_006', 'Obtain any sponsor-required SOPs', NULL, 'Training', 1, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 63, 1, NOW(), NOW()),
('FULL_064', 'TPL_006', 'CRA Study Planning using CRA resourcing form', NULL, 'Training', 1, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 64, 1, NOW(), NOW()),
('FULL_065', 'TPL_006', 'Laboratory sample tracker (as needed)', NULL, 'Delegated:  Clinical/Regulatory Affairs', 1, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 65, 1, NOW(), NOW()),
('FULL_066', 'TPL_006', 'Slot Management Tracker', NULL, 'Delegated:  Clinical/Regulatory Affairs', 90, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 66, 1, NOW(), NOW()),
('FULL_067', 'TPL_006', 'Site List Request', NULL, 'Delegated:  Clinical/Regulatory Affairs', 1, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 67, 1, NOW(), NOW()),
('FULL_068', 'TPL_006', 'Sharepoint folder setup', NULL, 'Delegated:  Clinical/Regulatory Affairs', 14, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 68, 1, NOW(), NOW()),
('FULL_069', 'TPL_006', 'Electronic mailbox setup (PM)', NULL, 'Delegated:  Clinical/Regulatory Affairs', 14, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 69, 1, NOW(), NOW()),
('FULL_070', 'TPL_006', 'Site Essential Document Review', NULL, 'Delegated:  Clinical/Regulatory Affairs', 14, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 70, 1, NOW(), NOW()),
('FULL_071', 'TPL_006', 'Startup Tracking (Start-up is responsible)
▪ Site selection/final site list
▪ Site activation projection tracker                      ▪ Feasibility tracker', NULL, 'Delegated:  Clinical/Regulatory Affairs', 1, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 71, 1, NOW(), NOW()),
('FULL_072', 'TPL_006', '1572', NULL, 'Delegated:  Clinical/Regulatory Affairs', 7, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 72, 1, NOW(), NOW()),
('FULL_073', 'TPL_006', 'Country/site feasibility (Start-up is responsible)
▪ Country selection
▪ Site ID
▪ Site selection', NULL, 'Delegated:  Clinical/Regulatory Affairs', 1, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 73, 1, NOW(), NOW()),
('FULL_074', 'TPL_006', 'Central and Local IRB submission completed?', NULL, 'Delegated:  Clinical/Regulatory Affairs', 1, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 74, 1, NOW(), NOW()),
('FULL_075', 'TPL_006', 'Ensure Innovations CVs current and filed', NULL, 'Delegated:  Clinical/Regulatory Affairs', 1, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 75, 1, NOW(), NOW()),
('FULL_076', 'TPL_006', 'Database build timelines sent to you?
▪ Ensure scheduling or timelines are established for periodic database cuts and lock', NULL, 'Delegated:  Clinical/Regulatory Affairs', 90, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 76, 1, NOW(), NOW()),
('FULL_077', 'TPL_006', 'Program for patient profiles
Program for derived data sets', NULL, 'Delegated:  Data Management/Biostistics', 90, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 77, 1, NOW(), NOW()),
('FULL_078', 'TPL_006', 'Case Report Form (CRF) started?', NULL, 'Delegated:  Data Management/Biostistics', 90, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 78, 1, NOW(), NOW());

INSERT INTO template_tasks (
    task_id, template_id, task_name, task_code, category,
    typical_duration_days, min_duration_days, max_duration_days, p25_duration_days, p75_duration_days,
    is_milestone, is_critical_path, is_recurring, recurrence_interval_days,
    description, responsible_role, notes,
    parent_task_id, sort_order, outline_level,
    created_at, updated_at
) VALUES
('FULL_079', 'TPL_006', 'CRF Completion Guidelines started?', NULL, 'Delegated:  Data Management/Biostistics', 90, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 79, 1, NOW(), NOW()),
('FULL_080', 'TPL_006', 'Data Transfer Agreement(s) (DTA)', NULL, 'Delegated:  Data Management/Biostistics', 7, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 80, 1, NOW(), NOW()),
('FULL_081', 'TPL_006', 'Argus Database Build Initiated', NULL, 'Delegated:  Data Management/Biostistics', 90, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 81, 1, NOW(), NOW()),
('FULL_082', 'TPL_006', 'SAE form created?', NULL, 'Delegated:  Safety', 90, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 82, 1, NOW(), NOW()),
('FULL_083', 'TPL_006', 'Pregnancy Form created?', NULL, 'Delegated:  Safety', 90, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 83, 1, NOW(), NOW()),
('FULL_084', 'TPL_006', 'Protocol Writing/Finalization', NULL, 'Delegated:  Medical Writing', 1, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 84, 1, NOW(), NOW()),
('FULL_085', 'TPL_006', 'Investigator Brochure (IB) writing', NULL, 'Delegated:  Medical Writing', 1, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 85, 1, NOW(), NOW()),
('FULL_086', 'TPL_006', 'Informed Consent Form (ICF) writing', NULL, 'Delegated:  Medical Writing', 1, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, '', NULL, 86, 1, NOW(), NOW()),
('FULL_087', 'TPL_006', 'First Person In (FPI)', 'FPI', 'Study Conduct', 1, NULL, NULL, NULL, NULL, 1, 0, 0, NULL, 'First participant enrolled in the study', NULL, NULL, NULL, 87, 1, NOW(), NOW()),
('FULL_088', 'TPL_006', 'First Person Dosed (FPD)', 'FPD', 'Study Conduct', 1, NULL, NULL, NULL, NULL, 1, 0, 0, NULL, 'First participant receives study intervention/drug', NULL, NULL, NULL, 88, 1, NOW(), NOW()),
('FULL_089', 'TPL_006', 'First Cohort Review (FCR)', 'FCR', 'Study Conduct', 1, NULL, NULL, NULL, NULL, 1, 0, 0, NULL, 'Review of first cohort data before proceeding (if applicable)', NULL, NULL, NULL, 89, 1, NOW(), NOW()),
('FULL_090', 'TPL_006', 'Last Patient In (LPI)', 'LPI', 'Study Conduct', 1, NULL, NULL, NULL, NULL, 1, 0, 0, NULL, 'Last participant enrolled in the study', NULL, NULL, NULL, 90, 1, NOW(), NOW()),
('FULL_091', 'TPL_006', 'Last Person Dosed (LPD)', 'LPD', 'Study Conduct', 1, NULL, NULL, NULL, NULL, 1, 0, 0, NULL, 'Last participant receives final dose of study intervention', NULL, NULL, NULL, 91, 1, NOW(), NOW()),
('FULL_092', 'TPL_006', 'Last Participant Last Visit (LPLV)', 'LPLV', 'Study Conduct', 1, NULL, NULL, NULL, NULL, 1, 0, 0, NULL, 'Last participant completes final study visit', NULL, NULL, NULL, 92, 1, NOW(), NOW()),
('FULL_093', 'TPL_006', 'Last Specimen Collection', 'LSC', 'Study Conduct', 1, NULL, NULL, NULL, NULL, 1, 0, 0, NULL, 'Final biological specimen collected from last participant', NULL, NULL, NULL, 93, 1, NOW(), NOW()),
('FULL_094', 'TPL_006', 'Follow Up', 'FOLLOW_UP', 'Study Conduct', 1, NULL, NULL, NULL, NULL, 1, 0, 0, NULL, 'Post-study follow-up period', NULL, NULL, NULL, 94, 1, NOW(), NOW()),
('FULL_095', 'TPL_006', 'IRB Continuing Review', 'IRB_REVIEW', 'Study Conduct', 1, NULL, NULL, NULL, NULL, 0, 0, 1, 365, 'Ongoing throughout study conduct', NULL, NULL, NULL, 95, 1, NOW(), NOW()),
('FULL_096', 'TPL_006', 'FDA Annual Report', 'FDA_ANNUAL', 'Study Conduct', 1, NULL, NULL, NULL, NULL, 0, 0, 1, 365, 'Submit 60 days within anniversary date the IND went into effect (if sponsor of IND)', NULL, NULL, NULL, 96, 1, NOW(), NOW()),
('FULL_097', 'TPL_006', 'Clinical data entry completed', 'CDB_001', 'Data Management', 4, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, '4 days after last subject, last visit', NULL, NULL, NULL, 97, 1, NOW(), NOW()),
('FULL_098', 'TPL_006', 'Data cleaning and querying', 'CDB_002', 'Data Management', 14, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, '2 weeks after data entry completion', NULL, NULL, NULL, 98, 1, NOW(), NOW()),
('FULL_099', 'TPL_006', 'Serious Adverse Event reconciliation', 'CDB_003', 'Safety', 21, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, '3 weeks after data entry completion', NULL, NULL, NULL, 99, 1, NOW(), NOW()),
('FULL_100', 'TPL_006', 'Final monitoring visit', 'CDB_004', 'Monitoring', 35, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, '5 weeks after last subject, last visit', NULL, NULL, NULL, 100, 1, NOW(), NOW()),
('FULL_101', 'TPL_006', 'Resolution of all data management and monitoring queries', 'CDB_005', 'Data Management', 1, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, '1 day after final monitoring visit', NULL, NULL, NULL, 101, 1, NOW(), NOW()),
('FULL_102', 'TPL_006', 'Clinical database lock', 'CDB_006', 'Data Management', 1, NULL, NULL, NULL, NULL, 1, 0, 0, NULL, '1 day after resolution of all queries', NULL, NULL, NULL, 102, 1, NOW(), NOW()),
('FULL_103', 'TPL_006', 'Assay completion and transfer of laboratory data', 'LDB_001', 'Laboratory', 84, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, '12 weeks after last specimen collection', NULL, NULL, NULL, 103, 1, NOW(), NOW()),
('FULL_104', 'TPL_006', 'QC of laboratory data and distribution of queries', 'LDB_002', 'Laboratory', 4, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, '4 days after receipt of laboratory data', NULL, NULL, NULL, 104, 1, NOW(), NOW()),
('FULL_105', 'TPL_006', 'Resolution of laboratory queries', 'LDB_003', 'Laboratory', 7, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, '1 week after distribution of queries', NULL, NULL, NULL, 105, 1, NOW(), NOW()),
('FULL_106', 'TPL_006', 'Laboratory database lock', 'LDB_004', 'Laboratory', 1, NULL, NULL, NULL, NULL, 1, 0, 0, NULL, '1 day after resolution of lab queries', NULL, NULL, NULL, 106, 1, NOW(), NOW()),
('FULL_107', 'TPL_006', 'Preparation of draft Interim CSR', 'CSR_001', 'Regulatory', 84, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, '12 weeks after clinical AND laboratory database lock', NULL, NULL, NULL, 107, 1, NOW(), NOW()),
('FULL_108', 'TPL_006', 'PVG provides SAE narratives', 'CSR_002', 'Safety', 30, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, '30 days after clinical database lock', NULL, NULL, NULL, 108, 1, NOW(), NOW()),
('FULL_109', 'TPL_006', 'Distribute draft Interim CSR to PI for review', 'CSR_003', 'Regulatory', 1, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, '1 day after draft CSR complete', NULL, NULL, NULL, 109, 1, NOW(), NOW()),
('FULL_110', 'TPL_006', 'PI reviews and completes designated sections of CSR', 'CSR_004', 'Regulatory', 35, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, '4-6 weeks after distribution of draft CSR', NULL, NULL, NULL, 110, 1, NOW(), NOW()),
('FULL_111', 'TPL_006', 'Incorporate PI text, address comments, format CSR', 'CSR_005', 'Regulatory', 7, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, '1 week after receiving draft CSR from PI', NULL, NULL, NULL, 111, 1, NOW(), NOW()),
('FULL_112', 'TPL_006', 'Distribute draft CSR to DMID and PI for review', 'CSR_006', 'Regulatory', 1, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, '1 day after draft CSR complete', NULL, NULL, NULL, 112, 1, NOW(), NOW()),
('FULL_113', 'TPL_006', 'DMID reviews draft CSR and provides comments', 'CSR_007', 'Regulatory', 28, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, '4 weeks after distribution to DMID', NULL, NULL, NULL, 113, 1, NOW(), NOW()),
('FULL_114', 'TPL_006', 'Incorporate DMID comments and prepare final draft CSR', 'CSR_008', 'Regulatory', 7, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, '1 week after receipt of DMID comments', NULL, NULL, NULL, 114, 1, NOW(), NOW()),
('FULL_115', 'TPL_006', 'Receive DMID and PI approval to finalize CSR', 'CSR_009', 'Regulatory', 3, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, '3 days after final draft distributed', NULL, NULL, NULL, 115, 1, NOW(), NOW()),
('FULL_116', 'TPL_006', 'Prepare approved CSR per regulatory requirements', 'CSR_010', 'Regulatory', 3, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, '3 days after approval to finalize', NULL, NULL, NULL, 116, 1, NOW(), NOW()),
('FULL_117', 'TPL_006', 'Lead PI signs signature page and returns', 'CSR_011', 'Regulatory', 3, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, '3 days after notification of approved CSR', NULL, NULL, NULL, 117, 1, NOW(), NOW()),
('FULL_118', 'TPL_006', 'Distribute approved CSR to CROMS portals', 'CSR_012', 'Regulatory', 1, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, '1 day after receipt of PI signature', NULL, NULL, NULL, 118, 1, NOW(), NOW()),
('FULL_119', 'TPL_006', 'RAS submits final, signed CSR to FDA', 'CSR_013', 'Regulatory', 17, NULL, NULL, NULL, NULL, 1, 0, 0, NULL, '2-3 weeks after signature page posted', NULL, NULL, NULL, 119, 1, NOW(), NOW());

-- Template Dependencies (75 dependencies)

INSERT INTO template_dependencies (
    dependency_id, template_id, predecessor_task_id, successor_task_id,
    dependency_type, lag_days, is_hard_dependency,
    created_at
) VALUES
('DEP_TPL001_SS_009_SS_084_0', 'TPL_001', 'SS_084', 'SS_009', 'finish-to-start', 0, 0, NOW()),
('DEP_TPL001_SS_012_SS_001_1', 'TPL_001', 'SS_001', 'SS_012', 'finish-to-start', 0, 0, NOW()),
('DEP_TPL001_SS_013_SS_014_2', 'TPL_001', 'SS_014', 'SS_013', 'finish-to-start', 0, 0, NOW()),
('DEP_TPL001_SS_014_SS_001_3', 'TPL_001', 'SS_001', 'SS_014', 'finish-to-start', 0, 0, NOW()),
('DEP_TPL001_SS_014_SS_084_4', 'TPL_001', 'SS_084', 'SS_014', 'finish-to-start', 0, 0, NOW()),
('DEP_TPL001_SS_015_SS_014_5', 'TPL_001', 'SS_014', 'SS_015', 'finish-to-start', 0, 0, NOW()),
('DEP_TPL001_SS_016_SS_014_6', 'TPL_001', 'SS_014', 'SS_016', 'finish-to-start', 0, 0, NOW()),
('DEP_TPL001_SS_018_SS_001_7', 'TPL_001', 'SS_001', 'SS_018', 'finish-to-start', 0, 0, NOW()),
('DEP_TPL001_SS_018_SS_084_8', 'TPL_001', 'SS_084', 'SS_018', 'finish-to-start', 0, 0, NOW()),
('DEP_TPL001_SS_019_SS_001_9', 'TPL_001', 'SS_001', 'SS_019', 'finish-to-start', 0, 0, NOW()),
('DEP_TPL001_SS_019_SS_084_10', 'TPL_001', 'SS_084', 'SS_019', 'finish-to-start', 0, 0, NOW()),
('DEP_TPL001_SS_020_SS_001_11', 'TPL_001', 'SS_001', 'SS_020', 'finish-to-start', 0, 0, NOW()),
('DEP_TPL001_SS_022_SS_014_12', 'TPL_001', 'SS_014', 'SS_022', 'finish-to-start', 0, 0, NOW()),
('DEP_TPL001_SS_041_SS_014_13', 'TPL_001', 'SS_014', 'SS_041', 'finish-to-start', 0, 0, NOW()),
('DEP_TPL001_SS_042_SS_001_14', 'TPL_001', 'SS_001', 'SS_042', 'finish-to-start', 0, 0, NOW()),
('DEP_TPL001_SS_043_SS_057_15', 'TPL_001', 'SS_057', 'SS_043', 'finish-to-start', 0, 0, NOW()),
('DEP_TPL001_SS_044_SS_084_16', 'TPL_001', 'SS_084', 'SS_044', 'finish-to-start', 0, 0, NOW()),
('DEP_TPL001_SS_045_SS_014_17', 'TPL_001', 'SS_014', 'SS_045', 'finish-to-start', 0, 0, NOW()),
('DEP_TPL001_SS_046_SS_014_18', 'TPL_001', 'SS_014', 'SS_046', 'finish-to-start', 0, 0, NOW()),
('DEP_TPL001_SS_048_SS_057_19', 'TPL_001', 'SS_057', 'SS_048', 'finish-to-start', 0, 0, NOW()),
('DEP_TPL001_SS_049_SS_057_20', 'TPL_001', 'SS_057', 'SS_049', 'finish-to-start', 0, 0, NOW()),
('DEP_TPL001_SS_050_SS_057_21', 'TPL_001', 'SS_057', 'SS_050', 'finish-to-start', 0, 0, NOW()),
('DEP_TPL001_SS_051_SS_057_22', 'TPL_001', 'SS_057', 'SS_051', 'finish-to-start', 0, 0, NOW()),
('DEP_TPL001_SS_052_SS_057_23', 'TPL_001', 'SS_057', 'SS_052', 'finish-to-start', 0, 0, NOW()),
('DEP_TPL001_SS_053_SS_057_24', 'TPL_001', 'SS_057', 'SS_053', 'finish-to-start', 0, 0, NOW()),
('DEP_TPL001_SS_054_SS_057_25', 'TPL_001', 'SS_057', 'SS_054', 'finish-to-start', 0, 0, NOW()),
('DEP_TPL001_SS_055_SS_057_26', 'TPL_001', 'SS_057', 'SS_055', 'finish-to-start', 0, 0, NOW()),
('DEP_TPL001_SS_056_SS_057_27', 'TPL_001', 'SS_057', 'SS_056', 'finish-to-start', 0, 0, NOW()),
('DEP_TPL001_SS_059_SS_057_28', 'TPL_001', 'SS_057', 'SS_059', 'finish-to-start', 0, 0, NOW()),
('DEP_TPL001_SS_061_SS_084_29', 'TPL_001', 'SS_084', 'SS_061', 'finish-to-start', 0, 0, NOW()),
('DEP_TPL001_SS_062_SS_057_30', 'TPL_001', 'SS_057', 'SS_062', 'finish-to-start', 0, 0, NOW()),
('DEP_TPL001_SS_063_SS_057_31', 'TPL_001', 'SS_057', 'SS_063', 'finish-to-start', 0, 0, NOW()),
('DEP_TPL001_SS_065_SS_032_32', 'TPL_001', 'SS_032', 'SS_065', 'finish-to-start', 0, 0, NOW()),
('DEP_TPL001_SS_067_SS_001_33', 'TPL_001', 'SS_001', 'SS_067', 'finish-to-start', 0, 0, NOW()),
('DEP_TPL001_SS_068_SS_001_34', 'TPL_001', 'SS_001', 'SS_068', 'finish-to-start', 0, 0, NOW()),
('DEP_TPL001_SS_069_SS_001_35', 'TPL_001', 'SS_001', 'SS_069', 'finish-to-start', 0, 0, NOW()),
('DEP_TPL001_SS_071_SS_084_36', 'TPL_001', 'SS_084', 'SS_071', 'finish-to-start', 0, 0, NOW()),
('DEP_TPL001_SS_071_SS_014_37', 'TPL_001', 'SS_014', 'SS_071', 'finish-to-start', 0, 0, NOW()),
('DEP_TPL001_SS_072_SS_084_38', 'TPL_001', 'SS_084', 'SS_072', 'finish-to-start', 0, 0, NOW()),
('DEP_TPL001_SS_073_SS_084_39', 'TPL_001', 'SS_084', 'SS_073', 'finish-to-start', 0, 0, NOW()),
('DEP_TPL001_SS_073_SS_014_40', 'TPL_001', 'SS_014', 'SS_073', 'finish-to-start', 0, 0, NOW()),
('DEP_TPL001_SS_075_SS_001_41', 'TPL_001', 'SS_001', 'SS_075', 'finish-to-start', 0, 0, NOW()),
('DEP_TPL001_SS_076_SS_001_42', 'TPL_001', 'SS_001', 'SS_076', 'finish-to-start', 0, 0, NOW()),
('DEP_TPL001_SS_076_SS_084_43', 'TPL_001', 'SS_084', 'SS_076', 'finish-to-start', 0, 0, NOW()),
('DEP_TPL001_SS_077_SS_081_44', 'TPL_001', 'SS_081', 'SS_077', 'finish-to-start', 0, 0, NOW()),
('DEP_TPL001_SS_078_SS_001_45', 'TPL_001', 'SS_001', 'SS_078', 'finish-to-start', 0, 0, NOW()),
('DEP_TPL001_SS_078_SS_084_46', 'TPL_001', 'SS_084', 'SS_078', 'finish-to-start', 0, 0, NOW()),
('DEP_TPL001_SS_079_SS_001_47', 'TPL_001', 'SS_001', 'SS_079', 'finish-to-start', 0, 0, NOW()),
('DEP_TPL001_SS_079_SS_084_48', 'TPL_001', 'SS_084', 'SS_079', 'finish-to-start', 0, 0, NOW()),
('DEP_TPL001_SS_082_SS_081_49', 'TPL_001', 'SS_081', 'SS_082', 'finish-to-start', 0, 0, NOW());

INSERT INTO template_dependencies (
    dependency_id, template_id, predecessor_task_id, successor_task_id,
    dependency_type, lag_days, is_hard_dependency,
    created_at
) VALUES
('DEP_TPL001_SS_083_SS_081_50', 'TPL_001', 'SS_081', 'SS_083', 'finish-to-start', 0, 0, NOW()),
('DEP_TPL001_SS_086_SS_084_51', 'TPL_001', 'SS_084', 'SS_086', 'finish-to-start', 0, 0, NOW()),
('DEP_TPL003_CDB_002_CDB_001', 'TPL_003', 'CDB_001', 'CDB_002', 'finish-to-start', 0, 1, NOW()),
('DEP_TPL003_CDB_003_CDB_001', 'TPL_003', 'CDB_001', 'CDB_003', 'finish-to-start', 0, 1, NOW()),
('DEP_TPL003_CDB_004_CDB_002', 'TPL_003', 'CDB_002', 'CDB_004', 'finish-to-start', 0, 1, NOW()),
('DEP_TPL003_CDB_004_CDB_003', 'TPL_003', 'CDB_003', 'CDB_004', 'finish-to-start', 0, 1, NOW()),
('DEP_TPL003_CDB_005_CDB_004', 'TPL_003', 'CDB_004', 'CDB_005', 'finish-to-start', 0, 1, NOW()),
('DEP_TPL003_CDB_006_CDB_005', 'TPL_003', 'CDB_005', 'CDB_006', 'finish-to-start', 0, 1, NOW()),
('DEP_TPL003_LDB_002_LDB_001', 'TPL_003', 'LDB_001', 'LDB_002', 'finish-to-start', 0, 1, NOW()),
('DEP_TPL003_LDB_003_LDB_002', 'TPL_003', 'LDB_002', 'LDB_003', 'finish-to-start', 0, 1, NOW()),
('DEP_TPL003_LDB_004_LDB_003', 'TPL_003', 'LDB_003', 'LDB_004', 'finish-to-start', 0, 1, NOW()),
('DEP_TPL003_CSR_001_CDB_006', 'TPL_003', 'CDB_006', 'CSR_001', 'finish-to-start', 0, 1, NOW()),
('DEP_TPL003_CSR_001_LDB_004', 'TPL_003', 'LDB_004', 'CSR_001', 'finish-to-start', 0, 1, NOW()),
('DEP_TPL003_CSR_002_CDB_006', 'TPL_003', 'CDB_006', 'CSR_002', 'finish-to-start', 0, 1, NOW()),
('DEP_TPL003_CSR_003_CSR_001', 'TPL_003', 'CSR_001', 'CSR_003', 'finish-to-start', 0, 1, NOW()),
('DEP_TPL003_CSR_004_CSR_003', 'TPL_003', 'CSR_003', 'CSR_004', 'finish-to-start', 0, 1, NOW()),
('DEP_TPL003_CSR_005_CSR_004', 'TPL_003', 'CSR_004', 'CSR_005', 'finish-to-start', 0, 1, NOW()),
('DEP_TPL003_CSR_006_CSR_005', 'TPL_003', 'CSR_005', 'CSR_006', 'finish-to-start', 0, 1, NOW()),
('DEP_TPL003_CSR_007_CSR_006', 'TPL_003', 'CSR_006', 'CSR_007', 'finish-to-start', 0, 1, NOW()),
('DEP_TPL003_CSR_008_CSR_007', 'TPL_003', 'CSR_007', 'CSR_008', 'finish-to-start', 0, 1, NOW()),
('DEP_TPL003_CSR_009_CSR_008', 'TPL_003', 'CSR_008', 'CSR_009', 'finish-to-start', 0, 1, NOW()),
('DEP_TPL003_CSR_010_CSR_009', 'TPL_003', 'CSR_009', 'CSR_010', 'finish-to-start', 0, 1, NOW()),
('DEP_TPL003_CSR_011_CSR_010', 'TPL_003', 'CSR_010', 'CSR_011', 'finish-to-start', 0, 1, NOW()),
('DEP_TPL003_CSR_012_CSR_011', 'TPL_003', 'CSR_011', 'CSR_012', 'finish-to-start', 0, 1, NOW()),
('DEP_TPL003_CSR_013_CSR_012', 'TPL_003', 'CSR_012', 'CSR_013', 'finish-to-start', 0, 1, NOW());

-- Migration 015 complete: 6 templates, 291 tasks, 75 dependencies
