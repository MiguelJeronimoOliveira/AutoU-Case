"""Background task for checking new emails periodically."""

import asyncio
import logging
from typing import Optional

from app.core.config import settings
from app.services.email_processor import EmailProcessor
from app.services.email_service import EmailService

logger = logging.getLogger(__name__)


class EmailBackgroundTask:
    """Background task for periodically checking and processing new emails."""
    
    def __init__(
        self,
        email_service: EmailService,
        email_processor: EmailProcessor
    ):
        """
        Initialize background task.
        
        Args:
            email_service: Email service instance
            email_processor: Email processor instance
        """
        self.email_service = email_service
        self.email_processor = email_processor
        self.is_running = False
        self._task: Optional[asyncio.Task] = None
    
    async def check_emails_loop(self) -> None:
        """Main loop for checking emails periodically."""
        logger.info("Background task de verificação de emails iniciada")
        self.is_running = True
        
        while self.is_running:
            try:
                # Fetch new emails
                emails_data = self.email_service.fetch_emails(
                    limit=10,
                    unread_only=True
                )
                
                if emails_data:
                    logger.info(f"Encontrados {len(emails_data)} novo(s) email(s)")
                    
                    # Process each email
                    processed_count = 0
                    for email_data in emails_data:
                        try:
                            self.email_processor.process_received_email(email_data)
                            processed_count += 1
                        except Exception as e:
                            logger.error(f"Erro ao processar email {email_data.get('id', 'unknown')}: {str(e)}")
                            continue
                    
                    if processed_count > 0:
                        logger.info(f"{processed_count} email(s) processado(s) com sucesso")
                
                # Wait before next check
                await asyncio.sleep(settings.email_check_interval)
                
            except Exception as e:
                logger.error(f"Erro no loop de verificação de emails: {str(e)}")
                await asyncio.sleep(settings.email_check_interval)
    
    def start(self) -> None:
        """Start the background task."""
        if self.is_running:
            logger.warning("Background task já está em execução")
            return
        
        try:
            self._task = asyncio.create_task(self.check_emails_loop())
            logger.info("Background task iniciada com sucesso")
        except Exception as e:
            logger.error(f"Erro ao iniciar background task: {str(e)}")
            raise
    
    def stop(self) -> None:
        """Stop the background task."""
        if not self.is_running:
            return
        
        self.is_running = False
        if self._task:
            self._task.cancel()
        logger.info("Background task parada")

