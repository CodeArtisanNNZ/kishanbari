from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.orm import Session
from .config import get_settings
from .database import Base, engine, get_db
from .models import Analysis, Feedback, Field, SoilTest, User, Verification
from .rules import analyze
from .ml import model_status
from .schemas import AnalysisOut, FeedbackCreate, FeedbackOut, FieldCreate, FieldOut, Login, Register, ReviewUpdate, TestCreate, TestOut, Token, UserOut
from .security import admin_user, create_token, current_user, hash_password, verify_password

@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(title="Kishan Bari API", version="0.1.0", lifespan=lifespan, docs_url="/docs")
app.add_middleware(CORSMiddleware, allow_origins=get_settings().origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

@app.get("/health")
def health(): return {"status":"ok","service":"kishan-bari-api","ml":model_status()}

@app.post("/api/v1/auth/register", response_model=Token, status_code=201)
def register(data: Register, db: Session = Depends(get_db)):
    email = data.email.lower()
    if db.scalar(select(User).where(User.email == email)): raise HTTPException(409, "এই ইমেইল ইতিমধ্যে ব্যবহৃত")
    user = User(name=data.name.strip(), email=email, phone=data.phone, password_hash=hash_password(data.password), is_admin=email == get_settings().admin_email.lower())
    db.add(user); db.commit(); db.refresh(user)
    return Token(access_token=create_token(user))

@app.post("/api/v1/auth/login", response_model=Token)
def login(data: Login, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == data.email.lower()))
    if not user or not verify_password(data.password, user.password_hash): raise HTTPException(status.HTTP_401_UNAUTHORIZED, "ইমেইল বা পাসওয়ার্ড সঠিক নয়")
    return Token(access_token=create_token(user))

@app.get("/api/v1/me", response_model=UserOut)
def me(user: User = Depends(current_user)): return user

@app.post("/api/v1/fields", response_model=FieldOut, status_code=201)
def create_field(data: FieldCreate, user: User = Depends(current_user), db: Session = Depends(get_db)):
    field = Field(user_id=user.id, **data.model_dump()); db.add(field); db.commit(); db.refresh(field); return field

@app.get("/api/v1/fields", response_model=list[FieldOut])
def list_fields(user: User = Depends(current_user), db: Session = Depends(get_db)):
    return db.scalars(select(Field).where(Field.user_id == user.id).order_by(Field.created_at.desc())).all()

def owned_field(db: Session, field_id: str, user: User) -> Field:
    field = db.scalar(select(Field).where(Field.id == field_id, Field.user_id == user.id))
    if not field: raise HTTPException(404, "জমি পাওয়া যায়নি")
    return field

@app.post("/api/v1/soil-tests", response_model=TestOut, status_code=201)
def create_test(data: TestCreate, user: User = Depends(current_user), db: Session = Depends(get_db)):
    owned_field(db, data.field_id, user)
    test = SoilTest(**data.model_dump()); db.add(test); db.commit(); db.refresh(test); return test

@app.get("/api/v1/soil-tests", response_model=list[TestOut])
def list_tests(field_id: str | None = None, user: User = Depends(current_user), db: Session = Depends(get_db)):
    query = select(SoilTest).join(Field).where(Field.user_id == user.id)
    if field_id: query = query.where(SoilTest.field_id == field_id)
    return db.scalars(query.order_by(SoilTest.submitted_at.desc())).all()

@app.post("/api/v1/soil-tests/{test_id}/analyze", response_model=AnalysisOut, status_code=201)
def run_analysis(test_id: str, user: User = Depends(current_user), db: Session = Depends(get_db)):
    test = db.scalar(select(SoilTest).join(Field).where(SoilTest.id == test_id, Field.user_id == user.id))
    if not test: raise HTTPException(404, "পরীক্ষা পাওয়া যায়নি")
    result, confidence, expert = analyze(test)
    analysis = Analysis(test_id=test.id, result=result, confidence=confidence, requires_expert=expert)
    db.add(analysis); db.commit(); db.refresh(analysis); return analysis

@app.get("/api/v1/soil-tests/{test_id}/analyses", response_model=list[AnalysisOut])
def list_analyses(test_id: str, user: User = Depends(current_user), db: Session = Depends(get_db)):
    test = db.scalar(select(SoilTest).join(Field).where(SoilTest.id == test_id, Field.user_id == user.id))
    if not test: raise HTTPException(404, "পরীক্ষা পাওয়া যায়নি")
    return db.scalars(select(Analysis).where(Analysis.test_id == test_id).order_by(Analysis.created_at.desc())).all()

@app.post("/api/v1/analyses/{analysis_id}/feedback", response_model=FeedbackOut, status_code=201)
def add_feedback(analysis_id: str, data: FeedbackCreate, user: User = Depends(current_user), db: Session = Depends(get_db)):
    analysis = db.scalar(select(Analysis).join(SoilTest).join(Field).where(Analysis.id == analysis_id, Field.user_id == user.id))
    if not analysis: raise HTTPException(404, "ফল পাওয়া যায়নি")
    feedback = Feedback(analysis_id=analysis_id, user_id=user.id, **data.model_dump()); db.add(feedback); db.commit(); db.refresh(feedback); return feedback

@app.get("/api/v1/admin/review", response_model=list[TestOut])
def review_queue(limit: int = Query(50, ge=1, le=200), _: User = Depends(admin_user), db: Session = Depends(get_db)):
    return db.scalars(select(SoilTest).where(SoilTest.verification.in_([Verification.unverified, Verification.needs_review])).limit(limit)).all()

@app.patch("/api/v1/admin/soil-tests/{test_id}", response_model=TestOut)
def review_test(test_id: str, data: ReviewUpdate, _: User = Depends(admin_user), db: Session = Depends(get_db)):
    test = db.get(SoilTest, test_id)
    if not test: raise HTTPException(404, "পরীক্ষা পাওয়া যায়নি")
    test.verification = Verification(data.verification); db.commit(); db.refresh(test); return test
