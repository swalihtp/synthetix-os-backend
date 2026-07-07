from pathlib import Path
from docx import Document
import pypdf
from langchain_text_splitters import RecursiveCharacterTextSplitter
from workflows.market_inteligence_workflow.services.ai_client import ai_client


def load_documents(document_paths):

    contents = []

    for path in document_paths:

        path = Path(path)

        suffix = path.suffix.lower()

        if suffix == ".pdf":
            text = extract_text_from_pdf(path)

        elif suffix == ".docx":
            text = extract_text_from_docx(path)

        elif suffix == ".txt":
            text = extract_text_from_txt(path)

        else:
            continue

        contents.append({"file_name": path.name, "content": text})

    return contents


def extract_text_from_pdf(file_path):

    text = []

    with open(file_path, "rb") as file:

        reader = pypdf.PdfReader(file)

        for page in reader.pages:

            page_text = page.extract_text()

            if page_text:
                text.append(page_text)

    return "\n".join(text)


def extract_text_from_docx(file_path):

    doc = Document(file_path)

    paragraphs = []

    for paragraph in doc.paragraphs:

        paragraphs.append(paragraph.text)

    return "\n".join(paragraphs)


def extract_text_from_txt(file_path):

    with open(file_path, "r", encoding="utf-8") as file:

        return file.read()


def chunk_document(text, chunk_size=3000, chunk_overlap=300):

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=chunk_overlap
    )

    return splitter.split_text(text)


def prepare_document_context(documents):

    context = []

    for document in documents:

        content = document["content"]
  
        if len(content) > 20000:

            content = summarize_large_document(content)

        context.append({"file_name": document["file_name"], "content": content})

    return context


DOCUMENT_SUMMARY_PROMPT = """
Summarize the following document.

Focus on:

- company overview
- products
- services
- customers
- strengths
- market position

Document:

{document}
"""


def summarize_large_document(text):

    chunks = chunk_document(text)

    summaries = []

    for chunk in chunks:

        summary = ai_client.generate_text(
            prompt_template=DOCUMENT_SUMMARY_PROMPT, payload={"document": chunk}
        )

        summaries.append(summary)

    return "\n".join(summaries)
