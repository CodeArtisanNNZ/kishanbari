import enum
import uuid
from datetime import datetime, timezone
from sqlalchemy import Boolean, DateTime, Enum, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base

def uid() -> str: return str(uuid.uuid4())
def now() -> datetime: return datetime.now(timezone.utc)

class Verification(str, enum.Enum):
    unverified = "unverified"
    needs_review = "needs_review"
    verified = "verified"
    rejected = "rejected"

class User(Base):
    __tablename__ = "users"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    name: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    phone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    fields: Mapped[list["Field"]] = relationship(back_populates="owner", cascade="all, delete-orphan")

class Field(Base):
    __tablename__ = "fields"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(120))
    district: Mapped[str] = mapped_column(String(80))
    upazila: Mapped[str] = mapped_column(String(80))
    area_bigha: Mapped[float | None] = mapped_column(Float, nullable=True)
    current_crop: Mapped[str | None] = mapped_column(String(100), nullable=True)
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    owner: Mapped[User] = relationship(back_populates="fields")
    tests: Mapped[list["SoilTest"]] = relationship(back_populates="field", cascade="all, delete-orphan")

class SoilTest(Base):
    __tablename__ = "soil_tests"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    field_id: Mapped[str] = mapped_column(ForeignKey("fields.id", ondelete="CASCADE"), index=True)
    ph: Mapped[float | None] = mapped_column(Float, nullable=True)
    nitrogen: Mapped[str | None] = mapped_column(String(20), nullable=True)
    phosphorus: Mapped[str | None] = mapped_column(String(20), nullable=True)
    potassium: Mapped[str | None] = mapped_column(String(20), nullable=True)
    texture: Mapped[str | None] = mapped_column(String(30), nullable=True)
    moisture: Mapped[float | None] = mapped_column(Float, nullable=True)
    drainage: Mapped[str | None] = mapped_column(String(30), nullable=True)
    target_crop: Mapped[str | None] = mapped_column(String(100), nullable=True)
    kit_version: Mapped[str] = mapped_column(String(40), default="manual-v1")
    verification: Mapped[Verification] = mapped_column(Enum(Verification), default=Verification.unverified)
    submitted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    field: Mapped[Field] = relationship(back_populates="tests")
    analyses: Mapped[list["Analysis"]] = relationship(back_populates="soil_test", cascade="all, delete-orphan")

class Analysis(Base):
    __tablename__ = "analyses"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    test_id: Mapped[str] = mapped_column(ForeignKey("soil_tests.id", ondelete="CASCADE"), index=True)
    model_version: Mapped[str] = mapped_column(String(50), default="rules-v1")
    result: Mapped[dict] = mapped_column(JSON)
    confidence: Mapped[float] = mapped_column(Float)
    requires_expert: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    soil_test: Mapped[SoilTest] = relationship(back_populates="analyses")

class Feedback(Base):
    __tablename__ = "feedback"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    analysis_id: Mapped[str] = mapped_column(ForeignKey("analyses.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    helpful: Mapped[bool] = mapped_column(Boolean)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
