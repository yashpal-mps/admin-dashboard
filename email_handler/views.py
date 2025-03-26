from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .tasks import analyze_email_response
from communication.email_service import EmailService

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
