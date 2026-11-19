
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from uuid import uuid4

from extension import db
from model import (
    Application,
    UserDocument,
    ApplicationDocument,
    Requirement,
    RequirementGroup
)

application_document_bp = Blueprint(
    "application_documents",
    __name__,
    url_prefix="/api/applications"
)


@application_document_bp.route(
    "/<application_id>/documents",
    methods=["POST"]
)
@jwt_required()
def attach_document(application_id):

    user_id = get_jwt_identity()
    data = request.get_json()

    if not data:
        return jsonify({
            "success": False,
            "message": "Request body is required"
        }), 400

    document_id = data.get("document_id")
    requirement_option_id = data.get("requirement_option_id")

    if not document_id or not requirement_option_id:
        return jsonify({
            "success": False,
            "message": "document_id and requirement_option_id are required"
        }), 400

    # 1. Check application ownership
    application = Application.query.filter_by(
        application_id=application_id,
        user_id=user_id
    ).first()

    if not application:
        return jsonify({
            "success": False,
            "message": "Application not found"
        }), 404

    # 2. Check document ownership
    document = UserDocument.query.filter_by(
        document_id=document_id,
        user_id=user_id,
        is_active=True
    ).first()

    if not document:
        return jsonify({
            "success": False,
            "message": "Document not found"
        }), 404

    # 3. Check that the requirement belongs to this service
    requirement = (
        db.session.query(Requirement)
        .join(
            RequirementGroup,
            Requirement.group_id == RequirementGroup.group_id
        )
        .filter(
            Requirement.option_id == requirement_option_id,
            RequirementGroup.service_id == application.service_id
        )
        .first()
    )

    if not requirement:
        return jsonify({
            "success": False,
            "message": "Requirement does not belong to this application service"
        }), 400

    # 4. Check document type compatibility
    if requirement.document_type_id != document.document_type_id:
        return jsonify({
            "success": False,
            "message": "This document type does not match the selected requirement"
        }), 400

    # 5. Prevent duplicate active attachments
    existing_attachment = ApplicationDocument.query.filter_by(
        application_id=application_id,
        document_id=document_id,
        requirement_option_id=requirement_option_id,
        is_active=True
    ).first()

    if existing_attachment:
        return jsonify({
            "success": False,
            "message": "This document is already attached to this requirement"
        }), 409

    # 6. Create attachment
    attachment = ApplicationDocument(
        application_document_id=f"ADOC-{uuid4().hex[:12].upper()}",
        application_id=application_id,
        document_id=document_id,
        requirement_option_id=requirement_option_id
    )

    try:
        db.session.add(attachment)
        db.session.commit()

    except Exception:
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": "Could not attach document"
        }), 500

    return jsonify({
        "success": True,
        "message": "Document attached successfully",
        "attachment": {
            "application_document_id": attachment.application_document_id,
            "application_id": attachment.application_id,
            "document_id": attachment.document_id,
            "requirement_option_id": attachment.requirement_option_id,
            "attached_at": attachment.attached_at.isoformat()
        }
    }), 201



@application_document_bp.route(
    "/<application_id>/documents",
    methods=["GET"]
)
@jwt_required()
def get_application_documents(application_id):

    user_id = get_jwt_identity()

    # Check application ownership
    application = Application.query.filter_by(
        application_id=application_id,
        user_id=user_id
    ).first()

    if not application:
        return jsonify({
            "success": False,
            "message": "Application not found"
        }), 404

    attachments = (
        db.session.query(ApplicationDocument, UserDocument, Requirement)
        .join(
            UserDocument,
            ApplicationDocument.document_id == UserDocument.document_id
        )
        .join(
            Requirement,
            ApplicationDocument.requirement_option_id == Requirement.option_id
        )
        .filter(
            ApplicationDocument.application_id == application_id,
            ApplicationDocument.is_active == True,
            UserDocument.is_active == True
        )
        .all()
    )

    result = []

    for attachment, document, requirement in attachments:

        result.append({
            "application_document_id": attachment.application_document_id,
            "document_id": document.document_id,
            "document_name": document.document_name,
            "original_filename": document.original_filename,
            "document_type_id": document.document_type_id,
            "requirement_option_id": requirement.option_id,
            "attached_at": attachment.attached_at.isoformat(),
            "download_url": f"/api/documents/{document.document_id}/download"
        })

    return jsonify({
        "success": True,
        "application_id": application_id,
        "total_documents": len(result),
        "documents": result
    }), 200




@application_document_bp.route(
    "/<application_id>/documents/<application_document_id>",
    methods=["DELETE"]
)
@jwt_required()
def detach_application_document(application_id, application_document_id):

    user_id = get_jwt_identity()

    # Check application ownership
    application = Application.query.filter_by(
        application_id=application_id,
        user_id=user_id
    ).first()

    if not application:
        return jsonify({
            "success": False,
            "message": "Application not found"
        }), 404

    # Find active attachment
    attachment = ApplicationDocument.query.filter_by(
        application_id=application_id,
        application_document_id=application_document_id,
        is_active=True
    ).first()

    if not attachment:
        return jsonify({
            "success": False,
            "message": "Attached document not found"
        }), 404

    # Soft delete the attachment only
    attachment.is_active = False

    try:
        db.session.commit()

    except Exception:
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": "Could not detach document"
        }), 500

    return jsonify({
        "success": True,
        "message": "Document detached successfully",
        "application_document_id": application_document_id
    }), 200
