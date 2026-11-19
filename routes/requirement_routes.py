
from flask import Blueprint, jsonify
from model import RequirementGroup, Service, Requirement, DocumentType
from extension import db

requirement_bp = Blueprint("requirement", __name__)


@requirement_bp.get("/api/services/<service_id>/requirements")
def get_service_requirements(service_id):

    service = Service.query.filter_by(
        service_id=service_id
    ).first()

    if not service:
        return jsonify({
            "success": False,
            "message": "Service not found"
        }), 404

    groups = RequirementGroup.query.filter_by(
        service_id=service_id
    ).all()

    rows = (
        db.session.query(Requirement, DocumentType)
        .join(
            DocumentType,
            Requirement.document_type_id == DocumentType.document_type_id
        )
        .join(
            RequirementGroup,
            Requirement.group_id == RequirementGroup.group_id
        )
        .filter(RequirementGroup.service_id == service_id)
        .all()
    )

    documents_by_group = {}

    for requirement, document in rows:

        documents_by_group.setdefault(
            requirement.group_id, []
        ).append({
            "option_id": requirement.option_id,
            "document_type_id": document.document_type_id,
            "document_name": document.document_name,
            "document_category": document.document_category,
            "description": document.description,
            "original_or_copy_requirement": document.original_or_copy_requirement,
            "format_or_size_constraints": document.format_or_size_constraints,
            "special_conditions": document.special_conditions,
            "applicable_context": requirement.applicable_context,
            "official_acceptance_conditions": requirement.official_acceptance_conditions,
            "verification_status": requirement.verification_status
        })

    result = []

    for group in groups:

        result.append({
            "group_id": group.group_id,
            "group_name": group.group_name,
            "description": group.description,
            "selection_mode": group.selection_mode,
            "min_selections": group.min_selections,
            "max_selections": group.max_selections,
            "documents": documents_by_group.get(group.group_id, [])
        })

    return jsonify({
        "success": True,
        "service": {
            "service_id": service.service_id,
            "service_name": service.service_name
        },
        "total_groups": len(result),
        "requirement_groups": result
    }), 200
