from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .tasks import analyze_email_response

@csrf_exempt
def handle_incoming_email(request):
    """Receives email responses via Mailgun webhook."""
    sender = request.POST.get("sender")
    body = request.POST.get("body-plain", "")

    if sender and body:
        analyze_email_response.delay(sender, body) 
        return JsonResponse({"status": "received"}, status=200)

    return JsonResponse({"error": "Invalid data"}, status=400)
