from workflows.email_workflow.services.documents.extractors.pdf_extractor import extract_pdf_text
from workflows.email_workflow.services.documents.extractors.docx_extractor import extract_docx_text
from workflows.email_workflow.services.documents.extractors.txt_extractor import extract_txt_text
from workflows.email_workflow.services.documents.utils.cleaner import clean_text


SUPPORTED_TYPES = {
    "application/pdf": extract_pdf_text,

    "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        extract_docx_text,

    "text/plain": extract_txt_text,

}


def process_document(attachment: dict) -> str:

    mime_type = attachment.get("mime_type")

    processor = SUPPORTED_TYPES.get(mime_type)

    if not processor:
        raise ValueError(f"Unsupported mime type: {mime_type}")

    raw_text = processor(attachment)

    cleaned = clean_text(raw_text)

    return cleaned