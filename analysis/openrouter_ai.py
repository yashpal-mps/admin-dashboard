import requests
from django.conf import settings
import json

OPENROUTER_API_KEY = settings.OPENROUTER_API_KEY


def process_email(task_type, text, lead=None):

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    if task_type == "generate_email":
        # Extract lead information if lead object is provided
        lead_info = ""
        if lead:
            lead_info = (
                f"Lead Name: {lead.name}\n"
                f"Company: {lead.company_name}\n"
                f"City: {lead.city}\n"
                f"State: {lead.state}\n"
                f"Country: {lead.country}\n"
            )
            if hasattr(lead, 'reference') and lead.reference:
                lead_info += f"Reference/Notes: {lead.reference}\n"

        # Extract agent details from text
        agent_name = "Sales Representative"
        agent_role = "Sales Agent"
        agent_contact = ""

        # Try to extract agent details from the text
        for line in text.split('\n'):
            if "Agent Name:" in line:
                agent_name = line.split(':', 1)[1].strip()
            elif "Agent Role:" in line:
                agent_role = line.split(':', 1)[1].strip()
            elif "Agent Contact:" in line:
                agent_contact = line.split(':', 1)[1].strip()

        system_prompt = (
            f"You are {agent_name}, a {agent_role}. "
            "You are writing an email to a potential customer. "
            "Write this email as if you ARE the agent, not an AI writing on behalf of the agent. "
            "Use first person ('I', 'me', 'my') throughout the email. "
            "You will receive details about the lead, product, and yourself (as the agent) in your instructions. "

            "Craft a personalized, well-structured email that highlights how the product can solve problems for the lead. "
            "Your email should be professional, persuasive, and encourage a response from the recipient. "
            "Include specific product details and features that would be most relevant to the lead. "
            "Position yourself as a helpful resource rather than just selling a product. "

            "The email should be engaging, clear, and persuasive, ensuring that the recipient understands the value proposition. "
            "Include a clear call-to-action that encourages the recipient to reply with their thoughts, questions, or to schedule a meeting. "

            f"Address the recipient by their name: {lead.name if lead else 'Valued Customer'}. "
            "Personalize the email by referencing their company and any other relevant information provided. "

            "End the email with your name and contact information if available. "

            "Ensure that the email is fully ready to send without requiring manual edits. "
            "Avoid placeholders, vague statements, or incomplete thoughts. "
            "Use professional and natural-sounding language with proper grammar. "

            "Do NOT include: subject lines, generic greetings, or any special formatting. "
            "The output must be only the email body in plain text."
        )

        # Combine lead info with the campaign/product/agent details in text
        complete_prompt = f"{lead_info}\n\n{text}" if lead_info else text

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": complete_prompt}
        ]

    elif task_type == "analyze_response":
        print("entering analyze_response")
        system_prompt = "Analyze the sentiment of the given email response and classify it strictly " \
            "as one of the following: 'hot', 'warm', 'won', 'cold', or 'lost'. Respond with only one word—no additional text, " \
            "explanations, or formatting. Your output must be exactly one of these five words."
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text}
        ]

    else:
        return "error: invalid task type"

    data = {
        "model": "google/gemma-3-4b-it:free",
        "messages": messages
    }

    response = requests.post(url, json=data, headers=headers)

    if response.status_code == 200:
        try:
            print("entering try")
            return response.json()["choices"][0]["message"]["content"].strip()
        except (KeyError, IndexError):
            print("KeyError or IndexError")
            return "error: unexpected response format"

    return f"error: {response.status_code} {response.text}"
