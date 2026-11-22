<<<<<<< HEAD

from datetime import datetime
from uuid import uuid4

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from extension import db
from model import Application, ApplicationStatusHistory


application_status_bp = Blueprint(
    "application_status",
    __name__,
    url_prefix="/api/applications"
)


ALLOWED_TRANSITIONS = {
    "DRAFT": ["READY_TO_APPLY", "CANCELLED"],
    "READY_TO_APPLY": ["SUBMITTED_EXTERNALLY", "CANCELLED"],
    "SUBMITTED_EXTERNALLY": [
        "UNDER_REVIEW",
        "NEEDS_CORRECTION",
        "APPROVED",
        "REJECTED"
    ],
    "UNDER_REVIEW": [
        "NEEDS_CORRECTION",
        "APPROVED",
        "REJECTED"
    ],
    "NEEDS_CORRECTION": ["SUBMITTED_EXTERNALLY"],
    "APPROVED": [],
    "REJECTED": [],
    "CANCELLED": []
}


@application_status_bp.patch("/<application_id>/status")
@jwt_required()
def update_application_status(application_id):

    data = request.get_json(silent=True) or {}

    new_status = data.get("new_status")
    remarks = data.get("remarks")

    if not new_status:
        return jsonify({
            "success": False,
            "message": "new_status is required"
        }), 400

    if not isinstance(new_status, str):
        return jsonify({
            "success": False,
            "message": "new_status must be a string"
        }), 400

    if remarks is not None and not isinstance(remarks, str):
        return jsonify({
            "success": False,
            "message": "remarks must be a string"
        }), 400

    new_status = new_status.strip().upper()

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

    previous_status = application.application_status or "DRAFT"

    allowed_statuses = ALLOWED_TRANSITIONS.get(
        previous_status,
        []
    )

    if new_status not in allowed_statuses:
        return jsonify({
            "success": False,
            "message": "Invalid status transition",
            "current_status": previous_status,
            "requested_status": new_status,
            "allowed_statuses": allowed_statuses
        }), 409

    current_time = datetime.utcnow()

    history = ApplicationStatusHistory(
        history_id=f"ASH-{uuid4().hex[:12].upper()}",
        application_id=application_id,
        previous_status=previous_status,
        new_status=new_status,
        remarks=remarks,
        update_source="USER",
        changed_by=user_id,
        changed_at=current_time
    )

    application.application_status = new_status
    application.last_status_updated_at = current_time

    if new_status == "SUBMITTED_EXTERNALLY":
        application.submitted_at = current_time

    try:
        db.session.add(history)
        db.session.commit()

    except Exception:
        db.session.rollback()

        return jsonify({
            "success": False,
            "message": "Unable to update application status"
        }), 500

    return jsonify({
        "success": True,
        "message": "Application status updated successfully",
        "application_id": application_id,
        "previous_status": previous_status,
        "new_status": new_status,
        "changed_at": current_time.isoformat()
    }), 200


@application_status_bp.get("/<application_id>/status")
@jwt_required()
def get_application_status(application_id):

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

    return jsonify({
        "success": True,
        "application_id": application.application_id,
        "service_id": application.service_id,
        "application_reference": application.application_reference,
        "application_status": application.application_status,
        "application_mode": application.application_mode,
        "submitted_at": (
            application.submitted_at.isoformat()
            if application.submitted_at else None
        ),
        "last_status_updated_at": (
            application.last_status_updated_at.isoformat()
            if application.last_status_updated_at else None
        )
    }), 200


@application_status_bp.get("/<application_id>/status-history")
@jwt_required()
def get_application_status_history(application_id):

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

    history_records = (
        ApplicationStatusHistory.query
        .filter_by(application_id=application_id)
        .order_by(ApplicationStatusHistory.changed_at.desc())
        .all()
    )

    history = []

    for record in history_records:

        history.append({
            "history_id": record.history_id,
            "previous_status": record.previous_status,
            "new_status": record.new_status,
            "remarks": record.remarks,
            "update_source": record.update_source,
            "changed_by": record.changed_by,
            "changed_at": record.changed_at.isoformat()
        })

    return jsonify({
        "success": True,
        "application_id": application.application_id,
        "current_status": application.application_status,
        "total_updates": len(history),
        "history": history
    }), 200
=======

from datetime import datetime
from uuid import uuid4

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from extension import db
from model import Application, ApplicationStatusHistory


application_status_bp = Blueprint(
    "application_status",
    __name__,
    url_prefix="/api/applications"
)


ALLOWED_TRANSITIONS = {
    "DRAFT": ["READY_TO_APPLY", "CANCELLED"],
    "READY_TO_APPLY": ["SUBMITTED_EXTERNALLY", "CANCELLED"],
    "SUBMITTED_EXTERNALLY": [
        "UNDER_REVIEW",
        "NEEDS_CORRECTION",
        "APPROVED",
        "REJECTED"
    ],
    "UNDER_REVIEW": [
        "NEEDS_CORRECTION",
        "APPROVED",
        "REJECTED"
    ],
    "NEEDS_CORRECTION": ["SUBMITTED_EXTERNALLY"],
    "APPROVED": [],
    "REJECTED": [],
    "CANCELLED": []
}


@application_status_bp.patch("/<application_id>/status")
@jwt_required()
def update_application_status(application_id):

    data = request.get_json(silent=True) or {}

    new_status = data.get("new_status")
    remarks = data.get("remarks")

    if not new_status:
        return jsonify({
            "success": False,
            "message": "new_status is required"
        }), 400

    if not isinstance(new_status, str):
        return jsonify({
            "success": False,
            "message": "new_status must be a string"
        }), 400

    if remarks is not None and not isinstance(remarks, str):
        return jsonify({
            "success": False,
            "message": "remarks must be a string"
        }), 400

    new_status = new_status.strip().upper()

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

    previous_status = application.application_status or "DRAFT"

    allowed_statuses = ALLOWED_TRANSITIONS.get(
        previous_status,
        []
    )

    if new_status not in allowed_statuses:
        return jsonify({
            "success": False,
            "message": "Invalid status transition",
            "current_status": previous_status,
            "requested_status": new_status,
            "allowed_statuses": allowed_statuses
        }), 409

    current_time = datetime.utcnow()

    history = ApplicationStatusHistory(
        history_id=f"ASH-{uuid4().hex[:12].upper()}",
        application_id=application_id,
        previous_status=previous_status,
        new_status=new_status,
        remarks=remarks,
        update_source="USER",
        changed_by=user_id,
        changed_at=current_time
    )

    application.application_status = new_status
    application.last_status_updated_at = current_time

    if new_status == "SUBMITTED_EXTERNALLY":
        application.submitted_at = current_time

    try:
        db.session.add(history)
        db.session.commit()

    except Exception:
        db.session.rollback()

        return jsonify({
            "success": False,
            "message": "Unable to update application status"
        }), 500

    return jsonify({
        "success": True,
        "message": "Application status updated successfully",
        "application_id": application_id,
        "previous_status": previous_status,
        "new_status": new_status,
        "changed_at": current_time.isoformat()
    }), 200


@application_status_bp.get("/<application_id>/status")
@jwt_required()
def get_application_status(application_id):

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

    return jsonify({
        "success": True,
        "application_id": application.application_id,
        "service_id": application.service_id,
        "application_reference": application.application_reference,
        "application_status": application.application_status,
        "application_mode": application.application_mode,
        "submitted_at": (
            application.submitted_at.isoformat()
            if application.submitted_at else None
        ),
        "last_status_updated_at": (
            application.last_status_updated_at.isoformat()
            if application.last_status_updated_at else None
        )
    }), 200


@application_status_bp.get("/<application_id>/status-history")
@jwt_required()
def get_application_status_history(application_id):

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

    history_records = (
        ApplicationStatusHistory.query
        .filter_by(application_id=application_id)
        .order_by(ApplicationStatusHistory.changed_at.desc())
        .all()
    )

    history = []

    for record in history_records:

        history.append({
            "history_id": record.history_id,
            "previous_status": record.previous_status,
            "new_status": record.new_status,
            "remarks": record.remarks,
            "update_source": record.update_source,
            "changed_by": record.changed_by,
            "changed_at": record.changed_at.isoformat()
        })

    return jsonify({
        "success": True,
        "application_id": application.application_id,
        "current_status": application.application_status,
        "total_updates": len(history),
        "history": history
    }), 200
>>>>>>> c981506dbd2f314e63b7e90f4ab444ee1eca2d2c
