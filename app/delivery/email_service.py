"""
Email delivery service for sending job results and failure notifications.
"""
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
from typing import List
import time

from app.config import config

logger = logging.getLogger(__name__)


def _create_smtp_connection(config: dict):
    """Create and configure SMTP connection."""
    server = smtplib.SMTP(config['host'], config['port'])
    server.ehlo()
    
    if config['use_tls']:
        server.starttls()
        server.ehlo()
    
    server.login(config['user'], config['password'])
    return server


def send_email(job_name: str, recipients: List[str], csv_content: str) -> None:
    """
    Send email with CSV attachment containing job results.
    
    Args:
        job_name: Name of the job
        recipients: List of email addresses to send to
        csv_content: CSV content as string
        
    Raises:
        Exception: If email delivery fails after retries
    """
    # Test mode: skip actual email sending
    import os
    if os.getenv('ENVIRONMENT') == 'test':
        logger.info(f"TEST MODE: Skipping email send for job '{job_name}' to {len(recipients)} recipient(s)")
        logger.info(f"TEST MODE: CSV content size: {len(csv_content)} bytes")
        return
    
    smtp_config = config.get_smtp_config()
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    subject = f"Job Results: {job_name} - {timestamp}"
    
    # Create message
    msg = MIMEMultipart()
    msg['From'] = smtp_config['from_email']
    msg['To'] = ', '.join(recipients)
    msg['Subject'] = subject
    
    # Email body
    body = f"""
Hello,

The scheduled job '{job_name}' has completed successfully.

Please find the results attached as a CSV file.

Execution Time: {timestamp}

Best regards,
Scheduled Jobs Service
"""
    msg.attach(MIMEText(body, 'plain'))
    
    # Attach CSV file
    attachment = MIMEBase('application', 'octet-stream')
    attachment.set_payload(csv_content.encode('utf-8'))
    encoders.encode_base64(attachment)
    attachment.add_header(
        'Content-Disposition',
        f'attachment; filename="{job_name}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
    )
    msg.attach(attachment)
    
    # Send with retry logic (2 attempts with 5-second delay)
    max_attempts = 2
    for attempt in range(1, max_attempts + 1):
        try:
            logger.info(f"Sending email for job '{job_name}' to {len(recipients)} recipient(s) (attempt {attempt}/{max_attempts})")
            server = _create_smtp_connection(smtp_config)
            server.send_message(msg)
            server.quit()
            logger.info(f"Email sent successfully for job '{job_name}'")
            return
        except Exception as e:
            logger.error(f"Failed to send email for job '{job_name}' (attempt {attempt}/{max_attempts}): {str(e)}")
            if attempt < max_attempts:
                logger.info(f"Retrying in 5 seconds...")
                time.sleep(5)
            else:
                logger.error(f"All email delivery attempts failed for job '{job_name}'")
                raise


def send_failure_email(job_name: str, recipients: List[str], error_message: str) -> None:
    """
    Send failure notification email to consumers.
    
    Args:
        job_name: Name of the job that failed
        recipients: List of email addresses to notify
        error_message: Description of the error
        
    Raises:
        Exception: If email delivery fails after retries
    """
    # Test mode: skip actual email sending
    import os
    if os.getenv('ENVIRONMENT') == 'test':
        logger.info(f"TEST MODE: Skipping failure email for job '{job_name}' to {len(recipients)} recipient(s)")
        logger.info(f"TEST MODE: Error message: {error_message}")
        return
    
    smtp_config = config.get_smtp_config()
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    subject = f"Job Failure: {job_name} - {timestamp}"
    
    # Create message
    msg = MIMEMultipart()
    msg['From'] = smtp_config['from_email']
    msg['To'] = ', '.join(recipients)
    msg['Subject'] = subject
    
    # Email body
    body = f"""
Hello,

The scheduled job '{job_name}' has failed during execution.

Execution Time: {timestamp}

Error Details:
{error_message}

Please review the job configuration and data source, then contact your system administrator if the issue persists.

Best regards,
Scheduled Jobs Service
"""
    msg.attach(MIMEText(body, 'plain'))
    
    # Send with retry logic (2 attempts with 5-second delay)
    max_attempts = 2
    for attempt in range(1, max_attempts + 1):
        try:
            logger.info(f"Sending failure notification for job '{job_name}' to {len(recipients)} recipient(s) (attempt {attempt}/{max_attempts})")
            server = _create_smtp_connection(smtp_config)
            server.send_message(msg)
            server.quit()
            logger.info(f"Failure notification sent successfully for job '{job_name}'")
            return
        except Exception as e:
            logger.error(f"Failed to send failure notification for job '{job_name}' (attempt {attempt}/{max_attempts}): {str(e)}")
            if attempt < max_attempts:
                logger.info(f"Retrying in 5 seconds...")
                time.sleep(5)
            else:
                logger.error(f"All failure notification attempts failed for job '{job_name}'")
                raise
