import os
from student_persona_manager import StudentPersonaManager
from models.intent_classifier import IntentClassifier
from openai import OpenAI
from dotenv import load_dotenv
# from analysis.conversation_analyzer import ConversationAnalyzer # This line is removed

# Load OpenAI API key from .env
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

import json, time, os

# 放在文件最上方，替代原有的 analyzer 导入
from collections import Counter
from typing import Dict, Any, List, Tuple, Optional

def _norm(label: str) -> str:
    return (label or "other").strip().lower().replace(" ", "_")

class ConversationStats:
    def __init__(self):
        self.student_counts = Counter()
        self.advisor_counts = Counter()
        # 记录顺序事件用于配对：[(role, norm_label)]
        self.events = []

    def add(self, role: str, label: str):
        n = _norm(label)
        if role == "student":
            self.student_counts[n] += 1
        else:
            self.advisor_counts[n] += 1
        self.events.append((role, n))

    def pair_same_diff(self):
        same = diff = 0
        # 仅统计“学生→顾问”的相邻配对
        for i in range(1, len(self.events)):
            prev_role, prev_lab = self.events[i-1]
            curr_role, curr_lab = self.events[i]
            if prev_role == "student" and curr_role == "advisor":
                if prev_lab == curr_lab:
                    same += 1
                else:
                    diff += 1
        return same, diff

    def report_text(self):
        same, diff = self.pair_same_diff()
        lines = []
        lines.append("Student counts:")
        for k, v in self.student_counts.most_common():
            lines.append(f"- {k}: {v}")
        lines.append("\nAdvisor counts:")
        for k, v in self.advisor_counts.most_common():
            lines.append(f"- {k}: {v}")
        lines.append(f"\nQ→A pairs: same={same}, different={diff}")
        return "\n".join(lines)

class ConversationAnalyzer:
    # ... existing code ...

    def get_transcript(self, max_messages: int = 40) -> str:
        parts = []
        for e in self.events[-max_messages:]:
            who = "Student" if e.role == "student" else "Advisor"
            parts.append(f"{who}: {e.text}")
        return "\n".join(parts)

    def summarize_with_llm(self, client, model: str = "gpt-3.5-turbo") -> Dict[str, Any]:
        transcript = self.get_transcript()
        dist = self.talk_move_distribution()["overall"]
        prompt = (
            "You analyze a peer advising session.\n"
            "Summarize concisely and return strict JSON with keys: "
            "summary (3-5 bullets), student_concerns (bullets), "
            "advisor_strategies (bullets), action_items (checklist, short verbs).\n\n"
            f"Transcript:\n{transcript}\n\n"
            f"Talk-move distribution (overall): {json.dumps(dist)}"
        )
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=250,
            temperature=0.2
        )
        content = resp.choices[0].message.content.strip()
        try:
            data = json.loads(content)
        except Exception:
            # robust fallback if model didn't return JSON
            data = {"summary": [content], "student_concerns": [], "advisor_strategies": [], "action_items": []}
        self._summary = data
        return data

    def summarize_heuristic(self) -> Dict[str, Any]:
        # fallback without LLM
        concerns = []
        strategies = []
        if self.events:
            concerns.append("Clarify research interests and program fit")
            strategies.append("Asked probing questions and reframed goals")
        data = {
            "summary": ["Brief advising conversation focused on aligning goals and next steps."],
            "student_concerns": concerns,
            "advisor_strategies": strategies,
            "action_items": ["Outline goals", "Collect resources", "Schedule follow-up"]
        }
        self._summary = data
        return data

    def get_summary(self) -> Dict[str, Any]:
        return getattr(self, "_summary", {
            "summary": [], "student_concerns": [], "advisor_strategies": [], "action_items": []
        })

    def to_json(self) -> Dict[str, Any]:
        base = {
            "events": [asdict(e) for e in self.events],
            "distribution": self.talk_move_distribution(),
            "transitions": self.transition_patterns(),
        }
        base["summary_sections"] = self.get_summary()
        return base

def display_persona_options(spm):
    """Display all persona options for user to choose from"""
    print(" Welcome to the MAE Peer Advisor Multi-Turn Training System!")
    print("=" * 80)
    print("Please select a student persona to practice with:\n")
    
    personas = spm.list_personas()
    for i, persona_id in enumerate(personas, 1):
        persona = spm.get_persona(persona_id)
        print(f"{i}. {persona_id.upper()} - {persona['description']}")
        print(f"   Traits: {', '.join(persona['traits'][:3])}...")
        print(f"   Help Seeking: {persona['help_seeking_behavior']}")
        print()

def get_user_persona_choice(spm):
    """Get user's choice of persona"""
    personas = spm.list_personas()
    
    while True:
        try:
            choice = input(f"Enter your choice (1-{len(personas)}) or type the persona name: ").strip().lower()
            
            # Check if user entered a number
            if choice.isdigit():
                choice_num = int(choice)
                if 1 <= choice_num <= len(personas):
                    return personas[choice_num - 1]
                else:
                    print(f"Please enter a number between 1 and {len(personas)}.")
                    continue
            
            # Check if user entered a persona name
            if choice in personas:
                return choice
            else:
                print(f"Invalid choice. Please enter 1-{len(personas)} or one of: {', '.join(personas)}")
                
        except ValueError:
            print("Please enter a valid number or persona name.")

def analyze_intent(message: str, intent_classifier: IntentClassifier, role: str = "student") -> None:
    """
    Analyze and display the intent of a message
    """
    try:
        intent_result = intent_classifier.classify(message)
        role_icon = "👨‍🎓" if role == "student" else "👨‍🏫"
        print(f"{role_icon} {role.title()} Intent: {intent_result['intent']} (confidence: {intent_result['confidence']:.2f})")
        return intent_result
    except Exception as e:
        print(f"⚠️ Could not classify {role}'s intent: {e}")
        return {"intent": "general", "confidence": 0.0}

def generate_student_reply_with_intent(persona_id, persona, dialogue_history, intent_classifier):
    """
    Generate student reply considering both student and advisor intents
    """
    # Get the last exchange (both advisor and student messages)
    last_advisor_message = ""
    last_student_message = ""
    for turn in reversed(dialogue_history):
        if turn["role"] == "user" and not last_advisor_message:
            last_advisor_message = turn["content"]
        elif turn["role"] == "assistant" and not last_student_message:
            last_student_message = turn["content"]
        if last_advisor_message and last_student_message:
            break
    
    # Analyze intents for both messages if they exist
    advisor_intent = None
    student_intent = None
    
    if last_advisor_message and intent_classifier:
        advisor_intent = analyze_intent(last_advisor_message, intent_classifier, "advisor")
    
    if last_student_message and intent_classifier:
        student_intent = analyze_intent(last_student_message, intent_classifier, "student")
    
    # Build persona description with intent context
    persona_desc = (
        f"You are a MAE student with the following characteristics:\n"
        f"Persona: {persona_id}\n"
        f"Description: {persona['description']}\n"
        f"Traits: {', '.join(persona['traits'])}\n"
        f"Help Seeking: {persona['help_seeking_behavior']}\n"
    )
    
    if advisor_intent and student_intent:
        persona_desc += (
            f"\nContext:\n"
            f"- Your last intent: {student_intent['intent']}\n"
            f"- Advisor's last intent: {advisor_intent['intent']}\n"
            f"Consider both intents when formulating your response."
        )
    
    # Build conversation history for prompt
    messages = [
        {"role": "system", "content": persona_desc}
    ]
    for turn in dialogue_history:
        messages.append({"role": turn["role"], "content": turn["content"]})

    messages.append({
        "role": "system", 
        "content": (
            "Continue as the student. Consider the advisor's intent and your previous intent. "
            "Ask a follow-up question or share your thoughts naturally."
        )
    })

    # Call OpenAI API
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        max_tokens=150,
        temperature=0.7
    )
    return response.choices[0].message.content.strip()

def show_analysis(analyzer: ConversationAnalyzer, client):
    # build summary (LLM if available)
    try:
        summary = analyzer.summarize_with_llm(client)
    except Exception:
        summary = analyzer.summarize_heuristic()

    # pretty print to console
    print("\nConversation Summary")
    print("--------------------")
    for b in summary.get("summary", []):
        print(f"- {b}")
    if summary.get("student_concerns"):
        print("\nStudent Concerns")
        for b in summary["student_concerns"]:
            print(f"- {b}")
    if summary.get("advisor_strategies"):
        print("\nAdvisor Strategies Observed")
        for b in summary["advisor_strategies"]:
            print(f"- {b}")
    if summary.get("action_items"):
        print("\nAction Items")
        for b in summary["action_items"]:
            print(f"- [ ] {b}")

    # also print distributions/transitions
    print("\n" + analyzer.report_text())

def main():
    spm = StudentPersonaManager()
    
    # Initialize intent classifier
    print("🤖 Loading RoBERTa intent classification model...")
    try:
        intent_classifier = IntentClassifier("../pre-train/balanced_finetuned_model")
        print("✅ Intent classifier loaded successfully!")
        print("🔍 Intent classification is active for both student and advisor messages.\n")
    except Exception as e:
        print(f"❌ Failed to load intent classifier: {e}")
        print("⚠️ Continuing without intent classification...")
        intent_classifier = None
    
    # 初始化统计器
    stats = ConversationStats()

    # Display persona options and get user choice
    display_persona_options(spm)
    current_persona = get_user_persona_choice(spm)
    
    print(f"\n✅ You selected: {current_persona.upper()}")
    print("Type 'switch' to change persona, 'quit' to exit.")
    print("Both your responses and student messages will be analyzed for intent.\n")

    while True:
        persona = spm.get_persona(current_persona)
        print(f"\n--- Student Persona: {current_persona.upper()} ---")
        print(f"Description: {persona['description']}")
        print(f"Traits: {', '.join(persona['traits'])}")
        print(f"Help Seeking: {persona['help_seeking_behavior']}\n")

        # Get a random opening question
        opening_question = spm.get_random_opening_question(current_persona)
        
        # Analyze opening question intent
        if intent_classifier:
            # 学生开场问题分类后
            res = intent_classifier.classify(opening_question)
            print(f"👨‍🎓 Student Intent: {res['intent']} (conf: {res['confidence']:.2f})")
            stats.add("student", res["intent"])

        # Start conversation history
        dialogue_history = [
            {"role": "assistant", "content": opening_question}
        ]
        print(f"Student: {opening_question}\n")

        while True:
            advisor_reply = input("Your response (as peer advisor): ").strip()
            
            if advisor_reply.lower() == "quit":
                print("\nGenerating analysis...\n")
                print(stats.report_text())
                return
            elif advisor_reply.lower() == "analysis":
                print("\n" + stats.report_text() + "\n")
                continue
            elif advisor_reply.lower() == "switch":
                print("\n" + "="*50)
                display_persona_options(spm)
                new_persona = get_user_persona_choice(spm)
                if new_persona in spm.list_personas():
                    current_persona = new_persona
                    print(f"\n✅ Switched to: {current_persona.upper()}")
                    break
                else:
                    print("Invalid persona. Staying with current persona.")
                    continue
            
            # Analyze advisor's reply intent
            if intent_classifier:
                # 顾问回复分类后
                res = intent_classifier.classify(advisor_reply)
                print(f"👨‍🏫 Advisor Intent: {res['intent']} (conf: {res['confidence']:.2f})")
                stats.add("advisor", res["intent"])
            
            # Add advisor reply to history
            dialogue_history.append({"role": "user", "content": advisor_reply})

            # Generate and analyze student's reply
            print("\nStudent is thinking...\n")
            student_reply = generate_student_reply_with_intent(
                current_persona, 
                persona, 
                dialogue_history, 
                intent_classifier
            )
            
            print(f"Student: {student_reply}\n")
            dialogue_history.append({"role": "assistant", "content": student_reply})

            if intent_classifier:
                # 学生追问分类后
                res = intent_classifier.classify(student_reply)
                print(f"👨‍🎓 Student Intent: {res['intent']} (conf: {res['confidence']:.2f})")
                stats.add("student", res["intent"])

if __name__ == "__main__":
    main() 