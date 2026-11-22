<<<<<<< HEAD

import json
from datetime import date
from flask import Blueprint, jsonify, request
from utils.rule_evaluator import calculate_age, get_next_qualifying_date,evaluate_rule,parse_outcome
from model import Service, EligibilityRule

eligibility_bp = Blueprint("eligibility", __name__)


@eligibility_bp.get("/api/services/<service_id>/eligibility-rules")
def get_eligibility_rules(service_id):

    service = Service.query.filter_by(
        service_id=service_id
    ).first()

    if not service:
        return jsonify({
            "success": False,
            "message": "Service not found"
        }), 404

    rules = EligibilityRule.query.filter_by(
        service_id=service_id
    ).all()

    result = []

    for rule in rules:
        result.append({
            "rule_id": rule.rule_id,
            "rule_code": rule.rule_code,
            "question_text": rule.question_text,
            "condition_type": rule.condition_type,
            "condition_config": rule.condition_config,
            "outcome_if_true": rule.outcome_if_true,
            "outcome_if_false": rule.outcome_if_false,
            "verification_status": rule.verification_status
        })

    return jsonify({
        "success": True,
        "service": {
            "service_id": service.service_id,
            "service_name": service.service_name
        },
        "total_rules": len(result),
        "eligibility_rules": result
    }), 200


# New POST endpoint
@eligibility_bp.post("/api/services/<service_id>/check-eligibility")
def check_eligibility(service_id):

    service = Service.query.filter_by(
        service_id=service_id
    ).first()

    if not service:
        return jsonify({
            "success": False,
            "message": "Service not found"
        }), 404

    answers = request.get_json(silent=True)

    if not isinstance(answers, dict):
        return jsonify({
            "success": False,
            "message": "Please provide answers in JSON format"
        }), 400

    rules = EligibilityRule.query.filter_by(
        service_id=service_id
    ).order_by(EligibilityRule.rule_id).all()

    if not rules:
        return jsonify({
            "success": False,
            "message": "No eligibility rules found"
        }), 404

    today = date.today()
    results = []

    for rule in rules:

        evaluation = evaluate_rule(rule, answers, today)

        results.append({
            "rule_id": rule.rule_id,
            "rule_code": rule.rule_code,
            "question_text": rule.question_text,
            **evaluation
        })

    statuses = [result["status"] for result in results]

    if "REJECT" in statuses:
        overall_status = "REJECT"

    elif any(status in ["INCOMPLETE", "INVALID_ANSWER",
                        "INVALID_RULE", "UNKNOWN"]
            for status in statuses):
        overall_status = "INCOMPLETE"

    elif "REROUTE" in statuses:
        overall_status = "REROUTE"

    elif all(status == "PROCEED" for status in statuses):
        overall_status = "PROCEED"

    else:
        overall_status = "INCOMPLETE"

    return jsonify({
        "success": True,
        "service": {
            "service_id": service.service_id,
            "service_name": service.service_name
        },
        "overall_status": overall_status,
        "total_rules": len(results),
        "results": results
    }), 200
=======

import json
from datetime import date
from flask import Blueprint, jsonify, request
from utils.rule_evaluator import calculate_age, get_next_qualifying_date,evaluate_rule,parse_outcome
from model import Service, EligibilityRule

eligibility_bp = Blueprint("eligibility", __name__)


@eligibility_bp.get("/api/services/<service_id>/eligibility-rules")
def get_eligibility_rules(service_id):

    service = Service.query.filter_by(
        service_id=service_id
    ).first()

    if not service:
        return jsonify({
            "success": False,
            "message": "Service not found"
        }), 404

    rules = EligibilityRule.query.filter_by(
        service_id=service_id
    ).all()

    result = []

    for rule in rules:
        result.append({
            "rule_id": rule.rule_id,
            "rule_code": rule.rule_code,
            "question_text": rule.question_text,
            "condition_type": rule.condition_type,
            "condition_config": rule.condition_config,
            "outcome_if_true": rule.outcome_if_true,
            "outcome_if_false": rule.outcome_if_false,
            "verification_status": rule.verification_status
        })

    return jsonify({
        "success": True,
        "service": {
            "service_id": service.service_id,
            "service_name": service.service_name
        },
        "total_rules": len(result),
        "eligibility_rules": result
    }), 200


# New POST endpoint
@eligibility_bp.post("/api/services/<service_id>/check-eligibility")
def check_eligibility(service_id):

    service = Service.query.filter_by(
        service_id=service_id
    ).first()

    if not service:
        return jsonify({
            "success": False,
            "message": "Service not found"
        }), 404

    answers = request.get_json(silent=True)

    if not isinstance(answers, dict):
        return jsonify({
            "success": False,
            "message": "Please provide answers in JSON format"
        }), 400

    rules = EligibilityRule.query.filter_by(
        service_id=service_id
    ).order_by(EligibilityRule.rule_id).all()

    if not rules:
        return jsonify({
            "success": False,
            "message": "No eligibility rules found"
        }), 404

    today = date.today()
    results = []

    for rule in rules:

        evaluation = evaluate_rule(rule, answers, today)

        results.append({
            "rule_id": rule.rule_id,
            "rule_code": rule.rule_code,
            "question_text": rule.question_text,
            **evaluation
        })

    statuses = [result["status"] for result in results]

    if "REJECT" in statuses:
        overall_status = "REJECT"

    elif any(status in ["INCOMPLETE", "INVALID_ANSWER",
                        "INVALID_RULE", "UNKNOWN"]
            for status in statuses):
        overall_status = "INCOMPLETE"

    elif "REROUTE" in statuses:
        overall_status = "REROUTE"

    elif all(status == "PROCEED" for status in statuses):
        overall_status = "PROCEED"

    else:
        overall_status = "INCOMPLETE"

    return jsonify({
        "success": True,
        "service": {
            "service_id": service.service_id,
            "service_name": service.service_name
        },
        "overall_status": overall_status,
        "total_rules": len(results),
        "results": results
    }), 200
>>>>>>> c981506dbd2f314e63b7e90f4ab444ee1eca2d2c
