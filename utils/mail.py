from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
from app.models import sender_mail, send_mail
import smtplib
import os

def SendAnEmail(body: str, email=None, attachments=None):
    """
    Sends an email with the provided body, recipients, and attachments.

    Parameters:
        body (str): The email content.
        email (list): List of recipient email addresses. If None, fetches all from `send_mail` table.
        attachments (list): List of file paths to attach to the email.
    """
    email = email or []
    attachments = attachments or []

    # Fetch the sender email configuration from the database
    obj = sender_mail.objects.filter(email="rikenkhadela777@gmail.com").first()
    if not obj:
        print("Sender email information not found in the database.")
        return

    sender_email = obj.email
    sender_password = obj.sender_password
    subject = obj.subject

    # If email list is empty, populate it with recipients from the database
    if not email:
        email = [recipient.email for recipient in send_mail.objects.all()]

    if not email:
        print("No recipients found.")
        return

    msg = f"""Hello, this is an email from Webscrapping server!\nAn error we got : {body}\nThanks."""
            
    for recipient_email in email:
        print(f"Sending email to: {recipient_email}")

        # Construct the email message
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = recipient_email
        message["Subject"] = subject

        # Attach the email body
        message.attach(MIMEText(msg, "plain"))

        # Attach any provided files
        for attachment in attachments:
            if os.path.exists(attachment):
                with open(attachment, "rb") as f:
                    attachment_data = MIMEImage(f.read())
                    attachment_data.add_header(
                        "Content-Disposition", "attachment", filename=os.path.basename(attachment)
                    )
                    message.attach(attachment_data)
            else:
                print(f"Attachment file not found: {attachment}")

        # Send the email
        try:
            with smtplib.SMTP_SSL(obj.server, obj.port) as server:
                server.login(sender_email, sender_password)
                server.sendmail(sender_email, recipient_email, message.as_string())
            print(f"Email sent successfully to {recipient_email}!")
        except Exception as e:
            print(f"Error sending email to {recipient_email}: {e}")