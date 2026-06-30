# import os
# import uuid
# import boto3
# from botocore.exceptions import ClientError
# from django.conf import settings
# from workflows.market_inteligence_workflow.state import MarketState
# from agent.models import Agent, S3MarketIntelligenceReport
# from accounts.models import User

# def upload_to_s3_node(state: MarketState) -> MarketState:

#     execution=state['execution_instance']
#     if execution.s3_url:
#         return {'s3_url':execution.s3_url}
#     report_path = state.get("report_path")

#     if not report_path:
#         return {
#             "errors": [
#                 *(state.get("errors") or []),
#                 "Report path not found."
#             ]
#         }

#     if not os.path.exists(report_path):
#         return {
#             "errors": [
#                 *(state.get("errors") or []),
#                 f"PDF file does not exist: {report_path}"
#             ]
#         }

#     try:

#         s3_client = boto3.client(
#             "s3",
#             aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
#             aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
#             region_name=settings.AWS_S3_REGION_NAME,
#         )

#         file_name = os.path.basename(report_path)

#         s3_key = (
#             f"market-reports/"
#             f"user-{state.get('user_id')}/"
#             f"{uuid.uuid4()}-{file_name}"
#         )

#         s3_client.upload_file(
#             report_path,
#             settings.AWS_STORAGE_BUCKET_NAME,
#             s3_key,
#             ExtraArgs={
#                 "ContentType": "application/pdf"
#             }
#         )
        
#         os.remove(report_path)

#         s3_url = (
#             f"https://{settings.AWS_STORAGE_BUCKET_NAME}.s3."
#             f"{settings.AWS_S3_REGION_NAME}.amazonaws.com/{s3_key}"
#         )
        
#         user = User.objects.get(id=str(state['user_id']))
#         agent = Agent.objects.get(user=user,name__iexact="Market Intelligence Agent")
        
        
#         presigned_url = s3_client.generate_presigned_url(
#             "get_object",
#             Params={
#                 "Bucket": settings.AWS_STORAGE_BUCKET_NAME,
#                 "Key": s3_key
#             },
#             ExpiresIn=3600
#         )

#         report = S3MarketIntelligenceReport.objects.create(
#             agent=agent,
#             s3_key=s3_key,
#             s3_url=s3_url,
#         )
#         execution.s3_url=s3_url
#         execution.save()
        

#         return {
#             "s3_key": s3_key,
#             "s3_url": s3_url,
#             "report_id": report.id,
#             "s3_presigned_url": presigned_url
#         }

#     except Agent.DoesNotExist as e:
#         execution.status = "failed"
#         execution.error_message = str(e)
#         return {
            
#             "errors": [
#                 *(state.get("errors") or []),
#                 "Agent not found."
#             ]
#         }

#     except ClientError as e:
#         execution.status = "failed"
#         execution.error_message = str(e)
#         return {
#             "errors": [
#                 *(state.get("errors") or []),
#                 f"S3 upload failed: {str(e)}"
#             ]
#         }

#     except Exception as e:
#         execution.status = "failed"
#         execution.error_message = str(e)
#         return {
#             "errors": [
#                 *(state.get("errors") or []),
#                 f"Unexpected upload error: {str(e)}"
#             ]
#         }