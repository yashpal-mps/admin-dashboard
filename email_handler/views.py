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


def send_daily_message(lead, campaign):
    """Sends an automated email and logs the action."""
    try:
        recipient = lead.email

        products = campaign.products.all()  # Get all products as a queryset
        agent = campaign.agent

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

        product_info = ""
        for i, product in enumerate(products, 1):
            product_info += f"Product {i} Name: {product.name if hasattr(product, 'name') else ''}\n"
            product_info += f"Product {i} Description: {product.description if hasattr(product, 'description') else ''}\n"
            product_info += f"Product {i} Price: ${product.price if hasattr(product, 'price') else ''}\n"
            product_info += f"Product {i} Category: {product.category if hasattr(product, 'category') else ''}\n"
            product_info += f"Product {i} Type: {product.type if hasattr(product, 'type') else ''}\n\n"

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

        body = process_email("generate_email", ai_prompt, agent, lead)

        if body and isinstance(body, str):
            body = body.strip()
            parts = body.split('\n', 1)

        if len(parts) > 0:
            subject = parts[0].strip()

        if len(parts) > 1:
            email_content = parts[1].lstrip('\n')
            email_content = email_content.strip()

        elif len(parts) == 1:
            subject = parts[0].strip()
            email_content = ""
        else:
            print("Warning: Received empty or invalid body content.")
            subject = ""
            email_content = ""

        print(f"Extracted Subject: '{subject}'")
        print("---")
        print(f"Extracted Email Content:\n{email_content}")
        print("---")

        email = EmailService(recipient, subject, email_content)
        response = email.send_message()

    except Exception as e:
        logger.error(f"Error sending email to {recipient}: {str(e)}")
