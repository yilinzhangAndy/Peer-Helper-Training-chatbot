from core.chatbot_pipeline import ChatbotPipeline

if __name__ == "__main__":
    chatbot = ChatbotPipeline()
    persona = "alpha"
    while True:
        user_input = input("User: ")
        if user_input.lower() in ["exit", "quit"]:
            break
        result = chatbot.process_message(user_input, persona)
        print(f"\n[Persona: {result['persona']}]")
        print(f"Intent: {result['intent']}")
        print(f"Context: {result['context'][:100]}...")
        print(f"Chatbot: {result['answer']}\n") 