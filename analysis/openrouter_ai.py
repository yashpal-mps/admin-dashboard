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

        system_prompt = (
            "You are an AI assistant generating a personalized sales email based on the detailed context provided in the user message. "
            "Your primary goal is to generate both a compelling subject line and a SHORT, CONCISE, and effective email body (under 150 words for the body)."
            "\n\n"
            "**Instructions:**\n"
            "1.  **Analyze Context:** Carefully read the entire user message to identify all key details: the sales agent's name/company, the potential customer's (lead) name/company/location, the product(s)/service(s) being offered (including features or benefits), and any campaign context.\n"

            "2.  **Create Subject Line:** Generate a compelling email subject line designed to maximize the chance of the email being opened. It should be concise and relevant to the core message, product, or benefit being offered. \n"
            "    * **Crucially: The subject line MUST NOT be a greeting.** Do NOT include 'Hi [Lead Name]', 'Hello [Lead Name]', or just the lead's name in the subject.\n"
            "    * **Examples of appropriate subject styles:** 'Boosting Productivity at [Lead Company]?', 'Quick Question about [Product Category]', 'Idea for [Lead Company]', '[Product Name] Offer', 'Unlock [Benefit] for [Lead Company]'.\n"
            "    * This subject line MUST be the very first line of your output.\n"

            "3.  **Adopt Persona (for Body):** Write the email body *as if you are* the sales agent identified in the user message. Use the first person ('I', 'me', 'my').\n"

            "4.  **Personalize (for Body):** Start the email body content (beginning on Line 3, after the blank line) with a personalized greeting addressing the lead directly by name (e.g., 'Hi [Lead Name],', 'Hello [Lead Name],'). Briefly mention their company if provided in the user message, showing you've done some research (based *only* on the provided text).\n"

            "5.  **Focus (for Body):** In the email body, highlight 1-2 key benefits of the product/service that seem most relevant based on the information available about the lead in the user message.\n"

            "6.  **Conciseness (for Body):** Keep the email body direct and under 150 words.\n"

            "7.  **Call to Action (for Body):** Include a clear, simple call-to-action in the email body (e.g., 'Are you available for a brief chat next week?', 'Would you be open to learning more?').\n"

            "8.  **Signature (for Body):** If the agent's name and email address are specified in the user message, include them at the end of the email body. Do not add placeholders if details are missing.\n"

            "9.  **Output Format:** Your entire output MUST follow this structure exactly:\n"
            "    * **Line 1:** The email subject line (created according to instruction #2 - **it must NOT be a greeting**).\n"
            "    * **Line 2:** A single blank line.\n"
            "    * **Line 3 onwards:** The complete email body, starting with the personalized greeting (e.g., 'Hi [Lead Name],'), followed by the main content, closing, and signature if applicable.\n"
            "    * Ensure there is no extra text before the subject line or after the email body."
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text}
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
