"""Email service for receiving and sending emails via IMAP and SMTP."""

import email
import imaplib
import logging
import smtplib
from datetime import datetime
from email.header import decode_header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import List, Optional

from app.core.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    """Service for handling email operations (IMAP and SMTP)."""
    
    def __init__(self):
        """Initialize email service with settings."""
        self.imap_server = settings.email_imap_server
        self.imap_port = settings.email_imap_port
        self.smtp_server = settings.email_smtp_server
        self.smtp_port = settings.email_smtp_port
        self.email_address = settings.email_address
        self.email_password = settings.email_password
        self.use_ssl = settings.email_use_ssl
        
    def _decode_mime_words(self, s: str) -> str:
        """Decode MIME encoded words in email headers."""
        decoded_parts = decode_header(s)
        decoded_str = ""
        for part, encoding in decoded_parts:
            if isinstance(part, bytes):
                if encoding:
                    decoded_str += part.decode(encoding)
                else:
                    decoded_str += part.decode('utf-8', errors='ignore')
            else:
                decoded_str += part
        return decoded_str
    
    def _get_email_body(self, msg: email.message.Message) -> str:
        """Extract email body text from message."""
        body = ""
        
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))
                
                if content_type == "text/plain" and "attachment" not in content_disposition:
                    try:
                        body += part.get_payload(decode=True).decode('utf-8', errors='ignore')
                    except Exception:
                        try:
                            body += part.get_payload(decode=True).decode('latin-1', errors='ignore')
                        except Exception:
                            pass
        else:
            try:
                body = msg.get_payload(decode=True).decode('utf-8', errors='ignore')
            except Exception:
                try:
                    body = msg.get_payload(decode=True).decode('latin-1', errors='ignore')
                except Exception:
                    body = str(msg.get_payload())
        
        return body.strip()
    
    def fetch_emails(
        self,
        limit: int = 10,
        unread_only: bool = True
    ) -> List[dict]:
        """
        Fetch emails from IMAP server.
        
        Args:
            limit: Maximum number of emails to fetch
            unread_only: Whether to fetch only unread emails
            
        Returns:
            List of email dictionaries with id, subject, sender, recipient, content, received_at
        """
        emails = []
        
        try:
            # Connect to IMAP server
            if self.use_ssl:
                mail = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
            else:
                mail = imaplib.IMAP4(self.imap_server, self.imap_port)
            
            # Login
            mail.login(self.email_address, self.email_password)
            
            # Select inbox
            mail.select("INBOX")
            
            # Search for emails
            if unread_only:
                status, messages = mail.search(None, 'UNSEEN')
            else:
                status, messages = mail.search(None, 'ALL')
            
            if status != 'OK':
                logger.error("Erro ao buscar emails")
                mail.close()
                mail.logout()
                return emails
            
            # Get email IDs
            email_ids = messages[0].split()
            
            # Limit number of emails
            email_ids = email_ids[-limit:] if len(email_ids) > limit else email_ids
            
            # Fetch each email
            for email_id in reversed(email_ids):  # Most recent first
                try:
                    status, msg_data = mail.fetch(email_id, '(RFC822)')
                    
                    if status != 'OK':
                        continue
                    
                    # Parse email
                    raw_email = msg_data[0][1]
                    msg = email.message_from_bytes(raw_email)
                    
                    # Extract information
                    subject = self._decode_mime_words(msg.get("Subject", ""))
                    sender = self._decode_mime_words(msg.get("From", ""))
                    recipient = self.email_address
                    message_id = msg.get("Message-ID", "")
                    
                    # Parse date
                    date_str = msg.get("Date", "")
                    try:
                        received_at = email.utils.parsedate_to_datetime(date_str)
                    except Exception:
                        received_at = datetime.now()
                    
                    # Get body
                    body = self._get_email_body(msg)
                    
                    # Extract email address from sender (remove name if present)
                    sender_email = sender
                    if '<' in sender and '>' in sender:
                        sender_email = sender.split('<')[1].split('>')[0]
                    elif '@' in sender:
                        sender_email = sender.strip()
                    
                    emails.append({
                        'id': email_id.decode('utf-8'),
                        'message_id': message_id,
                        'subject': subject,
                        'sender': sender_email,
                        'recipient': recipient,
                        'content': body,
                        'received_at': received_at
                    })
                    
                except Exception as e:
                    logger.warning(f"Erro ao processar email {email_id}: {str(e)}")
                    continue
            
            mail.close()
            mail.logout()
            
        except Exception as e:
            logger.error(f"Erro ao buscar emails: {str(e)}")
        
        return emails
    
    def send_email(
        self,
        to_address: str,
        subject: str,
        body: str,
        reply_to_message_id: Optional[str] = None
    ) -> bool:
        """
        Send email via SMTP.
        
        Args:
            to_address: Recipient email address
            subject: Email subject
            body: Email body text
            reply_to_message_id: Optional Message-ID to reply to
            
        Returns:
            True if email was sent successfully, False otherwise
        """
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.email_address
            msg['To'] = to_address
            msg['Subject'] = subject
            
            # Add reply headers if replying
            if reply_to_message_id:
                msg['In-Reply-To'] = reply_to_message_id
                msg['References'] = reply_to_message_id
            
            # Add body
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
            # Connect to SMTP server
            if self.use_ssl:
                server = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port)
            else:
                server = smtplib.SMTP(self.smtp_server, self.smtp_port)
                server.starttls()
            
            # Login and send
            server.login(self.email_address, self.email_password)
            text = msg.as_string()
            server.sendmail(self.email_address, to_address, text)
            server.quit()
            
            logger.info(f"Email enviado com sucesso para {to_address}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao enviar email: {str(e)}")
            return False
    
    def mark_email_as_read(self, email_id: str) -> bool:
        """
        Mark email as read in IMAP.
        
        Args:
            email_id: Email ID to mark as read
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if self.use_ssl:
                mail = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
            else:
                mail = imaplib.IMAP4(self.imap_server, self.imap_port)
            
            mail.login(self.email_address, self.email_password)
            mail.select("INBOX")
            mail.store(email_id.encode('utf-8'), '+FLAGS', '\\Seen')
            mail.close()
            mail.logout()
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao marcar email como lido: {str(e)}")
            return False

