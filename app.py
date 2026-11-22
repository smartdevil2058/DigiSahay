import os
from dotenv import load_dotenv
from flask import Flask, jsonify,Blueprint, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import URL, text
from extension import db
from routes.service_routes import service_bp
from routes.requirement_routes import requirement_bp
from routes.eligibility_routes import eligibility_bp
from routes.center_routes import center_bp
from routes.application_routes import application_bp
from routes.appointment_routes import appointment_bp
from routes.requirement_evaluation_routes import requirement_evaluation_bp
from flask_jwt_extended import JWTManager
from datetime import timedelta
from routes.auth_routes import auth_bp
from routes.document_routes import document_bp
from routes.application_document_routes import application_document_bp
from routes.application_readiness_routes import application_readiness_bp
from routes.application_status_routes import application_status_bp
from routes.frontend_routes import frontend_bp
from routes.survey_routes import survey_bp

load_dotenv()
app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024
app.config["UPLOAD_FOLDER"] = os.path.join(
    app.root_path, "uploads", "user_documents"
)
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")

app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=30)

jwt = JWTManager(app)
database_url = URL.create(
    drivername= "mysql+pymysql",
    username=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST","localhost"),
    port=int(os.getenv("DB_PORT", "3306")),
    database=os.getenv("DB_NAME","digisahay")
)

app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_size": 2,
    "max_overflow": 1,
    "pool_recycle": 280,
    "pool_pre_ping": True,
}
db.init_app(app)
import model

app.register_blueprint(service_bp)
app.register_blueprint(requirement_bp)
app.register_blueprint(eligibility_bp)
app.register_blueprint(center_bp)
app.register_blueprint(application_bp)
app.register_blueprint(appointment_bp)
app.register_blueprint(requirement_evaluation_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(document_bp)
app.register_blueprint(application_document_bp)
app.register_blueprint(application_readiness_bp)
app.register_blueprint(application_status_bp)
app.register_blueprint(frontend_bp)
app.register_blueprint(survey_bp)
@app.get("/api")
def api_status():
    return jsonify({
        "project" : "Digisahay",
        "message": "Backend is running"
    })
@app.get("/health/jwt")
def jwt_health():
    return jsonify({
        "jwt_configured": bool(
            app.config.get("JWT_SECRET_KEY")
        ),
        "jwt_manager_initialized": jwt is not None
    })
@app.get("/health/db")
def health():
    try:
        db.session.execute(text("SELECT 1"))
        return jsonify({
            "database" : "connected",
            "status" : "healthy"
        })
    except:
        app.logger.exception("Database connection failed")
        return jsonify({
                    "database" : "disconnected",
                    "status" : "error"
                }),500

@app.get("/health/model")
def model_health():
    return jsonify({
        "Registered table" : sorted(db.metadata.tables.keys()),
        "total tables" : len(db.metadata.tables)
    })

@app.get("/health/schema")
def schema_health():
    try:
        with app.app_context():
            db.metadata.sorted_tables
        return jsonify({
            "Schema" : "Valid",
            "Status" : "Success"
        })
    except Exception:
        app.logger.exception("Schema validation failed")
        return jsonify({
            "Schema" : "In Valid",
            "Status" : "error"
        })

@app.get("/setup/table_creation")
def create_table():
    try:
        with app.app_context():
            db.create_all()

        return jsonify({
            "MSG" : "All the table are created succesfully",
            "total_tables" : len(db.metadata.tables)
        })
    except Exception:
        app.logger.exception("Table creation failed")
        return jsonify({
            "MSG" : "Table creation Failed due to unexpected error",
            "Status" : "Error"
        })


if __name__ == "__main__":
    app.run(debug=True)