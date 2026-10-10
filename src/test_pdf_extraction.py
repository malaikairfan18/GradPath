from pathlib import Path
from tempfile import TemporaryDirectory

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from gradpath.cv_reader import read_cv


def main():
    with TemporaryDirectory() as temp_dir:
        pdf_path = Path(temp_dir) / "sample_cv.pdf"

        pdf = canvas.Canvas(str(pdf_path), pagesize=letter)
        pdf.drawString(72, 750, "Alex Example")
        pdf.drawString(72, 725, "Education: BS Data Science")
        pdf.drawString(72, 700, "Skills: Python, SQL, and Power BI")
        pdf.drawString(
            72, 675,
            "Projects: Built a sales analytics dashboard."
        )
        pdf.save()

        result = read_cv(pdf_path)
        text = result["extracted_text"]

        print("PDF status:", result["extraction_status"])
        print("PDF contains Python:", "Python" in text)
        print("PDF contains education:", "Education" in text)
        print("PDF character count:", result["text_char_count"])
        print("PDF warnings:", result["extraction_warnings"])


if __name__ == "__main__":
    main()
