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

        # Get products and agent details from the campaign
        products = campaign.products.all()  # Get all products as a queryset
        agent = campaign.agent

        # Create a context dictionary with all the details
        context = {
            'lead_name': lead.name if hasattr(lead, 'name') else "Valued Customer",
            'lead_email': lead.email,
            'lead_company': lead.company_name if hasattr(lead, 'company_name') else "",
            'lead_city': lead.city if hasattr(lead, 'city') else "",
            'lead_state': lead.state if hasattr(lead, 'state') else "",
            'lead_country': lead.country if hasattr(lead, 'country') else "",

            'agent_name': agent.name if hasattr(agent, 'name') else "",
            'agent_email': agent.email if hasattr(agent, 'email') else "",
            'agent_company': agent.company if hasattr(agent, 'company') else "",

            'campaign_name': campaign.name,
            'campaign_description': campaign.description,
        }

        # Format product information for multiple products
        product_info = ""
        for i, product in enumerate(products, 1):
            product_info += f"Product {i} Name: {product.name if hasattr(product, 'name') else ''}\n"
            product_info += f"Product {i} Description: {product.description if hasattr(product, 'description') else ''}\n"
            product_info += f"Product {i} Price: ${product.price if hasattr(product, 'price') else ''}\n"
            product_info += f"Product {i} Category: {product.category if hasattr(product, 'category') else ''}\n"
            product_info += f"Product {i} Type: {product.type if hasattr(product, 'type') else ''}\n\n"

        # Format the prompt with all the context details
        ai_prompt = (
            "Please write a personalized sales email with the following details:\n"
            f"Lead Name: {context['lead_name']}\n"
            f"Lead Email: {context['lead_email']}\n"
            f"Lead Company: {context['lead_company']}\n"
            f"Lead Location: {context['lead_city']}, {context['lead_state']}, {context['lead_country']}\n\n"
            f"{product_info}"
            f"Agent Name: {context['agent_name']}\n"
            f"Agent Email: {context['agent_email']}\n"
            f"Agent Company: {context['agent_company']}\n\n"
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
