from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from communication.email_service import EmailService
from rest_framework.views import APIView
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from celery import shared_task
from celery.schedules import crontab
from celery.task import periodic_task
from .tasks import analyze_email_response
from dashboard.models import Lead

@shared_task
def post_to_leads():
 
    leads = Lead.objects.all()  # Replace with your logic to retrieve leads
    for lead in leads:
        send_daily_message(lead)  # Replace with your logic to send messages

# Periodic task to schedule at 9 AM every day
@periodic_task(run_every=crontab(hour=9, minute=0))
def scheduled_post_to_leads():
    post_to_leads.delay()

class HandleIncomingEmailView(APIView):
    
    @csrf_exempt  # Disable CSRF for this endpoint (can be handled differently in production)
    def post(self, request):
        sender = request.data.get("sender")
        body = request.data.get("body-plain", "")
        
        if sender and body:
            analyze_email_response.delay(sender, body)  # Calls the task asynchronously
            return Response({"status": "received"}, status=200)

        return Response({"error": "Invalid data"}, status=400)

def get_all_leads():
    # Replace this with your actual logic to fetch leads
    return [{"id": 1, "email": "yash011033@gmail.com"}, {"id": 2, "email": "yashpal@pariqsha.com"}]

def send_daily_message(lead):
    # Replace this with your actual logic to post messages
    print(f"Sending message to {lead['email']}")
    

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

    
class SendEmailView(View):
    """Handles sending emails using Mailgun."""
    
    def post(self, request):
        """Sends an email when accessed via GET request."""
        try:
            recipient = "yashpal@pariqsha.com"
            body = "This is an automated email sent by Mailgun."
            
            email = EmailService(recipient, body)
            response = email.send_message()
            
            return JsonResponse({"message": "Email sent successfully", "response": response}, status=200)

        except Exception as e:
            return JsonResponse({"error": f"Failed to send email: {str(e)}"}, status=500)
