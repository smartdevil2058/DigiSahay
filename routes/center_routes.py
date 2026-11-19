
from flask import Blueprint, jsonify, request

from extension import db
from model import Service, ServiceCenter, CenterService

center_bp = Blueprint("center", __name__)


def center_to_dict(center):
    return {
        "center_id": center.center_id,
        "center_name": center.center_name,
        "center_type": center.center_type,
        "authority_name": center.authority_name,
        "address_line": center.address_line,
        "city": center.city,
        "district": center.district,
        "state": center.state,
        "pincode": center.pincode,
        "latitude": center.latitude,
        "longitude": center.longitude,
        "contact_number": center.contact_number,
        "operating_hours": center.operating_hours,
        "official_source_url": center.official_source_url,
        "data_last_verified": (
            center.data_last_verified.isoformat()
            if center.data_last_verified else None
        ),
        "verification_status": center.verification_status,
        "notes": center.notes
    }


def service_to_dict(center_service, service):
    return {
        "service_id": service.service_id,
        "service_name": service.service_name,
        "service_available": center_service.service_available,
        "appointment_supported": center_service.appointment_supported,
        "booking_method": center_service.booking_method,
        "official_booking_url": center_service.official_booking_url,
        "availability_source": center_service.availability_source,
        "verification_status": center_service.verification_status,
        "last_verified_at": (
            center_service.last_verified_at.isoformat()
            if center_service.last_verified_at else None
        )
    }


@center_bp.get("/api/centers")
def get_centers():

    service_id = request.args.get("service_id")
    district = request.args.get("district")
    city = request.args.get("city")
    pincode = request.args.get("pincode")

    if service_id:
        service = Service.query.filter_by(
            service_id=service_id
        ).first()

        if not service:
            return jsonify({
                "success": False,
                "message": "Service not found"
            }), 404

    query = (
        db.session.query(ServiceCenter, CenterService, Service)
        .join(
            CenterService,
            ServiceCenter.center_id == CenterService.center_id
        )
        .join(
            Service,
            CenterService.service_id == Service.service_id
        )
        .filter(
            CenterService.service_available.is_(True),
            Service.is_active.is_(True)
        )
    )

    if service_id:
        query = query.filter(
            CenterService.service_id == service_id
        )

    if district:
        query = query.filter(
            ServiceCenter.district.ilike(district.strip())
        )

    if city:
        query = query.filter(
            ServiceCenter.city.ilike(city.strip())
        )

    if pincode:
        query = query.filter(
            ServiceCenter.pincode == pincode.strip()
        )

    rows = query.order_by(
        ServiceCenter.center_name
    ).all()

    centers = {}

    for center, center_service, service in rows:

        if center.center_id not in centers:
            centers[center.center_id] = center_to_dict(center)
            centers[center.center_id]["services"] = []

        centers[center.center_id]["services"].append(
            service_to_dict(center_service, service)
        )

    result = list(centers.values())

    return jsonify({
        "success": True,
        "total_centers": len(result),
        "filters": {
            "service_id": service_id,
            "district": district,
            "city": city,
            "pincode": pincode
        },
        "centers": result
    }), 200


@center_bp.get("/api/centers/<center_id>")
def get_center_details(center_id):

    center = ServiceCenter.query.filter_by(
        center_id=center_id
    ).first()

    if not center:
        return jsonify({
            "success": False,
            "message": "Service centre not found"
        }), 404

    rows = (
        db.session.query(CenterService, Service)
        .join(
            Service,
            CenterService.service_id == Service.service_id
        )
        .filter(CenterService.center_id == center_id)
        .all()
    )

    services = []

    for center_service, service in rows:
        services.append(
            service_to_dict(center_service, service)
        )

    result = center_to_dict(center)
    result["services"] = services

    return jsonify({
        "success": True,
        "center": result
    }), 200
