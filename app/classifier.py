"""Email classification module using ML models."""

import logging
import os
from typing import Optional, Tuple

import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline

from app.core.config import settings
from app.core.constants import EMPTY_EMAIL_CONFIDENCE
from app.models import EmailCategory

logger = logging.getLogger(__name__)


class EmailClassifier:
    
    def __init__(self) -> None:
        self.model_name = settings.get_model_name()
        self.tokenizer: Optional[AutoTokenizer] = None
        self.classifier = None
        self.ml_model = None
        self._load_model()
    
    #load the ML model for email classification
    #@return: None
    def _load_model(self) -> None:
        try:
            logger.info(f"Carregando modelo de classificação: {self.model_name}")
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            
            try:
                self.ml_model = AutoModelForSequenceClassification.from_pretrained(
                    self.model_name
                )
                device = "cuda" if torch.cuda.is_available() else "cpu"
                self.ml_model.to(device)
                self.ml_model.eval()
                logger.info(f"Modelo fine-tuned carregado em {device}")
            except Exception:
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
            logger.error(error_msg)
            raise RuntimeError(error_msg)
    
    #classify the email using ML model
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
        
        if not (self.ml_model or self.classifier):
            raise RuntimeError("Modelo ML não disponível. Verifique se o modelo foi carregado corretamente.")
        
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
        
        logger.debug(
            f"Email classificado como {category.value} "
            f"com confiança {confidence:.2f} (ML)"
        )
        
        return category, confidence, reasoning

