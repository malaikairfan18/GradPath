"""FastAPI bridge between the GradPath frontend and Python engines."""

from pathlib import Path
import tempfile
import uuid

from pydantic import BaseModel

from gradpath.learning_recommendations import recommend_learning_actions
from gradpath.skill_gap import analyze_skill_gaps
import hmac
import os
import secrets

from fastapi import (
    Depends,
    FastAPI,
    File,
    HTTPException,
    Request,
    Response,
    UploadFile,
)
from fastapi.middleware.cors import CORSMiddleware

from gradpath.auth import (
    DEFAULT_AUTH_DATABASE_PATH,
    authenticate_user,
    register_user,
)
from gradpath.sessions import (
    DEFAULT_SESSION_TTL_SECONDS,
    create_session,
    get_session_user,
    revoke_session,
)

from gradpath.cv_profile import build_candidate_profile
from gradpath.cv_history import (
    get_cv_analysis,
    list_cv_analyses,
    save_cv_analysis,
)

MAX_UPLOAD_BYTES = 5 * 1024 * 1024
ALLOWED_EXTENSIONS = {".pdf", ".docx"}

app = FastAPI(title="GradPath API", version="0.1.0")

class CareerPlanRequest(BaseModel):
    candidate_profile: dict
    target_role: str

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

def get_auth_database_path() -> Path:
    """Return the database path used for authentication and sessions."""
    return DEFAULT_AUTH_DATABASE_PATH

def get_current_user(
    request: Request,
    database_path: Path = Depends(get_auth_database_path),
) -> dict:
    """Return the authenticated user from the server-side session cookie."""
    session_token = request.cookies.get("gradpath_session")

    user = get_session_user(
        session_token,
        database_path=database_path,
    )

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Authentication required.",
        )

    return user

ALLOWED_FRONTEND_ORIGINS = {
    "http://localhost:5173",
    "http://127.0.0.1:5173",
}

SESSION_COOKIE_NAME = "gradpath_session"
CSRF_COOKIE_NAME = "gradpath_csrf"

@app.get("/health")
def health_check():
    """Confirm that the API is running."""
    return {"status": "ok", "service": "GradPath API"}

@app.post("/api/cv/analyze")
async def analyze_cv(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
    database_path: Path = Depends(get_auth_database_path),
):
    """Analyze a CV and persist its structured profile for the logged-in user."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="Please select a CV file.")

    extension = Path(file.filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Unsupported format. Please upload a PDF or DOCX file.",
        )

    temporary_path = None

    try:
        content = await file.read(MAX_UPLOAD_BYTES + 1)

        if not content:
            raise HTTPException(
                status_code=400,
                detail="The uploaded file is empty.",
            )

        if len(content) > MAX_UPLOAD_BYTES:
            raise HTTPException(
                status_code=413,
                detail="The CV must be 5 MB or smaller.",
            )

        with tempfile.NamedTemporaryFile(
            prefix="gradpath_cv_",
            suffix=extension,
            delete=False,
        ) as temporary_file:
            temporary_file.write(content)
            temporary_path = Path(temporary_file.name)

        candidate_id = f"user_{current_user['user_id']}"

        profile = build_candidate_profile(
            temporary_path,
            candidate_id=candidate_id,
        )

        saved_analysis = save_cv_analysis(
            user_id=current_user["user_id"],
            original_filename=Path(file.filename).name,
            file_type=extension.lstrip("."),
            profile=profile,
            database_path=database_path,
        )

        return {
            "cv_id": saved_analysis["cv_id"],
            "created_at": saved_analysis["created_at"],
            "profile": saved_analysis["profile"],
        }

    except HTTPException:
        raise
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=422,
            detail=(
                "We could not analyze this file. Please check that it is "
                "a readable PDF or DOCX and try again."
            ),
        ) from exc
    finally:
        await file.close()

        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)

@app.get("/api/cv/history")
def get_cv_history(
    current_user: dict = Depends(get_current_user),
    database_path: Path = Depends(get_auth_database_path),
):
    """List saved CV analyses belonging to the authenticated user."""
    try:
        analyses = list_cv_analyses(
            user_id=current_user["user_id"],
            database_path=database_path,
        )
        return {"analyses": analyses}
    except (ValueError, OSError) as exc:
        raise HTTPException(
            status_code=500,
            detail="Unable to retrieve CV history.",
        ) from exc

@app.get("/api/cv/history/{cv_id}")
def get_saved_cv_analysis(
    cv_id: str,
    current_user: dict = Depends(get_current_user),
    database_path: Path = Depends(get_auth_database_path),
):
    """Retrieve one saved CV analysis owned by the authenticated user."""
    try:
        analysis = get_cv_analysis(
            cv_id=cv_id,
            user_id=current_user["user_id"],
            database_path=database_path,
        )
    except (ValueError, OSError) as exc:
        raise HTTPException(
            status_code=500,
            detail="Unable to retrieve the CV analysis.",
        ) from exc

    if analysis is None:
        # Use the same response for missing and other users' CV IDs.
        raise HTTPException(
            status_code=404,
            detail="CV analysis not found.",
        )

    return {"analysis": analysis}

@app.post("/api/career/plan")
def generate_career_plan(request: CareerPlanRequest):
    """Generate role-specific skill gaps and learning recommendations."""
    try:
        skill_gaps = analyze_skill_gaps(
            candidate_profile=request.candidate_profile,
            target_role=request.target_role,
        )

        learning_actions = recommend_learning_actions(
            skill_gaps=skill_gaps,
            target_role=request.target_role,
        )

        return {
            "target_role": request.target_role,
            "skill_gaps": skill_gaps,
            "learning_actions": learning_actions,
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str

class LoginRequest(BaseModel):
    username_or_email: str
    password: str

def _secure_cookies() -> bool:
    return os.getenv("GRADPATH_COOKIE_SECURE", "").lower() == "true"

def _validate_csrf(request: Request) -> None:
    origin = request.headers.get("origin")
    cookie_token = request.cookies.get(CSRF_COOKIE_NAME)
    header_token = request.headers.get("X-CSRF-Token")

    if origin not in ALLOWED_FRONTEND_ORIGINS:
        raise HTTPException(
            status_code=403,
            detail="Invalid request origin.",
        )

    if (
        not cookie_token
        or not header_token
        or not hmac.compare_digest(cookie_token, header_token)
    ):
        raise HTTPException(
            status_code=403,
            detail="CSRF validation failed.",
        )

def _set_session_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=token,
        max_age=DEFAULT_SESSION_TTL_SECONDS,
        httponly=True,
        secure=_secure_cookies(),
        samesite="lax",
        path="/",
    )

def _set_csrf_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        key=CSRF_COOKIE_NAME,
        value=token,
        max_age=DEFAULT_SESSION_TTL_SECONDS,
        httponly=False,
        secure=_secure_cookies(),
        samesite="lax",
        path="/",
    )

@app.get("/api/auth/csrf")
def get_csrf_token(response: Response):
    """Issue a CSRF token for subsequent authentication requests."""
    token = secrets.token_urlsafe(32)
    _set_csrf_cookie(response, token)

    return {"csrf_token": token}

@app.post("/api/auth/register")
def register(
    request: Request,
    response: Response,
    payload: RegisterRequest,
    database_path: Path = Depends(get_auth_database_path),
):
    """Register a user and create an authenticated session."""
    _validate_csrf(request)

    try:
        user = register_user(
            username=payload.username,
            email=payload.email,
            password=payload.password,
            database_path=database_path,
        )

        session = create_session(
            user_id=user["user_id"],
            database_path=database_path,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    _set_session_cookie(response, session["token"])

    return {"user": user}

@app.post("/api/auth/login")
def login(
    request: Request,
    response: Response,
    payload: LoginRequest,
    database_path: Path = Depends(get_auth_database_path),
):
    """Authenticate a user and create a session."""
    _validate_csrf(request)

    user = authenticate_user(
        username_or_email=payload.username_or_email,
        password=payload.password,
        database_path=database_path,
    )

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid username/email or password.",
        )

    session = create_session(
        user_id=user["user_id"],
        database_path=database_path,
    )

    _set_session_cookie(response, session["token"])

    return {"user": user}

@app.get("/api/auth/me")
def get_me(
    current_user: dict = Depends(get_current_user),
):
    """Return the currently authenticated user's identity."""
    return {"user": current_user}

@app.post("/api/auth/logout")
def logout(
    request: Request,
    response: Response,
    database_path: Path = Depends(get_auth_database_path),
):
    """Revoke the current session and clear authentication cookies."""
    _validate_csrf(request)

    session_token = request.cookies.get(SESSION_COOKIE_NAME)

    if session_token:
        revoke_session(
            session_token,
            database_path=database_path,
        )

    response.delete_cookie(
        key=SESSION_COOKIE_NAME,
        path="/",
        secure=_secure_cookies(),
        httponly=True,
        samesite="lax",
    )
    response.delete_cookie(
        key=CSRF_COOKIE_NAME,
        path="/",
        secure=_secure_cookies(),
        httponly=False,
        samesite="lax",
    )

    return {"message": "Logged out successfully."}
