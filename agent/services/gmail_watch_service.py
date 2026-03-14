# # services/gmail_watch_service.py

# from googleapiclient.discovery import build


# def start_gmail_watch(access_token):

#     service = build(
#         "gmail",
#         "v1",
#         credentials=access_token
#     )

#     request = {
#         "labelIds": ["INBOX"],
#         "topicName": "projects/YOUR_PROJECT/topics/gmail-email-events",
#     }

#     response = service.users().watch(
#         userId="me",
#         body=request
#     ).execute()

#     return response