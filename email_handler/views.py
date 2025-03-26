# from rest_framework.views import APIView
# from rest_framework.response import Response
# from django.views.decorators.csrf import csrf_exempt

# class HandleIncomingEmailView(APIView):
    
#     @csrf_exempt  # Disable CSRF for this endpoint (can be handled differently in production)
#     def post(self, request):
#         sender = request.data.get("sender")
#         body = request.data.get("body-plain", "")
        
#         if sender and body:
#             analyze_email_response.delay(sender, body)  # Calls the task asynchronously
#             return Response({"status": "received"}, status=200)

#         return Response({"error": "Invalid data"}, status=400)


from rest_framework.views import APIView
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from celery import shared_task
from celery.schedules import crontab
from celery.task import periodic_task
from .tasks import analyze_email_response
from dashboard.models import Lead

# Define your asynchronous task
@shared_task
def post_to_leads():
    # Logic to post to all leads
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

# Helper methods
def get_all_leads():
    # Replace this with your actual logic to fetch leads
    return [{"id": 1, "email": "yash011033@gmail.com"}, {"id": 2, "email": "yashpal@pariqsha.com"}]

def send_daily_message(lead):
    # Replace this with your actual logic to post messages
    print(f"Sending message to {lead['email']}")