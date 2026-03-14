import smtplib
from email.message import EmailMessage
import os
from utils.logger_config import get_logger

logger = get_logger(__name__)

def send_email_with_video(sender_email, sender_password, recipient_email, subject, body, video_path):
    """
    Sends an email with the generated video attached.
    """
    # Create the email
    msg = EmailMessage()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = subject
    msg.set_content(body)

    # Attach the video
    with open(video_path, 'rb') as f:
        video_data = f.read()
        video_name = os.path.basename(video_path)
        msg.add_attachment(video_data, maintype='video', subtype='mp4', filename=video_name)

    # Send the email via SMTP
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:  # Use your SMTP server and port
            smtp.login(sender_email, sender_password)
            smtp.send_message(msg)
        logger.info(f"Email sent successfully to {recipient_email}")
    except Exception as e:
        logger.error(f"Error sending email: {e}")

