import random
from string import digits
import smtplib
import ssl
from email.message import EmailMessage
import os 


SENDER = os.getenv('SENDER_EMAIL')
PASSWORD = os.getenv('SENDER_PASSWORD')

SENDER="tandauapp@gmail.com"
PASSWORD="2003720an" 
print(SENDER)
def generate_otp(length=6):
    return ''.join(random.choices(digits, k=length))

def send_reset_password_email(email, otp):
    email_content = f'Your OTP for password reset is: {otp}'

    email_message = EmailMessage()
    email_message["From"] = SENDER
    email_message["To"] = email
    email_message["Subject"] = "Password Reset OTP"
    email_message.set_content(email_content)

    smtp_server = "smtp.gmail.com"
    smtp_port = 465

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, smtp_port, context=context) as server:
        server.login(SENDER, PASSWORD)
        server.send_message(email_message)

def reset_password_with_otp(email):
    otp = generate_otp()
    # Here you should associate this OTP with the user's email address, 
    # either by storing it in the database or using some other method.

    # For demonstration purposes, I'm printing the OTP. In production, 
    # you should send it via email.
    print("Generated OTP:", otp)

    # Sending OTP to the user's email
    send_reset_password_email(email, otp)

# Example usage:
reset_password_with_otp('user@example.com')
