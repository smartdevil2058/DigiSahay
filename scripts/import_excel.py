import sys
import pandas as pd 
from pathlib import Path
import secrets
from werkzeug.security import generate_password_hash


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT))
FILE_PATH = ROOT / "data" / "DigiSahay_rulebook (1).xlsx"
from app import app
from extension import db
from model import Service, Source,DocumentType,ServiceCenter, EligibilityRule,RequirementGroup,SubmissionRoute,Requirement,ServiceRoute,CenterService,RequirementSource,User,Application,Appointment
def clean_value(value):
    if pd.isna(value):
        return None
    return value
def to_bool(value):
    value = clean_value(value)
    if value is None or isinstance(value, bool):
        return value
    s = str(value).strip().upper()
    if s in ("TRUE", "YES", "1"):
        return True
    return False 
def import_services():
    df = pd.read_excel(
        FILE_PATH,
        sheet_name="Services"
    )
    df = df.replace(r"^\s*$", pd.NA, regex=True)
    df = df.dropna(how="all").copy()
    df.columns = df.columns.astype(str).str.strip()

    imported = 0
    with app.app_context():
        try:

            for _, row in df.iterrows():
                service_id = clean_value(row["service_id"])

                if not service_id:
                    raise ValueError("A service record has no service ID")
                existing = db.session.get(Service,service_id)
                if existing:
                    print(f"skipping existing service :{service_id}")
                    continue
                service = Service(
                    service_id=service_id,
                    service_name=clean_value(row["service_name"]),
                    service_category=clean_value(row["service_category"]),
                    application_or_update_type=clean_value(
                        row["application_or_update_type"]
                    ),
                    form_name_or_number=clean_value(
                        row["form_name_or_number"]
                    ),
                    description=clean_value(row["description"]),
                    responsible_authority=clean_value(
                        row["responsible_authority"]
                    ),
                    official_service_url=clean_value(
                        row["official_service_url"]
                    ),
                    is_active=clean_value(row["is_active"]),
                    verification_status=clean_value(
                        row["verification_status"]
                    )
                )
                db.session.add(service)
                imported+=1

                db.session.commit()
                print(f"Service is imported sucessfully {imported}")

                total = db.session.query(Service).count()
                print(f"total services currently in database:{total}")
        except Exception:
            db.session.rollback()
            raise
def import_sources():
    df = pd.read_excel(
        FILE_PATH,
        sheet_name="Sources"
    )

    df = df.replace(r"^\s*$", pd.NA, regex=True)
    df = df.dropna(how="all").copy()
    df.columns = df.columns.astype(str).str.strip()

    imported = 0

    with app.app_context():
        try:
            for _, row in df.iterrows():

                source_id = clean_value(row["source_id"])

                if not source_id:
                    raise ValueError("A source record has no source_id")

                existing = db.session.get(Source, source_id)

                if existing:
                    print(f"Skipping existing source: {source_id}")
                    continue

                source = Source(
                    source_id=source_id,
                    source_name=clean_value(row["source_name"]),
                    responsible_authority=clean_value(row["responsible_authority"]),
                    source_url=clean_value(row["source_url"]),
                    source_type=clean_value(row["source_type"]),
                    relevant_section_or_page=clean_value(row["relevant_section_or_page"]),
                    date_checked=clean_value(row["date_checked"]),
                    last_verified_at=clean_value(row["last_verified_at"]),
                    verification_status=clean_value(row["verification_status"]),
                    notes=clean_value(row["notes"])
                )

                db.session.add(source)
                imported += 1

            db.session.commit()

            total = db.session.query(Source).count()

            print(f"\nSources imported successfully: {imported}")
            print(f"Total sources currently in database: {total}")

        except Exception:
            db.session.rollback()
            raise

def import_document_types():
    df = pd.read_excel(
        FILE_PATH,
        sheet_name="Document Types"
    )

    df = df.replace(r"^\s*$", pd.NA, regex=True)
    df = df.dropna(how="all").copy()
    df.columns = df.columns.astype(str).str.strip()

    imported = 0

    with app.app_context():
        try:
            for _, row in df.iterrows():

                document_type_id = clean_value(row["document_type_id"])

                if not document_type_id:
                    raise ValueError(
                        "A document type record has no document_type_id"
                    )

                existing = db.session.get(
                    DocumentType,
                    document_type_id
                )

                if existing:
                    print(f"Skipping existing document type: {document_type_id}")
                    continue

                document = DocumentType(
                    document_type_id=document_type_id,
                    document_name=clean_value(row["document_name"]),
                    document_category=clean_value(row["document_category"]),
                    description=clean_value(row["description"]),
                    original_or_copy_requirement=clean_value(
                        row["original_or_copy_requirement"]
                    ),
                    format_or_size_constraints=clean_value(
                        row["format_or_size_constraints"]
                    ),
                    special_conditions=clean_value(row["special_conditions"]),
                    is_active=clean_value(row["is_active"]),
                    verification_status=clean_value(
                        row["verification_status"]
                    )
                )

                db.session.add(document)
                imported += 1

            db.session.commit()

            total = db.session.query(DocumentType).count()

            print(f"\nDocument Types imported successfully: {imported}")
            print(f"Total Document Types currently in database: {total}")

        except Exception:
            db.session.rollback()
            raise

def import_service_centers():
    df = pd.read_excel(
        FILE_PATH,
        sheet_name="Service Centers"
    )

    df = df.replace(r"^\s*$", pd.NA, regex=True)
    df = df.dropna(how="all").copy()
    df.columns = df.columns.astype(str).str.strip()

    imported = 0

    with app.app_context():
        try:
            for _, row in df.iterrows():

                center_id = clean_value(row["center_id"])

                if not center_id:
                    raise ValueError("A service center has no center_id")

                existing = db.session.get(ServiceCenter, center_id)

                if existing:
                    print(f"Skipping existing center: {center_id}")
                    continue

                center = ServiceCenter(
                    center_id=center_id,
                    center_name=clean_value(row["center_name"]),
                    center_type=clean_value(row["center_type"]),
                    authority_name=clean_value(row["authority_name"]),
                    address_line=clean_value(row["address_line"]),
                    city=clean_value(row["city"]),
                    district=clean_value(row["district"]),
                    state=clean_value(row["state"]),
                    pincode=clean_value(row["pincode"]),
                    latitude=clean_value(row["latitude"]),
                    longitude=clean_value(row["longitude"]),
                    contact_number=clean_value(row["contact_number"]),
                    operating_hours=clean_value(row["operating_hours"]),
                    official_source_url=clean_value(row["official_source_url"]),
                    data_last_verified=clean_value(row["data_last_verified"]),
                    verification_status=clean_value(row["verification_status"]),
                    notes=clean_value(row["notes"])
                )

                db.session.add(center)
                imported += 1

            db.session.commit()

            total = db.session.query(ServiceCenter).count()

            print(f"\nService Centers imported successfully: {imported}")
            print(f"Total Service Centers currently in database: {total}")

        except Exception:
            db.session.rollback()
            raise


def import_eligibility_rules():
    df = pd.read_excel(
        FILE_PATH,
        sheet_name="Eligibility Rules"
    )

    df = df.replace(r"^\s*$", pd.NA, regex=True)
    df = df.dropna(how="all").copy()
    df.columns = df.columns.astype(str).str.strip()

    imported = 0

    with app.app_context():
        try:
            for _, row in df.iterrows():

                rule_id = clean_value(row["rule_id"])

                if not rule_id:
                    raise ValueError("An eligibility rule has no rule_id")

                existing = db.session.get(EligibilityRule, rule_id)

                if existing:
                    print(f"Skipping existing rule: {rule_id}")
                    continue

                rule = EligibilityRule(
                    rule_id=rule_id,
                    service_id=clean_value(row["service_id"]),
                    rule_code=clean_value(row["rule_code"]),
                    question_text=clean_value(row["question_text"]),
                    condition_type=clean_value(row["condition_type"]),
                    condition_config=clean_value(row["condition_config"]),
                    outcome_if_true=clean_value(row["outcome_if_true"]),
                    outcome_if_false=clean_value(row["outcome_if_false"]),
                    source_id=clean_value(row["source_id"]),
                    verification_status=clean_value(
                        row["verification_status"]
                    )
                )

                db.session.add(rule)
                imported += 1

            db.session.commit()

            total = db.session.query(EligibilityRule).count()

            print(f"\nEligibility Rules imported successfully: {imported}")
            print(f"Total Eligibility Rules currently in database: {total}")

        except Exception:
            db.session.rollback()
            raise

def import_requirement_groups():
    df = pd.read_excel(
        FILE_PATH,
        sheet_name="Requirement Groups"
    )

    df = df.replace(r"^\s*$", pd.NA, regex=True)
    df = df.dropna(how="all").copy()
    df.columns = df.columns.astype(str).str.strip()

    imported = 0

    with app.app_context():
        try:
            for _, row in df.iterrows():

                group_id = clean_value(row["group_id"])

                if not group_id:
                    raise ValueError("A requirement group has no group_id")

                existing = db.session.get(RequirementGroup, group_id)

                if existing:
                    print(f"Skipping existing group: {group_id}")
                    continue

                group = RequirementGroup(
                    group_id=group_id,
                    service_id=clean_value(row["service_id"]),
                    group_name=clean_value(row["group_name"]),
                    description=clean_value(row["description"]),
                    selection_mode=clean_value(row["selection_mode"]),
                    min_selections=clean_value(row["min_selections"]),
                    max_selections=clean_value(row["max_selections"]),
                    condition_rule_id=clean_value(row["condition_rule_id"]),
                    verification_status=clean_value(
                        row["verification_status"]
                    )
                )

                db.session.add(group)
                imported += 1

            db.session.commit()

            total = db.session.query(RequirementGroup).count()

            print(f"\nRequirement Groups imported successfully: {imported}")
            print(f"Total Requirement Groups currently in database: {total}")

        except Exception:
            db.session.rollback()
            raise


def import_submission_routes():
    df = pd.read_excel(
        FILE_PATH,
        sheet_name="Submission Routes"
    )

    df = df.replace(r"^\s*$", pd.NA, regex=True)
    df = df.dropna(how="all").copy()
    df.columns = df.columns.astype(str).str.strip()

    imported = 0

    with app.app_context():
        try:
            for _, row in df.iterrows():

                route_id = clean_value(row["route_id"])

                if not route_id:
                    raise ValueError("A submission route has no route_id")

                existing = db.session.get(SubmissionRoute, route_id)

                if existing:
                    print(f"Skipping existing route: {route_id}")
                    continue

                route = SubmissionRoute(
                    route_id=route_id,
                    service_id=clean_value(row["service_id"]),
                    route_type=clean_value(row["route_type"]),
                    route_name=clean_value(row["route_name"]),
                    official_url=clean_value(row["official_url"]),
                    instructions=clean_value(row["instructions"]),
                    appointment_required=to_bool(row["appointment_required"]),
                    physical_visit_required=to_bool(row["physical_visit_required"]),
                    available_geographic_scope=clean_value(
                        row["available_geographic_scope"]
                    ),
                    verification_status=clean_value(
                        row["verification_status"]
                    ),
                    source_id=clean_value(row["source_id"])
                )

                db.session.add(route)
                imported += 1

            db.session.commit()

            total = db.session.query(SubmissionRoute).count()

            print(f"\nSubmission Routes imported successfully: {imported}")
            print(f"Total Submission Routes currently in database: {total}")

        except Exception:
            db.session.rollback()
            raise

def import_requirements():
    df = pd.read_excel(
        FILE_PATH,
        sheet_name="Requirements"
    )

    df = df.replace(r"^\s*$", pd.NA, regex=True)
    df = df.dropna(how="all").copy()
    df.columns = df.columns.astype(str).str.strip()

    imported = 0

    with app.app_context():
        try:
            for _, row in df.iterrows():

                option_id = clean_value(row["option_id"])

                if not option_id:
                    raise ValueError("A requirement has no option_id")

                existing = db.session.get(Requirement, option_id)

                if existing:
                    print(f"Skipping existing requirement: {option_id}")
                    continue

                requirement = Requirement(
                    option_id=option_id,
                    group_id=clean_value(row["group_id"]),
                    document_type_id=clean_value(row["document_type_id"]),
                    condition_rule_id=clean_value(row["condition_rule_id"]),
                    applicable_context=clean_value(row["applicable_context"]),
                    official_acceptance_conditions=clean_value(
                        row["official_acceptance_conditions"]
                    ),
                    verification_status=clean_value(
                        row["verification_status"]
                    ),
                    source_id=clean_value(row["source_id"])
                )

                db.session.add(requirement)
                imported += 1

            db.session.commit()

            total = db.session.query(Requirement).count()

            print(f"\nRequirements imported successfully: {imported}")
            print(f"Total Requirements currently in database: {total}")

        except Exception:
            db.session.rollback()
            raise

def import_service_routes():
    df = pd.read_excel(
        FILE_PATH,
        sheet_name="Service Routes"
    )

    df = df.replace(r"^\s*$", pd.NA, regex=True)
    df = df.dropna(how="all").copy()
    df.columns = df.columns.astype(str).str.strip()

    imported = 0

    with app.app_context():
        try:
            for _, row in df.iterrows():

                route_id = clean_value(row["route_id"])

                if not route_id:
                    raise ValueError("A service route has no route_id")

                existing = db.session.get(ServiceRoute, route_id)

                if existing:
                    print(f"Skipping existing service route: {route_id}")
                    continue

                route = ServiceRoute(
                    route_id=route_id,
                    service_id=clean_value(row["service_id"]),
                    route_name=clean_value(row["route_name"]),
                    route_type=clean_value(row["route_type"]),
                    authority_name=clean_value(row["authority_name"]),
                    official_service_url=clean_value(row["official_service_url"]),
                    official_booking_url=clean_value(row["official_booking_url"]),
                    application_method=clean_value(row["application_method"]),
                    appointment_required=clean_value(row["appointment_required"]),
                    physical_visit_required=clean_value(row["physical_visit_required"]),
                    available_geographic_scope=clean_value(
                        row["available_geographic_scope"]
                    ),
                    integration_status=clean_value(row["integration_status"]),
                    instructions=clean_value(row["instructions"]),
                    source_id=clean_value(row["source_id"]),
                    verification_status=clean_value(row["verification_status"]),
                    last_verified_at=clean_value(row["last_verified_at"]),
                    notes=clean_value(row["notes"])
                )

                db.session.add(route)
                imported += 1

            db.session.commit()

            total = db.session.query(ServiceRoute).count()

            print(f"\nService Routes imported successfully: {imported}")
            print(f"Total Service Routes currently in database: {total}")

        except Exception:
            db.session.rollback()
            raise

def import_center_services():
    df = pd.read_excel(
        FILE_PATH,
        sheet_name="Center Services"
    )

    df = df.replace(r"^\s*$", pd.NA, regex=True)
    df = df.dropna(how="all").copy()
    df.columns = df.columns.astype(str).str.strip()

    imported = 0

    with app.app_context():
        try:
            for _, row in df.iterrows():

                center_service_id = clean_value(
                    row["center_service_id"]
                )

                if not center_service_id:
                    raise ValueError(
                        "A center service record has no center_service_id"
                    )

                existing = db.session.get(
                    CenterService,
                    center_service_id
                )

                if existing:
                    print(
                        f"Skipping existing center service: {center_service_id}"
                    )
                    continue

                center_service = CenterService(
                    center_service_id=center_service_id,
                    center_id=clean_value(row["center_id"]),
                    service_id=clean_value(row["service_id"]),
                    service_available=clean_value(row["service_available"]),
                    appointment_supported=clean_value(
                        row["appointment_supported"]
                    ),
                    booking_method=clean_value(row["booking_method"]),
                    official_booking_url=clean_value(
                        row["official_booking_url"]
                    ),
                    availability_source=clean_value(
                        row["availability_source"]
                    ),
                    verification_status=clean_value(
                        row["verification_status"]
                    ),
                    last_verified_at=clean_value(row["last_verified_at"]),
                    notes=clean_value(row["notes"])
                )

                db.session.add(center_service)
                imported += 1

            db.session.commit()

            total = db.session.query(CenterService).count()

            print(f"\nCenter Services imported successfully: {imported}")
            print(f"Total Center Services currently in database: {total}")

        except Exception:
            db.session.rollback()
            raise

def import_requirement_sources():
    df = pd.read_excel(
        FILE_PATH,
        sheet_name="Requirement Sources"
    )

    df = df.replace(r"^\s*$", pd.NA, regex=True)
    df = df.dropna(how="all").copy()
    df.columns = df.columns.astype(str).str.strip()

    imported = 0

    with app.app_context():
        try:
            for _, row in df.iterrows():

                link_id = clean_value(row["link_id"])

                if not link_id:
                    raise ValueError(
                        "A requirement source record has no link_id"
                    )

                existing = db.session.get(RequirementSource, link_id)

                if existing:
                    print(f"Skipping existing link: {link_id}")
                    continue

                requirement_source = RequirementSource(
                    link_id=link_id,
                    source_id=clean_value(row["source_id"]),
                    record_type=clean_value(row["record_type"]),
                    record_id=clean_value(row["record_id"]),
                    evidence_note=clean_value(row["evidence_note"])
                )

                db.session.add(requirement_source)
                imported += 1

            db.session.commit()

            total = db.session.query(RequirementSource).count()

            print(f"\nRequirement Sources imported successfully: {imported}")
            print(f"Total Requirement Sources currently in database: {total}")

        except Exception:
            db.session.rollback()
            raise

def import_demo_users():
    sheets = ["Applications", "Appointments"]
    user_ids = set()

    for sheet in sheets:
        df = pd.read_excel(FILE_PATH, sheet_name=sheet)
        df = df.replace(r"^\s*$", pd.NA, regex=True)
        df = df.dropna(how="all")

        for value in df["user_id"].dropna():
            user_id = str(value).strip()
            if user_id:
                user_ids.add(user_id)

    imported = 0

    with app.app_context():
        try:
            for user_id in sorted(user_ids):

                existing = db.session.get(User, user_id)

                if existing:
                    print(f"Skipping existing user: {user_id}")
                    continue

                user = User(
                    user_id=user_id,
                    email=f"{user_id.lower()}@demo.digisahay.invalid",
                    password_hash=generate_password_hash(
                        secrets.token_urlsafe(32)
                    ),
                    preferred_language="en"
                )

                db.session.add(user)
                imported += 1

            db.session.commit()

            total = db.session.query(User).count()

            print(f"\nDemo users imported: {imported}")
            print(f"Total users in database: {total}")

        except Exception:
            db.session.rollback()
            raise

def import_applications():
    df = pd.read_excel(FILE_PATH, sheet_name="Applications")
    df = df.replace(r"^\s*$", pd.NA, regex=True)
    df = df.dropna(how="all").copy()
    df.columns = df.columns.astype(str).str.strip()

    imported = 0

    with app.app_context():
        try:
            for _, row in df.iterrows():

                application_id = clean_value(row["application_id"])

                if not application_id:
                    raise ValueError("Application record has no application_id")

                existing = db.session.get(Application, application_id)

                if existing:
                    print(f"Skipping existing application: {application_id}")
                    continue

                application = Application(
                    application_id=application_id,
                    user_id=str(row["user_id"]).strip(),
                    service_id=clean_value(row["service_id"]),
                    application_reference=clean_value(row["application_reference"]),
                    application_mode=clean_value(row["application_mode"]),
                    application_status=clean_value(row["application_status"]),
                    submitted_at=clean_value(row["submitted_at"]),
                    last_status_updated_at=clean_value(row["last_status_updated_at"]),
                    official_status_source=clean_value(row["official_status_source"]),
                    related_appointment_id=clean_value(row["related_appointment_id"]),
                    notes=clean_value(row["notes"])
                )

                db.session.add(application)
                imported += 1

            db.session.commit()

            print(f"\nApplications imported successfully: {imported}")
            print(
                "Total applications currently in database:",
                db.session.query(Application).count()
            )

        except Exception:
            db.session.rollback()
            raise

def import_appointments():
    df = pd.read_excel(FILE_PATH, sheet_name="Appointments")
    df = df.replace(r"^\s*$", pd.NA, regex=True)
    df = df.dropna(how="all").copy()
    df.columns = df.columns.astype(str).str.strip()

    imported = 0

    with app.app_context():
        try:
            for _, row in df.iterrows():

                appointment_id = clean_value(row["appointment_id"])

                if not appointment_id:
                    raise ValueError("Appointment record has no appointment_id")

                existing = db.session.get(Appointment, appointment_id)

                if existing:
                    print(f"Skipping existing appointment: {appointment_id}")
                    continue

                appointment = Appointment(
                    appointment_id=appointment_id,
                    user_id=str(row["user_id"]).strip(),
                    application_id=clean_value(row["application_id"]),
                    center_id=clean_value(row["center_id"]),
                    service_id=clean_value(row["service_id"]),
                    requested_date=clean_value(row["requested_date"]),
                    requested_time=clean_value(row["requested_time"]),
                    confirmed_date=clean_value(row["confirmed_date"]),
                    confirmed_time=clean_value(row["confirmed_time"]),
                    booking_reference=clean_value(row["booking_reference"]),
                    booking_method=clean_value(row["booking_method"]),
                    official_booking_url=clean_value(row["official_booking_url"]),
                    appointment_status=clean_value(row["appointment_status"]),
                    created_at=clean_value(row["created_at"]),
                    updated_at=clean_value(row["updated_at"]),
                    notes=clean_value(row["notes"])
                )

                db.session.add(appointment)
                imported += 1

            db.session.commit()

            print(f"\nAppointments imported successfully: {imported}")
            print(
                "Total appointments currently in database:",
                db.session.query(Appointment).count()
            )

        except Exception:
            db.session.rollback()
            raise

if __name__ == "__main__":
    import_services()
    import_sources()
    import_document_types()
    import_service_centers()
    import_eligibility_rules()
    import_requirement_groups()
    import_submission_routes()
    import_requirements()
    import_service_routes()
    import_center_services()
    import_requirement_sources()
    import_demo_users()
    import_applications()
    import_appointments()