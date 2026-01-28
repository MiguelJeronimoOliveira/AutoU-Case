"""Email classification module using keyword-based and ML approaches."""

import logging
from typing import Optional, Tuple

import torch
from transformers import AutoTokenizer, pipeline

from app.models import EmailCategory

logger = logging.getLogger(__name__)

# Constants
MODEL_NAME = "distilbert-base-uncased"
BASE_CONFIDENCE = 0.5
CONFIDENCE_INCREMENT = 0.1
MAX_CONFIDENCE = 0.9
EMPTY_EMAIL_CONFIDENCE = 0.0

PRODUCTIVE_KEYWORDS = [
    "suporte",
    "ajuda",
    "problema",
    "erro",
    "bug",
    "solicitação",
    "pedido",
    "pergunta",
    "questão",
    "atualização",
    "status",
    "caso",
    "ticket",
    "urgente",
    "ação",
    "necessário",
    "requerido",
    "por favor",
    "precisa",
    "assistência",
    "técnico",
    "correção",
    "corrigir",
]

UNPRODUCTIVE_KEYWORDS = [
    "obrigado",
    "obrigada",
    "agradeço",
    "agradecemos",
    "parabéns",
    "apreciação",
    "gratidão",
    "saudação",
    "olá",
    "oi",
    "cordiais saudações",
    "saudações",
    "cumprimentos",
    "atenciosamente",
]


class EmailClassifier:
    
    def __init__(self) -> None:
        self.model_name = MODEL_NAME
        self.tokenizer: Optional[AutoTokenizer] = None
        self.classifier = None
        self._load_model()
    
    def _load_model(self) -> None:

        try:
            logger.info(f"Loading classification model: {self.model_name}")
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            
            device = 0 if torch.cuda.is_available() else -1
            self.classifier = pipeline(
                "text-classification",
                model=self.model_name,
                tokenizer=self.tokenizer,
                device=device
            )
            logger.info("Classification model loaded successfully")
        except Exception as e:
            error_msg = f"Error loading classification model: {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
    
    def _count_keywords(self, text: str, keywords: list[str]) -> int:

        text_lower = text.lower()
        return sum(1 for keyword in keywords if keyword in text_lower)
    
    def _calculate_confidence(
        self,
        keyword_count: int,
        base_confidence: float = BASE_CONFIDENCE
    ) -> float:

        confidence = base_confidence + (keyword_count * CONFIDENCE_INCREMENT)
        return min(MAX_CONFIDENCE, confidence)
    
    def classify_email(
        self,
        email_content: str
    ) -> Tuple[EmailCategory, float, str]:

        if not email_content or not email_content.strip():
            return (
                EmailCategory.UNPRODUCTIVE,
                EMPTY_EMAIL_CONFIDENCE,
                "Empty email content"
            )
        
        productive_count = self._count_keywords(
            email_content,
            PRODUCTIVE_KEYWORDS
        )
        unproductive_count = self._count_keywords(
            email_content,
            UNPRODUCTIVE_KEYWORDS
        )
        
        if productive_count > unproductive_count:
            category = EmailCategory.PRODUCTIVE
            confidence = self._calculate_confidence(productive_count)
            reasoning = (
                f"Email contains {productive_count} productive keywords "
                f"indicating action is required"
            )
        elif unproductive_count > productive_count:
            category = EmailCategory.UNPRODUCTIVE
            confidence = self._calculate_confidence(unproductive_count)
            reasoning = (
                f"Email contains {unproductive_count} unproductive keywords "
                f"indicating no immediate action needed"
            )
        else:
            category = EmailCategory.PRODUCTIVE
            confidence = BASE_CONFIDENCE
            reasoning = (
                "Email classification is uncertain, "
                "defaulting to productive"
            )
        
        logger.debug(
            f"Classified email as {category.value} "
            f"with confidence {confidence:.2f}"
        )
        
        return category, confidence, reasoning

