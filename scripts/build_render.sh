#!/bin/bash
# Script de build inteligente para Render
# Instala Git LFS se necessário e baixa os modelos

set -e

echo "🔧 Iniciando build no Render..."

# Instalar dependências Python
echo "📦 Instalando dependências Python..."
pip install -r requirements.txt

# Função para instalar Git LFS
install_git_lfs() {
    echo "📥 Tentando instalar Git LFS..."
    
    # Detectar sistema operacional
    if command -v apt-get &> /dev/null; then
        # Ubuntu/Debian
        sudo apt-get update -qq
        sudo apt-get install -y git-lfs
    elif command -v yum &> /dev/null; then
        # CentOS/RHEL
        sudo yum install -y git-lfs
    elif command -v brew &> /dev/null; then
        # macOS
        brew install git-lfs
    else
        echo "⚠️  Não foi possível instalar Git LFS automaticamente"
        return 1
    fi
    
    # Inicializar Git LFS
    git lfs install
    return 0
}

# Função para baixar modelos via Git LFS
download_models_lfs() {
    echo "📥 Baixando modelos via Git LFS..."
    if git lfs pull; then
        echo "✅ Modelos baixados com sucesso via Git LFS"
        return 0
    else
        echo "❌ Falha ao baixar modelos via Git LFS"
        return 1
    fi
}

# Função para baixar modelos alternativamente
download_models_alternative() {
    echo "📥 Tentando baixar modelos alternativamente..."
    if [ -f "scripts/download_models.sh" ]; then
        chmod +x scripts/download_models.sh
        bash scripts/download_models.sh
    else
        echo "⚠️  Script de download alternativo não encontrado"
        return 1
    fi
}

# Verificar se Git LFS está instalado
if ! command -v git-lfs &> /dev/null; then
    echo "⚠️  Git LFS não está instalado"
    
    # Tentar instalar
    if install_git_lfs; then
        echo "✅ Git LFS instalado com sucesso"
    else
        echo "⚠️  Não foi possível instalar Git LFS, tentando método alternativo..."
        download_models_alternative
        exit 0
    fi
fi

# Tentar baixar modelos via Git LFS
if download_models_lfs; then
    echo "✅ Build concluído com sucesso!"
else
    echo "⚠️  Falha ao baixar modelos via Git LFS, tentando método alternativo..."
    download_models_alternative
fi

echo "✅ Build finalizado!"

