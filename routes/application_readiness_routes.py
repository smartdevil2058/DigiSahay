<<<<<<< HEAD

from datetime import date

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from extension import db
from model import (
    Application,
    ApplicationDocument,
    UserDocument,
    Requirement,
    RequirementGroup,
    EligibilityRule,
    DocumentType
)

from utils.rule_evaluator import evaluate_rule


application_readiness_bp = Blueprint(
    "application_readiness",
    __name__,
    url_prefix="/api/applications"
)


def evaluate_condition(rule, answers):

    if not rule:
        return {
            "status": "NO_CONDITION",
            "applicable": True
        }

    if rule.verification_status != "VERIFIED":
        return {
            "status": "NEEDS_REVIEW",
            "applicable": False
        }

    result = evaluate_rule(rule, answers, date.today())

    if result["status"] == "INVALID_RULE":
        return {
            "status": "NEEDS_REVIEW",
            "applicable": False
        }

    if result["status"] in ("INCOMPLETE", "INVALID_ANSWER"):
        return {
            "status": "NEEDS_ANSWER",
            "applicable": False
        }

    return {
        "status": "APPLICABLE" if result.get("passed") else "NOT_APPLICABLE",
        "applicable": bool(result.get("passed"))
    }


def context_matches(applicable_context, applicant_context):

    if not applicable_context:
        return True

    contexts = [
        value.strip()
        for value in applicable_context.split(",")
    ]

    return (
        "ALL_APPLICANTS" in contexts
        or applicant_context in contexts
    )


@application_readiness_bp.post("/<application_id>/readiness")
@jwt_required()
def check_application_readiness(application_id):

    data = request.get_json(silent=True) or {}

    answers = data.get("answers", {})
    applicant_context = data.get(
        "applicant_context",
        "ALL_APPLICANTS"
    )

    if not isinstance(answers, dict):
        return jsonify({
            "success": False,
            "message": "answers must be a JSON object"
        }), 400

    user_id = get_jwt_identity()

    application = Application.query.filter_by(
        application_id=application_id,
        user_id=user_id
    ).first()

    if not application:
        return jsonify({
            "success": False,
            "message": "Application not found"
        }), 404

    eligibility_rules = EligibilityRule.query.filter_by(
        service_id=application.service_id
    ).all()

    eligibility_results = []

    eligibility_rejected = False
    eligibility_needs_review = False

    for rule in eligibility_rules:

        if rule.verification_status != "VERIFIED":
            result = {
                "status": "NEEDS_REVIEW",
                "message": "Rule has not been verified"
            }

        else:
            result = evaluate_rule(
                rule,
                answers,
                date.today()
            )

        status = result.get("status")

        if status == "REJECT":
            eligibility_rejected = True

        elif status != "PROCEED":
            eligibility_needs_review = True

        eligibility_results.append({
            "rule_id": rule.rule_id,
            "question": rule.question_text,
            "status": status,
            "message": result.get("message", "")
        })

    active_attachments = ApplicationDocument.query.filter_by(
        application_id=application_id,
        is_active=True
    ).all()

    attached_documents = []
    attached_option_ids = set()

    for attachment in active_attachments:

        document = UserDocument.query.filter_by(
            document_id=attachment.document_id,
            user_id=user_id,
            is_active=True
        ).first()

        if not document:
            continue

        attached_documents.append({
            "application_document_id": attachment.application_document_id,
            "document_id": document.document_id,
            "document_name": document.document_name,
            "document_type_id": document.document_type_id,
            "requirement_option_id": attachment.requirement_option_id,
            "original_filename": document.original_filename
        })

        if attachment.requirement_option_id:
            attached_option_ids.add(
                attachment.requirement_option_id
            )

    groups = RequirementGroup.query.filter_by(
        service_id=application.service_id
    ).all()

    group_results = []
    missing_requirements = []

    requirements_need_review = False

    for group in groups:

        if group.selection_mode == "OPTIONAL":

            group_results.append({
                "group_id": group.group_id,
                "group_name": group.group_name,
                "selection_mode": group.selection_mode,
                "status": "OPTIONAL",
                "complete": True,
                "selected_option_ids": []
            })

            continue

        if group.condition_rule_id:

            condition_rule = EligibilityRule.query.get(
                group.condition_rule_id
            )

            condition = evaluate_condition(
                condition_rule,
                answers
            )

            if condition["status"] == "NEEDS_ANSWER":
                requirements_need_review = True

                group_results.append({
                    "group_id": group.group_id,
                    "group_name": group.group_name,
                    "status": "NEEDS_ANSWER",
                    "complete": False
                })

                continue

            if condition["status"] == "NEEDS_REVIEW":
                requirements_need_review = True

                group_results.append({
                    "group_id": group.group_id,
                    "group_name": group.group_name,
                    "status": "NEEDS_REVIEW",
                    "complete": False
                })

                continue

            if not condition["applicable"]:
                group_results.append({
                    "group_id": group.group_id,
                    "group_name": group.group_name,
                    "status": "NOT_APPLICABLE",
                    "complete": True,
                    "selected_option_ids": []
                })

                continue

        if group.verification_status != "VERIFIED":
            requirements_need_review = True

            group_results.append({
                "group_id": group.group_id,
                "group_name": group.group_name,
                "status": "NEEDS_REVIEW",
                "complete": False
            })

            continue

        requirements = (
            db.session.query(Requirement)
            .join(
                DocumentType,
                Requirement.document_type_id
                == DocumentType.document_type_id
            )
            .filter(
                Requirement.group_id == group.group_id,
                Requirement.verification_status == "VERIFIED",
                DocumentType.is_active.is_(True),
                DocumentType.verification_status == "VERIFIED"
            )
            .all()
        )

        applicable_requirements = []
        condition_review = False

        for requirement in requirements:

            if not context_matches(
                requirement.applicable_context,
                applicant_context
            ):
                continue

            if requirement.condition_rule_id:

                option_rule = EligibilityRule.query.get(
                    requirement.condition_rule_id
                )

                condition = evaluate_condition(
                    option_rule,
                    answers
                )

                if condition["status"] in (
                    "NEEDS_ANSWER",
                    "NEEDS_REVIEW"
                ):
                    condition_review = True
                    continue

                if not condition["applicable"]:
                    continue

            applicable_requirements.append(requirement)

        if condition_review:
            requirements_need_review = True

            group_results.append({
                "group_id": group.group_id,
                "group_name": group.group_name,
                "status": "NEEDS_REVIEW",
                "complete": False
            })

            continue

        if not applicable_requirements:
            requirements_need_review = True

            group_results.append({
                "group_id": group.group_id,
                "group_name": group.group_name,
                "status": "NEEDS_REVIEW",
                "complete": False,
                "message": "No verified applicable requirements found"
            })

            continue

        selected_option_ids = []

        for requirement in applicable_requirements:

            if requirement.option_id in attached_option_ids:
                selected_option_ids.append(
                    requirement.option_id
                )

        selection_mode = group.selection_mode
        minimum = group.min_selections or 0
        maximum = group.max_selections

        selected_count = len(selected_option_ids)
        available_count = len(applicable_requirements)

        if selection_mode == "ALL":

            complete = (
                selected_count == available_count
            )

        elif selection_mode in ("CHOOSE_ONE", "CONDITIONAL"):

            complete = selected_count >= minimum

            if maximum is not None:
                complete = (
                    complete and selected_count <= maximum
                )

        else:
            requirements_need_review = True
            complete = False

        group_status = (
            "COMPLETE" if complete else "MISSING_DOCUMENTS"
        )

        group_results.append({
            "group_id": group.group_id,
            "group_name": group.group_name,
            "selection_mode": selection_mode,
            "status": group_status,
            "complete": complete,
            "selected_option_ids": selected_option_ids,
            "minimum_selections": minimum,
            "maximum_selections": maximum,
            "available_options": [
                requirement.option_id
                for requirement in applicable_requirements
            ]
        })

        if not complete:
            missing_requirements.append({
                "group_id": group.group_id,
                "group_name": group.group_name,
                "selection_mode": selection_mode,
                "minimum_selections": minimum,
                "selected_count": selected_count
            })

    if eligibility_rejected:

        readiness_status = "INELIGIBLE"

    elif eligibility_needs_review or requirements_need_review:

        readiness_status = "NEEDS_REVIEW"

    elif missing_requirements:

        readiness_status = "REQUIREMENTS_PENDING"

    else:

        readiness_status = "READY_TO_APPLY"

    return jsonify({
        "success": True,
        "application_id": application.application_id,
        "service_id": application.service_id,
        "eligibility": eligibility_results,
        "groups": group_results,
        "attached_documents": attached_documents,
        "total_attached_documents": len(attached_documents),
        "missing_requirements": missing_requirements,
        "readiness_status": readiness_status
    }), 200
=======

from datetime import date

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from extension import db
from model import (
    Application,
    ApplicationDocument,
    UserDocument,
    Requirement,
    RequirementGroup,
    EligibilityRule,
    DocumentType
)

from utils.rule_evaluator import evaluate_rule


application_readiness_bp = Blueprint(
    "application_readiness",
    __name__,
    url_prefix="/api/applications"
)


def evaluate_condition(rule, answers):

    if not rule:
        return {
            "status": "NO_CONDITION",
            "applicable": True
        }

    if rule.verification_status != "VERIFIED":
        return {
            "status": "NEEDS_REVIEW",
            "applicable": False
        }

    result = evaluate_rule(rule, answers, date.today())

    if result["status"] == "INVALID_RULE":
        return {
            "status": "NEEDS_REVIEW",
            "applicable": False
        }

    if result["status"] in ("INCOMPLETE", "INVALID_ANSWER"):
        return {
            "status": "NEEDS_ANSWER",
            "applicable": False
        }

    return {
        "status": "APPLICABLE" if result.get("passed") else "NOT_APPLICABLE",
        "applicable": bool(result.get("passed"))
    }


def context_matches(applicable_context, applicant_context):

    if not applicable_context:
        return True

    contexts = [
        value.strip()
        for value in applicable_context.split(",")
    ]

    return (
        "ALL_APPLICANTS" in contexts
        or applicant_context in contexts
    )


@application_readiness_bp.post("/<application_id>/readiness")
@jwt_required()
def check_application_readiness(application_id):

    data = request.get_json(silent=True) or {}

    answers = data.get("answers", {})
    applicant_context = data.get(
        "applicant_context",
        "ALL_APPLICANTS"
    )

    if not isinstance(answers, dict):
        return jsonify({
            "success": False,
            "message": "answers must be a JSON object"
        }), 400

    user_id = get_jwt_identity()

    application = Application.query.filter_by(
        application_id=application_id,
        user_id=user_id
    ).first()

    if not application:
        return jsonify({
            "success": False,
            "message": "Application not found"
        }), 404

    eligibility_rules = EligibilityRule.query.filter_by(
        service_id=application.service_id
    ).all()

    eligibility_results = []

    eligibility_rejected = False
    eligibility_needs_review = False

    for rule in eligibility_rules:

        if rule.verification_status != "VERIFIED":
            result = {
                "status": "NEEDS_REVIEW",
                "message": "Rule has not been verified"
            }

        else:
            result = evaluate_rule(
                rule,
                answers,
                date.today()
            )

        status = result.get("status")

        if status == "REJECT":
            eligibility_rejected = True

        elif status != "PROCEED":
            eligibility_needs_review = True

        eligibility_results.append({
            "rule_id": rule.rule_id,
            "question": rule.question_text,
            "status": status,
            "message": result.get("message", "")
        })

    active_attachments = ApplicationDocument.query.filter_by(
        application_id=application_id,
        is_active=True
    ).all()

    attached_documents = []
    attached_option_ids = set()

    for attachment in active_attachments:

        document = UserDocument.query.filter_by(
            document_id=attachment.document_id,
            user_id=user_id,
            is_active=True
        ).first()

        if not document:
            continue

        attached_documents.append({
            "application_document_id": attachment.application_document_id,
            "document_id": document.document_id,
            "document_name": document.document_name,
            "document_type_id": document.document_type_id,
            "requirement_option_id": attachment.requirement_option_id,
            "original_filename": document.original_filename
        })

        if attachment.requirement_option_id:
            attached_option_ids.add(
                attachment.requirement_option_id
            )

    groups = RequirementGroup.query.filter_by(
        service_id=application.service_id
    ).all()

    group_results = []
    missing_requirements = []

    requirements_need_review = False

    for group in groups:

        if group.selection_mode == "OPTIONAL":

            group_results.append({
                "group_id": group.group_id,
                "group_name": group.group_name,
                "selection_mode": group.selection_mode,
                "status": "OPTIONAL",
                "complete": True,
                "selected_option_ids": []
            })

            continue

        if group.condition_rule_id:

            condition_rule = EligibilityRule.query.get(
                group.condition_rule_id
            )

            condition = evaluate_condition(
                condition_rule,
                answers
            )

            if condition["status"] == "NEEDS_ANSWER":
                requirements_need_review = True

                group_results.append({
                    "group_id": group.group_id,
                    "group_name": group.group_name,
                    "status": "NEEDS_ANSWER",
                    "complete": False
                })

                continue

            if condition["status"] == "NEEDS_REVIEW":
                requirements_need_review = True

                group_results.append({
                    "group_id": group.group_id,
                    "group_name": group.group_name,
                    "status": "NEEDS_REVIEW",
                    "complete": False
                })

                continue

            if not condition["applicable"]:
                group_results.append({
                    "group_id": group.group_id,
                    "group_name": group.group_name,
                    "status": "NOT_APPLICABLE",
                    "complete": True,
                    "selected_option_ids": []
                })

                continue

        if group.verification_status != "VERIFIED":
            requirements_need_review = True

            group_results.append({
                "group_id": group.group_id,
                "group_name": group.group_name,
                "status": "NEEDS_REVIEW",
                "complete": False
            })

            continue

        requirements = (
            db.session.query(Requirement)
            .join(
                DocumentType,
                Requirement.document_type_id
                == DocumentType.document_type_id
            )
            .filter(
                Requirement.group_id == group.group_id,
                Requirement.verification_status == "VERIFIED",
                DocumentType.is_active.is_(True),
                DocumentType.verification_status == "VERIFIED"
            )
            .all()
        )

        applicable_requirements = []
        condition_review = False

        for requirement in requirements:

            if not context_matches(
                requirement.applicable_context,
                applicant_context
            ):
                continue

            if requirement.condition_rule_id:

                option_rule = EligibilityRule.query.get(
                    requirement.condition_rule_id
                )

                condition = evaluate_condition(
                    option_rule,
                    answers
                )

                if condition["status"] in (
                    "NEEDS_ANSWER",
                    "NEEDS_REVIEW"
                ):
                    condition_review = True
                    continue

                if not condition["applicable"]:
                    continue

            applicable_requirements.append(requirement)

        if condition_review:
            requirements_need_review = True

            group_results.append({
                "group_id": group.group_id,
                "group_name": group.group_name,
                "status": "NEEDS_REVIEW",
                "complete": False
            })

            continue

        if not applicable_requirements:
            requirements_need_review = True

            group_results.append({
                "group_id": group.group_id,
                "group_name": group.group_name,
                "status": "NEEDS_REVIEW",
                "complete": False,
                "message": "No verified applicable requirements found"
            })

            continue

        selected_option_ids = []

        for requirement in applicable_requirements:

            if requirement.option_id in attached_option_ids:
                selected_option_ids.append(
                    requirement.option_id
                )

        selection_mode = group.selection_mode
        minimum = group.min_selections or 0
        maximum = group.max_selections

        selected_count = len(selected_option_ids)
        available_count = len(applicable_requirements)

        if selection_mode == "ALL":

            complete = (
                selected_count == available_count
            )

        elif selection_mode in ("CHOOSE_ONE", "CONDITIONAL"):

            complete = selected_count >= minimum

            if maximum is not None:
                complete = (
                    complete and selected_count <= maximum
                )

        else:
            requirements_need_review = True
            complete = False

        group_status = (
            "COMPLETE" if complete else "MISSING_DOCUMENTS"
        )

        group_results.append({
            "group_id": group.group_id,
            "group_name": group.group_name,
            "selection_mode": selection_mode,
            "status": group_status,
            "complete": complete,
            "selected_option_ids": selected_option_ids,
            "minimum_selections": minimum,
            "maximum_selections": maximum,
            "available_options": [
                requirement.option_id
                for requirement in applicable_requirements
            ]
        })

        if not complete:
            missing_requirements.append({
                "group_id": group.group_id,
                "group_name": group.group_name,
                "selection_mode": selection_mode,
                "minimum_selections": minimum,
                "selected_count": selected_count
            })

    if eligibility_rejected:

        readiness_status = "INELIGIBLE"

    elif eligibility_needs_review or requirements_need_review:

        readiness_status = "NEEDS_REVIEW"

    elif missing_requirements:

        readiness_status = "REQUIREMENTS_PENDING"

    else:

        readiness_status = "READY_TO_APPLY"

    return jsonify({
        "success": True,
        "application_id": application.application_id,
        "service_id": application.service_id,
        "eligibility": eligibility_results,
        "groups": group_results,
        "attached_documents": attached_documents,
        "total_attached_documents": len(attached_documents),
        "missing_requirements": missing_requirements,
        "readiness_status": readiness_status
    }), 200
>>>>>>> c981506dbd2f314e63b7e90f4ab444ee1eca2d2c
