#!/bin/bash
# Script para configurar Git LFS localmente
# Execute este script ANTES de fazer commit dos modelos

set -e

echo "🔧 Configurando Git LFS..."

# Verificar se Git LFS está instalado
if ! command -v git-lfs &> /dev/null; then
    echo "❌ Git LFS não está instalado!"
    echo ""
    echo "📥 Instale o Git LFS:"
    echo "   Windows: https://git-lfs.github.com/"
    echo "   macOS:   brew install git-lfs"
    echo "   Linux:   sudo apt-get install git-lfs"
    exit 1
fi

# Inicializar Git LFS
echo "✅ Inicializando Git LFS..."
git lfs install

# Verificar se .gitattributes existe
if [ ! -f .gitattributes ]; then
    echo "❌ Arquivo .gitattributes não encontrado!"
    echo "   Certifique-se de que o arquivo .gitattributes está no repositório."
    exit 1
fi

echo "✅ Git LFS configurado com sucesso!"
echo ""
echo "📝 Próximos passos:"
echo "   1. Adicione os modelos ao Git LFS:"
echo "      git add models/"
echo "   2. Faça commit:"
echo "      git commit -m 'Add models with Git LFS'"
echo "   3. Faça push:"
echo "      git push origin main"
echo ""
echo "⚠️  Nota: O primeiro push pode demorar se os modelos forem grandes."

