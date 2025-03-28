from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from communication.email_service import EmailService
from rest_framework.views import APIView
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from celery import shared_task
# from celery.schedules import crontab
# from celery.task import periodic_task
from .tasks import analyze_email_response
from dashboard.models import Lead
from analysis.openrouter_ai import process_email
import logging
logger = logging.getLogger(__name__)


@shared_task
def post_to_leads():

      leads = Lead.objects.all()
      if not leads.exists():
            logger.info("No leads found in the database.")
            return

      for lead in leads:
        send_daily_message(lead)


class HandleIncomingEmailView(APIView):
    
    @csrf_exempt  # Disable CSRF for this endpoint (can be handled differently in production)
    def post(self, request):
        sender = request.data.get("sender")
        body = request.data.get("body-plain", "")
        
        if sender and body:
            analyze_email_response.delay(sender, body)  # Calls the task asynchronously
            return Response({"status": "received"}, status=200)

        return Response({"error": "Invalid data"}, status=400)

# def get_all_leads():
#     # Replace this with your actual logic to fetch leads
#     return [{"id": 1, "email": "yash011033@gmail.com"}, {"id": 2, "email": "yashpal@pariqsha.com"}]

@method_decorator(csrf_exempt, name='dispatch')
class EmailHandler(View):
    """Handles sending and receiving emails with Mailgun."""
    
    def post(self, request):
        """Receives email responses via Mailgun webhook."""
        try:
            sender = request.POST.get("sender")
            body = request.POST.get("body-plain", "")

            if not sender or not body:
                return JsonResponse({"error": "Invalid data"}, status=400)

            analyze_email_response.delay(sender, body)
            return JsonResponse({"status": "received"}, status=200)

        except Exception as e:
            return JsonResponse({"error": f"Internal Server Error: {str(e)}"}, status=500)

    


def send_daily_message(lead):
    """Sends an automated email and logs the action."""
    try:
        recipient = lead.email
        body = process_email("generate_email", lead) 
        logger.info(f"Sending email to {recipient}")
        if not body or body.strip() == "":
            logger.error(f"Email content is empty for {recipient}. Skipping email.")
            return {"status": "error", "message": "Email content is empty."}
        
        logger.info(f"Email content: {body}")
        email = EmailService(recipient, body)
        response = email.send_message(lead)
        logger.info(f"Response: {response}")

    except Exception as e:
        logger.error(f"Error sending email to {recipient}: {str(e)}")