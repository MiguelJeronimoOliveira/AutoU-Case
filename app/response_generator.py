"""Email response generation module using Google Gemini with RAG."""

import logging
from typing import Optional

import google.generativeai as genai

from app.core.config import settings
from app.core.constants import (
    EMAIL_PREVIEW_LENGTH,
    GENERATION_TEMPERATURE,
    MAX_RESPONSE_LENGTH,
    PRODUCTIVE_PROMPT_TEMPLATE,
    PRODUCTIVE_TEMPLATE,
    UNPRODUCTIVE_PROMPT_TEMPLATE,
    UNPRODUCTIVE_TEMPLATE,
)
from app.models import EmailCategory
from app.rag_retriever import RAGRetriever

logger = logging.getLogger(__name__)


class ResponseGenerator:
    
    def __init__(self, use_rag: Optional[bool] = None) -> None:
        self.model_name = settings.gemini_model_name
        self.model: Optional[genai.GenerativeModel] = None
        self.use_rag = use_rag if use_rag is not None else settings.rag_enabled
        self.rag_retriever: Optional[RAGRetriever] = None
        
        self._load_model()
        
        if self.use_rag:
            try:
                self.rag_retriever = RAGRetriever()
                logger.info("RAG Retriever inicializado com sucesso")
            except Exception as e:
                logger.warning(f"Erro ao inicializar RAG Retriever: {str(e)}. Continuando sem RAG.")
                self.use_rag = False
                self.rag_retriever = None
    
    #load the Gemini model for response generation
    #@return: None
    def _load_model(self) -> None:
        try:
            api_key = settings.gemini_api_key
            if not api_key:
                raise ValueError(
                    "GEMINI_API_KEY não encontrada nas variáveis de ambiente. "
                    "Por favor, defina a variável GEMINI_API_KEY no arquivo .env ou nas variáveis de ambiente."
                )
            
            logger.info(f"Configurando Google Gemini: {self.model_name}")
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel(self.model_name)
            logger.info("Modelo Gemini carregado com sucesso")
        except Exception as e:
            error_msg = f"Erro ao carregar modelo Gemini: {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
    
    #truncate email content to maximum preview length
    #@param email_content: email content to truncate
    #@return: truncated email content
    def _truncate_email_content(self, email_content: str) -> str:
        if len(email_content) > EMAIL_PREVIEW_LENGTH:
            return email_content[:EMAIL_PREVIEW_LENGTH] + "..."
        return email_content
    
    #retrieve relevant context from RAG database
    #@param email_content: email content to search for
    #@param category: category of the email
    #@return: formatted context string
    def _retrieve_rag_context(self, email_content: str, category: EmailCategory) -> str:
        if not self.use_rag or not self.rag_retriever:
            return ""
        
        try:
            relevant_docs = self.rag_retriever.retrieve_relevant_context(
                query=email_content,
                category=category
            )
            
            if relevant_docs:
                context = self.rag_retriever.format_context_for_prompt(relevant_docs)
                logger.debug(f"Contexto RAG recuperado: {len(relevant_docs)} documentos")
                return context
            
            return ""
        except Exception as e:
            logger.warning(f"Erro ao recuperar contexto RAG: {str(e)}")
            return ""
    
    #create prompt for productive email responses
    #@param email_content: content of the email
    #@param category: category of the email
    #@return: formatted prompt string
    def _create_productive_prompt(self, email_content: str, category: EmailCategory) -> str:
        email_preview = self._truncate_email_content(email_content)
        rag_context = self._retrieve_rag_context(email_content, category)
        
        if not rag_context:
            rag_context = ""
        
        return PRODUCTIVE_PROMPT_TEMPLATE.format(
            email_content=email_preview,
            rag_context=rag_context
        )
    
    #create prompt for unproductive email responses
    #@param email_content: content of the email
    #@param category: category of the email
    #@return: formatted prompt string
    def _create_unproductive_prompt(self, email_content: str, category: EmailCategory) -> str:
        email_preview = self._truncate_email_content(email_content)
        rag_context = self._retrieve_rag_context(email_content, category)
        
        if not rag_context:
            rag_context = ""
        
        return UNPRODUCTIVE_PROMPT_TEMPLATE.format(
            email_content=email_preview,
            rag_context=rag_context
        )
    
    #generate response using Gemini model
    #@param prompt: prompt to send to the model
    #@return: generated response text
    def _generate_with_gemini(self, prompt: str) -> str:
        if not self.model:
            raise RuntimeError("Modelo não carregado")
        
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=GENERATION_TEMPERATURE,
                    max_output_tokens=MAX_RESPONSE_LENGTH * 2,
                )
            )
            
            generated_text = response.text.strip()
            
            if len(generated_text) > MAX_RESPONSE_LENGTH:
                generated_text = generated_text[:MAX_RESPONSE_LENGTH].rsplit(' ', 1)[0] + "..."
            
            return generated_text
        except Exception as e:
            logger.error(f"Erro ao gerar resposta com Gemini: {str(e)}")
            raise
    
    #get template response based on category
    #@param category: email category
    #@return: template response string
    def _get_template_response(self, category: EmailCategory) -> str:
        if category == EmailCategory.PRODUCTIVE:
            return PRODUCTIVE_TEMPLATE
        return UNPRODUCTIVE_TEMPLATE
    
    #save response to RAG knowledge base
    #@param email_content: content of the email
    #@param response: generated response
    #@param category: category of the email
    #@return: None
    def _save_response_to_knowledge_base(
        self,
        email_content: str,
        response: str,
        category: EmailCategory
    ) -> None:
        if not self.use_rag or not self.rag_retriever:
            return
        
        try:
            self.rag_retriever.add_knowledge(
                email_content=email_content,
                response=response,
                category=category
            )
            logger.info("Resposta salva na base de conhecimento RAG")
        except Exception as e:
            logger.warning(f"Erro ao salvar resposta na base de conhecimento: {str(e)}")
    
    #generate response for email using Gemini model
    #@param email_content: content of the email
    #@param category: category of the email
    #@param save_to_knowledge_base: whether to save response to RAG
    #@return: generated response text
    def generate_response(
        self,
        email_content: str,
        category: EmailCategory,
        save_to_knowledge_base: bool = True
    ) -> str:
        if not email_content or not email_content.strip():
            logger.warning("Conteúdo de email vazio fornecido")
            return self._get_template_response(category)
        
        if category == EmailCategory.PRODUCTIVE:
            prompt = self._create_productive_prompt(email_content, category)
        else:
            prompt = self._create_unproductive_prompt(email_content, category)
        
        try:
            response = self._generate_with_gemini(prompt)
            logger.debug(f"Resposta gerada para email {category.value}")
            
            # save to knowledge base for continuous training
            if save_to_knowledge_base and response:
                self._save_response_to_knowledge_base(
                    email_content=email_content,
                    response=response,
                    category=category
                )
            
            return response
        except Exception as e:
            logger.warning(
                f"Geração com modelo falhou, usando template: {str(e)}"
            )
            template_response = self._get_template_response(category)
            
            if save_to_knowledge_base and template_response:
                try:
                    self._save_response_to_knowledge_base(
                        email_content=email_content,
                        response=template_response,
                        category=category
                    )
                except Exception:
                    pass
            
            return template_response

