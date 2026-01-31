#!/bin/bash
# Script para baixar modelos durante o build no Render
# Use este script se não estiver usando Git LFS

set -e

echo "📥 Verificando se os modelos precisam ser baixados..."

MODEL_PATH="${MODEL_PATH:-models/email_classifier-pt-en/checkpoint-300}"
MODEL_DIR=$(dirname "$MODEL_PATH")

# Se os modelos já existem, não precisa baixar
if [ -d "$MODEL_PATH" ] && [ -f "$MODEL_PATH/model.safetensors" ]; then
    echo "✅ Modelos já existem em $MODEL_PATH"
    exit 0
fi

# Criar diretório se não existir
mkdir -p "$MODEL_DIR"

# Se você tiver os modelos em um storage externo (Google Drive, S3, etc),
# descomente e configure uma das opções abaixo:

# Opção 1: Baixar de URL direta (ex: Google Drive compartilhado)
# echo "📥 Baixando modelos de storage externo..."
# wget -O "$MODEL_PATH/model.safetensors" "https://seu-storage.com/models/model.safetensors"
# wget -O "$MODEL_PATH/config.json" "https://seu-storage.com/models/config.json"
# wget -O "$MODEL_PATH/tokenizer.json" "https://seu-storage.com/models/tokenizer.json"
# wget -O "$MODEL_PATH/tokenizer_config.json" "https://seu-storage.com/models/tokenizer_config.json"

# Opção 2: Usar Hugging Face (se os modelos estiverem publicados)
# echo "📥 Baixando modelos do Hugging Face..."
# python -c "from transformers import AutoTokenizer, AutoModelForSequenceClassification; \
#     AutoTokenizer.from_pretrained('seu-usuario/seu-modelo'); \
#     AutoModelForSequenceClassification.from_pretrained('seu-usuario/seu-modelo')"

# Opção 3: Usar modelo padrão se os modelos customizados não estiverem disponíveis
echo "⚠️  Modelos customizados não encontrados. Usando modelo padrão do Hugging Face."
echo "   Configure MODEL_PATH vazio ou use Git LFS para incluir os modelos."

