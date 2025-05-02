import os
from dotenv import load_dotenv

load_dotenv()


def test_password_encoding():
    password = os.getenv('IMAP_PASSWORD', 'dxc3V]TgXY$v')
    print("Password:", password)
    print("Password bytes:", password.encode('utf-8'))
    print("Password hex:", ' '.join(hex(b)[2:]
          for b in password.encode('utf-8')))

    # Test with escaped special characters
    escaped_password = password.replace('[', '\\[').replace(']', '\\]')
    print("\nEscaped password:", escaped_password)
    print("Escaped password bytes:", escaped_password.encode('utf-8'))
    print("Escaped password hex:", ' '.join(
        hex(b)[2:] for b in escaped_password.encode('utf-8')))


if __name__ == "__main__":
    test_password_encoding()
