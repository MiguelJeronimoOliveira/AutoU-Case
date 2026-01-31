"""Script para visualizar dados persistidos no ChromaDB."""

import json
import logging
from typing import List, Dict, Any

from app.rag_retriever import RAGRetriever
from app.models import EmailCategory

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


#format document for display
#@param doc_id: document ID
#@param document: document text
#@param metadata: document metadata
#@param distance: similarity distance
#@return: formatted document dictionary
def format_document(doc_id: str, document: str, metadata: Dict[str, Any], distance: float = None) -> Dict[str, Any]:
    similarity = 1.0 - distance if distance is not None else None
    
    return {
        "id": doc_id,
        "email_content": metadata.get("email_content", "")[:200] + "..." if len(metadata.get("email_content", "")) > 200 else metadata.get("email_content", ""),
        "response": metadata.get("response", ""),
        "category": metadata.get("category", "unknown"),
        "created_at": metadata.get("created_at", "unknown"),
        "similarity": f"{similarity:.4f}" if similarity is not None else None,
        "full_email": metadata.get("email_content", ""),
        "full_document": document
    }


#view all documents from RAG database
#@param limit: maximum number of documents to return
#@param category: optional category filter
#@return: list of formatted documents
def view_all_documents(limit: int = None, category: str = None) -> List[Dict[str, Any]]:
    try:
        rag_retriever = RAGRetriever()
        
        category_enum = None
        if category:
            category_enum = EmailCategory.PRODUCTIVE if category == "productive" else EmailCategory.UNPRODUCTIVE
        
        all_docs = rag_retriever.get_all_documents(limit=limit, category=category_enum)
        
        formatted_docs = []
        for doc in all_docs:
            formatted_doc = format_document(
                doc["id"],
                doc["document"],
                doc["metadata"],
                doc.get("distance")
            )
            formatted_docs.append(formatted_doc)
        
        return formatted_docs
            
    except Exception as e:
        logger.error(f"Erro ao visualizar documentos: {str(e)}")
        return []


#view documents filtered by category
#@param category: email category to filter by
#@param limit: maximum number of documents to return
#@return: list of formatted documents
def view_documents_by_category(category: EmailCategory, limit: int = None) -> List[Dict[str, Any]]:
    return view_all_documents(limit=limit, category=category.value)


#print documents in formatted table
#@param documents: list of documents to print
#@param show_full: whether to show full document content
#@return: None
def print_documents_table(documents: List[Dict[str, Any]], show_full: bool = False) -> None:
    if not documents:
        print("\n❌ Nenhum documento encontrado na base de conhecimento.")
        return
    
    print(f"\n{'='*80}")
    print(f"📊 DOCUMENTOS NA BASE DE CONHECIMENTO RAG ({len(documents)} encontrados)")
    print(f"{'='*80}\n")
    
    for i, doc in enumerate(documents, 1):
        print(f"\n{'─'*80}")
        print(f"📄 Documento #{i} (ID: {doc['id'][:8]}...)")
        print(f"{'─'*80}")
        print(f"📧 Categoria: {doc['category'].upper()}")
        print(f"📅 Criado em: {doc['created_at']}")
        if doc['similarity']:
            print(f"🎯 Similaridade: {doc['similarity']}")
        print(f"\n📨 Email:")
        print(f"   {doc['email_content']}")
        print(f"\n💬 Resposta:")
        print(f"   {doc['response']}")
        
        if show_full:
            print(f"\n📄 Documento completo:")
            print(f"   {doc['full_document'][:500]}...")
    
    print(f"\n{'='*80}\n")


#export documents to JSON file
#@param documents: list of documents to export
#@param output_file: output file path
#@return: None
def export_to_json(documents: List[Dict[str, Any]], output_file: str = "rag_data_export.json") -> None:
    try:
        export_data = []
        for doc in documents:
            export_data.append({
                "id": doc["id"],
                "category": doc["category"],
                "created_at": doc["created_at"],
                "email_content": doc["full_email"],
                "response": doc["response"]
            })
        
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"✅ Dados exportados para: {output_file}")
    except Exception as e:
        logger.error(f"Erro ao exportar dados: {str(e)}")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Visualiza dados persistidos no ChromaDB RAG"
    )
    parser.add_argument(
        "--category",
        type=str,
        choices=["productive", "unproductive"],
        help="Filtrar por categoria"
    )
    parser.add_argument(
        "--limit",
        type=int,
        help="Limitar número de documentos exibidos"
    )
    parser.add_argument(
        "--full",
        action="store_true",
        help="Mostrar documentos completos"
    )
    parser.add_argument(
        "--export",
        type=str,
        help="Exportar para arquivo JSON (especificar nome do arquivo)"
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Mostrar apenas estatísticas"
    )
    
    args = parser.parse_args()
    
    try:
        rag_retriever = RAGRetriever()
        stats = rag_retriever.get_collection_stats()
        
        print("\n" + "="*80)
        print("🔍 VISUALIZADOR DE DADOS RAG")
        print("="*80)
        print(f"\n📊 Estatísticas:")
        print(f"   Status: {stats.get('status', 'unknown')}")
        print(f"   Total de documentos: {stats.get('count', 0)}")
        print(f"   Caminho da base: {stats.get('db_path', 'unknown')}")
        
        if args.stats:
            return
        
        if stats.get('count', 0) == 0:
            print("\n⚠️  Base de conhecimento está vazia.")
            print("   Execute a API para gerar respostas e elas serão automaticamente adicionadas.")
            return
        
        category_filter = args.category
        documents = view_all_documents(limit=args.limit, category=category_filter)
        
        if category_filter:
            print(f"\n🔍 Filtrado por categoria: {category_filter}")
        
        print_documents_table(documents, show_full=args.full)
        
        if args.export:
            export_to_json(documents, args.export)
        
    except Exception as e:
        logger.error(f"Erro: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

