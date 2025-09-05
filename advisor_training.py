from student_persona_manager import StudentPersonaManager

def main():
    spm = StudentPersonaManager()
    print("Welcome to the MAE Peer Advisor Training System!")
    print("You will practice advising different types of students.")
    print("Available personas:", ", ".join(spm.list_personas()))
    print("Type 'switch' to change persona, 'quit' to exit.\n")

    current_persona = "alpha"
    while True:
        persona = spm.get_persona(current_persona)
        print(f"\n--- Student Persona: {current_persona.upper()} ---")
        print(f"Description: {persona['description']}")
        print(f"Traits: {', '.join(persona['traits'])}")
        print(f"Help Seeking: {persona['help_seeking_behavior']}")
        print(f"\nStudent says: \"{persona['sample_statement']}\"\n")

        advisor_reply = input("Your response (as peer advisor): ").strip()
        if advisor_reply.lower() == "quit":
            print("Session ended. Thank you!")
            break
        elif advisor_reply.lower() == "switch":
            print("Available personas:", ", ".join(spm.list_personas()))
            new_persona = input("Enter persona to switch to: ").strip().lower()
            if new_persona in spm.list_personas():
                current_persona = new_persona
            else:
                print("Invalid persona. Staying with current persona.")
            continue
        else:
            print("Response recorded. (In a real system, feedback could be provided here.)")
            print("Type 'switch' to try another persona, or 'quit' to exit.")

if __name__ == "__main__":
    main() 