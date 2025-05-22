import imaplib
import email
import logging
import base64
from django.conf import settings
from celery import shared_task
from analysis.openrouter_ai import process_email
from dashboard.models import Lead
from dashboard.models import Conversation

logger = logging.getLogger(__name__)

# Register this task explicitly


@shared_task(name='email_handler.email_fetcher.fetch_unread_emails')
def fetch_unread_emails():
    """
    Fetches unread reply emails and sends them for sentiment analysis.
    Only processes emails that are replies to messages sent from our address.
    """
    email_user = settings.IMAP_USER
    email_password = settings.IMAP_PASSWORD
    email_host = settings.IMAP_HOST
    email_port = settings.IMAP_PORT

    # Debug log the credentials (remove in production)
    logger.info(f"Debug: IMAP settings:")
    logger.info(f"Debug: Host: {email_host}")
    logger.info(f"Debug: Port: {email_port}")
    logger.info(f"Debug: User: {email_user}")
    logger.info(f"Debug: Password length: {len(email_password)}")
    logger.info(
        f"Debug: Password first/last char: {email_password[0]}/{email_password[-1]}")
    logger.info(f"Debug: Password hex: {email_password.encode('utf-8').hex()}")

    logger.info(
        f"Attempting to connect to {email_host}:{email_port} with user {email_user}")
    logger.info("Using IMAP4_SSL connection")

    try:
        # Use IMAP4_SSL for secure connection
        mail = imaplib.IMAP4_SSL(email_host, email_port)
        logger.info("Connected to server")
        logger.info(f"Server capabilities: {mail.capabilities}")
        logger.info("Attempting to login...")

        # Try simple login first
        try:
            mail.login(email_user, email_password)
            logger.info("Login successful using regular login")
        except Exception as e:
            logger.error(f"Regular login failed: {str(e)}")
            raise

        mail.select("INBOX")

        status, messages = mail.search(None, "UNSEEN")

        if status != "OK":
            logger.error("Failed to search for unread emails")
            return

        email_ids = messages[0].split()

        logger.info(f"Found {len(email_ids)} unread emails")

        for email_id in email_ids:
            status, msg_data = mail.fetch(email_id, "(RFC822)")

            if status != "OK":
                logger.error(f"Failed to fetch email {email_id}")
                continue

            raw_email = msg_data[0][1]
            msg = email.message_from_bytes(raw_email)

            references = msg.get("References", "")
            in_reply_to = msg.get("In-Reply-To", "")

            if not references and not in_reply_to:
                logger.info(f"Skipping email {email_id} - not a reply")
                continue

            print("Email is a reply")

            from_email = msg.get("From", "")
            sender_name, sender_email = email.utils.parseaddr(from_email)

            subject = msg.get("Subject", "")

            print("Sender is -- ", sender_email)

            body = ""
            original_email = ""
            found_content = False

            if msg.is_multipart():
                for part in msg.walk():
                    content_type = part.get_content_type()
                    content_disposition = part.get("Content-Disposition")

                    print(
                        f"Processing part: {content_type}, Content-Disposition: {content_disposition}")

                    if content_disposition and "attachment" in content_disposition:
                        continue

                    if content_type in ["text/plain", "text/html"]:
                        try:        
                            content = part.get_payload(decode=True)
                            if content:
                                content = content.decode(
                                    errors="replace").strip()
                                print("Extracted content:", content)
                                found_content = True

                                if "On" in content and "wrote:" in content:
                                    print("Found original email in body")
                                    if content.strip().endswith(">") or ">" not in content:
                                        parts = content.split("On", 1)
                                        if len(parts) > 1:
                                            original_email = parts[1].strip()
                                            body = parts[0].strip()
                                            print(
                                                "Extracted body (top reply):", body)
                                        else:
                                            body = content
                                            print("Extracted body2:", body)
                                    else:
                                        lines = content.splitlines()
                                        reply_lines = []
                                        in_reply = False

                                        for line in lines:
                                            if line.startswith(">"):
                                                in_reply = True
                                            elif in_reply and line.strip() and not line.startswith("On") and "wrote:" not in line:
                                                reply_lines.append(line)

                                        if reply_lines:
                                            body = "\n".join(
                                                reply_lines).strip()
                                            print(
                                                "Extracted body (bottom reply):", body)
                                        else:
                                            parts = content.split("On", 1)
                                            if len(parts) > 1:
                                                original_email = parts[1].strip(
                                                )
                                                body = parts[0].strip()
                                                print(
                                                    "Extracted body (fallback):", body)
                                            else:
                                                body = content
                                                print(
                                                    "Extracted body (fallback2):", body)
                                else:
                                    body = content
                                    print("Extracted body3:", body)
                                break
                        except Exception as e:
                            print("Decoding error:", e)

            else:
                try:
                    content = msg.get_payload(decode=True).decode(
                        errors="replace").strip()
                    found_content = True
                    print("Extracted content:", content)

                    if "On" in content and "wrote:" in content:
                        if content.strip().endswith(">") or ">" not in content:
                            parts = content.split("On", 1)
                            if len(parts) > 1:
                                original_email = parts[1].strip()
                                body = parts[0].strip()
                            else:
                                body = content
                        else:
                            lines = content.splitlines()
                            reply_lines = []
                            in_reply = False

                            for line in lines:
                                if line.startswith(">"):
                                    in_reply = True
                                elif in_reply and line.strip() and not line.startswith("On") and "wrote:" not in line:
                                    reply_lines.append(line)

                            if reply_lines:
                                body = "\n".join(reply_lines).strip()
                            else:
                                parts = content.split("On", 1)
                                if len(parts) > 1:
                                    original_email = parts[1].strip()
                                    body = parts[0].strip()
                                else:
                                    body = content
                    else:
                        body = content
                except Exception as e:
                    print("Error decoding single-part email:", e)

            if not found_content:
                print("No Content-Disposition found in any part")

            print("Body is -- ", body)

            if body:
                print("Entering analyze_email")
                analyze_email(sender_email, sender_name, body, original_email)
                mail.store(email_id, "+FLAGS", "\\Seen")

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
def analyze_email(sender_email, sender_name, body, original_email=None):
    try:
        # Combine original email and reply if available
        if original_email:
            combined_text = f"Original email:\n{original_email}\n\nUser's reply:\n{body}"
        else:
            combined_text = body

        # Call the OpenRouter API for sentiment analysis with combined text
        print("entering process_email")
        category = process_email(
            task_type="analyze_response", text=combined_text)
        print("exiting process_email")
        print(category)

        logger.info(f"Categorized email from {sender_email}: {category}")

        # Get or create lead based on email
        lead, created = Lead.objects.get_or_create(
            email=sender_email,
            defaults={
                'name': sender_name,
                'type': category
            }
        )

        if not created:
            # Update existing lead's type
            lead.type = category
            lead.save()
            logger.info(
                f"Updated lead status for {sender_email} to {category}")
        else:
            logger.info(
                f"Created new lead for {sender_email} with status {category}")
            
        Conversation.objects.create(
            lead=lead,
            message=original_email or '',
            user_reply=body
        )

    except Exception as e:
        logger.error(f"Error analyzing email from {sender_email}: {str(e)}")
