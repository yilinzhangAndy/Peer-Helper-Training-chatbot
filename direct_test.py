#!/usr/bin/env python3
"""
Direct test - bypass all import issues
"""

import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_vector_store_direct():
    """Test vector store directly"""
    print("🧪 Testing vector store directly...")
    
    try:
        # Import the class directly
        import importlib.util
        spec = importlib.util.spec_from_file_location("vector_store", "rag_system/vector_store.py")
        vector_store_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(vector_store_module)
        
        # Create vector store
        vs = vector_store_module.VectorStore()
        vs.test_search()
        return True
        
    except Exception as e:
        print(f"❌ Vector store test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_persona_manager_direct():
    """Test persona manager directly"""
    print("\n👤 Testing persona manager directly...")
    
    try:
        # Import the class directly
        import importlib.util
        spec = importlib.util.spec_from_file_location("persona_manager", "personas/persona_manager.py")
        persona_manager_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(persona_manager_module)
        
        # Create persona manager
        pm = persona_manager_module.PersonaManager()
        
        # Test getting all personas
        all_personas = pm.get_all_personas()
        print(f"📋 Total personas: {len(all_personas)}")
        
        # Test one persona
        alpha_persona = pm.get_persona("alpha")
        print(f"🎭 Alpha persona: {alpha_persona['name']} - {alpha_persona['description']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Persona manager test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print(" Direct Step 2 Test")
    print("=" * 50)
    
    # Test vector store
    vs_ok = test_vector_store_direct()
    
    # Test persona manager
    pm_ok = test_persona_manager_direct()
    
    # Summary
    print("\n" + "=" * 50)
    if vs_ok and pm_ok:
        print(" Step 2 test passed!")
        print("✅ Vector store working properly")
        print("✅ Persona manager working properly")
    else:
        print("❌ Step 2 test failed")

if __name__ == "__main__":
    main() 