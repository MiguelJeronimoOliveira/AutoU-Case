"""Script para preparar dados de treinamento a partir dos exemplos de emails."""

import json
import os
from pathlib import Path
from typing import List, Dict

from datasets import Dataset

#Load email from the examples directory and create a labeled dataset
#@param data_dir: directory containing the example emails
#@return: list of dictionaries with 'text' and 'label'
def load_email_examples(data_dir: str = "exemples") -> List[Dict[str, str]]:
    data_dir_path = Path(data_dir)
    examples = []

    for file_path in data_dir_path.glob("email_*.txt"):
        # determine the label based on the file name
        if file_path.stem.startswith("email_produtivo"):
            label = 1  # productive
        elif file_path.stem.startswith("email_nao_produtivo"):
            label = 0  # unproductive
        elif "misto" in file_path.stem:
            label = 1
        else:
            # for other cases, try to infer from the content
            continue
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read().strip()
            
            if content:
                examples.append({
                    "text": content,
                    "label": label
                })
                print(f"✓ Carregado: {file_path.name} -> Label: {label}")
        except Exception as e:
            print(f"✗ Erro ao ler {file_path.name}: {e}")
    
    return examples

#create a Hugging Face dataset from the examples
#@param examples: list of dictionaries with 'text' and 'label'
#@param output_file: file to save the dataset
#@return: Hugging Face dataset
def create_dataset(examples: List[Dict[str, str]], output_file: str = "training_data.json") -> Dataset:

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(examples, f, ensure_ascii=False, indent=2)
    
    print(f"\n✓ Dataset salvo em: {output_file}")
    print(f"✓ Total de exemplos: {len(examples)}")
    print(f"  - Produtivos (label 1): {sum(1 for ex in examples if ex['label'] == 1)}")
    print(f"  - Não produtivos (label 0): {sum(1 for ex in examples if ex['label'] == 0)}")
    
    # create Hugging Face dataset
    dataset = Dataset.from_list(examples)
    
    return dataset

#augment the data by creating simple variations of the emails
#@param examples: list of dictionaries with 'text' and 'label'
#@param augment_factor: how many times to augment the dataset
#@return: list of dictionaries with 'text' and 'label'
def augment_data(examples: List[Dict[str, str]], augment_factor: int = 2) -> List[Dict[str, str]]:
    augmented = examples.copy()
    
    # for each example, create some simple variations
    for example in examples:
        text = example["text"]
        label = example["label"]
        
        # simple variations: add/remove spaces, change punctuation
        variations = [
            text.replace("  ", " "),  # remove double spaces
            text.replace("\n\n", "\n"),  # remove double empty lines
            text.strip() + "\n",  # add a new line
        ]
        
        for variation in variations[:augment_factor]:
            if variation != text and len(variation.strip()) > 10:
                augmented.append({
                    "text": variation,
                    "label": label
                })
    
    return augmented


if __name__ == "__main__":
    print("Preparando dados de treinamento...\n")
    
    examples = load_email_examples()
    
    if not examples:
        print("❌ Nenhum exemplo encontrado!")
        exit(1)
    
    if len(examples) < 20:
        print("\nAumentando dataset...")
        examples = augment_data(examples, augment_factor=2)
    
    dataset = create_dataset(examples)
    
    print("\n✅ Preparação de dados concluída!")
    print("\nPróximo passo: Execute 'python app/train_classifier.py' para treinar o modelo.")



