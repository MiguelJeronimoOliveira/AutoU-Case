"""RAG (Retrieval-Augmented Generation) module for email response generation."""

import logging
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

from app.models import EmailCategory

logger = logging.getLogger(__name__)

# Constants
RAG_DB_PATH = "rag_knowledge_base"
EMBEDDING_MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2" 
TOP_K_RESULTS = 3 
MIN_SIMILARITY_SCORE = 0.5


class RAGRetriever:
    
    def __init__(self, db_path: str = RAG_DB_PATH):
        self.db_path = db_path
        self.embedding_model: Optional[SentenceTransformer] = None
        self.client: Optional[chromadb.ClientAPI] = None
        self.collection: Optional[chromadb.Collection] = None
        self._initialize()
    
    def _initialize(self) -> None:
        try:

            logger.info(f"Carregando modelo de embedding: {EMBEDDING_MODEL_NAME}")
            self.embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)
            logger.info("Modelo de embedding carregado com sucesso")
            
            # create directory for the database if it doesn't exist
            Path(self.db_path).mkdir(parents=True, exist_ok=True)
            
            # initialize ChromaDB
            logger.info(f"Inicializando ChromaDB em: {self.db_path}")
            self.client = chromadb.PersistentClient(
                path=self.db_path,
                settings=Settings(anonymized_telemetry=False)
            )
            
            collection_name = "email_responses"
            try:
                self.collection = self.client.get_collection(name=collection_name)
                logger.info(f"Collection '{collection_name}' encontrada")
            except Exception:
                self.collection = self.client.create_collection(
                    name=collection_name,
                    metadata={"description": "Base de conhecimento de respostas de email"}
                )
                logger.info(f"Collection '{collection_name}' criada")
            
            logger.info("RAG Retriever inicializado com sucesso")
            
        except Exception as e:
            error_msg = f"Erro ao inicializar RAG Retriever: {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
    
    def _generate_embedding(self, text: str) -> List[float]:
        if not self.embedding_model:
            raise RuntimeError("Modelo de embedding não carregado")
        
        try:
            embedding = self.embedding_model.encode(text, convert_to_numpy=True)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Erro ao gerar embedding: {str(e)}")
            raise
    
    # add knowledge to the database
    #return: the id of the document added
    def add_knowledge(
        self,
        email_content: str,
        response: str,
        category: EmailCategory,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:

        if not self.collection:
            raise RuntimeError("Collection não inicializada")
        
        try:
            # create document combining email and response for better search
            document_text = f"Email: {email_content}\nResposta: {response}"
            
            # generate embedding
            embedding = self._generate_embedding(document_text)
            
            # create unique id
            doc_id = str(uuid.uuid4())
            
            doc_metadata = {
                "email_content": email_content[:500],
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
            
            logger.info(f"Documento adicionado à base de conhecimento: {doc_id}")
            return doc_id
            
        except Exception as e:
            logger.error(f"Erro ao adicionar conhecimento: {str(e)}")
            raise
    
    # retrieve relevant context from the database
    #return: a list of relevant documents
    def retrieve_relevant_context(
        self,
        query: str,
        category: Optional[EmailCategory] = None,
        top_k: int = TOP_K_RESULTS
    ) -> List[Dict[str, Any]]:

        if not self.collection:
            logger.warning("Collection não inicializada, retornando lista vazia")
            return []
        
        try:
            query_embedding = self._generate_embedding(query)
            
            # Preparar filtros de metadata
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
            
            logger.debug(f"Recuperados {len(relevant_docs)} documentos relevantes")
            return relevant_docs
            
        except Exception as e:
            logger.error(f"Erro ao recuperar contexto: {str(e)}")
            # return empty list in case of error to not break the flow
            return []
    
    # format documents for prompt
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
    
    # get all documents from the database
    #return: a list of all documents
    def get_all_documents(
        self,
        limit: Optional[int] = None,
        category: Optional[EmailCategory] = None
    ) -> List[Dict[str, Any]]:

        if not self.collection:
            return []
        
        try:
            
            all_documents = []
            seen_ids = set()
            
            query_terms = ["email", "resposta", "solicitação", "contato", "mensagem", "obrigado"]
            
            for term in query_terms:
                try:
                    results = self.collection.query(
                        query_texts=[term],
                        n_results=100
                    )
                    
                    if results["ids"] and len(results["ids"][0]) > 0:
                        for i, doc_id in enumerate(results["ids"][0]):
                            if doc_id not in seen_ids:
                                seen_ids.add(doc_id)
                                metadata = results["metadatas"][0][i]
                                
                                # filter by category if specified
                                if category and metadata.get("category") != category.value:
                                    continue
                                
                                all_documents.append({
                                    "id": doc_id,
                                    "document": results["documents"][0][i],
                                    "metadata": metadata,
                                    "distance": results["distances"][0][i] if results["distances"] else None
                                })
                                
                                if limit and len(all_documents) >= limit:
                                    break
                    
                    if limit and len(all_documents) >= limit:
                        break
                        
                except Exception as e:
                    logger.debug(f"Erro ao buscar com termo '{term}': {str(e)}")
                    continue
            
            try:
                all_documents.sort(
                    key=lambda x: x["metadata"].get("created_at", ""),
                    reverse=True
                )
            except Exception:
                pass 
            
            return all_documents[:limit] if limit else all_documents
            
        except Exception as e:
            logger.error(f"Erro ao obter todos os documentos: {str(e)}")
            return []
    
    # get collection stats
    #return: a dictionary with the stats
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
            logger.error(f"Erro ao obter estatísticas: {str(e)}")
            return {"count": 0, "status": "error", "error": str(e)}

