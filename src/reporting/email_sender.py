"""Email dispatch functionality for reports."""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from pathlib import Path
from typing import List, Optional
import os

from ..models.schemas import EmailConfig
from ..utils.logger import get_logger

logger = get_logger(__name__)


class EmailSender:
    """
    Sends email reports with attachments.
    
    Features:
    - HTML email support
    - PDF attachments
    - Multiple recipients
    - CC/BCC support
    - Error handling and retries
    """
    
    def __init__(self, config: EmailConfig):
        """
        Initialize email sender.
        
        Args:
            config: Email configuration
        """
        self.config = config
    
    def send_email(
        self,
        subject: str,
        html_body: str,
        plain_body: Optional[str] = None,
        attachments: Optional[List[Path]] = None,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None
    ) -> bool:
        """
        Send an email with optional attachments.
        
        Args:
            subject: Email subject
            html_body: HTML email body
            plain_body: Plain text fallback (optional)
            attachments: List of file paths to attach
            cc: CC recipients
            bcc: BCC recipients
            
        Returns:
            True if sent successfully, False otherwise
        """
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{self.config.sender_name} <{self.config.sender_email}>"
            msg['To'] = ', '.join(self.config.recipients)
            
            if cc or self.config.cc:
                cc_list = (cc or []) + (self.config.cc or [])
                msg['Cc'] = ', '.join(cc_list)
            
            # Attach plain text version
            if plain_body:
                plain_part = MIMEText(plain_body, 'plain')
                msg.attach(plain_part)
            
            # Attach HTML version
            html_part = MIMEText(html_body, 'html')
            msg.attach(html_part)
            
            # Attach files
            if attachments:
                for file_path in attachments:
                    if not file_path.exists():
                        logger.warning(f"Attachment not found: {file_path}")
                        continue
                    
                    with open(file_path, 'rb') as f:
                        attachment = MIMEApplication(f.read())
                        attachment.add_header(
                            'Content-Disposition',
                            'attachment',
                            filename=file_path.name
                        )
                        msg.attach(attachment)
                    
                    logger.debug(f"Attached file: {file_path.name}")
            
            # Combine all recipients
            all_recipients = self.config.recipients.copy()
            if cc:
                all_recipients.extend(cc)
            if self.config.cc:
                all_recipients.extend(self.config.cc)
            if bcc:
                all_recipients.extend(bcc)
            
            # Send email
            with smtplib.SMTP(self.config.smtp_server, self.config.smtp_port) as server:
                if self.config.use_tls:
                    server.starttls()
                
                # Login
                server.login(self.config.username, self.config.password)
                
                # Send
                server.send_message(msg, to_addrs=all_recipients)
            
            logger.info(f"Email sent successfully to {len(all_recipients)} recipients")
            return True
            
        except smtplib.SMTPException as e:
            logger.error(f"SMTP error sending email: {e}")
            return False
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            return False
    
    def send_weekly_digest(
        self,
        subject: str,
        html_body: str,
        pdf_path: Optional[Path] = None
    ) -> bool:
        """
        Send weekly digest email.
        
        Args:
            subject: Email subject
            html_body: HTML body
            pdf_path: Optional PDF attachment
            
        Returns:
            True if sent successfully
        """
        attachments = [pdf_path] if pdf_path else None
        
        return self.send_email(
            subject=subject,
            html_body=html_body,
            attachments=attachments
        )
    
    def test_connection(self) -> bool:
        """
        Test email server connection.
        
        Returns:
            True if connection successful
        """
        try:
            with smtplib.SMTP(self.config.smtp_server, self.config.smtp_port) as server:
                if self.config.use_tls:
                    server.starttls()
                server.login(self.config.username, self.config.password)
            
            logger.info("Email server connection test successful")
            return True
            
        except Exception as e:
            logger.error(f"Email server connection test failed: {e}")
            return False
    
    @classmethod
    def from_env(cls, sender_email: str, recipients: List[str]) -> "EmailSender":
        """
        Create EmailSender from environment variables.
        
        Required environment variables:
        - SMTP_SERVER
        - SMTP_PORT
        - EMAIL_USERNAME
        - EMAIL_PASSWORD
        
        Args:
            sender_email: Sender email address
            recipients: List of recipient emails
            
        Returns:
            EmailSender instance
        """
        config = EmailConfig(
            smtp_server=os.getenv('SMTP_SERVER', 'smtp.gmail.com'),
            smtp_port=int(os.getenv('SMTP_PORT', '587')),
            username=os.getenv('EMAIL_USERNAME', ''),
            password=os.getenv('EMAIL_PASSWORD', ''),
            sender_email=sender_email,
            recipients=recipients,
            use_tls=os.getenv('EMAIL_USE_TLS', 'true').lower() == 'true'
        )
        
        return cls(config)




