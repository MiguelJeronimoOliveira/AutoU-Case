"""Email classification module using keyword-based and ML approaches."""

import logging
import os
from typing import Optional, Tuple

import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline

from app.models import EmailCategory

logger = logging.getLogger(__name__)

# Constants
# try to use fine-tuned model if it exists, otherwise use the base model
DEFAULT_MODEL_NAME = "distilbert-base-uncased"
FINE_TUNED_MODEL_PATH = "models/email_classifier"

# verify if fine-tuned model exists
if os.path.exists(FINE_TUNED_MODEL_PATH) and os.path.isdir(FINE_TUNED_MODEL_PATH):
    MODEL_NAME = FINE_TUNED_MODEL_PATH
    logger.info(f"Usando modelo fine-tunado: {MODEL_NAME}")
else:
    MODEL_NAME = DEFAULT_MODEL_NAME
    logger.info(f"Usando modelo base: {MODEL_NAME}")

BASE_CONFIDENCE = 0.5
CONFIDENCE_INCREMENT = 0.1
MAX_CONFIDENCE = 0.9
EMPTY_EMAIL_CONFIDENCE = 0.0
USE_ML_MODEL = True  # Flag to enable/disable ML model

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
    
    def __init__(self, use_ml_model: bool = USE_ML_MODEL) -> None:
        self.model_name = MODEL_NAME
        self.use_ml_model = use_ml_model
        self.tokenizer: Optional[AutoTokenizer] = None
        self.classifier = None
        self.ml_model = None
        self._load_model()
    
    def _load_model(self) -> None:

        if not self.use_ml_model:
            logger.info("ML model disabled, using only keyword-based classification")
            return
        
        try:
            logger.info(f"Carregando modelo de classificação: {self.model_name}")
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            
            # Tenta carregar como modelo fine-tunado primeiro
            try:
                self.ml_model = AutoModelForSequenceClassification.from_pretrained(
                    self.model_name
                )
                device = "cuda" if torch.cuda.is_available() else "cpu"
                self.ml_model.to(device)
                self.ml_model.eval()
                logger.info(f"Modelo fine-tuned carregado em {device}")
            except Exception:
                # if it fails, use pipeline (base model)
                device = 0 if torch.cuda.is_available() else -1
                self.classifier = pipeline(
                    "text-classification",
                    model=self.model_name,
                    tokenizer=self.tokenizer,
                    device=device
                )
                logger.info("Pipeline de classificação carregado")
            
            logger.info("Modelo de classificação carregado com sucesso")
        except Exception as e:
            error_msg = f"Erro ao carregar modelo de classificação: {str(e)}"
            logger.warning(error_msg)
            logger.warning("Continuando com classificação baseada em keywords")
            self.use_ml_model = False
    
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
    
    #classify the email using the ML model
    #@param email_content: content of the email
    #@return: tuple with the category, confidence and reasoning
    def _classify_with_ml(self, email_content: str) -> Tuple[EmailCategory, float, str]:

        if self.ml_model and self.tokenizer:
            device = next(self.ml_model.parameters()).device
            inputs = self.tokenizer(
                email_content,
                truncation=True,
                padding=True,
                max_length=512,
                return_tensors="pt"
            ).to(device)
            
            with torch.no_grad():
                outputs = self.ml_model(**inputs)
                predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
                predicted_class = predictions.argmax(dim=-1).item()
                confidence = predictions[0][predicted_class].item()
            
            # 0 = unproductive, 1 = productive
            category = EmailCategory.PRODUCTIVE if predicted_class == 1 else EmailCategory.UNPRODUCTIVE
            reasoning = f"Classificação ML: {category.value} (confiança: {confidence:.2f})"
            
        elif self.classifier:
            # use pipeline
            result = self.classifier(email_content)[0]
            label = result["label"].lower()
            confidence = result["score"]
            
            if "productive" in label or "pos" in label or "1" in label:
                category = EmailCategory.PRODUCTIVE
            else:
                category = EmailCategory.UNPRODUCTIVE
            
            reasoning = f"Classificação ML (pipeline): {category.value} (confiança: {confidence:.2f})"
        else:
            raise RuntimeError("Modelo ML não disponível")
        
        return category, confidence, reasoning
  
    #classify the email using the keywords
    #@param email_content: content of the email
    #@return: tuple with the category, confidence and reasoning
    def _classify_with_keywords(self, email_content: str) -> Tuple[EmailCategory, float, str]:

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
                f"Email contém {productive_count} palavras-chave produtivas "
                f"indicando que ação é necessária"
            )
        elif unproductive_count > productive_count:
            category = EmailCategory.UNPRODUCTIVE
            confidence = self._calculate_confidence(unproductive_count)
            reasoning = (
                f"Email contém {unproductive_count} palavras-chave não produtivas "
                f"indicando que nenhuma ação imediata é necessária"
            )
        else:
            category = EmailCategory.PRODUCTIVE
            confidence = BASE_CONFIDENCE
            reasoning = (
                "Classificação de email é incerta, "
                "padrão definido como produtivo"
            )
        
        return category, confidence, reasoning
    
    #classify the email
    #@param email_content: content of the email
    #@return: tuple with the category, confidence and reasoning
    def classify_email(
        self,
        email_content: str
    ) -> Tuple[EmailCategory, float, str]:
        if not email_content or not email_content.strip():
            return (
                EmailCategory.UNPRODUCTIVE,
                EMPTY_EMAIL_CONFIDENCE,
                "Conteúdo do email vazio"
            )
        
        # try to use ML model 
        if self.use_ml_model and (self.ml_model or self.classifier):
            try:
                category, confidence, reasoning = self._classify_with_ml(email_content)
                logger.debug(
                    f"Email classificado como {category.value} "
                    f"com confiança {confidence:.2f} (ML)"
                )
                return category, confidence, reasoning
            except Exception as e:
                logger.warning(f"Erro ao usar modelo ML: {e}. Usando fallback de keywords.")
        
        # fallback to keywords
        category, confidence, reasoning = self._classify_with_keywords(email_content)
        logger.debug(
            f"Email classificado como {category.value} "
            f"com confiança {confidence:.2f} (keywords)"
        )
        
        return category, confidence, reasoning

