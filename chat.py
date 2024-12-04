import openai
import config

# Set up the API key from config
openai.api_key = config.OpenAI_key

def chat_with_gpt():
    print("Welcome to the ChatGPT CLI. Type 'exit' to end the chat.")

    # Define the conversation
    messages = [{"role": "system", "content": "You are a helpful assistant."}]

    while True:
        # Get user input
        user_input = input("You: ")

        # Exit condition
        if user_input.lower() == "exit":
            print("Goodbye!")
            break

        # Append user input to messages
        messages.append({"role": "user", "content": user_input})

        try:
            # Get response from ChatGPT using the updated API
            response = openai.ChatCompletion.create(
                model="gpt-4",  # Use 'gpt-3.5-turbo' for a cheaper alternative
                messages=messages
            )

            # Extract and display the assistant's reply
            assistant_reply = response.choices[0].message["content"]
            print(f"ChatGPT: {assistant_reply}")

            # Append assistant's reply to the messages
            messages.append({"role": "assistant", "content": assistant_reply})

        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    chat_with_gpt()

