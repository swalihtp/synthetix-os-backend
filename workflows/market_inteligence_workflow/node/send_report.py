# from workflows.market_inteligence_workflow.state import MarketState
# from django.core.mail import EmailMultiAlternatives
# from django.conf import settings
# from accounts.models import User


# def send_report_node(state: MarketState) -> MarketState:
#     execution=state['execution_instance']
#     try:

#         user = User.objects.get(id=state["user_id"])

#         presigned_url = state.get("s3_presigned_url")

#         if not presigned_url:
#             return {
#                 "errors": [*(state.get("errors") or []), "Presigned URL not found."]
#             }

#         subject = "Your Market Intelligence Report is Ready"

#         text_content = f"""
#             Hello {user.username},

#             Your AI-generated market intelligence report is ready.

#             Download Report:
#             {presigned_url}

#             Important:
#             - This secure download link will expire in 24 hours.

#             Regards,
#             Synthetix OS
#         """

#         html_content = f"""
#             <html>
#             <body>

#                 <h2>Market Intelligence Report Ready</h2>

#                 <p>Hello {user.username},</p>

#                 <p>
#                     Your AI-generated market intelligence report has been completed successfully.
#                 </p>

#                 <p>
#                     Click the button below to download your report:
#                 </p>

#                 <a href="{presigned_url}"
#                 style="
#                         display:inline-block;
#                         padding:12px 20px;
#                         background-color:#111827;
#                         color:white;
#                         text-decoration:none;
#                         border-radius:8px;
#                         font-weight:600;
#                 ">
#                 Download Report
#                 </a>

#                 <p style="margin-top:20px;">
#                     This secure link will expire in <strong>24 hours</strong>.
#                 </p>

#                 <br>

#                 <p>
#                     Regards,<br>
#                     Synthetix OS
#                 </p>

#             </body>
#             </html>
#             """

#         email = EmailMultiAlternatives(
#             subject=subject,
#             body=text_content,
#             from_email=settings.DEFAULT_FROM_EMAIL,
#             to=[user.email],
#         )

#         email.attach_alternative(html_content, "text/html")

#         email.send(fail_silently=False)
        
#         execution.status = "completed"
#         execution.save(update_fields=["status"])

#         return {"email_sent": True}

#     except User.DoesNotExist:
#         return {"errors": [*(state.get("errors") or []), "User not found."]}

#     except Exception as e:
#         return {
#             "errors": [*(state.get("errors") or []), f"Email sending failed: {str(e)}"]
#         }

