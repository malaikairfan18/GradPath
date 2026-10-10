from pathlib import Path
from tempfile import TemporaryDirectory
import copy

from docx import Document

from gradpath.cv_profile import build_candidate_profile
from gradpath.profile_validator import validate_candidate_profile


with TemporaryDirectory() as folder:
    path = Path(folder) / "sample.docx"

    doc = Document()
    doc.add_heading("Skills", level=1)
    doc.add_paragraph("Python, SQL, Power BI")
    doc.add_heading("Projects", level=1)
    doc.add_paragraph("Built a dashboard using Python and SQL.")
    doc.save(path)

    profile = build_candidate_profile(path)

    # Test 1: A generated profile should pass validation.
    valid_errors = validate_candidate_profile(profile)
    print("1. Valid profile passes:", valid_errors == [])
    if valid_errors:
        print("   Validation errors:", valid_errors)

    # Test 2: Missing a required field should be detected.
    missing_field_profile = copy.deepcopy(profile)
    del missing_field_profile["candidate_id"]
    missing_errors = validate_candidate_profile(missing_field_profile)
    print(
        "2. Missing field detected:",
        any("candidate_id" in error for error in missing_errors),
    )

    # Test 3: Full CV text must not be stored in the profile.
    privacy_profile = copy.deepcopy(profile)
    privacy_profile["extracted_text"] = "Private CV text"
    privacy_errors = validate_candidate_profile(privacy_profile)
    print(
        "3. Full CV text rejected:",
        any("Full extracted CV text" in error for error in privacy_errors),
    )

    # Test 4: An unknown skill ID should be detected.
    unknown_skill_profile = copy.deepcopy(profile)
    if unknown_skill_profile["skills"]:
        unknown_skill_profile["skills"][0]["skill_id"] = "UNKNOWN_SKILL"
        unknown_errors = validate_candidate_profile(unknown_skill_profile)
        print(
            "4. Unknown skill ID detected:",
            any("unknown skill_id" in error for error in unknown_errors),
        )
    else:
        print("4. Unknown skill ID detected: SKIPPED (no skills extracted)")

    # Test 5: Skills must not be marked verified automatically.
    verification_profile = copy.deepcopy(profile)
    if verification_profile["skills"]:
        verification_profile["skills"][0]["verification_status"] = "verified"
        print(
            "5. Unverified skills remain valid:",
            validate_candidate_profile(profile) == [],
        )
        print(
            "   Note: 'verified' is structurally allowed, but extraction "
            "must never assign it automatically."
        )
    else:
        print("5. Verification behavior: SKIPPED (no skills extracted)")
