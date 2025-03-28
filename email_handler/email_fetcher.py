import imaplib
import email
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
    email_user = settings.EMAIL_HOST_USER
    email_password = settings.EMAIL_HOST_PASSWORD
    email_host = settings.EMAIL_HOST

    mail = imaplib.IMAP4_SSL(email_host)

    try:
        mail.login(email_user, email_password)
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
            sender = email.utils.parseaddr(from_email)[1]

            subject = msg.get("Subject", "")

            print("Sender is -- ", sender)

            body = ""
            original_email = ""
            found_content = False  # To track if we found any readable content

            if msg.is_multipart():
                for part in msg.walk():
                    content_type = part.get_content_type()
                    content_disposition = part.get("Content-Disposition")

                    # Log for debugging
                    print(
                        f"Processing part: {content_type}, Content-Disposition: {content_disposition}")

                    # Skip attachments
                    if content_disposition and "attachment" in content_disposition:
                        continue

                    # Check if it's a readable email body
                    if content_type in ["text/plain", "text/html"]:
                        try:
                            content = part.get_payload(decode=True)
                            if content:
                                content = content.decode(
                                    errors="replace").strip()
                                print("Extracted content:", content)
                                found_content = True  # Mark that we found a valid body

                                if "On" in content and "wrote:" in content:
                                    print("Found original email in body")
                                    # Check if reply is at the end (after original email quoted with >)
                                    if content.strip().endswith(">") or ">" not in content:
                                        # Traditional format: reply at top
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
                                        # Reply might be at the bottom after quoted text
                                        lines = content.splitlines()
                                        reply_lines = []
                                        in_reply = False

                                        for line in lines:
                                            if line.startswith(">"):
                                                in_reply = True
                                            elif in_reply and line.strip() and not line.startswith("On") and "wrote:" not in line:
                                                # We found non-quoted text after quoted text - likely the reply
                                                reply_lines.append(line)

                                        if reply_lines:
                                            body = "\n".join(
                                                reply_lines).strip()
                                            print(
                                                "Extracted body (bottom reply):", body)
                                        else:
                                            # Fallback to original logic
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
                                break  # Stop after first valid text part
                        except Exception as e:
                            print("Decoding error:", e)

            else:
                try:
                    content = msg.get_payload(decode=True).decode(
                        errors="replace").strip()
                    found_content = True
                    print("Extracted content:", content)

                    if "On" in content and "wrote:" in content:
                        # Check if reply is at the end (after original email quoted with >)
                        if content.strip().endswith(">") or ">" not in content:
                            # Traditional format: reply at top
                            parts = content.split("On", 1)
                            if len(parts) > 1:
                                original_email = parts[1].strip()
                                body = parts[0].strip()
                            else:
                                body = content
                        else:
                            # Reply might be at the bottom after quoted text
                            lines = content.splitlines()
                            reply_lines = []
                            in_reply = False

                            for line in lines:
                                if line.startswith(">"):
                                    in_reply = True
                                elif in_reply and line.strip() and not line.startswith("On") and "wrote:" not in line:
                                    # We found non-quoted text after quoted text - likely the reply
                                    reply_lines.append(line)

                            if reply_lines:
                                body = "\n".join(reply_lines).strip()
                            else:
                                # Fallback to original logic
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

            try:
                lead = Lead.objects.get(email=sender)
                reference = lead
            except Lead.DoesNotExist:
                logger.warning(f"No lead found for sender {sender}")
                reference = None

            if body:
                print("Entering analyze_email")
                analyze_email(sender, body, reference, original_email)
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
def analyze_email(sender, body, reference=None, original_email=None):
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
