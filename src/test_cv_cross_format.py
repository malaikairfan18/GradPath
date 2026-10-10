"""Compare GradPath profile generation for equivalent PDF and DOCX CVs."""

from pathlib import Path
from tempfile import TemporaryDirectory

from docx import Document
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from gradpath.cv_profile import build_candidate_profile
from gradpath.profile_validator import validate_candidate_profile


CV_TEXT = [
    ("Technical Skills", "Python, SQL, Power BI"),
    ("Education", "BS Data Science, Example University"),
    ("Projects", "Built a dashboard using Python and SQL."),
]


def create_docx(path):
    doc = Document()
    for heading, content in CV_TEXT:
        doc.add_heading(heading, level=1)
        doc.add_paragraph(content)
    doc.save(path)


def create_pdf(path):
    pdf = canvas.Canvas(str(path), pagesize=letter)
    y = 750

    for heading, content in CV_TEXT:
        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawString(60, y, heading)
        y -= 22
        pdf.setFont("Helvetica", 10)
        pdf.drawString(60, y, content)
        y -= 35

    pdf.save()


with TemporaryDirectory() as folder:
    folder = Path(folder)
    docx_path = folder / "sample.docx"
    pdf_path = folder / "sample.pdf"

    create_docx(docx_path)
    create_pdf(pdf_path)

    docx_profile = build_candidate_profile(docx_path)
    pdf_profile = build_candidate_profile(pdf_path)

    docx_skills = {skill["skill_name"] for skill in docx_profile["skills"]}
    pdf_skills = {skill["skill_name"] for skill in pdf_profile["skills"]}

    print("DOCX extraction status:", docx_profile["source_document"]["extraction_status"])
    print("PDF extraction status:", pdf_profile["source_document"]["extraction_status"])
    print("DOCX skills:", sorted(docx_skills))
    print("PDF skills:", sorted(pdf_skills))
    print("Same normalized skills:", docx_skills == pdf_skills)
    print(
        "DOCX profile validation:",
        validate_candidate_profile(docx_profile) == [],
    )
    print(
        "PDF profile validation:",
        validate_candidate_profile(pdf_profile) == [],
    )
    print(
        "Both profiles exclude raw text:",
        "extracted_text" not in docx_profile
        and "extracted_text" not in pdf_profile,
    )
    print(
        "Both profiles keep skills unverified:",
        all(
            skill["verification_status"] == "unverified"
            for profile in (docx_profile, pdf_profile)
            for skill in profile["skills"]
        ),
    )
