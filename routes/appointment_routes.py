
from flask import Blueprint, jsonify

from model import Appointment, ServiceCenter, Service
from extension import db

appointment_bp = Blueprint("appointment", __name__)


def appointment_to_dict(appointment, center, service):

    return {
        "appointment_id": appointment.appointment_id,
        "application_id": appointment.application_id,

        "service": {
            "service_id": service.service_id,
            "service_name": service.service_name
        },

        "center": {
            "center_id": center.center_id,
            "center_name": center.center_name,
            "address_line": center.address_line,
            "city": center.city,
            "district": center.district,
            "pincode": center.pincode,
            "contact_number": center.contact_number
        },

        "requested_date": appointment.requested_date.isoformat(),
        "requested_time": appointment.requested_time.isoformat(),

        "confirmed_date": (
            appointment.confirmed_date.isoformat()
            if appointment.confirmed_date else None
        ),

        "confirmed_time": (
            appointment.confirmed_time.isoformat()
            if appointment.confirmed_time else None
        ),

        "booking_reference": appointment.booking_reference,
        "booking_method": appointment.booking_method,
        "official_booking_url": appointment.official_booking_url,
        "appointment_status": appointment.appointment_status,

        "created_at": appointment.created_at.isoformat(),
        "updated_at": appointment.updated_at.isoformat(),

        "notes": appointment.notes
    }


@appointment_bp.get("/api/users/<user_id>/appointments")
def get_user_appointments(user_id):

    rows = (
        db.session.query(Appointment, ServiceCenter, Service)
        .join(
            ServiceCenter,
            Appointment.center_id == ServiceCenter.center_id
        )
        .join(
            Service,
            Appointment.service_id == Service.service_id
        )
        .filter(Appointment.user_id == user_id)
        .order_by(Appointment.requested_date.desc())
        .all()
    )

    result = []

    for appointment, center, service in rows:
        result.append(
            appointment_to_dict(appointment, center, service)
        )

    return jsonify({
        "success": True,
        "user_id": user_id,
        "total_appointments": len(result),
        "appointments": result
    }), 200


@appointment_bp.get("/api/appointments/<appointment_id>")
def get_appointment_details(appointment_id):

    row = (
        db.session.query(Appointment, ServiceCenter, Service)
        .join(
            ServiceCenter,
            Appointment.center_id == ServiceCenter.center_id
        )
        .join(
            Service,
            Appointment.service_id == Service.service_id
        )
        .filter(
            Appointment.appointment_id == appointment_id
        )
        .first()
    )

    if not row:
        return jsonify({
            "success": False,
            "message": "Appointment not found"
        }), 404

    appointment, center, service = row

    return jsonify({
        "success": True,
        "appointment": appointment_to_dict(
            appointment, center, service
        )
    }), 200
