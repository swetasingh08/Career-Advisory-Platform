from io import BytesIO

from docx import Document
from pypdf import PdfReader


def extract_text_from_upload(uploaded_file):
    if uploaded_file is None:
        return ""

    name = uploaded_file.name.lower()
    data = uploaded_file.getvalue()

    try:
        if name.endswith(".pdf"):
            reader = PdfReader(BytesIO(data))
            return "\n".join(page.extract_text() or "" for page in reader.pages).strip()
        if name.endswith(".docx"):
            document = Document(BytesIO(data))
            return "\n".join(paragraph.text for paragraph in document.paragraphs).strip()
        if name.endswith(".txt"):
            return data.decode("utf-8", errors="ignore").strip()
    except Exception as exc:
        raise ValueError(f"Could not read file: {exc}") from exc

    raise ValueError("Unsupported file type. Please upload PDF, DOCX, or TXT.")
