"""Storage service for emails and suggestions using ChromaDB with embeddings."""

import logging
from datetime import datetime
from typing import Dict, List, Optional
from uuid import uuid4

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

from app.core.config import settings
from app.models import EmailCategory, EmailSuggestion, ReceivedEmail

logger = logging.getLogger(__name__)


class EmailStorage:
    """ChromaDB-based storage for emails and suggestions with embeddings."""
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize email storage with ChromaDB.
        
        Args:
            db_path: Path to ChromaDB storage (defaults to RAG path)
        """
        self.db_path = db_path or settings.rag_knowledge_base_path
        self.embedding_model: Optional[SentenceTransformer] = None
        self.client: Optional[chromadb.ClientAPI] = None
        self.emails_collection: Optional[chromadb.Collection] = None
        self.suggestions_collection: Optional[chromadb.Collection] = None
        
        self._initialize()
    
    def _initialize(self) -> None:
        """Initialize ChromaDB client and collections."""
        try:
            # Load embedding model
            embedding_model_name = settings.rag_embedding_model_name
            logger.info(f"Carregando modelo de embedding: {embedding_model_name}")
            self.embedding_model = SentenceTransformer(embedding_model_name)
            logger.info("Modelo de embedding carregado com sucesso")
            
            # Initialize ChromaDB client
            import os
            from pathlib import Path
            Path(self.db_path).mkdir(parents=True, exist_ok=True)
            
            logger.info(f"Inicializando ChromaDB em: {self.db_path}")
            self.client = chromadb.PersistentClient(
                path=self.db_path,
                settings=Settings(anonymized_telemetry=False)
            )
            
            # Create or get emails collection
            try:
                self.emails_collection = self.client.get_collection(name="emails")
                logger.info("Collection 'emails' encontrada")
            except Exception:
                self.emails_collection = self.client.create_collection(
                    name="emails",
                    metadata={"description": "Received emails with embeddings"}
                )
                logger.info("Collection 'emails' criada")
            
            # Create or get suggestions collection
            try:
                self.suggestions_collection = self.client.get_collection(name="suggestions")
                logger.info("Collection 'suggestions' encontrada")
            except Exception:
                self.suggestions_collection = self.client.create_collection(
                    name="suggestions",
                    metadata={"description": "Email response suggestions"}
                )
                logger.info("Collection 'suggestions' criada")
            
            logger.info("EmailStorage inicializado com sucesso")
            
        except Exception as e:
            error_msg = f"Erro ao inicializar EmailStorage: {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
    
    def _generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text."""
        if not self.embedding_model:
            raise RuntimeError("Embedding model not loaded")
        
        if not text or not text.strip():
            logger.warning("Texto vazio fornecido para geração de embedding")
            return [0.0] * 384  # Default dimension
        
        try:
            # Truncate if too long
            max_length = settings.rag_max_email_length
            processed_text = text[:max_length] if len(text) > max_length else text
            
            embedding = self.embedding_model.encode(processed_text, convert_to_numpy=True)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Erro ao gerar embedding: {str(e)}")
            raise
    
    def _email_to_metadata(self, email: ReceivedEmail) -> Dict:
        """Convert ReceivedEmail to metadata dictionary."""
        # Store full content in metadata (ChromaDB metadata has size limits, so we truncate if needed)
        content_preview = email.content[:5000] if len(email.content) > 5000 else email.content
        
        return {
            "id": email.id,
            "message_id": email.message_id or "",
            "subject": email.subject,
            "sender": email.sender,
            "recipient": email.recipient,
            "content": email.content,  # Full content stored here
            "received_at": email.received_at.isoformat(),
            "category": email.category.value if email.category else "",
            "confidence": str(email.confidence) if email.confidence else "",
            "has_suggestion": str(email.has_suggestion),
            "suggestion_id": email.suggestion_id or ""
        }
    
    def _metadata_to_email(self, metadata: Dict, content: str) -> ReceivedEmail:
        """Convert metadata and content to ReceivedEmail."""
        return ReceivedEmail(
            id=metadata.get("id", ""),
            message_id=metadata.get("message_id") or None,
            subject=metadata.get("subject", ""),
            sender=metadata.get("sender", ""),
            recipient=metadata.get("recipient", ""),
            content=content,
            received_at=datetime.fromisoformat(metadata.get("received_at", datetime.now().isoformat())),
            category=EmailCategory(metadata["category"]) if metadata.get("category") else None,
            confidence=float(metadata["confidence"]) if metadata.get("confidence") else None,
            has_suggestion=metadata.get("has_suggestion", "False") == "True",
            suggestion_id=metadata.get("suggestion_id") or None
        )
    
    def _suggestion_to_metadata(self, suggestion: EmailSuggestion) -> Dict:
        """Convert EmailSuggestion to metadata dictionary."""
        return {
            "id": suggestion.id,
            "email_id": suggestion.email_id,
            "status": suggestion.status,
            "created_at": suggestion.created_at.isoformat(),
            "approved_at": suggestion.approved_at.isoformat() if suggestion.approved_at else "",
            "sent_at": suggestion.sent_at.isoformat() if suggestion.sent_at else ""
        }
    
    def _metadata_to_suggestion(self, metadata: Dict, suggested_response: str) -> EmailSuggestion:
        """Convert metadata and response to EmailSuggestion."""
        return EmailSuggestion(
            id=metadata.get("id", ""),
            email_id=metadata.get("email_id", ""),
            suggested_response=suggested_response,
            status=metadata.get("status", "pending"),
            created_at=datetime.fromisoformat(metadata.get("created_at", datetime.now().isoformat())),
            approved_at=datetime.fromisoformat(metadata["approved_at"]) if metadata.get("approved_at") else None,
            sent_at=datetime.fromisoformat(metadata["sent_at"]) if metadata.get("sent_at") else None
        )
    
    def save_email(self, email: ReceivedEmail) -> None:
        """Save or update email in ChromaDB with embedding."""
        if not self.emails_collection:
            raise RuntimeError("Emails collection not initialized")
        
        try:
            # Generate embedding from email content
            embedding = self._generate_embedding(email.content)
            
            # Create document text (for search and display)
            # Store full content in document for retrieval
            document_text = f"Assunto: {email.subject}\nDe: {email.sender}\nConteúdo: {email.content}"
            
            # Convert to metadata
            # Store content in metadata too, but ChromaDB may truncate very long metadata
            metadata = self._email_to_metadata(email)
            
            # Check if email already exists
            try:
                existing = self.emails_collection.get(ids=[email.id])
                if existing and existing.get("ids"):
                    # Update existing
                    self.emails_collection.update(
                        ids=[email.id],
                        embeddings=[embedding],
                        documents=[document_text],
                        metadatas=[metadata]
                    )
                    logger.debug(f"Email {email.id} atualizado")
                else:
                    # Add new
                    self.emails_collection.add(
                        ids=[email.id],
                        embeddings=[embedding],
                        documents=[document_text],
                        metadatas=[metadata]
                    )
                    logger.debug(f"Email {email.id} salvo")
            except Exception:
                # If get fails, try to add
                self.emails_collection.add(
                    ids=[email.id],
                    embeddings=[embedding],
                    documents=[document_text],
                    metadatas=[metadata]
                )
                logger.debug(f"Email {email.id} salvo (novo)")
            
        except Exception as e:
            logger.error(f"Erro ao salvar email: {str(e)}")
            raise
    
    def get_email(self, email_id: str) -> Optional[ReceivedEmail]:
        """Get email by ID."""
        if not self.emails_collection:
            return None
        
        try:
            results = self.emails_collection.get(ids=[email_id])
            if not results or not results.get("ids") or len(results["ids"]) == 0:
                return None
            
            idx = 0
            metadata = results["metadatas"][idx] if results.get("metadatas") else {}
            
            # Get content from metadata (preferred) or document
            content = metadata.get("content", "")
            if not content:
                document = results["documents"][idx] if results.get("documents") else ""
                if document and "Conteúdo: " in document:
                    content = document.split("Conteúdo: ", 1)[1]
                elif document:
                    content = document
            
            return self._metadata_to_email(metadata, content)
            
        except Exception as e:
            logger.error(f"Erro ao obter email {email_id}: {str(e)}")
            return None
    
    def list_emails(
        self,
        limit: int = 50,
        offset: int = 0,
        has_suggestion: Optional[bool] = None
    ) -> List[ReceivedEmail]:
        """List emails with optional filters."""
        if not self.emails_collection:
            return []
        
        try:
            # Get all emails
            all_results = self.emails_collection.get()
            
            if not all_results or not all_results.get("ids"):
                return []
            
            emails = []
            for i, email_id in enumerate(all_results["ids"]):
                metadata = all_results["metadatas"][i] if all_results.get("metadatas") else {}
                
                # Get content from metadata (preferred) or document
                content = metadata.get("content", "")
                if not content:
                    document = all_results["documents"][i] if all_results.get("documents") else ""
                    if document and "Conteúdo: " in document:
                        content = document.split("Conteúdo: ", 1)[1]
                    elif document:
                        content = document
                
                # Filter by has_suggestion if specified
                if has_suggestion is not None:
                    email_has_suggestion = metadata.get("has_suggestion", "False") == "True"
                    if email_has_suggestion != has_suggestion:
                        continue
                
                email_obj = self._metadata_to_email(metadata, content)
                emails.append(email_obj)
            
            # Sort by received_at descending
            emails.sort(key=lambda x: x.received_at, reverse=True)
            
            # Apply pagination
            return emails[offset:offset + limit]
            
        except Exception as e:
            logger.error(f"Erro ao listar emails: {str(e)}")
            return []
    
    def save_suggestion(self, suggestion: EmailSuggestion) -> None:
        """Save or update suggestion in ChromaDB."""
        if not self.suggestions_collection:
            raise RuntimeError("Suggestions collection not initialized")
        
        try:
            metadata = self._suggestion_to_metadata(suggestion)
            
            # Use suggestion response as document text
            document_text = suggestion.suggested_response
            
            # Check if suggestion already exists
            try:
                existing = self.suggestions_collection.get(ids=[suggestion.id])
                if existing and existing.get("ids"):
                    # Update existing
                    self.suggestions_collection.update(
                        ids=[suggestion.id],
                        documents=[document_text],
                        metadatas=[metadata]
                    )
                    logger.debug(f"Sugestão {suggestion.id} atualizada")
                else:
                    # Add new
                    self.suggestions_collection.add(
                        ids=[suggestion.id],
                        documents=[document_text],
                        metadatas=[metadata]
                    )
                    logger.debug(f"Sugestão {suggestion.id} salva")
            except Exception:
                # If get fails, try to add
                self.suggestions_collection.add(
                    ids=[suggestion.id],
                    documents=[document_text],
                    metadatas=[metadata]
                )
                logger.debug(f"Sugestão {suggestion.id} salva (nova)")
            
        except Exception as e:
            logger.error(f"Erro ao salvar sugestão: {str(e)}")
            raise
    
    def get_suggestion(self, suggestion_id: str) -> Optional[EmailSuggestion]:
        """Get suggestion by ID."""
        if not self.suggestions_collection:
            return None
        
        try:
            results = self.suggestions_collection.get(ids=[suggestion_id])
            if not results or not results.get("ids") or len(results["ids"]) == 0:
                return None
            
            idx = 0
            metadata = results["metadatas"][idx] if results.get("metadatas") else {}
            document = results["documents"][idx] if results.get("documents") else ""
            
            return self._metadata_to_suggestion(metadata, document)
            
        except Exception as e:
            logger.error(f"Erro ao obter sugestão {suggestion_id}: {str(e)}")
            return None
    
    def get_suggestion_by_email_id(self, email_id: str) -> Optional[EmailSuggestion]:
        """Get suggestion by email ID."""
        if not self.suggestions_collection:
            return None
        
        try:
            # Query by email_id in metadata
            results = self.suggestions_collection.get(
                where={"email_id": email_id}
            )
            
            if not results or not results.get("ids") or len(results["ids"]) == 0:
                return None
            
            idx = 0
            metadata = results["metadatas"][idx] if results.get("metadatas") else {}
            document = results["documents"][idx] if results.get("documents") else ""
            
            return self._metadata_to_suggestion(metadata, document)
            
        except Exception as e:
            logger.error(f"Erro ao obter sugestão por email_id {email_id}: {str(e)}")
            return None
    
    def list_suggestions(
        self,
        limit: int = 50,
        offset: int = 0,
        status: Optional[str] = None
    ) -> List[EmailSuggestion]:
        """List suggestions with optional status filter."""
        if not self.suggestions_collection:
            return []
        
        try:
            # Get all suggestions
            where_filter = {"status": status} if status else None
            all_results = self.suggestions_collection.get(where=where_filter)
            
            if not all_results or not all_results.get("ids"):
                return []
            
            suggestions = []
            for i, suggestion_id in enumerate(all_results["ids"]):
                metadata = all_results["metadatas"][i] if all_results.get("metadatas") else {}
                document = all_results["documents"][i] if all_results.get("documents") else ""
                
                # Filter by status if specified
                if status and metadata.get("status") != status:
                    continue
                
                suggestion_obj = self._metadata_to_suggestion(metadata, document)
                suggestions.append(suggestion_obj)
            
            # Sort by created_at descending
            suggestions.sort(key=lambda x: x.created_at, reverse=True)
            
            # Apply pagination
            return suggestions[offset:offset + limit]
            
        except Exception as e:
            logger.error(f"Erro ao listar sugestões: {str(e)}")
            return []
    
    def update_email_suggestion(self, email_id: str, suggestion_id: str) -> None:
        """Update email to reference a suggestion."""
        email_obj = self.get_email(email_id)
        if email_obj:
            email_obj.has_suggestion = True
            email_obj.suggestion_id = suggestion_id
            self.save_email(email_obj)
    
    def search_similar_emails(
        self,
        query: str,
        limit: int = 10,
        category: Optional[EmailCategory] = None
    ) -> List[Dict]:
        """
        Search for similar emails using semantic search.
        
        Args:
            query: Search query text
            limit: Maximum number of results
            category: Optional category filter
            
        Returns:
            List of dictionaries with email data and similarity scores
        """
        if not self.emails_collection or not self.embedding_model:
            return []
        
        try:
            # Generate query embedding
            query_embedding = self._generate_embedding(query)
            
            # Build where filter
            where_filter = {}
            if category:
                where_filter["category"] = category.value
            
            # Search
            results = self.emails_collection.query(
                query_embeddings=[query_embedding],
                n_results=limit,
                where=where_filter if where_filter else None
            )
            
            similar_emails = []
            if results["ids"] and len(results["ids"][0]) > 0:
                for i, email_id in enumerate(results["ids"][0]):
                    distance = results["distances"][0][i] if results["distances"] else 0.0
                    similarity = 1.0 - distance
                    
                    metadata = results["metadatas"][0][i] if results.get("metadatas") else {}
                    
                    # Get content from metadata (preferred) or document
                    content = metadata.get("content", "")
                    if not content:
                        document = results["documents"][0][i] if results.get("documents") else ""
                        if document and "Conteúdo: " in document:
                            content = document.split("Conteúdo: ", 1)[1]
                        elif document:
                            content = document
                    
                    email_obj = self._metadata_to_email(metadata, content)
                    
                    similar_emails.append({
                        "email": email_obj,
                        "similarity": similarity
                    })
            
            return similar_emails
            
        except Exception as e:
            logger.error(f"Erro ao buscar emails similares: {str(e)}")
            return []
    
    def delete_email(self, email_id: str) -> bool:
        """
        Delete an email and its associated suggestion if exists.
        
        Args:
            email_id: ID of email to delete
            
        Returns:
            True if email was deleted, False otherwise
        """
        if not self.emails_collection:
            return False
        
        try:
            # Check if email exists
            email_obj = self.get_email(email_id)
            if not email_obj:
                logger.warning(f"Email {email_id} não encontrado para deletar")
                return False
            
            # Delete associated suggestion if exists
            if email_obj.suggestion_id:
                try:
                    if self.suggestions_collection:
                        self.suggestions_collection.delete(ids=[email_obj.suggestion_id])
                        logger.info(f"Sugestão {email_obj.suggestion_id} deletada junto com email {email_id}")
                except Exception as e:
                    logger.warning(f"Erro ao deletar sugestão associada: {str(e)}")
            
            # Delete email
            self.emails_collection.delete(ids=[email_id])
            logger.info(f"Email {email_id} deletado com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao deletar email {email_id}: {str(e)}")
            return False
    
    def clear_all_emails(self) -> int:
        """
        Clear all emails and their associated suggestions.
        
        Returns:
            Number of emails deleted
        """
        if not self.emails_collection:
            return 0
        
        try:
            # Get all emails
            all_results = self.emails_collection.get()
            
            if not all_results or not all_results.get("ids"):
                logger.info("Nenhum email para deletar")
                return 0
            
            email_ids = all_results["ids"]
            count = len(email_ids)
            
            # Get all suggestions to delete
            suggestion_ids_to_delete = []
            if self.suggestions_collection:
                suggestions_results = self.suggestions_collection.get()
                if suggestions_results and suggestions_results.get("ids"):
                    suggestion_ids_to_delete = suggestions_results["ids"]
            
            # Delete all suggestions first
            if suggestion_ids_to_delete:
                try:
                    self.suggestions_collection.delete(ids=suggestion_ids_to_delete)
                    logger.info(f"{len(suggestion_ids_to_delete)} sugestão(ões) deletada(s)")
                except Exception as e:
                    logger.warning(f"Erro ao deletar sugestões: {str(e)}")
            
            # Delete all emails
            self.emails_collection.delete(ids=email_ids)
            logger.info(f"{count} email(s) deletado(s) com sucesso")
            
            return count
            
        except Exception as e:
            logger.error(f"Erro ao limpar emails: {str(e)}")
            raise