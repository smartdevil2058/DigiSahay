from flask import Blueprint, render_template, request
from model import Service, ServiceCenter

frontend_bp = Blueprint("frontend", __name__)


@frontend_bp.get("/")
@frontend_bp.get("/dashboard")
def index():
    return render_template("index.html", active_page="dashboard")


@frontend_bp.get("/services")
def services_page():
    services = Service.query.order_by(Service.service_name).all()
    return render_template("services.html", services=services, active_page="services")


@frontend_bp.get("/prerequisite-checker")
def prerequisite_checker_page():
    services = Service.query.order_by(Service.service_name).all()
    selected_service_id = request.args.get("service_id", "SVC-VOTER-NEW")
    return render_template(
        "prerequisite_checker.html",
        services=services,
        selected_service_id=selected_service_id,
        active_page="prerequisite_checker",
    )


@frontend_bp.get("/apply")
def apply_page():
    services = Service.query.order_by(Service.service_name).all()
    selected_service_id = request.args.get("service_id", "SVC-VOTER-NEW")
    return render_template(
        "apply.html",
        services=services,
        selected_service_id=selected_service_id,
        active_page="apply",
    )


@frontend_bp.get("/documents")
def documents_page():
    return render_template("documents.html", active_page="documents")


@frontend_bp.get("/applications")
def applications_page():
    return render_template("applications.html", active_page="applications")


@frontend_bp.get("/centers")
def centers_page():
    centers = ServiceCenter.query.order_by(ServiceCenter.center_name).all()
    return render_template("centers.html", centers=centers, active_page="centers")


@frontend_bp.get("/auth")
@frontend_bp.get("/login")
def auth_page():
    return render_template("auth.html", active_page="auth")


@frontend_bp.get("/profile")
def profile_page():
    return render_template("profile.html", active_page="profile")


# ==============================================================================
# Prototype Routes (Rendered from templates/prototype/)
# ==============================================================================
@frontend_bp.get("/prototype")
def prototype_index():
    return render_template("prototype/index.html")


@frontend_bp.get("/prototype/home")
def prototype_home():
    return render_template("prototype/home.html")


@frontend_bp.get("/prototype/profile")
def prototype_profile():
    return render_template("prototype/profile.html")


@frontend_bp.get("/prototype/apply")
def prototype_apply():
    return render_template("prototype/apply.html")
