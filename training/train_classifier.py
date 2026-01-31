import json
import logging
import os
import random
import numpy as np
from pathlib import Path
from typing import Optional, Dict

import torch
from datasets import Dataset, load_dataset, ClassLabel
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    TrainingArguments,
    Trainer,
    DataCollatorWithPadding,
    EarlyStoppingCallback
)
from sklearn.metrics import (
    accuracy_score, 
    precision_recall_fscore_support, 
    confusion_matrix,
    classification_report
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Configurações para reprodutibilidade
def set_seed(seed: int = 42):
    """Define seed para reprodutibilidade."""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False

# Configurations
MODEL_NAME = "bert-base-multilingual-cased"  # BERTimbau - especializado em português brasileiro
NUM_LABELS = 2  # productive (1) or unproductive (0)
MAX_LENGTH = 512
BATCH_SIZE = 8
LEARNING_RATE = 2e-5
NUM_EPOCHS = 10  # Aumentado, mas com early stopping
OUTPUT_DIR = "models/email_classifier-pt-en"
TRAINING_DATA_FILE = "training_data.pt-en.json"
SEED = 42  # Seed para reprodutibilidade

#load the training data from the JSON file
#@param data_file: path to the JSON file
#@return: Hugging Face dataset
def load_training_data(data_file: str = TRAINING_DATA_FILE) -> Dataset:
    if not os.path.exists(data_file):
        raise FileNotFoundError(
            f"Training data file not found: {data_file}\n"
            f"Execute primeiro: python training/training_data.py"
        )
    
    # load data from JSON file
    with open(data_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    dataset = Dataset.from_list(data)
    
    # Verifica balanceamento das classes
    labels = [item["label"] for item in data]
    from collections import Counter
    label_counts = Counter(labels)
    total = len(labels)
    
    logger.info(f"Dataset carregado: {total} exemplos")
    logger.info(f"Distribuição de classes:")
    for label, count in sorted(label_counts.items()):
        percentage = (count / total) * 100
        label_name = "Produtivo" if label == 1 else "Não Produtivo"
        logger.info(f"  {label_name} (label {label}): {count} ({percentage:.2f}%)")
    
    # Avisa se há desbalanceamento significativo
    if len(label_counts) == 2:
        min_count = min(label_counts.values())
        max_count = max(label_counts.values())
        imbalance_ratio = max_count / min_count
        if imbalance_ratio > 1.5:
            logger.warning(f"⚠️  Desbalanceamento detectado (razão {imbalance_ratio:.2f}:1)")
            logger.warning("   Considere usar class_weight no modelo ou balancear os dados")
    
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
    
    # Métricas gerais (weighted average)
    precision_weighted, recall_weighted, f1_weighted, _ = precision_recall_fscore_support(
        labels, predictions, average="weighted", zero_division=0
    )
    
    # Métricas por classe
    precision_per_class, recall_per_class, f1_per_class, support = precision_recall_fscore_support(
        labels, predictions, average=None, zero_division=0
    )
    
    # Métricas macro average (média simples entre classes)
    precision_macro, recall_macro, f1_macro, _ = precision_recall_fscore_support(
        labels, predictions, average="macro", zero_division=0
    )
    
    accuracy = accuracy_score(labels, predictions)
    
    # Confusion matrix
    cm = confusion_matrix(labels, predictions)
    
    metrics = {
        "accuracy": accuracy,
        "f1_weighted": f1_weighted,
        "precision_weighted": precision_weighted,
        "recall_weighted": recall_weighted,
        "f1_macro": f1_macro,
        "precision_macro": precision_macro,
        "recall_macro": recall_macro,
        # Métricas por classe
        "f1_class_0": f1_per_class[0] if len(f1_per_class) > 0 else 0.0,
        "precision_class_0": precision_per_class[0] if len(precision_per_class) > 0 else 0.0,
        "recall_class_0": recall_per_class[0] if len(recall_per_class) > 0 else 0.0,
        "f1_class_1": f1_per_class[1] if len(f1_per_class) > 1 else 0.0,
        "precision_class_1": precision_per_class[1] if len(precision_per_class) > 1 else 0.0,
        "recall_class_1": recall_per_class[1] if len(recall_per_class) > 1 else 0.0,
    }
    
    # Usa f1_macro como métrica principal (melhor para dados desbalanceados)
    metrics["f1"] = f1_macro
    
    return metrics

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
    use_gpu: bool = True,
    seed: int = SEED
):

    logger.info("=" * 60)
    logger.info("Iniciando fine-tuning do BERTimbau (BERT para português)")
    logger.info("=" * 60)
    
    # verify GPU
    device = "cuda" if torch.cuda.is_available() and use_gpu else "cpu"
    logger.info(f"Dispositivo: {device}")
    
    # Define seed para reprodutibilidade
    set_seed(seed)
    
    logger.info("Carregando dados de treinamento...")
    dataset = load_training_data(train_data_file)
    
    # Converte coluna label para ClassLabel para permitir estratificação
    dataset = dataset.cast_column("label", ClassLabel(num_classes=2, names=["Não Produtivo", "Produtivo"]))
    
    # Divide em train/val/test (70/15/15) com estratificação
    # Primeiro divide em train e temp (temp = val + test)
    dataset_split = dataset.train_test_split(
        test_size=0.3, 
        seed=seed,
        stratify_by_column="label"  # Estratificação por label
    )
    train_dataset = dataset_split["train"]
    temp_dataset = dataset_split["test"]
    
    # Divide temp em val e test (50/50 de temp = 15/15 do total)
    val_test_split = temp_dataset.train_test_split(
        test_size=0.5,
        seed=seed,
        stratify_by_column="label"
    )
    eval_dataset = val_test_split["train"]  # Validação
    test_dataset = val_test_split["test"]    # Teste final
    
    logger.info(f"\nDivisão dos dados:")
    logger.info(f"  Treino: {len(train_dataset)} exemplos ({len(train_dataset)/len(dataset)*100:.1f}%)")
    logger.info(f"  Validação: {len(eval_dataset)} exemplos ({len(eval_dataset)/len(dataset)*100:.1f}%)")
    logger.info(f"  Teste: {len(test_dataset)} exemplos ({len(test_dataset)/len(dataset)*100:.1f}%)")
    
    # load tokenizer and model
    logger.info(f"Carregando modelo: {model_name}")
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    
    # Configura dropout para regularização
    model = AutoModelForSequenceClassification.from_pretrained(
        model_name,
        num_labels=NUM_LABELS,
        hidden_dropout_prob=0.3,  # Dropout nas camadas ocultas
        attention_probs_dropout_prob=0.2,  # Dropout na atenção
    )
    
    # Calcula class weights para lidar com desbalanceamento (se necessário)
    from collections import Counter
    # Converte ClassLabel para int se necessário
    labels = [int(item["label"]) if hasattr(item["label"], '__int__') else item["label"] for item in train_dataset]
    label_counts = Counter(labels)
    total = len(labels)
    
    if len(label_counts) == 2:
        # Calcula weights inversamente proporcionais à frequência
        class_weights = [
            total / (len(label_counts) * label_counts.get(0, 1)),
            total / (len(label_counts) * label_counts.get(1, 1))
        ]
        logger.info(f"Class weights calculados: {class_weights}")
        logger.info("  (Usando loss function padrão - class weights podem ser adicionados se necessário)")
    
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
    test_dataset = test_dataset.map(
        lambda x: tokenize_function(x, tokenizer),
        batched=True,
        remove_columns=["text"]
    )
    
    train_dataset = train_dataset.rename_column("label", "labels")
    eval_dataset = eval_dataset.rename_column("label", "labels")
    test_dataset = test_dataset.rename_column("label", "labels")
    
    # data collator for dynamic padding
    data_collator = DataCollatorWithPadding(tokenizer=tokenizer)
    
    # Calcula warmup steps proporcional ao dataset (10% dos steps ou mínimo 100)
    num_training_steps = len(train_dataset) // batch_size * num_epochs
    warmup_steps = max(100, int(num_training_steps * 0.1))
    
    logger.info(f"\nConfigurações de treinamento:")
    logger.info(f"  Total de steps: {num_training_steps}")
    logger.info(f"  Warmup steps: {warmup_steps}")
    logger.info(f"  Learning rate: {learning_rate}")
    logger.info(f"  Weight decay: 0.01")
    logger.info(f"  Dropout: 0.3 (hidden), 0.2 (attention)")
    
    training_args = TrainingArguments(
        output_dir=output_dir,
        num_train_epochs=num_epochs,
        per_device_train_batch_size=batch_size,
        per_device_eval_batch_size=batch_size * 2,  # Batch maior para validação (mais rápido)
        learning_rate=learning_rate,
        weight_decay=0.01,  # Regularização L2
        logging_dir=f"{output_dir}/logs",
        logging_steps=50,  # Log mais frequente
        eval_strategy="steps",  # Avalia por steps, não só por epoch
        eval_steps=max(100, len(train_dataset) // (batch_size * 4)),  # 4 avaliações por epoch
        save_strategy="steps",
        save_steps=max(100, len(train_dataset) // (batch_size * 4)),
        load_best_model_at_end=True,
        metric_for_best_model="f1_macro",  # Usa f1_macro (melhor para dados desbalanceados)
        greater_is_better=True,
        save_total_limit=3,  # Mantém apenas 3 checkpoints
        warmup_steps=warmup_steps,
        lr_scheduler_type="linear",  # Learning rate scheduling linear
        fp16=torch.cuda.is_available(),  # Mixed precision se GPU disponível
        report_to="none",  # Desabilita wandb/tensorboard por padrão
        gradient_accumulation_steps=2,  # Acumula gradientes (efetivamente batch_size * 2)
        dataloader_num_workers=0,  # Evita problemas de multiprocessing no Windows
        seed=seed,  # Seed para reprodutibilidade
        remove_unused_columns=False,
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
    
    logger.info("\n" + "=" * 60)
    logger.info("Iniciando treinamento...")
    logger.info("=" * 60)
    
    trainer.train()
    
    logger.info("\n" + "=" * 60)
    logger.info("Avaliando modelo no conjunto de VALIDAÇÃO...")
    logger.info("=" * 60)
    eval_results = trainer.evaluate(eval_dataset=eval_dataset)
    
    logger.info("\nResultados da Validação:")
    logger.info("-" * 60)
    logger.info(f"Accuracy: {eval_results.get('eval_accuracy', 0):.4f}")
    logger.info(f"F1 Macro: {eval_results.get('eval_f1_macro', 0):.4f}")
    logger.info(f"F1 Weighted: {eval_results.get('eval_f1_weighted', 0):.4f}")
    logger.info(f"Precision Macro: {eval_results.get('eval_precision_macro', 0):.4f}")
    logger.info(f"Recall Macro: {eval_results.get('eval_recall_macro', 0):.4f}")
    logger.info("\nMétricas por classe (Validação):")
    logger.info(f"  Classe 0 (Não Produtivo):")
    logger.info(f"    Precision: {eval_results.get('eval_precision_class_0', 0):.4f}")
    logger.info(f"    Recall: {eval_results.get('eval_recall_class_0', 0):.4f}")
    logger.info(f"    F1: {eval_results.get('eval_f1_class_0', 0):.4f}")
    logger.info(f"  Classe 1 (Produtivo):")
    logger.info(f"    Precision: {eval_results.get('eval_precision_class_1', 0):.4f}")
    logger.info(f"    Recall: {eval_results.get('eval_recall_class_1', 0):.4f}")
    logger.info(f"    F1: {eval_results.get('eval_f1_class_1', 0):.4f}")
    
    # Avalia no conjunto de TESTE (dados nunca vistos)
    logger.info("\n" + "=" * 60)
    logger.info("Avaliando modelo no conjunto de TESTE (dados nunca vistos)...")
    logger.info("=" * 60)
    test_results = trainer.evaluate(eval_dataset=test_dataset)
    
    logger.info("\nResultados do Teste:")
    logger.info("-" * 60)
    logger.info(f"Accuracy: {test_results.get('eval_accuracy', 0):.4f}")
    logger.info(f"F1 Macro: {test_results.get('eval_f1_macro', 0):.4f}")
    logger.info(f"F1 Weighted: {test_results.get('eval_f1_weighted', 0):.4f}")
    logger.info(f"Precision Macro: {test_results.get('eval_precision_macro', 0):.4f}")
    logger.info(f"Recall Macro: {test_results.get('eval_recall_macro', 0):.4f}")
    logger.info("\nMétricas por classe (Teste):")
    logger.info(f"  Classe 0 (Não Produtivo):")
    logger.info(f"    Precision: {test_results.get('eval_precision_class_0', 0):.4f}")
    logger.info(f"    Recall: {test_results.get('eval_recall_class_0', 0):.4f}")
    logger.info(f"    F1: {test_results.get('eval_f1_class_0', 0):.4f}")
    logger.info(f"  Classe 1 (Produtivo):")
    logger.info(f"    Precision: {test_results.get('eval_precision_class_1', 0):.4f}")
    logger.info(f"    Recall: {test_results.get('eval_recall_class_1', 0):.4f}")
    logger.info(f"    F1: {test_results.get('eval_f1_class_1', 0):.4f}")
    
    # Gera confusion matrix detalhada no teste
    logger.info("\n" + "=" * 60)
    logger.info("Confusion Matrix (Teste):")
    logger.info("=" * 60)
    predictions = trainer.predict(test_dataset)
    pred_labels = predictions.predictions.argmax(axis=-1)
    true_labels = test_dataset["labels"]
    cm = confusion_matrix(true_labels, pred_labels)
    logger.info(f"\n                Predito")
    logger.info(f"              Não-Prod  Produtivo")
    logger.info(f"Real Não-Prod    {cm[0][0]:5d}    {cm[0][1]:5d}")
    logger.info(f"     Produtivo    {cm[1][0]:5d}    {cm[1][1]:5d}")
    
    # Calcula diferença entre validação e teste (overfitting indicator)
    val_f1 = eval_results.get('eval_f1_macro', 0)
    test_f1 = test_results.get('eval_f1_macro', 0)
    f1_diff = val_f1 - test_f1
    
    logger.info("\n" + "=" * 60)
    logger.info("Análise de Overfitting:")
    logger.info("=" * 60)
    logger.info(f"F1 Macro (Validação): {val_f1:.4f}")
    logger.info(f"F1 Macro (Teste): {test_f1:.4f}")
    logger.info(f"Diferença: {f1_diff:.4f}")
    if f1_diff > 0.05:
        logger.warning("⚠️  Possível overfitting detectado (diferença > 0.05)")
        logger.warning("   Considere aumentar regularização ou reduzir complexidade do modelo")
    elif f1_diff < -0.05:
        logger.warning("⚠️  Modelo pode estar underfitting (teste melhor que validação)")
    else:
        logger.info("✓ Diferença aceitável - modelo generaliza bem")
    
    # Salva modelo e tokenizer
    logger.info(f"\nSalvando modelo em: {output_dir}")
    trainer.save_model()
    tokenizer.save_pretrained(output_dir)
    
    # Salva métricas em arquivo JSON
    metrics_file = os.path.join(output_dir, "metrics.json")
    with open(metrics_file, "w", encoding="utf-8") as f:
        json.dump({
            "validation": eval_results,
            "test": test_results,
            "confusion_matrix": cm.tolist(),
            "overfitting_analysis": {
                "val_f1_macro": val_f1,
                "test_f1_macro": test_f1,
                "difference": f1_diff
            }
        }, f, indent=2, ensure_ascii=False)
    logger.info(f"Métricas salvas em: {metrics_file}")
    
    logger.info("\n" + "=" * 60)
    logger.info("✅ Treinamento concluído com sucesso!")
    logger.info("=" * 60)
    logger.info(f"Modelo salvo em: {output_dir}")
    logger.info("\nPara usar o modelo treinado, atualize MODEL_NAME em classifier.py para:")
    logger.info(f'  MODEL_NAME = "{output_dir}"')


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Treina modelo BERTimbau (BERT português) para classificação de emails")
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
    parser.add_argument(
        "--seed",
        type=int,
        default=SEED,
        help=f"Seed para reprodutibilidade (padrão: {SEED})"
    )
    
    args = parser.parse_args()
    
    train_model(
        model_name=args.model_name,
        output_dir=args.output_dir,
        num_epochs=args.epochs,
        batch_size=args.batch_size,
        learning_rate=args.learning_rate,
        train_data_file=args.data_file,
        use_gpu=not args.no_gpu,
        seed=args.seed
    )

