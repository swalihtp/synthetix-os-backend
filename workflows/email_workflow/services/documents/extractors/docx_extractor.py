from docx import Document
import tempfile


def extract_docx_text(attachment):

    file_bytes = attachment["data"]

    full_text = []

    with tempfile.NamedTemporaryFile(
        suffix=".docx"
    ) as temp_file:

        temp_file.write(file_bytes)
        temp_file.flush()

        doc = Document(temp_file.name)

        for para in doc.paragraphs:
            full_text.append(para.text)

    return "\n".join(full_text)