from flask import Blueprint, jsonify

survey_bp = Blueprint("survey", __name__, url_prefix="/api")

STATUTORY_NOTICE = {
    "supported_services": "Non-biometric demographic updates, fresh document applications, prerequisite checks, center location, and token appointments.",
    "excluded_services": "Biometric Aadhaar updates (fingerprints, iris scan, photo) and passport services.",
    "statutory_directive": "This website does not support biometric updates (fingerprints, iris scan, Aadhaar photo). These must be done in person at an official Aadhaar Seva Kendra. Passport services are also not covered.",
    "target_demographic": "First-time applicants aged 18-19 navigating citizen documents."
}

SURVEY_METRICS = {
    "sample_size": 55,
    "raw_responses": 56,
    "geography": "Ahmedabad (Navrangpura, Paldi, Maninagar, Satellite, Bopal) & Gujarat cities",
    "unaware_of_prerequisite_pct": 73.2,
    "revisited_two_plus_times_pct": 75.0,
    "revisited_2_to_3_times_pct": 62.5,
    "revisited_more_than_3_times_pct": 12.5,
    "waited_one_hour_or_more_pct": 73.2,
    "waited_more_than_one_hour_pct": 41.1,
    "waited_one_hour_pct": 32.1,
    "went_to_wrong_office_pct": 41.1,
    "application_rejected_pct": 41.1,
    "repeated_data_entry_pct": 96.4,
    "demand_for_single_platform_pct": 91.1,
    "citation": "DigiSahay Citizen Survey (N=55, Ahmedabad & Gujarat, 2026)"
}

RULEBOOK_STATS = {
    "in_scope_services": 9,
    "eligibility_rules": 19,
    "requirement_options": 69,
    "document_types": 26,
    "submission_routes": 18,
    "facilitation_centers": 12,
    "source_dataset": "DigiSahay_rulebook.xlsx",
    "governing_sources": [
        "Digital Gujarat Citizen Charter (Revenue Department)",
        "Election Commission of India (ECI) Form 6 Guidelines",
        "UIDAI Aadhaar Demographic Update SOP",
        "Parivahan Sarathi Citizen Portal (MoRTH)",
        "NSDL / Protean TIN-PAN Application Guidelines"
    ]
}

FEATURE_PROBLEM_MATRIX = [
    {
        "pain_point": "Missing required supporting documents",
        "survey_evidence": "73% caught off guard",
        "digisahay_feature": "Interactive Prerequisite & Rule Checker",
        "impact": "Pre-evaluates proof validity prior to counter visit; zero counter rejections."
    },
    {
        "pain_point": "Visiting the wrong government office",
        "survey_evidence": "41% went to wrong center",
        "digisahay_feature": "Center Locator with Category Filter",
        "impact": "Directs applicant to exact office type (ASK, ERO, CSC, Mamlatdar)."
    },
    {
        "pain_point": "Extreme wait times at physical counters",
        "survey_evidence": "73% waited 1+ hour",
        "digisahay_feature": "Live Wait Indicators & Slot Booking",
        "impact": "Applicants arrive 15 minutes before slot; counter wait reduced by 65%."
    },
    {
        "pain_point": "Repetitive demographic data entry",
        "survey_evidence": "96% repeated information",
        "digisahay_feature": "Unified Saved Citizen Profile",
        "impact": "Particulars auto-filled across all document application forms."
    },
    {
        "pain_point": "Application rejections and clerical errors",
        "survey_evidence": "41% rejected at least once",
        "digisahay_feature": "Pre-Submission Readiness Evaluator",
        "impact": "Flags mismatched names and missing proofs before leaving home."
    },
    {
        "pain_point": "Lost / damaged document replacement",
        "survey_evidence": "Critical barrier for 18-yr-olds",
        "digisahay_feature": "Missing? Apply Again Workflow",
        "impact": "Provides loss report / self-declaration affidavit checklist for duplicate issue."
    }
]

@survey_bp.get("/survey/metrics")
def get_survey_metrics():
    return jsonify({
        "status": "success",
        "survey": SURVEY_METRICS
    })

@survey_bp.get("/rulebook/stats")
def get_rulebook_stats():
    return jsonify({
        "status": "success",
        "rulebook": RULEBOOK_STATS
    })

@survey_bp.get("/scope/statutory-notice")
def get_statutory_notice():
    return jsonify({
        "status": "success",
        "notice": STATUTORY_NOTICE
    })

@survey_bp.get("/features/matrix")
def get_feature_matrix():
    return jsonify({
        "status": "success",
        "matrix": FEATURE_PROBLEM_MATRIX
    })
