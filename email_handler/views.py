from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from communication.email_service import EmailService
from rest_framework.views import APIView
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from celery import shared_task
from .tasks import analyze_email_response
from dashboard.models import Lead
from analysis.openrouter_ai import process_email
import logging
from campaign.models.Campaign import Campaign

logger = logging.getLogger(__name__)


# class HandleIncomingEmailView(APIView):

#     # Disable CSRF for this endpoint (can be handled differently in production)
#     @csrf_exempt
#     def post(self, request):
#         sender = request.data.get("sender")
#         body = request.data.get("body-plain", "")

#         if sender and body:
#             # Calls the task asynchronously
#             analyze_email_response.delay(sender, body)
#             return Response({"status": "received"}, status=200)

#         return Response({"error": "Invalid data"}, status=400)


def send_daily_message(lead, campaign):
    """Sends an automated email and logs the action."""
    try:
        recipient = lead.email

        # Get product and agent details from the campaign
        product = campaign.products
        agent = campaign.agent

        # Create a context dictionary with all the details
        context = {
            'lead_name': lead.name if hasattr(lead, 'name') else "Valued Customer",
            'lead_email': lead.email,
            'lead_company': lead.company_name if hasattr(lead, 'company_name') else "",

            'product_name': product.name if hasattr(product, 'name') else "",
            'product_description': product.description if hasattr(product, 'description') else "",
            'product_features': product.features if hasattr(product, 'features') else "",
            'product_pricing': product.pricing if hasattr(product, 'pricing') else "",

            'agent_name': agent.name if hasattr(agent, 'name') else "",
            'agent_role': agent.role if hasattr(agent, 'role') else "",
            'agent_contact': agent.contact if hasattr(agent, 'contact') else "",

            'campaign_name': campaign.name,
            'campaign_description': campaign.description,
        }

        # Format the prompt with all the context details
        ai_prompt = (
            "Please write a personalized sales email with the following details:\n"
            f"Lead Name: {context['lead_name']}\n"
            f"Lead Email: {context['lead_email']}\n"
            f"Lead Company: {context['lead_company']}\n\n"
            f"Product Name: {context['product_name']}\n"
            f"Product Description: {context['product_description']}\n"
            f"Product Features: {context['product_features']}\n"
            f"Product Pricing: {context['product_pricing']}\n\n"
            f"Agent Name: {context['agent_name']}\n"
            f"Agent Role: {context['agent_role']}\n"
            f"Agent Contact: {context['agent_contact']}\n\n"
            f"Campaign Name: {context['campaign_name']}\n"
            f"Campaign Description: {context['campaign_description']}"
        )

        # Pass the formatted prompt to the AI along with the lead object
        body = process_email("generate_email", ai_prompt, lead)

        if not body or body.strip() == "":
            logger.error(
                f"Email content is empty for {recipient}. Skipping email.")
            return {"status": "error", "message": "Email content is empty."}

        email = EmailService(recipient, body)
        response = email.send_message(lead)

    except Exception as e:
        logger.error(f"Error sending email to {recipient}: {str(e)}")
