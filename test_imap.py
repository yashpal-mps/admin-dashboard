import imaplib
import os
from dotenv import load_dotenv

load_dotenv()


def test_imap_connection():
    # Get credentials from environment
    email_host = os.getenv('IMAP_HOST')
    email_port = int(os.getenv('IMAP_PORT'))
    email_user = os.getenv('IMAP_USER')
    email_password = os.getenv('IMAP_PASSWORD')

    print(f"Testing IMAP connection to {email_host}:{email_port}")
    print(f"Using username: {email_user}")

    try:
        # Connect to the server
        mail = imaplib.IMAP4_SSL(email_host, email_port)
        print("Connected to server")
        print(f"Server capabilities: {mail.capabilities}")

        # Try to login
        print("Attempting to login...")
        mail.login(email_user, email_password)
        print("Login successful!")

        # List available mailboxes
        print("\nAvailable mailboxes:")
        status, mailboxes = mail.list()
        if status == 'OK':
            for mailbox in mailboxes:
                print(mailbox.decode())

        # Logout
        mail.logout()
        print("\nConnection closed successfully")

    except Exception as e:
        print(f"\nError: {str(e)}")
        if 'mail' in locals():
            try:
                mail.logout()
            except:
                pass


if __name__ == "__main__":
    test_imap_connection()
