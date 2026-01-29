"""Email response generation module using Google Gemini with RAG."""

import logging
import os
from typing import Optional

import google.generativeai as genai
from dotenv import load_dotenv

from app.models import EmailCategory
from app.rag_retriever import RAGRetriever

load_dotenv()

logger = logging.getLogger(__name__)

# Constants
GEMINI_MODEL_NAME = "gemini-2.5-flash"
EMAIL_PREVIEW_LENGTH = 20000
MAX_RESPONSE_LENGTH = 1000
GENERATION_TEMPERATURE = 0.7
USE_RAG = True

# Template responses
PRODUCTIVE_TEMPLATE = (
    "Obrigado por entrar em contato conosco. Recebemos sua solicitação "
    "e a analisaremos em breve. Nossa equipe entrará em contato o mais "
    "rápido possível com uma solução."
)

UNPRODUCTIVE_TEMPLATE = (
    "Obrigado pela sua mensagem. Agradecemos suas palavras gentis e "
    "ficamos felizes em receber seu contato."
)

# Prompt templates
PRODUCTIVE_PROMPT_TEMPLATE = (
    "Você é um assistente especializado APENAS em gerar respostas profissionais para emails. "
    "Sua única função é criar respostas de email adequadas e profissionais.\n\n"
    "REGRAS OBRIGATÓRIAS:\n"
    "1. Analise o idioma do email recebido e responda APENAS no idioma do email recebido (português ou inglês). "
    "   Se o email estiver em português, responda em português. Se estiver em inglês, responda em inglês.\n"
    "2. NÃO invente informações, dados, prazos ou detalhes que não foram mencionados no email ou no contexto fornecido.\n"
    "3. NÃO saia do escopo de resposta de email. Não ofereça serviços não solicitados.\n"
    "4. Use APENAS informações do email recebido e do contexto RAG fornecido (se houver). "
    "   Não adicione informações externas ou conhecimento geral não relacionado.\n"
    "5. Seja direto, profissional e cordial. Evite textos longos ou desnecessários.\n\n"
    "{rag_context}"
    "Email recebido:\n{email_content}\n\n"
    "Gere uma resposta profissional de email seguindo rigorosamente as regras acima. "
    "A resposta deve ser direta, educada e agradecida. "
    "Se houver contexto relevante acima, use-o como referência para manter consistência, "
    "mas NÃO invente informações que não estejam explicitamente no contexto ou no email."
)

UNPRODUCTIVE_PROMPT_TEMPLATE = (
    "Você é um assistente especializado APENAS em gerar respostas profissionais para emails. "
    "Sua única função é criar respostas de email adequadas e profissionais.\n\n"
    "REGRAS OBRIGATÓRIAS:\n"
    "1. Analise o idioma do email recebido e responda APENAS no idioma do email recebido (português ou inglês). "
    "   Se o email estiver em português, responda em português. Se estiver em inglês, responda em inglês.\n"
    "2. NÃO invente informações, dados, prazos ou detalhes que não foram mencionados no email ou no contexto fornecido.\n"
    "3. NÃO saia do escopo de resposta de email. Não ofereça serviços não solicitados.\n"
    "4. Use APENAS informações do email recebido e do contexto RAG fornecido (se houver). "
    "   Não adicione informações externas ou conhecimento geral não relacionado.\n"
    "5. Seja direto, profissional e cordial. Evite textos longos ou desnecessários.\n\n"
    "{rag_context}"
    "Email recebido:\n{email_content}\n\n"
    "Gere uma resposta breve e agradecida de email seguindo rigorosamente as regras acima. "
    "A resposta deve ser agradecida e profissional. "
    "Se houver contexto relevante acima, use-o como referência para manter consistência, "
    "mas NÃO invente informações que não estejam explicitamente no contexto ou no email."
)


class ResponseGenerator:
    
    def __init__(self, use_rag: bool = USE_RAG) -> None:
        self.model_name = GEMINI_MODEL_NAME
        self.model: Optional[genai.GenerativeModel] = None
        self.use_rag = use_rag
        self.rag_retriever: Optional[RAGRetriever] = None
        
        self._load_model()
        
        # initialize RAG if enabled
        if self.use_rag:
            try:
                self.rag_retriever = RAGRetriever()
                logger.info("RAG Retriever inicializado com sucesso")
            except Exception as e:
                logger.warning(f"Erro ao inicializar RAG Retriever: {str(e)}. Continuando sem RAG.")
                self.use_rag = False
                self.rag_retriever = None
    
    def _load_model(self) -> None:
        try:
            api_key = os.getenv("GEMINI_API_KEY")
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
    
    def _truncate_email_content(self, email_content: str) -> str:
        if len(email_content) > EMAIL_PREVIEW_LENGTH:
            return email_content[:EMAIL_PREVIEW_LENGTH] + "..."
        return email_content
    
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
    
    def _create_productive_prompt(self, email_content: str, category: EmailCategory) -> str:
        email_preview = self._truncate_email_content(email_content)
        rag_context = self._retrieve_rag_context(email_content, category)
        
        if not rag_context:
            rag_context = ""
        
        return PRODUCTIVE_PROMPT_TEMPLATE.format(
            email_content=email_preview,
            rag_context=rag_context
        )
    
    def _create_unproductive_prompt(self, email_content: str, category: EmailCategory) -> str:
        email_preview = self._truncate_email_content(email_content)
        rag_context = self._retrieve_rag_context(email_content, category)
        
        if not rag_context:
            rag_context = ""
        
        return UNPRODUCTIVE_PROMPT_TEMPLATE.format(
            email_content=email_preview,
            rag_context=rag_context
        )
    
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
    
    def _get_template_response(self, category: EmailCategory) -> str:
        if category == EmailCategory.PRODUCTIVE:
            return PRODUCTIVE_TEMPLATE
        return UNPRODUCTIVE_TEMPLATE
    
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
            # fallback to template-based responses if model fails
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

