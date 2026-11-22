<<<<<<< HEAD
from flask import Blueprint,jsonify
from model import Service


service_bp = Blueprint("services",__name__)

@service_bp.get("/api/services")
def get_service():
    services = Service.query.order_by(Service.service_name).all()
    result = []

    for service in services:
        result.append({
            "service_id": service.service_id,
            "service_name": service.service_name,
            "service_category": service.service_category,
            "application_or_update_type": service.application_or_update_type,
            "form_name_or_number": service.form_name_or_number,
            "description": service.description,
            "responsible_authority": service.responsible_authority,
            "official_service_url": service.official_service_url,
            "is_active": service.is_active,
            "verification_status": service.verification_status
        })

    return jsonify({
        "Success" : True,
        "Total" : len(result),
        "services" : result
    }),200
=======
from flask import Blueprint,jsonify
from model import Service


service_bp = Blueprint("services",__name__)

@service_bp.get("/api/services")
def get_service():
    services = Service.query.order_by(Service.service_name).all()
    result = []

    for service in services:
        result.append({
            "service_id": service.service_id,
            "service_name": service.service_name,
            "service_category": service.service_category,
            "application_or_update_type": service.application_or_update_type,
            "form_name_or_number": service.form_name_or_number,
            "description": service.description,
            "responsible_authority": service.responsible_authority,
            "official_service_url": service.official_service_url,
            "is_active": service.is_active,
            "verification_status": service.verification_status
        })

    return jsonify({
        "Success" : True,
        "Total" : len(result),
        "services" : result
    }),200
>>>>>>> c981506dbd2f314e63b7e90f4ab444ee1eca2d2c
