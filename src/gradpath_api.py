"""FastAPI bridge between the GradPath frontend and Python engines."""

from pathlib import Path
import tempfile
import uuid

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from gradpath.cv_profile import build_candidate_profile


MAX_UPLOAD_BYTES = 5 * 1024 * 1024
ALLOWED_EXTENSIONS = {".pdf", ".docx"}

app = FastAPI(title="GradPath API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    """Confirm that the API is running."""
    return {"status": "ok", "service": "GradPath API"}


@app.post("/api/cv/analyze")
async def analyze_cv(file: UploadFile = File(...)):
    """Analyze a temporary PDF or DOCX and return its structured profile."""
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

        candidate_id = f"guest_{uuid.uuid4().hex}"
        profile = build_candidate_profile(
            temporary_path,
            candidate_id=candidate_id,
        )

        return {"profile": profile}

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
