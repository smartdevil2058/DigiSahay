<<<<<<< HEAD

from datetime import date, datetime, time
from sqlalchemy import Boolean,Date,DateTime,Float,ForeignKey,Integer,String,Text,Time
from sqlalchemy.orm import Mapped, mapped_column
from extension import db

class User(db.Model):
    __tablename__ = "users"

    user_id: Mapped[str] = mapped_column(
        String(50), primary_key=True
    )

    email: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )

    password_hash: Mapped[str] = mapped_column(
        String(255), nullable=False
    )

    preferred_language: Mapped[str] = mapped_column(
        String(20), default="en", nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )


class UserDocument(db.Model):
    __tablename__ = "user_documents"

    document_id: Mapped[str] = mapped_column(
        String(50), primary_key=True
    )

    user_id: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("users.user_id"),
        nullable=False,
        index=True
    )

    document_type_id: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("document_types.document_type_id"),
        nullable=False
    )

    document_name: Mapped[str] = mapped_column(
        String(255), nullable=False
    )

    original_filename: Mapped[str] = mapped_column(
        String(255), nullable=False
    )

    stored_filename: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False
    )

    storage_path: Mapped[str] = mapped_column(
        String(500), nullable=False
    )

    file_type: Mapped[str] = mapped_column(
        String(100), nullable=False
    )

    file_size: Mapped[int] = mapped_column(
        Integer, nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )

class Service(db.Model):
    __tablename__ = "services"

    service_id: Mapped[str] = mapped_column(
        String(50), primary_key=True
    )

    service_name: Mapped[str] = mapped_column(
        String(255), nullable=False
    )

    service_category: Mapped[str | None] = mapped_column(
        String(255), nullable=True
    )

    application_or_update_type: Mapped[str | None] = mapped_column(
        String(255), nullable=True
    )

    form_name_or_number: Mapped[str | None] = mapped_column(
        String(255), nullable=True
    )

    description: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )

    responsible_authority: Mapped[str | None] = mapped_column(
        String(255), nullable=True
    )

    official_service_url: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )

    verification_status: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )


class EligibilityRule(db.Model):
    __tablename__ = "eligibility_rules"

    rule_id: Mapped[str] = mapped_column(
        String(50), primary_key=True
    )

    service_id: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("services.service_id"),
        nullable=False
    )

    rule_code: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )

    question_text: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )

    condition_type: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )

    condition_config: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )

    outcome_if_true: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )

    outcome_if_false: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )

    source_id: Mapped[str | None] = mapped_column(
        String(50),
        ForeignKey("sources.source_id"),
        nullable=True
    )

    verification_status: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )



class RequirementGroup(db.Model):
    __tablename__ = "requirement_groups"

    group_id: Mapped[str] = mapped_column(
        String(50), primary_key=True
    )

    service_id: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("services.service_id"),
        nullable=False
    )

    group_name: Mapped[str] = mapped_column(
        String(255), nullable=False
    )

    description: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )

    selection_mode: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )

    min_selections: Mapped[int | None] = mapped_column(
        Integer, nullable=True
    )

    max_selections: Mapped[int | None] = mapped_column(
        Integer, nullable=True
    )

    condition_rule_id: Mapped[str | None] = mapped_column(
        String(50),
        ForeignKey("eligibility_rules.rule_id"),
        nullable=True
    )

    verification_status: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )



class DocumentType(db.Model):
    __tablename__ = "document_types"

    document_type_id: Mapped[str] = mapped_column(
        String(50), primary_key=True
    )

    document_name: Mapped[str] = mapped_column(
        String(255), nullable=False
    )

    document_category: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )

    description: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )

    original_or_copy_requirement: Mapped[str | None] = mapped_column(
        String(255), nullable=True
    )

    format_or_size_constraints: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )

    special_conditions: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )

    verification_status: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )



class Requirement(db.Model):
    __tablename__ = "requirements"

    option_id: Mapped[str] = mapped_column(
        String(50), primary_key=True
    )

    group_id: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("requirement_groups.group_id"),
        nullable=False
    )

    document_type_id: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("document_types.document_type_id"),
        nullable=False
    )

    condition_rule_id: Mapped[str | None] = mapped_column(
        String(50),
        ForeignKey("eligibility_rules.rule_id"),
        nullable=True
    )

    applicable_context: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )

    official_acceptance_conditions: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )

    verification_status: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )

    source_id: Mapped[str | None] = mapped_column(
        String(50),
        ForeignKey("sources.source_id"),
        nullable=True
    )


class SubmissionRoute(db.Model):
    __tablename__ = "submission_routes"

    route_id: Mapped[str] = mapped_column(
        String(50), primary_key=True
    )

    service_id: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("services.service_id"),
        nullable=False
    )

    route_type: Mapped[str] = mapped_column(
        String(100), nullable=False
    )

    route_name: Mapped[str] = mapped_column(
        Text, nullable=False
    )

    official_url: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )

    instructions: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )

    appointment_required: Mapped[bool | None] = mapped_column(
        Boolean, nullable=True
    )

    physical_visit_required: Mapped[bool | None] = mapped_column(
        Boolean, nullable=True
    )

    available_geographic_scope: Mapped[str | None] = mapped_column(
        String(255), nullable=True
    )

    verification_status: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )

    source_id: Mapped[str | None] = mapped_column(
        String(50),
        ForeignKey("sources.source_id"),
        nullable=True
    )



class Source(db.Model):
    __tablename__ = "sources"

    source_id: Mapped[str] = mapped_column(
        String(50), primary_key=True
    )

    source_name: Mapped[str] = mapped_column(
        Text, nullable=False
    )

    responsible_authority: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )

    source_url: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )

    source_type: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )

    relevant_section_or_page: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )

    date_checked: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True
    )

    last_verified_at: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True
    )

    verification_status: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )

    notes: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )


class RequirementSource(db.Model):
    __tablename__ = "requirement_sources"

    link_id: Mapped[str] = mapped_column(
        String(50), primary_key=True
    )

    source_id: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("sources.source_id"),
        nullable=False
    )

    record_type: Mapped[str] = mapped_column(
        String(100), nullable=False
    )

    # Intentionally NOT a foreign key.
    # It can refer to records in different tables.
    record_id: Mapped[str] = mapped_column(
        String(50), nullable=False
    )

    evidence_note: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )


class ServiceCenter(db.Model):
    __tablename__ = "service_centers"

    center_id: Mapped[str] = mapped_column(
        String(50), primary_key=True
    )

    center_name: Mapped[str] = mapped_column(
        Text, nullable=False
    )

    center_type: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )

    authority_name: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )

    address_line: Mapped[str] = mapped_column(
        Text, nullable=False
    )

    city: Mapped[str] = mapped_column(
        String(100), nullable=False
    )

    district: Mapped[str] = mapped_column(
        String(100), nullable=False
    )

    state: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )

    pincode: Mapped[str | None] = mapped_column(
        String(10), nullable=True
    )

    latitude: Mapped[float | None] = mapped_column(
        Float, nullable=True
    )

    longitude: Mapped[float | None] = mapped_column(
        Float, nullable=True
    )

    contact_number: Mapped[str | None] = mapped_column(
        String(20), nullable=True
    )

    operating_hours: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )

    official_source_url: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )

    data_last_verified: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True
    )

    verification_status: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )

    notes: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )

    @property
    def has_valid_coordinates(self) -> bool:
        """Validate that both latitude and longitude exist and are within valid geographic bounds."""
        if self.latitude is None or self.longitude is None:
            return False
        try:
            lat = float(self.latitude)
            lng = float(self.longitude)
            return -90.0 <= lat <= 90.0 and -180.0 <= lng <= 180.0
        except (ValueError, TypeError):
            return False

    @property
    def google_maps_url(self) -> str | None:
        """Generate authoritative Google Maps direct pinpoint URL using exact coordinates."""
        if not self.has_valid_coordinates:
            return None
        from urllib.parse import quote_plus
        label = quote_plus(str(self.center_name or "Service Center").strip())
        return f"https://www.google.com/maps?q={self.latitude},{self.longitude}+({label})"




class CenterService(db.Model):
    __tablename__ = "center_services"

    center_service_id: Mapped[str] = mapped_column(
        String(50), primary_key=True
    )

    center_id: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("service_centers.center_id"),
        nullable=False
    )

    service_id: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("services.service_id"),
        nullable=False
    )

    service_available: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )

    appointment_supported: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )

    booking_method: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )

    official_booking_url: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )

    availability_source: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )

    verification_status: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )

    last_verified_at: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True
    )

    notes: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )



class Application(db.Model):
    __tablename__ = "applications"

    application_id: Mapped[str] = mapped_column(
        String(50), primary_key=True
    )

    user_id: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("users.user_id"),
        nullable=False
    )

    service_id: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("services.service_id"),
        nullable=False
    )

    application_reference: Mapped[str | None] = mapped_column(
        String(255), nullable=True
    )

    application_mode: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )

    application_status: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )

    submitted_at: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True
    )

    last_status_updated_at: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True
    )

    official_status_source: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )

    related_appointment_id: Mapped[str | None] = mapped_column(
        String(50),
        ForeignKey(
            "appointments.appointment_id",
            use_alter=True,
            name="fk_application_related_appointment"
        ),
        nullable=True
    )

    notes: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )


class ApplicationStatusHistory(db.Model):
    __tablename__ = "application_status_history"

    history_id: Mapped[str] = mapped_column(
        String(50), primary_key=True
    )

    application_id: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("applications.application_id"),
        nullable=False,
        index=True
    )

    previous_status: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )

    new_status: Mapped[str] = mapped_column(
        String(100), nullable=False
    )

    remarks: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )

    update_source: Mapped[str] = mapped_column(
        String(50), nullable=False
    )

    changed_by: Mapped[str | None] = mapped_column(
        String(50),
        ForeignKey("users.user_id"),
        nullable=True
    )

    changed_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

class ApplicationDocument(db.Model):
    __tablename__ = "application_documents"

    application_document_id: Mapped[str] = mapped_column(
        String(50), primary_key=True
    )

    application_id: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("applications.application_id"),
        nullable=False
    )

    document_id: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("user_documents.document_id"),
        nullable=False
    )

    requirement_option_id: Mapped[str | None] = mapped_column(
        String(50),
        ForeignKey("requirements.option_id"),
        nullable=True
    )

    attached_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )

class Appointment(db.Model):
    __tablename__ = "appointments"

    appointment_id: Mapped[str] = mapped_column(
        String(50), primary_key=True
    )

    user_id: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("users.user_id"),
        nullable=False
    )

    application_id: Mapped[str | None] = mapped_column(
        String(50),
        ForeignKey("applications.application_id"),
        nullable=True
    )

    center_id: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("service_centers.center_id"),
        nullable=False
    )

    service_id: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("services.service_id"),
        nullable=False
    )

    requested_date: Mapped[date] = mapped_column(
        Date, nullable=False
    )

    requested_time: Mapped[time] = mapped_column(
        Time, nullable=False
    )

    confirmed_date: Mapped[date | None] = mapped_column(
        Date, nullable=True
    )

    confirmed_time: Mapped[time | None] = mapped_column(
        Time, nullable=True
    )

    booking_reference: Mapped[str | None] = mapped_column(
        String(255), nullable=True
    )

    booking_method: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )

    official_booking_url: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )

    appointment_status: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow,
        onupdate=datetime.utcnow, nullable=False
    )

    notes: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )



class ServiceRoute(db.Model):
    __tablename__ = "service_routes"

    route_id: Mapped[str] = mapped_column(
        String(50), primary_key=True
    )

    service_id: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("services.service_id"),
        nullable=False
    )

    route_name: Mapped[str] = mapped_column(
        Text, nullable=False
    )

    route_type: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )

    authority_name: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )

    official_service_url: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )

    official_booking_url: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )

    application_method: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )

    appointment_required: Mapped[bool | None] = mapped_column(
        Boolean, nullable=True
    )

    physical_visit_required: Mapped[bool | None] = mapped_column(
        Boolean, nullable=True
    )

    available_geographic_scope: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )

    integration_status: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )

    instructions: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )

    source_id: Mapped[str | None] = mapped_column(
        String(50),
        ForeignKey("sources.source_id"),
        nullable=True
    )

    verification_status: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )

    last_verified_at: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True
    )

    notes: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )
=======

from datetime import date, datetime, time
from sqlalchemy import Boolean,Date,DateTime,Float,ForeignKey,Integer,String,Text,Time
from sqlalchemy.orm import Mapped, mapped_column
from extension import db

class User(db.Model):
    __tablename__ = "users"

    user_id: Mapped[str] = mapped_column(
        String(50), primary_key=True
    )

    email: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )

    password_hash: Mapped[str] = mapped_column(
        String(255), nullable=False
    )

    preferred_language: Mapped[str] = mapped_column(
        String(20), default="en", nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )


class UserDocument(db.Model):
    __tablename__ = "user_documents"

    document_id: Mapped[str] = mapped_column(
        String(50), primary_key=True
    )

    user_id: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("users.user_id"),
        nullable=False,
        index=True
    )

    document_type_id: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("document_types.document_type_id"),
        nullable=False
    )

    document_name: Mapped[str] = mapped_column(
        String(255), nullable=False
    )

    original_filename: Mapped[str] = mapped_column(
        String(255), nullable=False
    )

    stored_filename: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False
    )

    storage_path: Mapped[str] = mapped_column(
        String(500), nullable=False
    )

    file_type: Mapped[str] = mapped_column(
        String(100), nullable=False
    )

    file_size: Mapped[int] = mapped_column(
        Integer, nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )

class Service(db.Model):
    __tablename__ = "services"

    service_id: Mapped[str] = mapped_column(
        String(50), primary_key=True
    )

    service_name: Mapped[str] = mapped_column(
        String(255), nullable=False
    )

    service_category: Mapped[str | None] = mapped_column(
        String(255), nullable=True
    )

    application_or_update_type: Mapped[str | None] = mapped_column(
        String(255), nullable=True
    )

    form_name_or_number: Mapped[str | None] = mapped_column(
        String(255), nullable=True
    )

    description: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )

    responsible_authority: Mapped[str | None] = mapped_column(
        String(255), nullable=True
    )

    official_service_url: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )

    verification_status: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )


class EligibilityRule(db.Model):
    __tablename__ = "eligibility_rules"

    rule_id: Mapped[str] = mapped_column(
        String(50), primary_key=True
    )

    service_id: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("services.service_id"),
        nullable=False
    )

    rule_code: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )

    question_text: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )

    condition_type: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )

    condition_config: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )

    outcome_if_true: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )

    outcome_if_false: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )

    source_id: Mapped[str | None] = mapped_column(
        String(50),
        ForeignKey("sources.source_id"),
        nullable=True
    )

    verification_status: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )



class RequirementGroup(db.Model):
    __tablename__ = "requirement_groups"

    group_id: Mapped[str] = mapped_column(
        String(50), primary_key=True
    )

    service_id: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("services.service_id"),
        nullable=False
    )

    group_name: Mapped[str] = mapped_column(
        String(255), nullable=False
    )

    description: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )

    selection_mode: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )

    min_selections: Mapped[int | None] = mapped_column(
        Integer, nullable=True
    )

    max_selections: Mapped[int | None] = mapped_column(
        Integer, nullable=True
    )

    condition_rule_id: Mapped[str | None] = mapped_column(
        String(50),
        ForeignKey("eligibility_rules.rule_id"),
        nullable=True
    )

    verification_status: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )



class DocumentType(db.Model):
    __tablename__ = "document_types"

    document_type_id: Mapped[str] = mapped_column(
        String(50), primary_key=True
    )

    document_name: Mapped[str] = mapped_column(
        String(255), nullable=False
    )

    document_category: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )

    description: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )

    original_or_copy_requirement: Mapped[str | None] = mapped_column(
        String(255), nullable=True
    )

    format_or_size_constraints: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )

    special_conditions: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )

    verification_status: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )



class Requirement(db.Model):
    __tablename__ = "requirements"

    option_id: Mapped[str] = mapped_column(
        String(50), primary_key=True
    )

    group_id: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("requirement_groups.group_id"),
        nullable=False
    )

    document_type_id: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("document_types.document_type_id"),
        nullable=False
    )

    condition_rule_id: Mapped[str | None] = mapped_column(
        String(50),
        ForeignKey("eligibility_rules.rule_id"),
        nullable=True
    )

    applicable_context: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )

    official_acceptance_conditions: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )

    verification_status: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )

    source_id: Mapped[str | None] = mapped_column(
        String(50),
        ForeignKey("sources.source_id"),
        nullable=True
    )


class SubmissionRoute(db.Model):
    __tablename__ = "submission_routes"

    route_id: Mapped[str] = mapped_column(
        String(50), primary_key=True
    )

    service_id: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("services.service_id"),
        nullable=False
    )

    route_type: Mapped[str] = mapped_column(
        String(100), nullable=False
    )

    route_name: Mapped[str] = mapped_column(
        Text, nullable=False
    )

    official_url: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )

    instructions: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )

    appointment_required: Mapped[bool | None] = mapped_column(
        Boolean, nullable=True
    )

    physical_visit_required: Mapped[bool | None] = mapped_column(
        Boolean, nullable=True
    )

    available_geographic_scope: Mapped[str | None] = mapped_column(
        String(255), nullable=True
    )

    verification_status: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )

    source_id: Mapped[str | None] = mapped_column(
        String(50),
        ForeignKey("sources.source_id"),
        nullable=True
    )



class Source(db.Model):
    __tablename__ = "sources"

    source_id: Mapped[str] = mapped_column(
        String(50), primary_key=True
    )

    source_name: Mapped[str] = mapped_column(
        Text, nullable=False
    )

    responsible_authority: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )

    source_url: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )

    source_type: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )

    relevant_section_or_page: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )

    date_checked: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True
    )

    last_verified_at: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True
    )

    verification_status: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )

    notes: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )


class RequirementSource(db.Model):
    __tablename__ = "requirement_sources"

    link_id: Mapped[str] = mapped_column(
        String(50), primary_key=True
    )

    source_id: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("sources.source_id"),
        nullable=False
    )

    record_type: Mapped[str] = mapped_column(
        String(100), nullable=False
    )

    # Intentionally NOT a foreign key.
    # It can refer to records in different tables.
    record_id: Mapped[str] = mapped_column(
        String(50), nullable=False
    )

    evidence_note: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )


class ServiceCenter(db.Model):
    __tablename__ = "service_centers"

    center_id: Mapped[str] = mapped_column(
        String(50), primary_key=True
    )

    center_name: Mapped[str] = mapped_column(
        Text, nullable=False
    )

    center_type: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )

    authority_name: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )

    address_line: Mapped[str] = mapped_column(
        Text, nullable=False
    )

    city: Mapped[str] = mapped_column(
        String(100), nullable=False
    )

    district: Mapped[str] = mapped_column(
        String(100), nullable=False
    )

    state: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )

    pincode: Mapped[str | None] = mapped_column(
        String(10), nullable=True
    )

    latitude: Mapped[float | None] = mapped_column(
        Float, nullable=True
    )

    longitude: Mapped[float | None] = mapped_column(
        Float, nullable=True
    )

    contact_number: Mapped[str | None] = mapped_column(
        String(20), nullable=True
    )

    operating_hours: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )

    official_source_url: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )

    data_last_verified: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True
    )

    verification_status: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )

    notes: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )

    @property
    def has_valid_coordinates(self) -> bool:
        """Validate that both latitude and longitude exist and are within valid geographic bounds."""
        if self.latitude is None or self.longitude is None:
            return False
        try:
            lat = float(self.latitude)
            lng = float(self.longitude)
            return -90.0 <= lat <= 90.0 and -180.0 <= lng <= 180.0
        except (ValueError, TypeError):
            return False

    @property
    def google_maps_url(self) -> str | None:
        """Generate authoritative Google Maps direct pinpoint URL using exact coordinates."""
        if not self.has_valid_coordinates:
            return None
        from urllib.parse import quote_plus
        label = quote_plus(str(self.center_name or "Service Center").strip())
        return f"https://www.google.com/maps?q={self.latitude},{self.longitude}+({label})"




class CenterService(db.Model):
    __tablename__ = "center_services"

    center_service_id: Mapped[str] = mapped_column(
        String(50), primary_key=True
    )

    center_id: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("service_centers.center_id"),
        nullable=False
    )

    service_id: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("services.service_id"),
        nullable=False
    )

    service_available: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )

    appointment_supported: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )

    booking_method: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )

    official_booking_url: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )

    availability_source: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )

    verification_status: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )

    last_verified_at: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True
    )

    notes: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )



class Application(db.Model):
    __tablename__ = "applications"

    application_id: Mapped[str] = mapped_column(
        String(50), primary_key=True
    )

    user_id: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("users.user_id"),
        nullable=False
    )

    service_id: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("services.service_id"),
        nullable=False
    )

    application_reference: Mapped[str | None] = mapped_column(
        String(255), nullable=True
    )

    application_mode: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )

    application_status: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )

    submitted_at: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True
    )

    last_status_updated_at: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True
    )

    official_status_source: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )

    related_appointment_id: Mapped[str | None] = mapped_column(
        String(50),
        ForeignKey(
            "appointments.appointment_id",
            use_alter=True,
            name="fk_application_related_appointment"
        ),
        nullable=True
    )

    notes: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )


class ApplicationStatusHistory(db.Model):
    __tablename__ = "application_status_history"

    history_id: Mapped[str] = mapped_column(
        String(50), primary_key=True
    )

    application_id: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("applications.application_id"),
        nullable=False,
        index=True
    )

    previous_status: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )

    new_status: Mapped[str] = mapped_column(
        String(100), nullable=False
    )

    remarks: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )

    update_source: Mapped[str] = mapped_column(
        String(50), nullable=False
    )

    changed_by: Mapped[str | None] = mapped_column(
        String(50),
        ForeignKey("users.user_id"),
        nullable=True
    )

    changed_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

class ApplicationDocument(db.Model):
    __tablename__ = "application_documents"

    application_document_id: Mapped[str] = mapped_column(
        String(50), primary_key=True
    )

    application_id: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("applications.application_id"),
        nullable=False
    )

    document_id: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("user_documents.document_id"),
        nullable=False
    )

    requirement_option_id: Mapped[str | None] = mapped_column(
        String(50),
        ForeignKey("requirements.option_id"),
        nullable=True
    )

    attached_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )

class Appointment(db.Model):
    __tablename__ = "appointments"

    appointment_id: Mapped[str] = mapped_column(
        String(50), primary_key=True
    )

    user_id: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("users.user_id"),
        nullable=False
    )

    application_id: Mapped[str | None] = mapped_column(
        String(50),
        ForeignKey("applications.application_id"),
        nullable=True
    )

    center_id: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("service_centers.center_id"),
        nullable=False
    )

    service_id: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("services.service_id"),
        nullable=False
    )

    requested_date: Mapped[date] = mapped_column(
        Date, nullable=False
    )

    requested_time: Mapped[time] = mapped_column(
        Time, nullable=False
    )

    confirmed_date: Mapped[date | None] = mapped_column(
        Date, nullable=True
    )

    confirmed_time: Mapped[time | None] = mapped_column(
        Time, nullable=True
    )

    booking_reference: Mapped[str | None] = mapped_column(
        String(255), nullable=True
    )

    booking_method: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )

    official_booking_url: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )

    appointment_status: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow,
        onupdate=datetime.utcnow, nullable=False
    )

    notes: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )



class ServiceRoute(db.Model):
    __tablename__ = "service_routes"

    route_id: Mapped[str] = mapped_column(
        String(50), primary_key=True
    )

    service_id: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("services.service_id"),
        nullable=False
    )

    route_name: Mapped[str] = mapped_column(
        Text, nullable=False
    )

    route_type: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )

    authority_name: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )

    official_service_url: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )

    official_booking_url: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )

    application_method: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )

    appointment_required: Mapped[bool | None] = mapped_column(
        Boolean, nullable=True
    )

    physical_visit_required: Mapped[bool | None] = mapped_column(
        Boolean, nullable=True
    )

    available_geographic_scope: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )

    integration_status: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )

    instructions: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )

    source_id: Mapped[str | None] = mapped_column(
        String(50),
        ForeignKey("sources.source_id"),
        nullable=True
    )

    verification_status: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )

    last_verified_at: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True
    )

    notes: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )
>>>>>>> c981506dbd2f314e63b7e90f4ab444ee1eca2d2c
