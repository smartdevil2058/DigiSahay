<<<<<<< HEAD

import os
from uuid import uuid4

from flask import Blueprint, request, jsonify, current_app, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
from extension import db
from model import UserDocument, DocumentType, User


document_bp = Blueprint(
    "documents",
    __name__,
    url_prefix="/api/documents"
)

ALLOWED_EXTENSIONS = {"pdf", "jpg", "jpeg", "png"}


def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


@document_bp.post("/upload")
@jwt_required(optional=True)
def upload_document():

    if "file" not in request.files:
        return jsonify({
            "success": False,
            "message": "No file provided"
        }), 400

    file = request.files["file"]

    if not file.filename:
        return jsonify({
            "success": False,
            "message": "No file selected"
        }), 400

    if not allowed_file(file.filename):
        return jsonify({
            "success": False,
            "message": "Only PDF, JPG, JPEG and PNG files are allowed"
        }), 400

    document_type_id = request.form.get("document_type_id")
    document_name = request.form.get("document_name") or file.filename

    document_type = None
    if document_type_id:
        document_type = db.session.get(DocumentType, document_type_id)

    if not document_type or not document_type.is_active:
        # Fallback to general proof type if specified type is not in DB
        document_type = DocumentType.query.filter_by(is_active=True).first()
        if document_type:
            document_type_id = document_type.document_type_id
        else:
            document_type_id = "DOC-OTHER"

    original_filename = secure_filename(file.filename)
    if not original_filename:
        original_filename = "document_upload"

    extension = original_filename.rsplit(".", 1)[1].lower() if "." in original_filename else "pdf"
    stored_filename = f"{uuid4().hex}.{extension}"

    upload_folder = current_app.config["UPLOAD_FOLDER"]
    os.makedirs(upload_folder, exist_ok=True)

    absolute_path = os.path.join(
        upload_folder, stored_filename
    )

    relative_path = os.path.join(
        "uploads", "user_documents", stored_filename
    ).replace("\\", "/")

    user_id = get_jwt_identity()
    if not user_id:
        email = (request.form.get("email") or request.form.get("applicant_email") or "").strip().lower()
        if email and "@" in email:
            u = User.query.filter_by(email=email).first()
            if not u:
                u = User(
                    user_id=f"USR-{uuid4().hex[:12].upper()}",
                    email=email,
                    password_hash=generate_password_hash("DigiSahay@2026"),
                    preferred_language="gu"
                )
                db.session.add(u)
                db.session.flush()
            user_id = u.user_id
        else:
            first_user = User.query.first()
            if first_user:
                user_id = first_user.user_id
            else:
                u = User(
                    user_id=f"USR-{uuid4().hex[:12].upper()}",
                    email="citizen.guest@digisahay.in",
                    password_hash=generate_password_hash("DigiSahay@2026"),
                    preferred_language="gu"
                )
                db.session.add(u)
                db.session.flush()
                user_id = u.user_id

    try:
        file.save(absolute_path)

        new_document = UserDocument(
            document_id=f"DOC-{uuid4().hex[:12].upper()}",
            user_id=user_id,
            document_type_id=document_type_id,
            document_name=document_name.strip(),
            original_filename=original_filename,
            stored_filename=stored_filename,
            storage_path=relative_path,
            file_type=extension,
            file_size=os.path.getsize(absolute_path)
        )

        db.session.add(new_document)
        db.session.commit()

    except Exception:
        db.session.rollback()

        if os.path.exists(absolute_path):
            os.remove(absolute_path)

        return jsonify({
            "success": False,
            "message": "Document upload failed"
        }), 500

    return jsonify({
        "success": True,
        "message": "Document uploaded successfully",
        "document": {
            "document_id": new_document.document_id,
            "document_name": new_document.document_name,
            "document_type_id": new_document.document_type_id,
            "file_type": new_document.file_type,
            "file_size": new_document.file_size,
            "created_at": new_document.created_at.isoformat()
        }
    }), 201



@document_bp.get("/")
@jwt_required()
def get_my_documents():

    user_id = get_jwt_identity()

    documents = (
        UserDocument.query
        .filter_by(user_id=user_id, is_active=True)
        .order_by(UserDocument.created_at.desc())
        .all()
    )

    document_list = []

    for doc in documents:
        document_list.append({
            "document_id": doc.document_id,
            "document_name": doc.document_name,
            "document_type_id": doc.document_type_id,
            "original_filename": doc.original_filename,
            "file_type": doc.file_type,
            "file_size": doc.file_size,
            "created_at": doc.created_at.isoformat()
        })

    return jsonify({
        "success": True,
        "total_documents": len(document_list),
        "documents": document_list
    }), 200


@document_bp.get("/<document_id>/download")
@jwt_required()
def download_document(document_id):

    user_id = get_jwt_identity()

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

    upload_folder = current_app.config["UPLOAD_FOLDER"]

    file_path = os.path.join(
        upload_folder,
        document.stored_filename
    )

    if not os.path.isfile(file_path):
        return jsonify({
            "success": False,
            "message": "Document file not found in storage"
        }), 404

    return send_file(
        file_path,
        as_attachment=True,
        download_name=document.original_filename
    )



@document_bp.delete("/<document_id>")
@jwt_required()
def delete_document(document_id):

    user_id = get_jwt_identity()

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

    upload_folder = current_app.config["UPLOAD_FOLDER"]

    file_path = os.path.join(
        upload_folder,
        document.stored_filename
    )

    try:
        document.is_active = False
        db.session.commit()

        if os.path.isfile(file_path):
            os.remove(file_path)

        return jsonify({
            "success": True,
            "message": "Document deleted successfully",
            "document_id": document_id
        }), 200

    except OSError:
        return jsonify({
            "success": False,
            "message": "Database updated, but file deletion failed"
        }), 500

    except Exception:
        db.session.rollback()

        return jsonify({
            "success": False,
            "message": "Document deletion failed"
        }), 500


@document_bp.put("/<document_id>/replace")
@jwt_required()
def replace_document(document_id):

    user_id = get_jwt_identity()

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

    if "file" not in request.files:
        return jsonify({
            "success": False,
            "message": "No replacement file provided"
        }), 400

    file = request.files["file"]

    if not file.filename:
        return jsonify({
            "success": False,
            "message": "No file selected"
        }), 400

    if not allowed_file(file.filename):
        return jsonify({
            "success": False,
            "message": "Only PDF, JPG, JPEG and PNG files are allowed"
        }), 400

    original_filename = secure_filename(file.filename)

    if not original_filename:
        return jsonify({
            "success": False,
            "message": "Invalid filename"
        }), 400

    extension = original_filename.rsplit(".", 1)[1].lower()

    stored_filename = f"{uuid4().hex}.{extension}"

    upload_folder = current_app.config["UPLOAD_FOLDER"]
    os.makedirs(upload_folder, exist_ok=True)

    new_file_path = os.path.join(
        upload_folder, stored_filename
    )

    old_file_path = os.path.join(
        upload_folder, document.stored_filename
    )

    try:
        file.save(new_file_path)

        old_stored_filename = document.stored_filename

        document.original_filename = original_filename
        document.stored_filename = stored_filename
        document.storage_path = os.path.join(
            "uploads", "user_documents", stored_filename
        ).replace("\\", "/")
        document.file_type = extension
        document.file_size = os.path.getsize(new_file_path)
        document.updated_at = datetime.utcnow()

        db.session.commit()

    except Exception:
        db.session.rollback()

        if os.path.exists(new_file_path):
            os.remove(new_file_path)

        return jsonify({
            "success": False,
            "message": "Document replacement failed"
        }), 500

    if os.path.isfile(old_file_path):
        try:
            os.remove(old_file_path)
        except OSError:
            current_app.logger.exception(
                "Old document file could not be removed"
            )

    return jsonify({
        "success": True,
        "message": "Document replaced successfully",
        "document": {
            "document_id": document.document_id,
            "document_name": document.document_name,
            "original_filename": document.original_filename,
            "file_type": document.file_type,
            "file_size": document.file_size,
            "updated_at": document.updated_at.isoformat()
        }
    }), 200

=======

import os
from uuid import uuid4

from flask import Blueprint, request, jsonify, current_app, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
from extension import db
from model import UserDocument, DocumentType, User


document_bp = Blueprint(
    "documents",
    __name__,
    url_prefix="/api/documents"
)

ALLOWED_EXTENSIONS = {"pdf", "jpg", "jpeg", "png"}


def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


@document_bp.post("/upload")
@jwt_required(optional=True)
def upload_document():

    if "file" not in request.files:
        return jsonify({
            "success": False,
            "message": "No file provided"
        }), 400

    file = request.files["file"]

    if not file.filename:
        return jsonify({
            "success": False,
            "message": "No file selected"
        }), 400

    if not allowed_file(file.filename):
        return jsonify({
            "success": False,
            "message": "Only PDF, JPG, JPEG and PNG files are allowed"
        }), 400

    document_type_id = request.form.get("document_type_id")
    document_name = request.form.get("document_name") or file.filename

    document_type = None
    if document_type_id:
        document_type = db.session.get(DocumentType, document_type_id)

    if not document_type or not document_type.is_active:
        # Fallback to general proof type if specified type is not in DB
        document_type = DocumentType.query.filter_by(is_active=True).first()
        if document_type:
            document_type_id = document_type.document_type_id
        else:
            document_type_id = "DOC-OTHER"

    original_filename = secure_filename(file.filename)
    if not original_filename:
        original_filename = "document_upload"

    extension = original_filename.rsplit(".", 1)[1].lower() if "." in original_filename else "pdf"
    stored_filename = f"{uuid4().hex}.{extension}"

    upload_folder = current_app.config["UPLOAD_FOLDER"]
    os.makedirs(upload_folder, exist_ok=True)

    absolute_path = os.path.join(
        upload_folder, stored_filename
    )

    relative_path = os.path.join(
        "uploads", "user_documents", stored_filename
    ).replace("\\", "/")

    user_id = get_jwt_identity()
    if not user_id:
        email = (request.form.get("email") or request.form.get("applicant_email") or "").strip().lower()
        if email and "@" in email:
            u = User.query.filter_by(email=email).first()
            if not u:
                u = User(
                    user_id=f"USR-{uuid4().hex[:12].upper()}",
                    email=email,
                    password_hash=generate_password_hash("DigiSahay@2026"),
                    preferred_language="gu"
                )
                db.session.add(u)
                db.session.flush()
            user_id = u.user_id
        else:
            first_user = User.query.first()
            if first_user:
                user_id = first_user.user_id
            else:
                u = User(
                    user_id=f"USR-{uuid4().hex[:12].upper()}",
                    email="citizen.guest@digisahay.in",
                    password_hash=generate_password_hash("DigiSahay@2026"),
                    preferred_language="gu"
                )
                db.session.add(u)
                db.session.flush()
                user_id = u.user_id

    try:
        file.save(absolute_path)

        new_document = UserDocument(
            document_id=f"DOC-{uuid4().hex[:12].upper()}",
            user_id=user_id,
            document_type_id=document_type_id,
            document_name=document_name.strip(),
            original_filename=original_filename,
            stored_filename=stored_filename,
            storage_path=relative_path,
            file_type=extension,
            file_size=os.path.getsize(absolute_path)
        )

        db.session.add(new_document)
        db.session.commit()

    except Exception:
        db.session.rollback()

        if os.path.exists(absolute_path):
            os.remove(absolute_path)

        return jsonify({
            "success": False,
            "message": "Document upload failed"
        }), 500

    return jsonify({
        "success": True,
        "message": "Document uploaded successfully",
        "document": {
            "document_id": new_document.document_id,
            "document_name": new_document.document_name,
            "document_type_id": new_document.document_type_id,
            "file_type": new_document.file_type,
            "file_size": new_document.file_size,
            "created_at": new_document.created_at.isoformat()
        }
    }), 201



@document_bp.get("/")
@jwt_required()
def get_my_documents():

    user_id = get_jwt_identity()

    documents = (
        UserDocument.query
        .filter_by(user_id=user_id, is_active=True)
        .order_by(UserDocument.created_at.desc())
        .all()
    )

    document_list = []

    for doc in documents:
        document_list.append({
            "document_id": doc.document_id,
            "document_name": doc.document_name,
            "document_type_id": doc.document_type_id,
            "original_filename": doc.original_filename,
            "file_type": doc.file_type,
            "file_size": doc.file_size,
            "created_at": doc.created_at.isoformat()
        })

    return jsonify({
        "success": True,
        "total_documents": len(document_list),
        "documents": document_list
    }), 200


@document_bp.get("/<document_id>/download")
@jwt_required()
def download_document(document_id):

    user_id = get_jwt_identity()

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

    upload_folder = current_app.config["UPLOAD_FOLDER"]

    file_path = os.path.join(
        upload_folder,
        document.stored_filename
    )

    if not os.path.isfile(file_path):
        return jsonify({
            "success": False,
            "message": "Document file not found in storage"
        }), 404

    return send_file(
        file_path,
        as_attachment=True,
        download_name=document.original_filename
    )



@document_bp.delete("/<document_id>")
@jwt_required()
def delete_document(document_id):

    user_id = get_jwt_identity()

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

    upload_folder = current_app.config["UPLOAD_FOLDER"]

    file_path = os.path.join(
        upload_folder,
        document.stored_filename
    )

    try:
        document.is_active = False
        db.session.commit()

        if os.path.isfile(file_path):
            os.remove(file_path)

        return jsonify({
            "success": True,
            "message": "Document deleted successfully",
            "document_id": document_id
        }), 200

    except OSError:
        return jsonify({
            "success": False,
            "message": "Database updated, but file deletion failed"
        }), 500

    except Exception:
        db.session.rollback()

        return jsonify({
            "success": False,
            "message": "Document deletion failed"
        }), 500


@document_bp.put("/<document_id>/replace")
@jwt_required()
def replace_document(document_id):

    user_id = get_jwt_identity()

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

    if "file" not in request.files:
        return jsonify({
            "success": False,
            "message": "No replacement file provided"
        }), 400

    file = request.files["file"]

    if not file.filename:
        return jsonify({
            "success": False,
            "message": "No file selected"
        }), 400

    if not allowed_file(file.filename):
        return jsonify({
            "success": False,
            "message": "Only PDF, JPG, JPEG and PNG files are allowed"
        }), 400

    original_filename = secure_filename(file.filename)

    if not original_filename:
        return jsonify({
            "success": False,
            "message": "Invalid filename"
        }), 400

    extension = original_filename.rsplit(".", 1)[1].lower()

    stored_filename = f"{uuid4().hex}.{extension}"

    upload_folder = current_app.config["UPLOAD_FOLDER"]
    os.makedirs(upload_folder, exist_ok=True)

    new_file_path = os.path.join(
        upload_folder, stored_filename
    )

    old_file_path = os.path.join(
        upload_folder, document.stored_filename
    )

    try:
        file.save(new_file_path)

        old_stored_filename = document.stored_filename

        document.original_filename = original_filename
        document.stored_filename = stored_filename
        document.storage_path = os.path.join(
            "uploads", "user_documents", stored_filename
        ).replace("\\", "/")
        document.file_type = extension
        document.file_size = os.path.getsize(new_file_path)
        document.updated_at = datetime.utcnow()

        db.session.commit()

    except Exception:
        db.session.rollback()

        if os.path.exists(new_file_path):
            os.remove(new_file_path)

        return jsonify({
            "success": False,
            "message": "Document replacement failed"
        }), 500

    if os.path.isfile(old_file_path):
        try:
            os.remove(old_file_path)
        except OSError:
            current_app.logger.exception(
                "Old document file could not be removed"
            )

    return jsonify({
        "success": True,
        "message": "Document replaced successfully",
        "document": {
            "document_id": document.document_id,
            "document_name": document.document_name,
            "original_filename": document.original_filename,
            "file_type": document.file_type,
            "file_size": document.file_size,
            "updated_at": document.updated_at.isoformat()
        }
    }), 200

>>>>>>> c981506dbd2f314e63b7e90f4ab444ee1eca2d2c
