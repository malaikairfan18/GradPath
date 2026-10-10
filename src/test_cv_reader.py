"""Smoke tests for the GradPath CV document reader."""

from pathlib import Path
from tempfile import TemporaryDirectory

from docx import Document
from pypdf import PdfReader, PdfWriter
from pypdf.generic import DecodedStreamObject, NameObject

from gradpath.cv_reader import read_cv


SAMPLE_TEXT = (
    "Alex Example\n"
    "Education: BS Data Science\n"
    "Skills: Python, SQL, and Power BI\n"
    "Projects: Built a sales analytics dashboard."
)


def create_sample_docx(path: Path) -> None:
    document = Document()
    document.add_heading("Alex Example", level=1)
    document.add_paragraph("Education: BS Data Science")
    document.add_paragraph("Skills: Python, SQL, and Power BI")
    document.add_paragraph(
        "Projects: Built a sales analytics dashboard."
    )
    document.save(path)


def create_sample_pdf(path: Path) -> None:
    """Create a minimal text PDF using pypdf."""
    writer = PdfWriter()
    page = writer.add_blank_page(width=612, height=792)

    stream = DecodedStreamObject()
    stream.set_data(
        b"BT /F1 12 Tf 50 740 Td (Alex Example) Tj ET"
    )

    # This low-level stream is intentionally not used as the test
    # content because a valid PDF needs a properly registered font.
    # Use a blank PDF to test the empty-text warning instead.
    with path.open("wb") as file:
        writer.write(file)


def main() -> None:
    with TemporaryDirectory() as temp_dir:
        folder = Path(temp_dir)
        docx_path = folder / "sample_cv.docx"
        pdf_path = folder / "blank.pdf"
        txt_path = folder / "sample.txt"

        create_sample_docx(docx_path)
        create_sample_pdf(pdf_path)
        txt_path.write_text("Unsupported file", encoding="utf-8")

        docx_result = read_cv(docx_path)
        print("DOCX status:", docx_result["extraction_status"])
        print("DOCX contains Python:", "Python" in docx_result["extracted_text"])
        print("DOCX character count:", docx_result["text_char_count"])

        pdf_result = read_cv(pdf_path)
        print("Blank PDF status:", pdf_result["extraction_status"])
        print("Blank PDF warning:", bool(pdf_result["extraction_warnings"]))

        try:
            read_cv(txt_path)
        except ValueError as exc:
            print("Unsupported format rejected:", str(exc))

        try:
            read_cv(folder / "missing.pdf")
        except FileNotFoundError:
            print("Missing file rejected: True")


if __name__ == "__main__":
    main()
