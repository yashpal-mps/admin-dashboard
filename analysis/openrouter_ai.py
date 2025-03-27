import requests
from django.conf import settings
import json

OPENROUTER_API_KEY = settings.OPENROUTER_API_KEY


# def analyze_response(text):
#     url = "https://openrouter.ai/api/v1/analyze"
#     headers = {"Authorization": f"Bearer {OPENROUTER_API_KEY}"}
#     data=json.dumps({
#     "model": "deepseek/deepseek-chat-v3-0324:free",
#     "messages": [
#       {
#         "role": "user",
#         "task": "sentiment-analysis",
#         "content": text
#       }
#     ],
#   })
#     response = requests.post(url, json=data, headers=headers)

#     if response.status_code == 200:
#         return response.json().get("category", "unknown")

#     return "error"


def process_email(task_type, lead=None, text=''):

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    if task_type == "generate_email":
        system_prompt = (
            "You are an AI assistant responsible for generating professional email bodies. "
            "Your task is to craft a well-structured email that prompts the recipient to respond. "
            "Do NOT include a subject line—generate only the email body. "

            f"Address the recipient by their name: {lead.name}. "
            "The email should be engaging, clear, and persuasive, ensuring that the recipient understands the request. "

            "The email should encourage the recipient to reply with their thoughts, feedback, or confirmation. "
            "Ensure that the email is fully ready to send without requiring manual edits. "

            "Avoid placeholders, vague statements like '[mention specific feedback]', or incomplete thoughts. "
            "Use professional and natural-sounding language with proper grammar. "

            "Do NOT include: subject lines, greetings (like 'Dear Yash'), sign-offs (like 'Best regards'), or any special formatting. "
            "The output must be only the email body in plain text."
        )

        messages = [
            {"role": "system", "content": system_prompt},
        ]
        if lead.reference:
            messages.append(
                {"role": "user", "content": f"Reference : {lead.reference}"})
        messages.append({"role": "user", "content": f"Context: {text}. "})

    elif task_type == "analyze_response":
        print('text', text)
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
    print(response.json())

    if response.status_code == 200:
        try:
            return response.json()["choices"][0]["message"]["content"].strip()
        except (KeyError, IndexError):
            return "error: unexpected response format"

    return f"error: {response.status_code} {response.text}"
