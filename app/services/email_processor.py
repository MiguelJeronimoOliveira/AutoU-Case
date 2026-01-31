"""Email processor service for handling received emails and generating suggestions."""

import logging
from datetime import datetime
from typing import TYPE_CHECKING, Optional
from uuid import uuid4

from app.classifier import EmailClassifier
from app.models import EmailCategory, EmailSuggestion, ReceivedEmail
from app.response_generator import ResponseGenerator
from app.services.email_storage import EmailStorage

if TYPE_CHECKING:
    from app.services.email_service import EmailService

logger = logging.getLogger(__name__)


class EmailProcessor:
    """Service for processing received emails and generating suggestions."""
    
    def __init__(
        self,
        classifier: EmailClassifier,
        response_generator: ResponseGenerator,
        email_storage: EmailStorage
    ):
        """
        Initialize email processor.
        
        Args:
            classifier: Email classifier instance
            response_generator: Response generator instance
            email_storage: Email storage instance
        """
        self.classifier = classifier
        self.response_generator = response_generator
        self.storage = email_storage
    
    def process_received_email(self, email_data: dict) -> ReceivedEmail:
        """
        Process a received email: classify it and generate suggestion.
        
        Args:
            email_data: Dictionary with email data (id, subject, sender, recipient, content, received_at)
            
        Returns:
            ReceivedEmail object with classification and suggestion
        """
        try:
            # Check if email already exists
            existing_email = self.storage.get_email(email_data['id'])
            if existing_email and existing_email.has_suggestion:
                logger.info(f"Email {email_data['id']} já processado")
                return existing_email
            
            # Classify email
            category, confidence, reasoning = self.classifier.classify_email(
                email_data['content']
            )
            
            # Generate response suggestion
            suggested_response = self.response_generator.generate_response(
                email_data['content'],
                category,
                save_to_knowledge_base=True
            )
            
            # Create ReceivedEmail object
            received_email = ReceivedEmail(
                id=email_data['id'],
                message_id=email_data.get('message_id'),
                subject=email_data['subject'],
                sender=email_data['sender'],
                recipient=email_data['recipient'],
                content=email_data['content'],
                received_at=email_data['received_at'],
                category=category,
                confidence=confidence,
                has_suggestion=True,
                suggestion_id=None  # Will be set after creating suggestion
            )
            
            # Create suggestion
            suggestion = EmailSuggestion(
                id=str(uuid4()),
                email_id=received_email.id,
                suggested_response=suggested_response,
                status="pending",
                created_at=datetime.now()
            )
            
            # Save email first (with embedding for RAG)
            self.storage.save_email(received_email)
            
            # Save suggestion
            self.storage.save_suggestion(suggestion)
            
            # Update email with suggestion ID
            received_email.suggestion_id = suggestion.id
            self.storage.save_email(received_email)
            
            # Also add to RAG knowledge base for future context retrieval
            if self.response_generator.use_rag and self.response_generator.rag_retriever:
                try:
                    self.response_generator.rag_retriever.add_knowledge(
                        email_content=email_data['content'],
                        response=suggested_response,
                        category=category,
                        metadata={
                            "email_id": received_email.id,
                            "sender": received_email.sender,
                            "subject": received_email.subject,
                            "received_at": received_email.received_at.isoformat()
                        }
                    )
                    logger.debug(f"Email {received_email.id} adicionado à base de conhecimento RAG")
                except Exception as e:
                    logger.warning(f"Erro ao adicionar email ao RAG: {str(e)}")
            
            logger.info(f"Email {received_email.id} processado com sucesso. Sugestão {suggestion.id} criada.")
            
            return received_email
            
        except Exception as e:
            logger.error(f"Erro ao processar email: {str(e)}")
            # Save email without suggestion if processing fails
            received_email = ReceivedEmail(
                id=email_data['id'],
                message_id=email_data.get('message_id'),
                subject=email_data['subject'],
                sender=email_data['sender'],
                recipient=email_data['recipient'],
                content=email_data['content'],
                received_at=email_data['received_at'],
                has_suggestion=False
            )
            self.storage.save_email(received_email)
            raise
    
    def approve_and_send_suggestion(
        self,
        suggestion_id: str,
        send_email: bool = True,
        email_service: Optional['EmailService'] = None
    ) -> bool:
        """
        Approve a suggestion and optionally send the email.
        
        Args:
            suggestion_id: ID of suggestion to approve
            send_email: Whether to send email immediately
            email_service: Optional EmailService instance to use for sending
            
        Returns:
            True if successful, False otherwise
        """
        try:
            suggestion = self.storage.get_suggestion(suggestion_id)
            if not suggestion:
                logger.error(f"Sugestão {suggestion_id} não encontrada")
                return False
            
            if suggestion.status != "pending":
                logger.warning(f"Sugestão {suggestion_id} já foi processada (status: {suggestion.status})")
                return False
            
            # Update suggestion status
            suggestion.status = "approved"
            suggestion.approved_at = datetime.now()
            
            if send_email:
                # Get email to send response to
                email_obj = self.storage.get_email(suggestion.email_id)
                if not email_obj:
                    logger.error(f"Email {suggestion.email_id} não encontrado")
                    return False
                
                # Use provided email_service or get from deps
                if email_service is None:
                    from app.api.deps import get_email_service
                    email_service = get_email_service()
                
                # Send email
                subject = f"Re: {email_obj.subject}"
                success = email_service.send_email(
                    to_address=email_obj.sender,
                    subject=subject,
                    body=suggestion.suggested_response,
                    reply_to_message_id=email_obj.message_id
                )
                
                if success:
                    suggestion.status = "sent"
                    suggestion.sent_at = datetime.now()
                    logger.info(f"Email enviado com sucesso para {email_obj.sender}")
                else:
                    logger.error(f"Falha ao enviar email para {email_obj.sender}")
                    return False
            
            # Save updated suggestion
            self.storage.save_suggestion(suggestion)
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao aprovar e enviar sugestão: {str(e)}")
            return False
    
    def reject_suggestion(self, suggestion_id: str) -> bool:
        """
        Reject a suggestion.
        
        Args:
            suggestion_id: ID of suggestion to reject
            
        Returns:
            True if successful, False otherwise
        """
        try:
            suggestion = self.storage.get_suggestion(suggestion_id)
            if not suggestion:
                logger.error(f"Sugestão {suggestion_id} não encontrada")
                return False
            
            suggestion.status = "rejected"
            self.storage.save_suggestion(suggestion)
            
            logger.info(f"Sugestão {suggestion_id} rejeitada")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao rejeitar sugestão: {str(e)}")
            return False

