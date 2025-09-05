import os
from student_persona_manager import StudentPersonaManager
from openai import OpenAI
from dotenv import load_dotenv

# Load OpenAI API key from .env
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

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

def generate_student_reply(persona_id, persona, dialogue_history):
    """
    Use OpenAI LLM to generate the next student (chatbot) reply based on persona and conversation history.
    """
    # Build persona description for prompt
    persona_desc = (
        f"You are a MAE student with the following characteristics:\n"
        f"Persona: {persona_id}\n"
        f"Description: {persona['description']}\n"
        f"Traits: {', '.join(persona['traits'])}\n"
        f"Help Seeking: {persona['help_seeking_behavior']}\n"
        f"Stay in character and continue the conversation as a student."
    )

    # Build conversation history for prompt
    messages = [
        {"role": "system", "content": persona_desc}
    ]
    for turn in dialogue_history:
        messages.append({"role": turn["role"], "content": turn["content"]})

    # Student should now respond
    messages.append({"role": "assistant", "content": "Continue as the student. Ask a follow-up question or share your thoughts."})

    # Call OpenAI API
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        max_tokens=150,
        temperature=0.7
    )
    return response.choices[0].message.content.strip()

def main():
    spm = StudentPersonaManager()
    
    # Display persona options and get user choice
    display_persona_options(spm)
    current_persona = get_user_persona_choice(spm)
    
    print(f"\n✅ You selected: {current_persona.upper()}")
    print("Type 'switch' to change persona, 'quit' to exit.\n")

    while True:
        persona = spm.get_persona(current_persona)
        print(f"\n--- Student Persona: {current_persona.upper()} ---")
        print(f"Description: {persona['description']}")
        print(f"Traits: {', '.join(persona['traits'])}")
        print(f"Help Seeking: {persona['help_seeking_behavior']}\n")

        # Get a random opening question for this persona
        opening_question = spm.get_random_opening_question(current_persona)
        
        # Start conversation history
        dialogue_history = [
            {"role": "assistant", "content": opening_question}
        ]
        print(f"Student: {opening_question}\n")

        while True:
            advisor_reply = input("Your response (as peer advisor): ").strip()
            if advisor_reply.lower() == "quit":
                print("Session ended. Thank you!")
                return
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
            else:
                # Add advisor reply to history
                dialogue_history.append({"role": "user", "content": advisor_reply})

                # Generate next student reply
                print("Student is thinking...\n")
                student_reply = generate_student_reply(current_persona, persona, dialogue_history)
                print(f"Student: {student_reply}\n")
                dialogue_history.append({"role": "assistant", "content": student_reply})

if __name__ == "__main__":
    main() 