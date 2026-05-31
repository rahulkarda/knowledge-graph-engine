import io
from typing import Tuple


class FileProcessor:
    def extract(self, filename: str, content_bytes: bytes) -> Tuple[str, str]:
        ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else "txt"
        title = filename.rsplit(".", 1)[0].replace("_", " ").replace("-", " ").title()

        if ext == "pdf":
            return title, self._extract_pdf(content_bytes)
        elif ext == "docx":
            return title, self._extract_docx(content_bytes)
        else:
            return title, content_bytes.decode("utf-8", errors="replace")

    def _extract_pdf(self, content_bytes: bytes) -> str:
        import fitz  # PyMuPDF
        doc = fitz.open(stream=content_bytes, filetype="pdf")
        pages = []
        for page in doc:
            pages.append(page.get_text())
        doc.close()
        return "\n".join(pages)

    def _extract_docx(self, content_bytes: bytes) -> str:
        from docx import Document
        doc = Document(io.BytesIO(content_bytes))
        return "\n".join(p.text for p in doc.paragraphs if p.text.strip())
