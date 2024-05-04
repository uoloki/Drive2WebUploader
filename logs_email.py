"""
This script sends the logs to the email and saves the logs for itself in the
current directory
"""

import smtplib
import logging
import json

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from pathlib import Path


# Set up logging configuration
logging.basicConfig(filename='email_subprocess.log', level=logging.DEBUG,
                    format='%(asctime)s:%(levelname)s:%(message)s')

def read_config(config_filename):
    """Reads JSON configuration file."""
    with open(config_filename, "r") as config_file:
        return json.load(config_file)

def create_email(sender, recipients, subject, body_text):
    """Creates and returns an email message object, handling multiple recipients."""
    msg = MIMEMultipart()
    msg['From'] = sender
    msg['To'] = ", ".join(recipients)  # Convert list of recipients to a comma-separated string
    msg['Subject'] = subject
    msg.attach(MIMEText(body_text, 'plain'))
    return msg


def attach_file(msg, file_path):
    """Attaches a file to the email message."""
    try:
        with file_path.open("rb") as attachment:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f"attachment; filename= {file_path.name}")
        msg.attach(part)
        logging.info("File attached successfully.")
    except Exception as e:
        logging.error(f"Failed to attach file: {e}")
        raise

def send_email(msg, gmail_user, gmail_app_password, smtp_port):
    """Sends the email message using SMTP."""
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', smtp_port) as server:
            server.login(gmail_user, gmail_app_password)
            # Pass the list directly to sendmail
            server.sendmail(msg['From'], msg['To'].split(', '), msg.as_string())
            logging.info("Email sent successfully!")
    except smtplib.SMTPException as e:
        logging.error(f"SMTP error occurred: {e}")
        raise



if __name__ == "__main__":
    config = read_config("email_config.json")

    sender = config['gmail_user']
    recipients = config['recipients']
    smtp_port = config['smtp_port']
    gmail_user = config['gmail_user']
    gmail_app_password = config['gmail_app_password']

    subject = 'Log File Attachment'
    body_text = "Attached is the drive_funcs.log file. Please review it."
    file_path = Path("drive_funcs.log")

    msg = create_email(sender, recipients, subject, body_text)
    attach_file(msg, file_path)
    send_email(msg, gmail_user, gmail_app_password, smtp_port)


