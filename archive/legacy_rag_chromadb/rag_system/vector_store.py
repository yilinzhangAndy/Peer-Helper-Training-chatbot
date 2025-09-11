import chromadb
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any, Optional
import numpy as np
import os

# Import knowledge base directly
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from knowledge_base import KnowledgeBase, KnowledgeItem

class VectorStore:
    """Vector database manager"""
    
    def __init__(self, persist_directory: str = "vector_db"):
        self.persist_directory = persist_directory
        self.client = chromadb.PersistentClient(path=persist_directory)
        
        # Initialize embedding model
        print("🔧 Loading sentence transformer model...")
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
        print("✅ Sentence transformer loaded successfully")
        
        # Initialize knowledge base
        self.knowledge_base = KnowledgeBase()
        
        # Create or get collection
        self.collection = self._get_or_create_collection()
        
        # Initialize vector database
        self._initialize_vector_store()
    
    def _get_or_create_collection(self):
        """Get or create vector collection"""
        try:
            collection = self.client.get_collection("mae_knowledge")
            print("✅ Loaded existing vector database")
            return collection
        except:
            collection = self.client.create_collection("mae_knowledge")
            print("✅ Created new vector database")
            return collection
    
    def _initialize_vector_store(self):
        """Initialize vector database"""
        # Check if data already exists
        if self.collection.count() > 0:
            print(f"📊 Vector database already has {self.collection.count()} records")
            return
        
        print("🔧 Initializing vector database...")
        
        # Prepare all knowledge base data
        all_items = []
        
        # 1. FAQ data
        faq_items = self.knowledge_base.get_knowledge_by_type("faq")
        for item in faq_items:
            all_items.append({
                "text": item.text,
                "type": "faq",
                "persona": None,
                "category": item.category
            })
        
        # 2. Scenario data
        scenario_items = self.knowledge_base.get_knowledge_by_type("scenario")
        for item in scenario_items:
            all_items.append({
                "text": item.text,
                "type": "scenario", 
                "persona": item.persona,
                "category": None
            })
        
        # 3. Training data
        training_items = self.knowledge_base.get_knowledge_by_type("training")
        for item in training_items:
            all_items.append({
                "text": item.text,
                "type": "training",
                "persona": None,
                "category": None
            })
        
        print(f"📚 Preparing to vectorize {len(all_items)} knowledge base items...")
        
        # Process in batches
        batch_size = 100
        for i in range(0, len(all_items), batch_size):
            batch = all_items[i:i+batch_size]
            
            # Generate embeddings
            texts = [item["text"] for item in batch]
            embeddings = self.embedder.encode(texts)
            
            # Prepare metadata
            metadatas = []
            ids = []
            
            for j, item in enumerate(batch):
                metadata = {
                    "type": item["type"],
                    "persona": item["persona"] or "",
                    "category": item["category"] or ""
                }
                metadatas.append(metadata)
                ids.append(f"{item['type']}_{i+j}")
            
            # Add to vector database
            self.collection.add(
                embeddings=embeddings.tolist(),
                documents=texts,
                metadatas=metadatas,
                ids=ids
            )
            
            print(f"✅ Processed {min(i+batch_size, len(all_items))}/{len(all_items)} items")
        
        print(f"🎉 Vector database initialization completed, {self.collection.count()} records total")
    
    def search(self, query: str, intent: str = None, persona: str = None, 
               n_results: int = 3) -> List[Dict[str, Any]]:
        """
        Search relevant documents
        
        Args:
            query: Query text
            intent: Intent type
            persona: User persona
            n_results: Number of results to return
            
        Returns:
            List of relevant documents
        """
        # Generate query embedding
        query_embedding = self.embedder.encode([query])
        
        # Build filter conditions (ChromaDB only supports one key in 'where')
        where_conditions = None
        if intent:
            where_conditions = {"type": intent}
        elif persona:
            where_conditions = {"persona": persona}
        
        # Execute search
        results = self.collection.query(
            query_embeddings=query_embedding.tolist(),
            where=where_conditions,
            n_results=n_results
        )
        
        # Format results
        formatted_results = []
        if results['documents'] and results['documents'][0]:
            for i, doc in enumerate(results['documents'][0]):
                formatted_results.append({
                    "text": doc,
                    "metadata": results['metadatas'][0][i],
                    "distance": results['distances'][0][i] if 'distances' in results else None
                })
        
        return formatted_results
    
    def get_relevant_context(self, query: str, intent: str, persona: str = None) -> str:
        """Get relevant context"""
        results = self.search(query, intent, persona, n_results=2)
        
        if not results:
            return ""
        
        # Combine relevant documents
        context_parts = []
        for result in results:
            context_parts.append(result["text"])
        
        return " ".join(context_parts)
    
    def test_search(self):
        """Test search functionality"""
        print("\n🧪 Testing vector search:")
        print("=" * 50)
        
        test_queries = [
            ("How to choose research direction?", "faq", None),
            ("I need help with study methods", "scenario", "alpha"),
            ("Career development planning", "training", None)
        ]
        
        for query, intent, persona in test_queries:
            print(f"\nQuery: {query}")
            print(f"Intent: {intent}, Persona: {persona}")
            
            results = self.search(query, intent, persona, n_results=2)
            
            for i, result in enumerate(results, 1):
                print(f"  Result {i}: {result['text'][:100]}...")
                print(f"    Type: {result['metadata']['type']}")
                print(f"    Persona: {result['metadata']['persona']}")
                if result['distance']:
                    print(f"    Distance: {result['distance']:.3f}")

# Test function
def test_vector_store():
    """Test vector store"""
    try:
        vs = VectorStore()
        vs.test_search()
        return vs
    except Exception as e:
        print(f"❌ Vector store test failed: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    test_vector_store() 