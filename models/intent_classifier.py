#!/usr/bin/env python3
import torch
import json
import os
from transformers import RobertaTokenizer, RobertaForSequenceClassification
from typing import Dict, Any, Tuple
import numpy as np

class IntentClassifier:
    """Intent classifier based on your trained RoBERTa model"""
    
    def __init__(self, model_path: str):
        """
        Initialize intent classifier
        
        Args:
            model_path: Path to the trained model
        """
        self.model_path = model_path
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        print(f"🔧 Loading model: {model_path}")
        print(f"🖥️ Using device: {self.device}")
        
        # Load model and tokenizer
        try:
            self.tokenizer = RobertaTokenizer.from_pretrained(model_path)
            self.model = RobertaForSequenceClassification.from_pretrained(model_path)
            self.model.to(self.device)
            self.model.eval()
            print("✅ Model loaded successfully")
        except Exception as e:
            print(f"❌ Model loading failed: {e}")
            raise
        
        # Load label mapping
        try:
            label_mapping_path = os.path.join(model_path, "label_mapping.json")
            with open(label_mapping_path, 'r', encoding='utf-8') as f:
                self.label_mapping = json.load(f)
            
            self.id_to_label = self.label_mapping["id_to_label"]
            self.label_to_id = self.label_mapping["label_to_id"]
            
            print(f"📋 Label mapping loaded successfully")
            print(f"🏷️ Supported intent classes: {list(self.label_to_id.keys())}")
        except Exception as e:
            print(f"❌ Label mapping loading failed: {e}")
            raise
    
    def classify(self, text: str) -> Dict[str, Any]:
        """
        Classify intent for input text
        
        Args:
            text: Input text
            
        Returns:
            Dictionary containing intent and confidence
        """
        # Preprocess text
        inputs = self.tokenizer(
            text,
            padding=True,
            truncation=True,
            max_length=512,
            return_tensors="pt"
        )
        
        # Move to device
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        # Predict
        with torch.no_grad():
            outputs = self.model(**inputs)
            logits = outputs.logits
            probabilities = torch.softmax(logits, dim=1)
            
            # Get prediction results
            predicted_id = torch.argmax(probabilities, dim=1).item()
            confidence = probabilities[0][predicted_id].item()
            
            # Get predicted label
            predicted_label = self.id_to_label[str(predicted_id)]
            
            # Get all class probabilities
            all_probabilities = probabilities[0].cpu().numpy()
            label_probabilities = {
                self.id_to_label[str(i)]: prob.item() 
                for i, prob in enumerate(all_probabilities)
            }
        
        return {
            "intent": predicted_label,
            "confidence": confidence,
            "all_probabilities": label_probabilities,
            "predicted_id": predicted_id
        }
    
    def get_intent_description(self, intent: str) -> str:
        """Get Chinese description for intent"""
        intent_descriptions = {
            "Exploration and Reflection": "Exploration and Reflection",
            "Feedback and Support": "Feedback and Support", 
            "Goal Setting and Planning": "Goal Setting and Planning",
            "Problem Solving and Critical Thinking": "Problem Solving and Critical Thinking",
            "Understanding and Clarification": "Understanding and Clarification"
        }
        return intent_descriptions.get(intent, intent)
    
    def test_classification(self, test_texts: list) -> None:
        """Test classification functionality"""
        print("\n🧪 Testing intent classification:")
        print("=" * 50)
        
        for i, text in enumerate(test_texts, 1):
            result = self.classify(text)
            print(f"\nTest {i}: {text[:50]}...")
            print(f"Predicted intent: {result['intent']}")
            print(f"Confidence: {result['confidence']:.3f}")
            print(f"Description: {self.get_intent_description(result['intent'])}")

# Test function
def test_intent_classifier():
    """Test intent classifier"""
    # Use your existing model path
    model_path = "../pre-train/checkpoint-3146"
    
    try:
        classifier = IntentClassifier(model_path)
        
        # Test texts
        test_texts = [
            "I want to learn how to choose research direction and advisor",
            "I need some advice about study methods",
            "How to balance study and work?",
            "I want to make a career development plan",
            "I encountered some learning difficulties and need help"
        ]
        
        classifier.test_classification(test_texts)
        
        return classifier
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return None

if __name__ == "__main__":
    test_intent_classifier()