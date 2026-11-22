<<<<<<< HEAD

from datetime import date
from flask import Blueprint, jsonify, request

from model import (
    Service,
    EligibilityRule,
    RequirementGroup,
    Requirement,
    DocumentType
)

from utils.rule_evaluator import evaluate_rule


requirement_evaluation_bp = Blueprint(
    "requirement_evaluation",
    __name__
)


def check_condition(rule_id, rules, answers, today):

    if not rule_id:
        return {
            "applicable": True,
            "status": "NO_CONDITION"
        }

    rule = rules.get(rule_id)

    if not rule:
        return {
            "applicable": False,
            "status": "INVALID_RULE",
            "message": f"Rule not found: {rule_id}"
        }

    result = evaluate_rule(rule, answers, today)

    if result.get("status") == "PROCEED":
        return {
            "applicable": True,
            "status": "PROCEED"
        }

    if result.get("status") == "REJECT":
        return {
            "applicable": False,
            "status": "REJECT",
            "message": result.get("message")
        }

    return {
        "applicable": False,
        "status": result.get("status"),
        "message": result.get("message")
    }


@requirement_evaluation_bp.post(
    "/api/services/<service_id>/requirements/evaluate"
)
def evaluate_requirements(service_id):

    service = Service.query.filter_by(
        service_id=service_id
    ).first()

    if not service:
        return jsonify({
            "success": False,
            "message": "Service not found"
        }), 404

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "success": False,
            "message": "Please provide valid JSON"
        }), 400

    answers = data.get("answers", {})
    selected_option_ids = data.get("selected_option_ids", [])
    applicant_context = data.get(
        "applicant_context",
        "ALL_APPLICANTS"
    )

    if not isinstance(answers, dict):
        return jsonify({
            "success": False,
            "message": "answers must be a JSON object"
        }), 400

    if (
        not isinstance(selected_option_ids, list)
        or not all(isinstance(x, str) for x in selected_option_ids)
    ):
        return jsonify({
            "success": False,
            "message": "selected_option_ids must be a list of strings"
        }), 400

    if not isinstance(applicant_context, str):
        return jsonify({
            "success": False,
            "message": "applicant_context must be a string"
        }), 400

    if len(selected_option_ids) != len(set(selected_option_ids)):
        return jsonify({
            "success": False,
            "message": "Duplicate selected option IDs are not allowed"
        }), 400

    groups = RequirementGroup.query.filter_by(
        service_id=service_id
    ).all()

    if not groups:
        return jsonify({
            "success": False,
            "message": "No requirement groups found"
        }), 404

    rules_list = EligibilityRule.query.filter_by(
        service_id=service_id
    ).all()

    rules = {
        rule.rule_id: rule
        for rule in rules_list
    }

    today = date.today()

    all_options = (
        Requirement.query
        .join(
            RequirementGroup,
            Requirement.group_id == RequirementGroup.group_id
        )
        .join(
            DocumentType,
            Requirement.document_type_id == DocumentType.document_type_id
        )
        .filter(
            RequirementGroup.service_id == service_id,
            DocumentType.is_active.is_(True)
        )
        .all()
    )


    options_by_group = {}

    for option in all_options:
        options_by_group.setdefault(
            option.group_id, []
        ).append(option)

    known_option_ids = {
        option.option_id
        for option in all_options
    }

    unknown_ids = (
        set(selected_option_ids) - known_option_ids
    )

    if unknown_ids:
        return jsonify({
            "success": False,
            "message": "Unknown or inactive document option IDs",
            "unknown_option_ids": sorted(unknown_ids)
        }), 400

    selected_ids = set(selected_option_ids)

    group_results = []
    all_missing = []
    checklist_complete = True

    for group in groups:

        group_condition = check_condition(
            group.condition_rule_id,
            rules,
            answers,
            today
        )

        if not group_condition["applicable"]:

            group_results.append({
                "group_id": group.group_id,
                "group_name": group.group_name,
                "selection_mode": group.selection_mode,
                "applicable": False,
                "condition_status": group_condition["status"],
                "message": group_condition.get("message"),
                "complete": None,
                "available_options": [],
                "selected_options": [],
                "missing_options": []
            })

            continue

        applicable_options = []

        for option in options_by_group.get(
            group.group_id, []
        ):

            context = option.applicable_context

            if (
                context
                and context != "ALL_APPLICANTS"
                and context != applicant_context
            ):
                continue

            option_condition = check_condition(
                option.condition_rule_id,
                rules,
                answers,
                today
            )

            if not option_condition["applicable"]:
                continue

            if option.verification_status != "VERIFIED":
                continue

            document = DocumentType.query.filter_by(
                document_type_id=option.document_type_id
            ).first()

            if not document:
                continue

            applicable_options.append({
                "option_id": option.option_id,
                "document_type_id": document.document_type_id,
                "document_name": document.document_name,
                "acceptance_instructions":
                    option.official_acceptance_conditions,
                "verification_status":
                    option.verification_status
            })

        available_ids = {
            option["option_id"]
            for option in applicable_options
        }

        selected_for_group = [
            option for option in applicable_options
            if option["option_id"] in selected_ids
        ]

        selected_for_group_ids = {
            option["option_id"]
            for option in selected_for_group
        }

        mode = group.selection_mode

        minimum = group.min_selections or 0
        maximum = group.max_selections

        
        remaining_selections = 0
        selection_error = None

        if mode == "ALL":
        
            required_ids = available_ids

            missing_ids = (
                required_ids - selected_for_group_ids
            )

            complete = len(missing_ids) == 0

        elif mode in ["CHOOSE_ONE", "CONDITIONAL"]:
        
            selected_count = len(selected_for_group_ids)

            remaining_selections = max(
                0,
                minimum - selected_count
            )

            missing_ids = set()

            if selected_count < minimum:
                complete = False
                selection_error = (
                    f"Select at least {minimum} document(s)"
                )

            elif maximum is not None and selected_count > maximum:
                complete = False
                selection_error = (
                    f"Select no more than {maximum} document(s)"
                )

            else:
                complete = True

        elif mode == "OPTIONAL":
        
            missing_ids = set()
            complete = True

        else:
        
            missing_ids = set()
            complete = False
            selection_error = "Unsupported selection mode"


        missing_options = [
            option
            for option in applicable_options
            if option["option_id"] in missing_ids
        ]

        if not complete:
            checklist_complete = False

        all_missing.extend([
            option["option_id"]
            for option in missing_options
        ])

        group_results.append({
            "group_id": group.group_id,
            "group_name": group.group_name,
            "selection_mode": mode,
            "applicable": True,
            "condition_status": group_condition["status"],
            "complete": complete,
            "minimum_selections": minimum,
            "maximum_selections": maximum,
            "available_options": applicable_options,
            "selected_options": selected_for_group,
            "missing_options": missing_options,
            "remaining_selections": remaining_selections,
            "selection_error": selection_error
        })

    return jsonify({
        "success": True,
        "service": {
            "service_id": service.service_id,
            "service_name": service.service_name
        },
        "document_checklist_complete": checklist_complete,
        "total_groups": len(group_results),
        "missing_option_ids": all_missing,
        "groups": group_results
    }), 200
=======

from datetime import date
from flask import Blueprint, jsonify, request

from model import (
    Service,
    EligibilityRule,
    RequirementGroup,
    Requirement,
    DocumentType
)

from utils.rule_evaluator import evaluate_rule


requirement_evaluation_bp = Blueprint(
    "requirement_evaluation",
    __name__
)


def check_condition(rule_id, rules, answers, today):

    if not rule_id:
        return {
            "applicable": True,
            "status": "NO_CONDITION"
        }

    rule = rules.get(rule_id)

    if not rule:
        return {
            "applicable": False,
            "status": "INVALID_RULE",
            "message": f"Rule not found: {rule_id}"
        }

    result = evaluate_rule(rule, answers, today)

    if result.get("status") == "PROCEED":
        return {
            "applicable": True,
            "status": "PROCEED"
        }

    if result.get("status") == "REJECT":
        return {
            "applicable": False,
            "status": "REJECT",
            "message": result.get("message")
        }

    return {
        "applicable": False,
        "status": result.get("status"),
        "message": result.get("message")
    }


@requirement_evaluation_bp.post(
    "/api/services/<service_id>/requirements/evaluate"
)
def evaluate_requirements(service_id):

    service = Service.query.filter_by(
        service_id=service_id
    ).first()

    if not service:
        return jsonify({
            "success": False,
            "message": "Service not found"
        }), 404

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "success": False,
            "message": "Please provide valid JSON"
        }), 400

    answers = data.get("answers", {})
    selected_option_ids = data.get("selected_option_ids", [])
    applicant_context = data.get(
        "applicant_context",
        "ALL_APPLICANTS"
    )

    if not isinstance(answers, dict):
        return jsonify({
            "success": False,
            "message": "answers must be a JSON object"
        }), 400

    if (
        not isinstance(selected_option_ids, list)
        or not all(isinstance(x, str) for x in selected_option_ids)
    ):
        return jsonify({
            "success": False,
            "message": "selected_option_ids must be a list of strings"
        }), 400

    if not isinstance(applicant_context, str):
        return jsonify({
            "success": False,
            "message": "applicant_context must be a string"
        }), 400

    if len(selected_option_ids) != len(set(selected_option_ids)):
        return jsonify({
            "success": False,
            "message": "Duplicate selected option IDs are not allowed"
        }), 400

    groups = RequirementGroup.query.filter_by(
        service_id=service_id
    ).all()

    if not groups:
        return jsonify({
            "success": False,
            "message": "No requirement groups found"
        }), 404

    rules_list = EligibilityRule.query.filter_by(
        service_id=service_id
    ).all()

    rules = {
        rule.rule_id: rule
        for rule in rules_list
    }

    today = date.today()

    all_options = (
        Requirement.query
        .join(
            RequirementGroup,
            Requirement.group_id == RequirementGroup.group_id
        )
        .join(
            DocumentType,
            Requirement.document_type_id == DocumentType.document_type_id
        )
        .filter(
            RequirementGroup.service_id == service_id,
            DocumentType.is_active.is_(True)
        )
        .all()
    )


    options_by_group = {}

    for option in all_options:
        options_by_group.setdefault(
            option.group_id, []
        ).append(option)

    known_option_ids = {
        option.option_id
        for option in all_options
    }

    unknown_ids = (
        set(selected_option_ids) - known_option_ids
    )

    if unknown_ids:
        return jsonify({
            "success": False,
            "message": "Unknown or inactive document option IDs",
            "unknown_option_ids": sorted(unknown_ids)
        }), 400

    selected_ids = set(selected_option_ids)

    group_results = []
    all_missing = []
    checklist_complete = True

    for group in groups:

        group_condition = check_condition(
            group.condition_rule_id,
            rules,
            answers,
            today
        )

        if not group_condition["applicable"]:

            group_results.append({
                "group_id": group.group_id,
                "group_name": group.group_name,
                "selection_mode": group.selection_mode,
                "applicable": False,
                "condition_status": group_condition["status"],
                "message": group_condition.get("message"),
                "complete": None,
                "available_options": [],
                "selected_options": [],
                "missing_options": []
            })

            continue

        applicable_options = []

        for option in options_by_group.get(
            group.group_id, []
        ):

            context = option.applicable_context

            if (
                context
                and context != "ALL_APPLICANTS"
                and context != applicant_context
            ):
                continue

            option_condition = check_condition(
                option.condition_rule_id,
                rules,
                answers,
                today
            )

            if not option_condition["applicable"]:
                continue

            if option.verification_status != "VERIFIED":
                continue

            document = DocumentType.query.filter_by(
                document_type_id=option.document_type_id
            ).first()

            if not document:
                continue

            applicable_options.append({
                "option_id": option.option_id,
                "document_type_id": document.document_type_id,
                "document_name": document.document_name,
                "acceptance_instructions":
                    option.official_acceptance_conditions,
                "verification_status":
                    option.verification_status
            })

        available_ids = {
            option["option_id"]
            for option in applicable_options
        }

        selected_for_group = [
            option for option in applicable_options
            if option["option_id"] in selected_ids
        ]

        selected_for_group_ids = {
            option["option_id"]
            for option in selected_for_group
        }

        mode = group.selection_mode

        minimum = group.min_selections or 0
        maximum = group.max_selections

        
        remaining_selections = 0
        selection_error = None

        if mode == "ALL":
        
            required_ids = available_ids

            missing_ids = (
                required_ids - selected_for_group_ids
            )

            complete = len(missing_ids) == 0

        elif mode in ["CHOOSE_ONE", "CONDITIONAL"]:
        
            selected_count = len(selected_for_group_ids)

            remaining_selections = max(
                0,
                minimum - selected_count
            )

            missing_ids = set()

            if selected_count < minimum:
                complete = False
                selection_error = (
                    f"Select at least {minimum} document(s)"
                )

            elif maximum is not None and selected_count > maximum:
                complete = False
                selection_error = (
                    f"Select no more than {maximum} document(s)"
                )

            else:
                complete = True

        elif mode == "OPTIONAL":
        
            missing_ids = set()
            complete = True

        else:
        
            missing_ids = set()
            complete = False
            selection_error = "Unsupported selection mode"


        missing_options = [
            option
            for option in applicable_options
            if option["option_id"] in missing_ids
        ]

        if not complete:
            checklist_complete = False

        all_missing.extend([
            option["option_id"]
            for option in missing_options
        ])

        group_results.append({
            "group_id": group.group_id,
            "group_name": group.group_name,
            "selection_mode": mode,
            "applicable": True,
            "condition_status": group_condition["status"],
            "complete": complete,
            "minimum_selections": minimum,
            "maximum_selections": maximum,
            "available_options": applicable_options,
            "selected_options": selected_for_group,
            "missing_options": missing_options,
            "remaining_selections": remaining_selections,
            "selection_error": selection_error
        })

    return jsonify({
        "success": True,
        "service": {
            "service_id": service.service_id,
            "service_name": service.service_name
        },
        "document_checklist_complete": checklist_complete,
        "total_groups": len(group_results),
        "missing_option_ids": all_missing,
        "groups": group_results
    }), 200
>>>>>>> c981506dbd2f314e63b7e90f4ab444ee1eca2d2c
