import imaplib
import email
from email.header import decode_header
import os
import logging
from django.conf import settings
from celery import shared_task
from analysis.openrouter_ai import process_email
from dashboard.models import Lead

logger = logging.getLogger(__name__)

# Register this task explicitly


@shared_task(name='email_handler.email_fetcher.fetch_unread_emails')
def fetch_unread_emails():
    """
    Fetches unread reply emails and sends them for sentiment analysis.
    Only processes emails that are replies to messages sent from our address.
    """
    # Email account credentials from settings
    email_user = settings.EMAIL_HOST_USER
    email_password = settings.EMAIL_HOST_PASSWORD
    email_host = settings.EMAIL_HOST

    # Connect to the IMAP server
    mail = imaplib.IMAP4_SSL(email_host)

    try:
        # Login to the email account
        mail.login(email_user, email_password)

        # Select the inbox
        mail.select("INBOX")

        # Search for unread emails
        status, messages = mail.search(None, "UNSEEN")

        if status != "OK":
            logger.error("Failed to search for unread emails")
            return

        # Get the list of email IDs
        email_ids = messages[0].split()

        logger.info(f"Found {len(email_ids)} unread emails")

        for email_id in email_ids:
            # Fetch the email
            status, msg_data = mail.fetch(email_id, "(RFC822)")

            if status != "OK":
                logger.error(f"Failed to fetch email {email_id}")
                continue

            # Parse the email
            raw_email = msg_data[0][1]
            msg = email.message_from_bytes(raw_email)

            # Check if this is a reply to our email
            references = msg.get("References", "")
            in_reply_to = msg.get("In-Reply-To", "")

            # If neither References nor In-Reply-To headers exist, skip this email
            if not references and not in_reply_to:
                logger.info(f"Skipping email {email_id} - not a reply")
                continue

            # Get sender email
            sender = msg.get("From", "").split(
                "<")[-1].strip(">") if "<" in msg.get("From", "") else msg.get("From", "")
            subject = msg.get("Subject", "")

            # Get email body
            body = ""
            original_email = ""
            if msg.is_multipart():
                for part in msg.walk():
                    content_type = part.get_content_type()
                    content_disposition = str(part.get("Content-Disposition"))

                    # Skip attachments
                    if "attachment" in content_disposition:
                        continue

                    # Get text/plain or text/html content
                    if content_type == "text/plain" or content_type == "text/html":
                        try:
                            content = part.get_payload(decode=True).decode()
                            # Check if this part contains the original email
                            if "On" in content and "wrote:" in content:
                                # Split the content to separate original email from reply
                                parts = content.split("On", 1)
                                if len(parts) > 1:
                                    original_email = parts[1].strip()
                                    body = parts[0].strip()
                                else:
                                    body = content
                            else:
                                body = content
                            break
                        except:
                            pass
            else:
                content = msg.get_payload(decode=True).decode()
                # Check if this part contains the original email
                if "On" in content and "wrote:" in content:
                    # Split the content to separate original email from reply
                    parts = content.split("On", 1)
                    if len(parts) > 1:
                        original_email = parts[1].strip()
                        body = parts[0].strip()
                    else:
                        body = content
                else:
                    body = content

            # Find lead associated with this email
            try:
                lead = Lead.objects.get(email=sender)
                reference = lead
            except Lead.DoesNotExist:
                logger.warning(f"No lead found for sender {sender}")
                reference = None

            # Send the email for sentiment analysis
            if body:
                analyze_email(sender, body, reference, original_email)

                # Mark the email as read
                mail.store(email_id, "+FLAGS", "\\Seen")

        # Close the connection
        mail.close()
        mail.logout()

    except Exception as e:
        logger.error(f"Error fetching emails: {str(e)}")
        if 'mail' in locals():
            try:
                mail.close()
                mail.logout()
            except:
                pass


@shared_task(name='email_handler.email_fetcher.analyze_email')
def analyze_email(sender, body, reference=None, original_email=None):
    try:
        # Combine original email and reply if available
        if original_email:
            combined_text = f"Original email:\n{original_email}\n\nUser's reply:\n{body}"
        else:
            combined_text = body

        # Call the OpenRouter API for sentiment analysis with combined text
        category = process_email(
            task_type="analyze_response", lead=reference, text=combined_text)

        logger.info(f"Categorized email from {sender}: {category}")

        # Update lead status based on sentiment if applicable
        if reference:
            reference.status = category
            reference.save()
            logger.info(f"Updated lead status for {sender} to {category}")

        return category

    except Exception as e:
        logger.error(f"Error analyzing email from {sender}: {str(e)}")
        return "error"
