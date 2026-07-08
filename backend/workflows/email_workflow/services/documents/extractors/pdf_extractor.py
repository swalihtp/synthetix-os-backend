import fitz
import tempfile


def extract_pdf_text(attachment):

    file_bytes = attachment["data"]

    text = ""

    with tempfile.NamedTemporaryFile(
        suffix=".pdf"
    ) as temp_file:

        temp_file.write(file_bytes)
        temp_file.flush()

        pdf = fitz.open(temp_file.name)

        for page in pdf:
            text += page.get_text()

    return text