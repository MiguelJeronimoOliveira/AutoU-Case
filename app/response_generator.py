"""Email response generation module using Google Gemini."""

import logging
import os
from typing import Optional

import google.generativeai as genai
from dotenv import load_dotenv

from app.models import EmailCategory

load_dotenv()

logger = logging.getLogger(__name__)

# Constants
GEMINI_MODEL_NAME = "gemini-2.5-flash"
EMAIL_PREVIEW_LENGTH = 2000
MAX_RESPONSE_LENGTH = 1000
GENERATION_TEMPERATURE = 0.7

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
    "Você é um assistente profissional de email. "
    "Gere uma resposta profissional e adequada em português brasileiro para o seguinte email.\n\n"
    "Email recebido:\n{email_content}\n\n"
    "Gere uma resposta profissional, cordial e objetiva. "
    "A resposta deve ser direta, mas educada, e indicar que a solicitação será analisada."
)

UNPRODUCTIVE_PROMPT_TEMPLATE = (
    "Você é um assistente profissional de email. "
    "Gere uma resposta educada e agradecida em português brasileiro para o seguinte email.\n\n"
    "Email recebido:\n{email_content}\n\n"
    "Gere uma resposta breve, cordial e agradecida, reconhecendo a mensagem recebida."
)


class ResponseGenerator:
    
    def __init__(self) -> None:
        self.model_name = GEMINI_MODEL_NAME
        self.model: Optional[genai.GenerativeModel] = None
        self._load_model()
    
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
    
    def _create_productive_prompt(self, email_content: str) -> str:
        email_preview = self._truncate_email_content(email_content)
        return PRODUCTIVE_PROMPT_TEMPLATE.format(email_content=email_preview)
    
    def _create_unproductive_prompt(self, email_content: str) -> str:
        email_preview = self._truncate_email_content(email_content)
        return UNPRODUCTIVE_PROMPT_TEMPLATE.format(email_content=email_preview)
    
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
    
    def generate_response(
        self,
        email_content: str,
        category: EmailCategory
    ) -> str:
        if not email_content or not email_content.strip():
            logger.warning("Conteúdo de email vazio fornecido")
            return self._get_template_response(category)
        
        if category == EmailCategory.PRODUCTIVE:
            prompt = self._create_productive_prompt(email_content)
        else:
            prompt = self._create_unproductive_prompt(email_content)
        
        try:
            response = self._generate_with_gemini(prompt)
            logger.debug(f"Resposta gerada para email {category.value}")
            return response
        except Exception as e:
            # Fallback to template-based responses if model fails
            logger.warning(
                f"Geração com modelo falhou, usando template: {str(e)}"
            )
            return self._get_template_response(category)

