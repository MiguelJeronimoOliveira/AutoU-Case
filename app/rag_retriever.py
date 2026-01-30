"""RAG (Retrieval-Augmented Generation) module for email response generation."""

import logging
import os
import re
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any

import chromadb
import numpy as np
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

from app.models import EmailCategory

logger = logging.getLogger(__name__)

RAG_DB_PATH = "rag_knowledge_base"
EMBEDDING_MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2" 
TOP_K_RESULTS = 3 
MIN_SIMILARITY_SCORE = 0.5
MAX_EMAIL_LENGTH_FOR_EMBEDDING = 50000


class RAGRetriever:
    
    def __init__(self, db_path: str = RAG_DB_PATH):
        self.db_path = db_path
        self.embedding_model: Optional[SentenceTransformer] = None
        self.client: Optional[chromadb.ClientAPI] = None
        self.collection: Optional[chromadb.Collection] = None
        self._initialize()
    
    def _initialize(self) -> None:
        try:

            logger.info(f"Loading embedding model: {EMBEDDING_MODEL_NAME}")
            self.embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)
            logger.info("Embedding model loaded successfully")
            
            Path(self.db_path).mkdir(parents=True, exist_ok=True)
            
            logger.info(f"Initializing ChromaDB at: {self.db_path}")
            self.client = chromadb.PersistentClient(
                path=self.db_path,
                settings=Settings(anonymized_telemetry=False)
            )
            
            collection_name = "email_responses"
            try:
                self.collection = self.client.get_collection(name=collection_name)
                logger.info(f"Collection '{collection_name}' found")
            except Exception:
                self.collection = self.client.create_collection(
                    name=collection_name,
                    metadata={"description": "Email response knowledge base"}
                )
                logger.info(f"Collection '{collection_name}' created")
            
            logger.info("RAG Retriever initialized successfully")
            
        except Exception as e:
            error_msg = f"Error initializing RAG Retriever: {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
    
    def _preprocess_text(self, text: str) -> str:
        if not text:
            return ""
        
        text = re.sub(r'\r\n|\r', '\n', text)
        text = re.sub(r'[ \t]+', ' ', text)
        lines = [line.strip() for line in text.split('\n')]
        text = '\n'.join(lines)
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = text.strip()
        
        return text
    
    def _normalize_embedding(self, embedding: np.ndarray) -> np.ndarray:
        """
        Normalizes embedding using L2 normalization.
        Improves cosine similarity search quality.
        """
        norm = np.linalg.norm(embedding)
        if norm > 0:
            return embedding / norm
        return embedding
    
    # generate embedding for the given text
    #args: text: the text to generate embedding for
    #normalize: if True, applies L2 normalization to the embedding
    #return: a list of floats representing the embedding
    def _generate_embedding(self, text: str, normalize: bool = True) -> List[float]:
        if not self.embedding_model:
            raise RuntimeError("Embedding model not loaded")
        
        if not text or not text.strip():
            logger.warning("Empty text provided for embedding generation")
            return [0.0] * 384
        
        try:
            processed_text = self._preprocess_text(text)
            
            if len(processed_text) > MAX_EMAIL_LENGTH_FOR_EMBEDDING:
                logger.warning(
                    f"Text truncated from {len(processed_text)} to "
                    f"{MAX_EMAIL_LENGTH_FOR_EMBEDDING} characters for embedding generation"
                )
                processed_text = processed_text[:MAX_EMAIL_LENGTH_FOR_EMBEDDING]
            
            embedding = self.embedding_model.encode(processed_text, convert_to_numpy=True)
            
            if normalize:
                embedding = self._normalize_embedding(embedding)
            
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}")
            raise
    
    def add_knowledge(
        self,
        email_content: str,
        response: str,
        category: EmailCategory,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        if not self.collection:
            raise RuntimeError("Collection not initialized")
        
        try:
            # Use only email_content for embedding to ensure consistency with queries
            # Response is stored only in metadata for reference
            embedding = self._generate_embedding(email_content, normalize=True)
            
            doc_id = str(uuid.uuid4())
            document_text = f"Email: {email_content}\nResposta: {response}"
            
            email_preview = email_content[:50000] if len(email_content) > 50000 else email_content
            
            doc_metadata = {
                "email_content": email_preview,
                "response": response,
                "category": category.value,
                "created_at": datetime.now().isoformat(),
                **(metadata or {})
            }
            
            self.collection.add(
                ids=[doc_id],
                embeddings=[embedding],
                documents=[document_text],
                metadatas=[doc_metadata]
            )
            
            try:
                current_count = self.collection.count()
                logger.debug(f"Total documents in collection after adding: {current_count}")
            except Exception as e:
                logger.warning(f"Error checking count after adding document: {str(e)}")
            
            logger.info(f"Document added to knowledge base: {doc_id} (email: {len(email_content)} chars, response: {len(response)} chars)")
            return doc_id
            
        except Exception as e:
            logger.error(f"Error adding knowledge: {str(e)}")
            raise
    
    # retrieve relevant context from the database
    #args: query: the query to retrieve relevant context
    #category: the category of the query
    #top_k: the number of top results to retrieve
    #return: a list of relevant documents
    def retrieve_relevant_context(
        self,
        query: str,
        category: Optional[EmailCategory] = None,
        top_k: int = TOP_K_RESULTS
    ) -> List[Dict[str, Any]]:
        if not self.collection:
            logger.warning("Collection not initialized, returning empty list")
            return []
        
        try:
            # Use normalize=True to ensure consistency with stored embeddings
            query_embedding = self._generate_embedding(query, normalize=True)
            
            where_filter = {}
            if category:
                where_filter["category"] = category.value
            
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                where=where_filter if where_filter else None
            )
            
            relevant_docs = []
            if results["ids"] and len(results["ids"][0]) > 0:
                for i, doc_id in enumerate(results["ids"][0]):
                    distance = results["distances"][0][i] if results["distances"] else 0.0
                    similarity = 1.0 - distance
                    
                    if similarity >= MIN_SIMILARITY_SCORE:
                        relevant_docs.append({
                            "id": doc_id,
                            "document": results["documents"][0][i],
                            "metadata": results["metadatas"][0][i],
                            "similarity": similarity
                        })
            
            logger.debug(f"Retrieved {len(relevant_docs)} relevant documents")
            return relevant_docs
            
        except Exception as e:
            logger.error(f"Error retrieving context: {str(e)}")
            return []
    
    # format documents for prompt
    #args: relevant_docs: a list of relevant documents
    #return: a formatted string with the context
    def format_context_for_prompt(self, relevant_docs: List[Dict[str, Any]]) -> str:
        if not relevant_docs:
            return ""
        
        context_parts = ["Contexto relevante de respostas anteriores:\n"]
        
        for i, doc in enumerate(relevant_docs, 1):
            metadata = doc.get("metadata", {})
            response = metadata.get("response", "")
            email_preview = metadata.get("email_content", "")[:200]
            similarity = doc.get("similarity", 0.0)
            
            context_parts.append(
                f"\n--- Exemplo {i} (similaridade: {similarity:.2f}) ---\n"
                f"Email similar: {email_preview}...\n"
                f"Resposta usada: {response}\n"
            )
        
        return "\n".join(context_parts)
    
    def get_all_documents(
        self,
        limit: Optional[int] = None,
        category: Optional[EmailCategory] = None
    ) -> List[Dict[str, Any]]:
        if not self.collection:
            return []
        
        try:
            all_results = self.collection.get()
            
            if not all_results or not all_results.get("ids"):
                return []
            
            all_documents = []
            
            for i, doc_id in enumerate(all_results["ids"]):
                metadata = all_results["metadatas"][i] if all_results.get("metadatas") else {}
                
                if category and metadata.get("category") != category.value:
                    continue
                
                all_documents.append({
                    "id": doc_id,
                    "document": all_results["documents"][i] if all_results.get("documents") else "",
                    "metadata": metadata
                })
            
            try:
                all_documents.sort(
                    key=lambda x: x["metadata"].get("created_at", ""),
                    reverse=True
                )
            except Exception:
                pass 
            
            return all_documents[:limit] if limit else all_documents
            
        except Exception as e:
            logger.error(f"Error getting all documents: {str(e)}")
            return []
    
    def get_collection_stats(self) -> Dict[str, Any]:
        if not self.collection:
            return {"count": 0, "status": "not_initialized"}
        
        try:
            count = self.collection.count()
            return {
                "count": count,
                "status": "active",
                "db_path": self.db_path
            }
        except Exception as e:
            logger.error(f"Error getting statistics: {str(e)}")
            return {"count": 0, "status": "error", "error": str(e)}
    
    def clear_history(self) -> int:
        if not self.collection:
            raise RuntimeError("Collection not initialized")
        
        try:
            count = self.collection.count()
            
            if count == 0:
                logger.info("No documents to remove")
                return 0
            
            all_results = self.collection.get()
            if all_results and all_results.get("ids"):
                all_ids = all_results["ids"]
                
                self.collection.delete(ids=all_ids)
                
                new_count = self.collection.count()
                logger.info(f"History cleared: {count} documents removed. {new_count} documents remaining.")
                
                return count
            else:
                logger.warning("No IDs found to remove")
                return 0
                
        except Exception as e:
            logger.error(f"Error clearing history: {str(e)}")
            raise

