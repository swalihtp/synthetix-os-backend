import requests
import os
from dotenv import load_dotenv

load_dotenv()


def analyze_intent(subject, body, intentions):



    payload = {
        "subject": subject,
        "email_body": body,
        "intentions": intentions,
    }

    try:
        print("BEFPRE REQUEST")

        response = requests.post(
            f'{os.getenv("AI_SERVICE_URL")}/api/analyze-intention',
            json=payload,
            timeout=120,
        )

        response.raise_for_status()

        print("AFTER REQUEST")

        return response.json()

    except requests.Timeout:
        raise Exception("AI service timeout")

    except requests.RequestException as e:
        raise Exception(f"AI service error: {str(e)}")


def ai_service(raw_email, extracted_docs, user, message_id_of_email, user_context):
    payload = {
        "raw_email": raw_email,
        "user_id": user,
        "extracted_documents": extracted_docs,
        "message_id": message_id_of_email,
        "user_context": user_context,
    }
    print(
        f"RAW EMAIL:{raw_email} EXTRACTED DOCUMENT: {extracted_docs} USER CONTEXT: {user_context}"
    )
    res = requests.post(
        f"{os.getenv("AI_SERVICE_URL")}/api/process-email", json=payload
    )

    return res.json()


def store_document_in_croma_db(
    raw_email: dict, reply_subject: str, reply_text: str, user_id: str
):
    payload = {
        "raw_email": raw_email,
        "user_id": user_id,
        "reply_subject": reply_subject,
        "reply_text": reply_text,
    }

    res = requests.post(f"{os.getenv("AI_SERVICE_URL")}/api/store-doc", json=payload)

    return res.json()


