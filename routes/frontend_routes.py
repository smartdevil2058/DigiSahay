<<<<<<< HEAD
from functools import wraps
from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    make_response,
)
from flask_jwt_extended import (
    verify_jwt_in_request,
    get_jwt_identity,
    unset_jwt_cookies,
)
from jwt.exceptions import ExpiredSignatureError
from extension import db
from model import User, Service, ServiceCenter
=======
from flask import Blueprint, render_template, request
from model import Service, ServiceCenter
>>>>>>> c981506dbd2f314e63b7e90f4ab444ee1eca2d2c

frontend_bp = Blueprint("frontend", __name__)


<<<<<<< HEAD
def get_authenticated_user():
    """
    Checks if current request contains a valid, non-expired JWT.
    Returns (user, status) where status is 'authenticated', 'expired', or 'unauthenticated'.
    """
    try:
        verify_jwt_in_request(optional=True)
        user_id = get_jwt_identity()
        if not user_id:
            return None, "unauthenticated"
        user = db.session.get(User, user_id)
        if not user:
            return None, "unauthenticated"
        return user, "authenticated"
    except ExpiredSignatureError:
        return None, "expired"
    except Exception:
        return None, "unauthenticated"


def citizen_login_required(view_func):
    """
    Protects sensitive citizen views by enforcing server-side authentication.
    Redirects unauthenticated or expired users to /auth with next parameter,
    and sets Cache-Control headers to block browser back-navigation after logout.
    """
    @wraps(view_func)
    def wrapped_view(*args, **kwargs):
        user, status = get_authenticated_user()
        next_target = request.full_path if request.query_string else request.path

        if status == "expired":
            resp = redirect(url_for("frontend.auth_page", expired="1", next=next_target))
            unset_jwt_cookies(resp)
            resp.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
            resp.headers["Pragma"] = "no-cache"
            return resp

        if status != "authenticated":
            resp = redirect(url_for("frontend.auth_page", next=next_target))
            resp.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
            resp.headers["Pragma"] = "no-cache"
            return resp

        response = make_response(view_func(*args, **kwargs))
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        return response

    return wrapped_view


@frontend_bp.get("/")
def index():
    """
    Root entry point:
    - Active valid session -> /dashboard
    - Expired session -> /auth?expired=1
    - Logged out / new visitor -> /auth
    """
    user, status = get_authenticated_user()
    if status == "authenticated":
        return redirect(url_for("frontend.dashboard"))
    if status == "expired":
        resp = redirect(url_for("frontend.auth_page", expired="1"))
        unset_jwt_cookies(resp)
        return resp
    return redirect(url_for("frontend.auth_page"))


@frontend_bp.get("/dashboard")
@citizen_login_required
def dashboard():
    return render_template("index.html", active_page="dashboard")


@frontend_bp.get("/login")
@frontend_bp.get("/auth")
def auth_page():
    user, status = get_authenticated_user()
    if status == "authenticated":
        next_target = request.args.get("next")
        if next_target and next_target.startswith("/"):
            return redirect(next_target)
        return redirect(url_for("frontend.dashboard"))

    return render_template("auth.html", active_page="auth")


@frontend_bp.get("/logout")
def logout():
    """
    Server-side logout:
    Invalidates session cookie, disables caching, and redirects to /auth?logged_out=1.
    """
    resp = redirect(url_for("frontend.auth_page", logged_out="1"))
    unset_jwt_cookies(resp)
    resp.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    resp.headers["Pragma"] = "no-cache"
    return resp


=======
@frontend_bp.get("/")
@frontend_bp.get("/dashboard")
def index():
    return render_template("index.html", active_page="dashboard")


>>>>>>> c981506dbd2f314e63b7e90f4ab444ee1eca2d2c
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
<<<<<<< HEAD
@citizen_login_required
=======
>>>>>>> c981506dbd2f314e63b7e90f4ab444ee1eca2d2c
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
<<<<<<< HEAD
@citizen_login_required
=======
>>>>>>> c981506dbd2f314e63b7e90f4ab444ee1eca2d2c
def documents_page():
    return render_template("documents.html", active_page="documents")


@frontend_bp.get("/applications")
<<<<<<< HEAD
@citizen_login_required
=======
>>>>>>> c981506dbd2f314e63b7e90f4ab444ee1eca2d2c
def applications_page():
    return render_template("applications.html", active_page="applications")


@frontend_bp.get("/centers")
def centers_page():
    centers = ServiceCenter.query.order_by(ServiceCenter.center_name).all()
    return render_template("centers.html", centers=centers, active_page="centers")


<<<<<<< HEAD
@frontend_bp.get("/profile")
@citizen_login_required
=======
@frontend_bp.get("/auth")
@frontend_bp.get("/login")
def auth_page():
    return render_template("auth.html", active_page="auth")


@frontend_bp.get("/profile")
>>>>>>> c981506dbd2f314e63b7e90f4ab444ee1eca2d2c
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
