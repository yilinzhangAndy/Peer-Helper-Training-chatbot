#!/usr/bin/env python3
"""
Step 2 test script: Test RAG system components
"""

import sys
import os

# Add project path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_step2():
    """Test step 2 components"""
    print("🚀 Starting Step 2 test: RAG System Construction")
    print("=" * 60)
    
    # 1. Test vector store
    print("\n1️⃣ Testing vector store...")
    try:
        from rag_system.vector_store import test_vector_store
        vs = test_vector_store()
        if vs:
            print("✅ Vector store test passed")
        else:
            print("❌ Vector store test failed")
            return False
    except Exception as e:
        print(f"❌ Vector store test error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # 2. Test persona manager
    print("\n2️⃣ Testing persona manager...")
    try:
        from personas.persona_manager import test_persona_manager
        pm = test_persona_manager()
        if pm:
            print("✅ Persona manager test passed")
        else:
            print("❌ Persona manager test failed")
            return False
    except Exception as e:
        print(f"❌ Persona manager test error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # 3. Test integrated RAG functionality
    print("\n3️⃣ Testing integrated RAG functionality...")
    try:
        # Test intent classification + vector search
        from models.intent_classifier import IntentClassifier
        from rag_system.vector_store import VectorStore
        
        # Load classifier
        classifier = IntentClassifier("../pre-train/balanced_finetuned_model")
        
        # Load vector store
        vs = VectorStore()
        
        # Test query
        test_query = "How to choose research direction and advisor?"
        print(f"   Test query: {test_query}")
        
        # Classify intent
        intent_result = classifier.classify(test_query)
        intent = intent_result["intent"]
        print(f"   Predicted intent: {intent}")
        
        # Search relevant documents
        results = vs.search(test_query, intent, "alpha", n_results=2)
        print(f"   Found {len(results)} relevant documents")
        
        for i, result in enumerate(results, 1):
            print(f"     Result {i}: {result['text'][:80]}...")
        
        print("✅ Integrated RAG test passed")
        
    except Exception as e:
        print(f"❌ Integrated RAG test error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n🎉 Step 2 test completed!")
    print("✅ Vector store working properly")
    print("✅ Persona manager initialized successfully")
    print("✅ RAG system integrated successfully")
    print("\n📋 Next step: System Integration")
    
    return True

if __name__ == "__main__":
    success = test_step2()
    if success:
        print("\n🚀 Ready to proceed to Step 3!")
    else:
        print("\n❌ Issues found in Step 2, please check error messages") 