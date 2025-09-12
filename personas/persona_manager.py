from typing import Dict, Any, List
import json
import os

class PersonaManager:
    """Persona manager"""
    
    def __init__(self):
        self.personas = self._initialize_personas()
    
    def _initialize_personas(self) -> Dict[str, Dict[str, Any]]:
        """Initialize four personas"""
        personas = {
            "alpha": {
                "name": "Alpha",
                "description": "Academic-oriented",
                "characteristics": [
                    "Focuses on academic research and theoretical depth",
                    "Likes to explore complex concepts",
                    "Values academic publications and conference participation",
                    "Tends to choose research-oriented courses"
                ],
                "communication_style": "Formal, academic",
                "focus_areas": [
                    "Research direction selection",
                    "Academic writing guidance",
                    "Research methodology",
                    "Academic conference participation"
                ],
                "response_templates": {
                    "greeting": "Hello! I'm your academic advisor. I notice you're interested in academic research, and I can help you plan your academic development path.",
                    "exploration": "Let's explore this academic topic in depth. Can you tell me about your current research interests and background?",
                    "planning": "Based on your academic goals, I suggest we develop a detailed research plan.",
                    "support": "Encountering challenges in academic pursuits is normal, let's analyze solutions together."
                }
            },
            "beta": {
                "name": "Beta", 
                "description": "Practice-oriented",
                "characteristics": [
                    "Focuses on practical application and skill development",
                    "Likes hands-on practice and project experience",
                    "Values internship and work opportunities",
                    "Tends to choose application-oriented courses"
                ],
                "communication_style": "Practical, direct",
                "focus_areas": [
                    "Internship opportunity finding",
                    "Skill development planning",
                    "Project experience accumulation",
                    "Professional practice guidance"
                ],
                "response_templates": {
                    "greeting": "Hello! I'm your practice advisor. I understand you want to gain more practical experience, and I can help you find suitable practice opportunities.",
                    "exploration": "Let's see what practical skills and experience you want to gain. Do you have specific practice goals?",
                    "planning": "Based on your practice needs, I suggest developing a skill training and practice plan.",
                    "support": "Encountering difficulties during practice is part of learning, we can find solutions together."
                }
            },
            "delta": {
                "name": "Delta",
                "description": "Career development-oriented", 
                "characteristics": [
                    "Focuses on career planning and employment preparation",
                    "Concerned about industry trends and market demands",
                    "Values network building and career development",
                    "Tends to choose career-oriented courses"
                ],
                "communication_style": "Professional, goal-oriented",
                "focus_areas": [
                    "Career planning guidance",
                    "Employment preparation support",
                    "Industry network building",
                    "Career development path"
                ],
                "response_templates": {
                    "greeting": "Hello! I'm your career development advisor. I understand you're concerned about career development, and I can help you plan your career path.",
                    "exploration": "Let's explore your career goals and interests. What type of work do you want to do?",
                    "planning": "Based on your career goals, I suggest developing a career development plan.",
                    "support": "Career development is a process, we can analyze your strengths and opportunities together."
                }
            },
            "echo": {
                "name": "Echo",
                "description": "Personal growth-oriented",
                "characteristics": [
                    "Focuses on personal development and self-improvement",
                    "Concerned about learning methods and efficiency",
                    "Values mental health and balance",
                    "Tends to choose comprehensive development courses"
                ],
                "communication_style": "Supportive, encouraging",
                "focus_areas": [
                    "Learning method guidance",
                    "Time management techniques",
                    "Mental health support",
                    "Personal growth planning"
                ],
                "response_templates": {
                    "greeting": "Hello! I'm your personal growth advisor. I care about your overall development, including learning, life, and mental health.",
                    "exploration": "Let's talk about your learning experience and personal feelings. How do you feel about your current learning state?",
                    "planning": "Based on your personal needs, I suggest developing a balanced learning and life plan.",
                    "support": "Everyone's growth rhythm is different, I'm here to support your personal development."
                }
            }
        }
        
        return personas
    
    def get_persona(self, persona_id: str) -> Dict[str, Any]:
        """Get specified persona information"""
        return self.personas.get(persona_id, {})
    
    def get_all_personas(self) -> Dict[str, Dict[str, Any]]:
        """Get all persona information"""
        return self.personas
    
    def get_persona_characteristics(self, persona_id: str) -> List[str]:
        """Get persona characteristics"""
        persona = self.get_persona(persona_id)
        return persona.get("characteristics", [])
    
    def get_persona_focus_areas(self, persona_id: str) -> List[str]:
        """Get persona focus areas"""
        persona = self.get_persona(persona_id)
        return persona.get("focus_areas", [])
    
    def get_response_template(self, persona_id: str, template_type: str) -> str:
        """Get persona response template"""
        persona = self.get_persona(persona_id)
        templates = persona.get("response_templates", {})
        return templates.get(template_type, "")
    
    def adapt_response_to_persona(self, response: str, persona_id: str) -> str:
        """Adapt response style to persona"""
        persona = self.get_persona(persona_id)
        if not persona:
            return response
        
        # Adapt response based on persona characteristics
        communication_style = persona.get("communication_style", "")
        
        if "academic" in communication_style:
            # Add academic expression
            response = f"From an academic perspective, {response}"
        elif "practical" in communication_style:
            # Add practical expression
            response = f"From a practical standpoint, {response}"
        elif "professional" in communication_style:
            # Add professional expression
            response = f"From a career development perspective, {response}"
        elif "supportive" in communication_style:
            # Add supportive expression
            response = f"I understand your feelings, {response}"
        
        return response

# Test function
def test_persona_manager():
    """Test persona manager"""
    try:
        pm = PersonaManager()
        
        print("\n👤 Testing persona manager:")
        print("=" * 50)
        
        # Test getting all personas
        all_personas = pm.get_all_personas()
        print(f"📋 Total personas: {len(all_personas)}")
        
        # Test each persona
        for persona_id, persona_info in all_personas.items():
            print(f"\n🎭 {persona_info['name']} ({persona_id}):")
            print(f"   Description: {persona_info['description']}")
            print(f"   Focus areas: {', '.join(persona_info['focus_areas'][:2])}...")
            
            # Test response template
            greeting = pm.get_response_template(persona_id, "greeting")
            print(f"   Greeting: {greeting[:50]}...")
        
        return pm
        
    except Exception as e:
        print(f"❌ Persona manager test failed: {e}")
        return None

if __name__ == "__main__":
    test_persona_manager() 