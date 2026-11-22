import json
from datetime import datetime
from uuid import uuid4
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash

from extension import db
from model import (
    Application,
    Service,
    User,
    ApplicationStatusHistory,
    ApplicationDocument,
    UserDocument,
    Requirement
)

application_bp = Blueprint("application", __name__)


def application_to_dict(application, service):
    applicant_details = {}
    if application.notes:
        try:
            applicant_details = json.loads(application.notes)
        except Exception:
            applicant_details = {"notes": application.notes}

    # Fetch attached documents if any
    attached_docs = []
    try:
        docs = (
            db.session.query(ApplicationDocument, UserDocument)
            .join(UserDocument, ApplicationDocument.document_id == UserDocument.document_id)
            .filter(
                ApplicationDocument.application_id == application.application_id,
                ApplicationDocument.is_active == True
            )
            .all()
        )
        for app_doc, user_doc in docs:
            attached_docs.append({
                "application_document_id": app_doc.application_document_id,
                "document_id": user_doc.document_id,
                "document_name": user_doc.document_name,
                "document_type_id": user_doc.document_type_id,
                "file_type": user_doc.file_type,
                "attached_at": app_doc.attached_at.isoformat() if app_doc.attached_at else None
            })
    except Exception:
        pass

    return {
        "application_id": application.application_id,
        "application_reference": application.application_reference,
        "service": {
            "service_id": service.service_id if service else None,
            "service_name": service.service_name if service else None
        },
        "application_mode": application.application_mode,
        "application_status": application.application_status,
        "submitted_at": (
            application.submitted_at.isoformat()
            if application.submitted_at else None
        ),
        "last_status_updated_at": (
            application.last_status_updated_at.isoformat()
            if application.last_status_updated_at else None
        ),
        "official_status_source": application.official_status_source,
        "related_appointment_id": application.related_appointment_id,
        "notes": application.notes,
        "applicant_details": applicant_details,
        "attached_documents": attached_docs
    }


@application_bp.get("/api/users/<user_id>/applications")
def get_user_applications(user_id):
    rows = (
        Application.query
        .join(
            Service,
            Application.service_id == Service.service_id
        )
        .filter(Application.user_id == user_id)
        .order_by(Application.submitted_at.desc())
        .all()
    )

    result = []
    for application in rows:
        service = Service.query.filter_by(
            service_id=application.service_id
        ).first()

        result.append(
            application_to_dict(application, service)
        )

    return jsonify({
        "success": True,
        "user_id": user_id,
        "total_applications": len(result),
        "applications": result
    }), 200


@application_bp.get("/api/applications/me")
@jwt_required()
def get_my_applications():
    user_id = get_jwt_identity()
    return get_user_applications(user_id)


@application_bp.get("/api/applications/<application_id>")
def get_application_details(application_id):
    row = (
        Application.query
        .join(
            Service,
            Application.service_id == Service.service_id
        )
        .filter(
            Application.application_id == application_id
        )
        .first()
    )

    if not row:
        return jsonify({
            "success": False,
            "message": "Application not found"
        }), 404

    application = row
    service = Service.query.filter_by(
        service_id=application.service_id
    ).first()

    return jsonify({
        "success": True,
        "application": application_to_dict(
            application, service
        )
    }), 200


@application_bp.post("/api/applications")
@jwt_required(optional=True)
def create_application():
    data = request.get_json(silent=True) or {}
    user_id = get_jwt_identity()

    if not user_id:
        user_id = data.get("user_id")

    # If user_id is still missing, check applicant email or create a user profile
    if not user_id:
        email = (data.get("applicant_email") or data.get("email") or "").strip().lower()
        if email and "@" in email:
            user = User.query.filter_by(email=email).first()
            if not user:
                user = User(
                    user_id=f"USR-{uuid4().hex[:12].upper()}",
                    email=email,
                    password_hash=generate_password_hash("DigiSahay@2026"),
                    preferred_language=data.get("preferred_language", "gu")
                )
                db.session.add(user)
                db.session.flush()
            user_id = user.user_id
        else:
            first_user = User.query.first()
            if first_user:
                user_id = first_user.user_id
            else:
                return jsonify({
                    "success": False,
                    "message": "A valid applicant email address or citizen sign-in is required"
                }), 400

    service_id = data.get("service_id")
    if not service_id:
        return jsonify({
            "success": False,
            "message": "service_id is required"
        }), 400

    service = Service.query.filter_by(service_id=service_id).first()
    if not service:
        return jsonify({
            "success": False,
            "message": "Service not found"
        }), 404

    # Generate IDs
    app_suffix = uuid4().hex[:6].upper()
    now = datetime.utcnow()
    now_str = now.strftime("%Y%m%d")
    application_id = f"APP-2026-{app_suffix}"
    srv_code = service.service_id.replace("SVC-", "").replace("-", "")
    application_reference = f"DIGI/{srv_code}/{now_str}/{app_suffix}"

    application_mode = data.get("application_mode", "ONLINE_ASSISTED")
    initial_status = data.get("application_status", "READY_TO_APPLY")

    applicant_data = {
        "full_name": data.get("applicant_name") or data.get("full_name") or "",
        "guardian_name": data.get("guardian_name") or data.get("father_name") or "",
        "dob": data.get("dob") or data.get("applicant_dob") or "",
        "gender": data.get("gender") or "",
        "mobile": data.get("mobile") or data.get("applicant_mobile") or "",
        "email": data.get("email") or data.get("applicant_email") or "",
        "address": data.get("address") or data.get("applicant_address") or "",
        "district": data.get("district") or data.get("applicant_district") or "Ahmedabad",
        "pincode": data.get("pincode") or data.get("applicant_pincode") or "",
        "application_mode": application_mode,
        "additional_notes": data.get("notes") or ""
    }

    application = Application(
        application_id=application_id,
        user_id=user_id,
        service_id=service_id,
        application_reference=application_reference,
        application_mode=application_mode,
        application_status=initial_status,
        submitted_at=now,
        last_status_updated_at=now,
        official_status_source="DigiSahay Direct Citizen Application Preparation",
        notes=json.dumps(applicant_data)
    )
    db.session.add(application)
    db.session.flush()

    # Initial history milestone
    history = ApplicationStatusHistory(
        history_id=f"HIST-{uuid4().hex[:12].upper()}",
        application_id=application_id,
        previous_status=None,
        new_status=initial_status,
        remarks=f"Citizen initiated application dossier for {service.service_name}",
        update_source="CITIZEN_PORTAL",
        changed_by=user_id,
        changed_at=now
    )
    db.session.add(history)

    # Attach documents if provided
    document_ids = data.get("document_ids", [])
    for doc_entry in document_ids:
        doc_id = doc_entry if isinstance(doc_entry, str) else doc_entry.get("document_id")
        req_opt_id = None if isinstance(doc_entry, str) else doc_entry.get("requirement_option_id")
        if doc_id:
            user_doc = UserDocument.query.filter_by(document_id=doc_id, is_active=True).first()
            if user_doc:
                if req_opt_id:
                    valid_req = Requirement.query.filter_by(option_id=req_opt_id).first()
                    if not valid_req:
                        req_opt_id = None
                app_doc = ApplicationDocument(
                    application_document_id=f"ADOC-{uuid4().hex[:12].upper()}",
                    application_id=application_id,
                    document_id=doc_id,
                    requirement_option_id=req_opt_id,
                    attached_at=now,
                    is_active=True
                )
                db.session.add(app_doc)

    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Application created successfully",
        "application_id": application_id,
        "application_reference": application_reference,
        "application": application_to_dict(application, service)
    }), 201
