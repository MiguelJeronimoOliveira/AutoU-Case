"""Script para inicializar e popular a base de conhecimento RAG com dados iniciais."""

import logging
import json
import os
import sys
from pathlib import Path

# Adicionar o diretório raiz ao path para permitir imports
root_dir = Path(__file__).parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from app.rag_retriever import RAGRetriever
from app.models import EmailCategory

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_training_data_for_rag(data_file: str = "training_data.json") -> list:
    """Carrega dados de treinamento para popular a base RAG inicial."""
    if not os.path.exists(data_file):
        logger.warning(f"Arquivo de dados não encontrado: {data_file}")
        return []
    
    try:
        with open(data_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        logger.info(f"Carregados {len(data)} exemplos do arquivo de treinamento")
        return data
    except Exception as e:
        logger.error(f"Erro ao carregar dados: {str(e)}")
        return []


def create_initial_responses(email_data: dict, category: EmailCategory) -> str:
    """
    Cria uma resposta inicial baseada no template para emails de treinamento.
    Isso ajuda a popular a base RAG com exemplos iniciais.
    """
    if category == EmailCategory.PRODUCTIVE:
        return (
            "Obrigado por entrar em contato conosco. Recebemos sua solicitação "
            "e a analisaremos em breve. Nossa equipe entrará em contato o mais "
            "rápido possível com uma solução."
        )
    else:
        return (
            "Obrigado pela sua mensagem. Agradecemos suas palavras gentis e "
            "ficamos felizes em receber seu contato."
        )


def initialize_rag_knowledge_base(
    training_data_file: str = "training_data.json",
    max_examples: int = 100
) -> None:
    """
    Inicializa a base de conhecimento RAG com dados de treinamento.
    
    Args:
        training_data_file: Caminho para o arquivo de dados de treinamento
        max_examples: Número máximo de exemplos para adicionar (para não sobrecarregar)
    """
    logger.info("=" * 60)
    logger.info("Inicializando base de conhecimento RAG")
    logger.info("=" * 60)
    
    # Inicializar RAG Retriever
    try:
        rag_retriever = RAGRetriever()
        stats = rag_retriever.get_collection_stats()
        logger.info(f"Estatísticas iniciais: {stats}")
    except Exception as e:
        logger.error(f"Erro ao inicializar RAG Retriever: {str(e)}")
        return
    
    # Verificar se já há dados
    if stats.get("count", 0) > 0:
        logger.info(f"Base de conhecimento já contém {stats['count']} documentos")
        logger.info("Continuando para adicionar mais exemplos do arquivo de treinamento...")
        # Nota: Em produção, você pode querer adicionar uma flag --force para sobrescrever
    
    # Carregar dados de treinamento
    training_data = load_training_data_for_rag(training_data_file)
    
    if not training_data:
        logger.warning("Nenhum dado de treinamento encontrado. Base RAG será criada vazia.")
        logger.info("A base será populada automaticamente conforme respostas forem geradas.")
        return
    
    # Adicionar exemplos à base
    added_count = 0
    skipped_count = 0
    
    for i, example in enumerate(training_data[:max_examples]):
        try:
            text = example.get("text", "")
            label = example.get("label", 0)
            
            if not text:
                skipped_count += 1
                continue
            
            # Converter label para categoria
            category = EmailCategory.PRODUCTIVE if label == 1 else EmailCategory.UNPRODUCTIVE
            
            # Criar resposta inicial
            response = create_initial_responses(example, category)
            
            # Adicionar à base de conhecimento
            rag_retriever.add_knowledge(
                email_content=text,
                response=response,
                category=category,
                metadata={
                    "source": "training_data",
                    "original_label": label
                }
            )
            
            added_count += 1
            
            if (i + 1) % 10 == 0:
                logger.info(f"Processados {i + 1}/{min(len(training_data), max_examples)} exemplos...")
        
        except Exception as e:
            logger.warning(f"Erro ao processar exemplo {i}: {str(e)}")
            skipped_count += 1
            continue
    
    # Estatísticas finais
    final_stats = rag_retriever.get_collection_stats()
    logger.info("\n" + "=" * 60)
    logger.info("Inicialização concluída!")
    logger.info("=" * 60)
    logger.info(f"Exemplos adicionados: {added_count}")
    logger.info(f"Exemplos ignorados: {skipped_count}")
    logger.info(f"Total na base: {final_stats.get('count', 0)} documentos")
    logger.info("=" * 60)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Inicializa a base de conhecimento RAG com dados de treinamento"
    )
    parser.add_argument(
        "--data-file",
        type=str,
        default="training_data.json",
        help="Arquivo de dados de treinamento (padrão: training_data.json)"
    )
    parser.add_argument(
        "--max-examples",
        type=int,
        default=100,
        help="Número máximo de exemplos para adicionar (padrão: 100)"
    )
    
    args = parser.parse_args()
    
    initialize_rag_knowledge_base(
        training_data_file=args.data_file,
        max_examples=args.max_examples
    )

