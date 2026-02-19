# simple_knowledge_base.py
"""
Simple knowledge base for RAG (Retrieval-Augmented Generation).
Loads knowledge from JSON files and provides simple keyword-based search.
"""
import os
import json
from typing import List, Dict, Any
from pathlib import Path


class SimpleKnowledgeBase:
    """
    Simple knowledge base that loads knowledge from JSON files
    and provides keyword-based search functionality.
    """
    
    def __init__(self, knowledge_base_dir: str = None):
        """
        Initialize the knowledge base.
        
        Args:
            knowledge_base_dir: Directory containing knowledge JSON files.
                               Defaults to 'knowledge_base' in the same directory.
        """
        if knowledge_base_dir is None:
            # Get the directory of this file
            current_dir = Path(__file__).parent
            knowledge_base_dir = current_dir / "knowledge_base"
        else:
            knowledge_base_dir = Path(knowledge_base_dir)
        
        self.knowledge_base_dir = knowledge_base_dir
        self.training_knowledge = []
        self.faq_knowledge = []
        self.uf_mae_knowledge = []  # UF MAE website knowledge
        self.mae_full_site_knowledge = []  # Crawled full MAE site (catalog, handbook, etc.)
        self.scenario_knowledge = {}
        
        # Load knowledge files
        self._load_knowledge()
    
    def _load_knowledge(self):
        """Load all knowledge files from the knowledge base directory."""
        try:
            # Load training knowledge
            training_file = self.knowledge_base_dir / "training_knowledge.json"
            if training_file.exists():
                with open(training_file, 'r', encoding='utf-8') as f:
                    self.training_knowledge = json.load(f)
            
            # Load FAQ knowledge
            faq_file = self.knowledge_base_dir / "faq_knowledge.json"
            if faq_file.exists():
                with open(faq_file, 'r', encoding='utf-8') as f:
                    self.faq_knowledge = json.load(f)
            
            # Load UF MAE website knowledge
            uf_mae_file = self.knowledge_base_dir / "uf_mae_website_knowledge.json"
            if uf_mae_file.exists():
                with open(uf_mae_file, 'r', encoding='utf-8') as f:
                    self.uf_mae_knowledge = json.load(f)
            
            # Load full MAE site crawl (run: python uf_mae_web_scraper.py crawl)
            mae_full_file = self.knowledge_base_dir / "mae_full_site_knowledge.json"
            if mae_full_file.exists():
                with open(mae_full_file, 'r', encoding='utf-8') as f:
                    self.mae_full_site_knowledge = json.load(f)
            
            # Load scenario knowledge
            scenario_file = self.knowledge_base_dir / "scenario_knowledge.json"
            if scenario_file.exists():
                with open(scenario_file, 'r', encoding='utf-8') as f:
                    self.scenario_knowledge = json.load(f)
        
        except Exception as e:
            print(f"⚠️ Warning: Failed to load some knowledge files: {e}")
            # Continue with empty knowledge bases
    
    def search(self, query: str, max_results: int = 5) -> List[str]:
        """
        Search the knowledge base for relevant content.
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return
            
        Returns:
            List of relevant content strings
        """
        if not query:
            return []
        
        query_lower = query.lower()
        results = []
        seen_content = set()  # Avoid duplicates
        
        # Search in training knowledge
        for item in self.training_knowledge:
            title = item.get("title", "").lower()
            content = item.get("content", "")
            
            # Simple keyword matching
            if any(keyword in title or keyword in content.lower() 
                   for keyword in query_lower.split() if len(keyword) > 2):
                if content and content not in seen_content:
                    results.append(content)
                    seen_content.add(content)
                    if len(results) >= max_results:
                        break
        
        # Search in full MAE site crawl (catalog, handbook, etc.)
        if len(results) < max_results:
            for item in self.mae_full_site_knowledge:
                question = item.get("question", "").lower()
                answer = item.get("answer", "")
                if any(keyword in question or keyword in answer.lower()
                       for keyword in query_lower.split() if len(keyword) > 2):
                    combined = f"{item.get('question', '')}: {answer}"
                    if combined not in seen_content:
                        results.append(combined)
                        seen_content.add(combined)
                        if len(results) >= max_results:
                            break

        # Search in UF MAE website knowledge
        if len(results) < max_results:
            for item in self.uf_mae_knowledge:
                question = item.get("question", "").lower()
                answer = item.get("answer", "")
                if any(keyword in question or keyword in answer.lower()
                       for keyword in query_lower.split() if len(keyword) > 2):
                    combined = f"{item.get('question', '')}: {answer}"
                    if combined not in seen_content:
                        results.append(combined)
                        seen_content.add(combined)
                        if len(results) >= max_results:
                            break

        # Search in FAQ knowledge
        if len(results) < max_results:
            for item in self.faq_knowledge:
                question = item.get("question", "").lower()
                answer = item.get("answer", "")
                
                # Match question or answer
                if any(keyword in question or keyword in answer.lower() 
                       for keyword in query_lower.split() if len(keyword) > 2):
                    # Combine question and answer for context
                    combined = f"{item.get('question', '')}: {answer}"
                    if combined not in seen_content:
                        results.append(combined)
                        seen_content.add(combined)
                        if len(results) >= max_results:
                            break
        
        # Search in scenario knowledge (flatten all scenarios)
        if len(results) < max_results:
            for persona, scenarios in self.scenario_knowledge.items():
                for scenario_item in scenarios:
                    scenario_text = scenario_item.get("scenario", "").lower()
                    responses = scenario_item.get("responses", [])
                    
                    if any(keyword in scenario_text 
                           for keyword in query_lower.split() if len(keyword) > 2):
                        # Combine scenario and responses
                        combined = f"{scenario_item.get('scenario', '')}: " + \
                                  "; ".join(responses[:2])  # Take first 2 responses
                        if combined not in seen_content:
                            results.append(combined)
                            seen_content.add(combined)
                            if len(results) >= max_results:
                                break
                if len(results) >= max_results:
                    break
        
        # If no results found, return some general knowledge
        if not results:
            # Return first few training knowledge items as fallback
            for item in self.training_knowledge[:max_results]:
                content = item.get("content", "")
                if content:
                    results.append(content)
        
        return results[:max_results]


# For testing
if __name__ == "__main__":
    kb = SimpleKnowledgeBase()
    print("Knowledge base loaded:")
    print(f"  Training knowledge: {len(kb.training_knowledge)} items")
    print(f"  FAQ knowledge: {len(kb.faq_knowledge)} items")
    print(f"  UF MAE website knowledge: {len(kb.uf_mae_knowledge)} items")
    print(f"  MAE full site crawl: {len(kb.mae_full_site_knowledge)} items")
    print(f"  Scenario knowledge: {len(kb.scenario_knowledge)} personas")
    
    # Test search
    test_query = "MAE advising student opening prompt"
    results = kb.search(test_query)
    print(f"\nSearch results for '{test_query}':")
    for i, result in enumerate(results, 1):
        print(f"  {i}. {result[:100]}...")
