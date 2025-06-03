import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from bericht_backend.utils.logger import get_logger

logger = get_logger(__name__)


def send_email(
    to_email: str,
    subject: str,
    body: str,
    word_attachment: bytes | None = None,
    word_filename: str = "document.docx",
):
    """
    Sends an email, optionally with an .ics or Word file attachment.

    Args:
        to_email: Recipient email address
        subject: Email subject
        body: Email body text
        word_attachment: Optional bytes content of the Word file
        word_filename: Filename for the attachment (default: document.docx)
    """
    from_email = "noreply@bs.ch"

    msg = MIMEMultipart()
    msg["From"] = from_email
    msg["To"] = to_email
    msg["Subject"] = subject

    msg.attach(MIMEText(body, "plain"))

    # If a Word file attachment was provided, attach it to the email
    if word_attachment:
        part = MIMEBase("application", "vnd.openxmlformats-officedocument.wordprocessingml.document")
        part.set_payload(word_attachment)
        encoders.encode_base64(part)
        part.add_header(
            "Content-Disposition",
            f"attachment; filename={word_filename}",
        )
        msg.attach(part)

    try:
        with smtplib.SMTP("mail.bs.ch") as server:
            _ = server.sendmail(from_email, to_email, msg.as_string())
        logger.info("Email sent successfully", to_email=to_email, subject=subject)
        return True
    except Exception as e:
        logger.error("Failed to send email", error=str(e), to_email=to_email, subject=subject)
        return False
