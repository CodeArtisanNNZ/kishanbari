from datetime import datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict, EmailStr, Field as PField

Level = Literal["low", "medium", "high", "unknown"]
class ORM(BaseModel): model_config = ConfigDict(from_attributes=True)
class Register(BaseModel):
    name: str = PField(min_length=2, max_length=120)
    email: EmailStr
    password: str = PField(min_length=8, max_length=128)
    phone: str | None = PField(default=None, max_length=30)
class Login(BaseModel): email: EmailStr; password: str
class Token(BaseModel): access_token: str; token_type: str = "bearer"
class UserOut(ORM): id: str; name: str; email: EmailStr; phone: str | None; is_admin: bool; created_at: datetime
class FieldCreate(BaseModel):
    name: str = PField(min_length=1, max_length=120)
    district: str = PField(min_length=2, max_length=80)
    upazila: str = PField(min_length=2, max_length=80)
    area_bigha: float | None = PField(default=None, gt=0, le=100000)
    current_crop: str | None = PField(default=None, max_length=100)
    latitude: float | None = PField(default=None, ge=-90, le=90)
    longitude: float | None = PField(default=None, ge=-180, le=180)
class FieldOut(FieldCreate, ORM): id: str; user_id: str; created_at: datetime
class TestCreate(BaseModel):
    field_id: str
    ph: float | None = PField(default=None, ge=0, le=14)
    nitrogen: Level | None = None
    phosphorus: Level | None = None
    potassium: Level | None = None
    texture: Literal["sand", "sandy_loam", "loam", "clay_loam", "clay", "unknown"] | None = None
    moisture: float | None = PField(default=None, ge=0, le=100)
    drainage: Literal["poor", "moderate", "good", "unknown"] | None = None
    target_crop: str | None = PField(default=None, max_length=100)
    kit_version: str = PField(default="manual-v1", max_length=40)
class TestOut(TestCreate, ORM): id: str; verification: str; submitted_at: datetime
class AnalysisOut(ORM): id: str; test_id: str; model_version: str; result: dict; confidence: float; requires_expert: bool; created_at: datetime
class FeedbackCreate(BaseModel): helpful: bool; comment: str | None = PField(default=None, max_length=1000)
class FeedbackOut(ORM): id: str; analysis_id: str; user_id: str; helpful: bool; comment: str | None; created_at: datetime
class ReviewUpdate(BaseModel): verification: Literal["needs_review", "verified", "rejected"]
