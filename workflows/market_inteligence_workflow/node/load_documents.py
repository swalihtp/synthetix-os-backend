from workflows.market_inteligence_workflow.services.document_service import load_documents, prepare_document_context


def load_documents_node(state):

    docs = load_documents(state.get("document_ids", []))

    prepared_docs = prepare_document_context(docs)

    return {"document_contents": prepared_docs}
