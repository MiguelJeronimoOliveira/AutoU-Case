import json
import logging
import os
from pathlib import Path
from typing import Optional

import torch
from datasets import Dataset, load_dataset
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    TrainingArguments,
    Trainer,
    DataCollatorWithPadding,
    EarlyStoppingCallback
)
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, confusion_matrix

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# configurations
MODEL_NAME = "distilbert-base-uncased"
NUM_LABELS = 2  # productive (1) or unproductive (0)
MAX_LENGTH = 512
BATCH_SIZE = 8
LEARNING_RATE = 2e-5
NUM_EPOCHS = 5
OUTPUT_DIR = "models/email_classifier"
TRAINING_DATA_FILE = "training_data.json"

#load the training data from the JSON file
#@param data_file: path to the JSON file
#@return: Hugging Face dataset
def load_training_data(data_file: str = TRAINING_DATA_FILE) -> Dataset:
    if not os.path.exists(data_file):
        raise FileNotFoundError(
            f"Training data file not found: {data_file}\n"
            f"Execute primeiro: python app/prepare_training_data.py"
        )
    
    # load data from JSON file
    with open(data_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    dataset = Dataset.from_list(data)
    
    logger.info(f"Dataset carregado: {len(dataset)} exemplos")
    return dataset

#tokenize the text of the dataset
#@param examples: examples of the dataset
#@param tokenizer: tokenizer of the model
#@param max_length: maximum length of the sequence
#@return: dictionary with the tokenized inputs
def tokenize_function(examples, tokenizer, max_length: int = MAX_LENGTH):

    return tokenizer(
        examples["text"],
        truncation=True,
        padding=True,
        max_length=max_length
    )

#compute the metrics of the model
#@param eval_pred: tuple with predictions and labels
#@return: dictionary with the metrics
def compute_metrics(eval_pred):
    predictions, labels = eval_pred
    predictions = predictions.argmax(axis=-1)
    
    precision, recall, f1, _ = precision_recall_fscore_support(
        labels, predictions, average="weighted"
    )
    accuracy = accuracy_score(labels, predictions)
    
    return {
        "accuracy": accuracy,
        "f1": f1,
        "precision": precision,
        "recall": recall
    }

#train the model
#@param model_name: name of the model
#@param output_dir: directory to save the model
#@param num_epochs: number of epochs
#@param batch_size: size of the batch
#@param learning_rate: learning rate
#@param train_data_file: path to the training data file
#@param use_gpu: whether to use GPU if available
def train_model(
    model_name: str = MODEL_NAME,
    output_dir: str = OUTPUT_DIR,
    num_epochs: int = NUM_EPOCHS,
    batch_size: int = BATCH_SIZE,
    learning_rate: float = LEARNING_RATE,
    train_data_file: str = TRAINING_DATA_FILE,
    use_gpu: bool = True
):

    logger.info("=" * 60)
    logger.info("Iniciando fine-tuning do DistilBERT")
    logger.info("=" * 60)
    
    # verify GPU
    device = "cuda" if torch.cuda.is_available() and use_gpu else "cpu"
    logger.info(f"Dispositivo: {device}")
    
    logger.info("Carregando dados de treinamento...")
    dataset = load_training_data(train_data_file)
    
    # divide into train and validation (80/20)
    dataset = dataset.train_test_split(test_size=0.2, seed=42)
    train_dataset = dataset["train"]
    eval_dataset = dataset["test"]
    
    logger.info(f"Treino: {len(train_dataset)} exemplos")
    logger.info(f"Validação: {len(eval_dataset)} exemplos")
    
    # load tokenizer and model
    logger.info(f"Carregando modelo: {model_name}")
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(
        model_name,
        num_labels=NUM_LABELS
    )
    
    # tokenize datasets
    logger.info("Tokenizando datasets...")
    train_dataset = train_dataset.map(
        lambda x: tokenize_function(x, tokenizer),
        batched=True,
        remove_columns=["text"]
    )
    eval_dataset = eval_dataset.map(
        lambda x: tokenize_function(x, tokenizer),
        batched=True,
        remove_columns=["text"]
    )
    
    train_dataset = train_dataset.rename_column("label", "labels")
    eval_dataset = eval_dataset.rename_column("label", "labels")
    
    # data collator for dynamic padding
    data_collator = DataCollatorWithPadding(tokenizer=tokenizer)
    
    training_args = TrainingArguments(
        output_dir=output_dir,
        num_train_epochs=num_epochs,
        per_device_train_batch_size=batch_size,
        per_device_eval_batch_size=batch_size,
        learning_rate=learning_rate,
        weight_decay=0.01,
        logging_dir=f"{output_dir}/logs",
        logging_steps=10,
        eval_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        metric_for_best_model="f1",
        greater_is_better=True,
        save_total_limit=3,
        warmup_steps=100,
        fp16=torch.cuda.is_available(),  # use mixed precision if GPU is available
        report_to="none",  # disable wandb/tensorboard by default
    )
    
    # create trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
        data_collator=data_collator,
        compute_metrics=compute_metrics,
        callbacks=[EarlyStoppingCallback(early_stopping_patience=3)]
    )
    
    logger.info("Iniciando treinamento...")
    trainer.train()
    
    logger.info("Avaliando modelo final...")
    eval_results = trainer.evaluate()
    
    logger.info("\n" + "=" * 60)
    logger.info("Resultados da Avaliação:")
    logger.info("=" * 60)
    for key, value in eval_results.items():
        logger.info(f"{key}: {value:.4f}")
    
    # save model and tokenizer
    logger.info(f"\nSalvando modelo em: {output_dir}")
    trainer.save_model()
    tokenizer.save_pretrained(output_dir)
    
    logger.info("\n✅ Treinamento concluído com sucesso!")
    logger.info(f"Modelo salvo em: {output_dir}")
    logger.info("\nPara usar o modelo treinado, atualize MODEL_NAME em classifier.py para:")
    logger.info(f'  MODEL_NAME = "{output_dir}"')


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Treina modelo DistilBERT para classificação de emails")
    parser.add_argument(
        "--model-name",
        type=str,
        default=MODEL_NAME,
        help=f"Nome do modelo base (padrão: {MODEL_NAME})"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=OUTPUT_DIR,
        help=f"Diretório de saída (padrão: {OUTPUT_DIR})"
    )
    parser.add_argument(
        "--epochs",
        type=int,
        default=NUM_EPOCHS,
        help=f"Número de épocas (padrão: {NUM_EPOCHS})"
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=BATCH_SIZE,
        help=f"Tamanho do batch (padrão: {BATCH_SIZE})"
    )
    parser.add_argument(
        "--learning-rate",
        type=float,
        default=LEARNING_RATE,
        help=f"Taxa de aprendizado (padrão: {LEARNING_RATE})"
    )
    parser.add_argument(
        "--data-file",
        type=str,
        default=TRAINING_DATA_FILE,
        help=f"Arquivo de dados (padrão: {TRAINING_DATA_FILE})"
    )
    parser.add_argument(
        "--no-gpu",
        action="store_true",
        help="Não usar GPU mesmo se disponível"
    )
    
    args = parser.parse_args()
    
    train_model(
        model_name=args.model_name,
        output_dir=args.output_dir,
        num_epochs=args.epochs,
        batch_size=args.batch_size,
        learning_rate=args.learning_rate,
        train_data_file=args.data_file,
        use_gpu=not args.no_gpu
    )

