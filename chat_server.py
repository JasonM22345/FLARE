# Chat Server (chat_server.py)
import openai
from flask import Flask, request, jsonify

app = Flask(__name__)

import config

# Set up the API key from config
openai.api_key = config.OpenAI_key


@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get('message', '')
    messages = [{"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": user_input}]
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages
        )
        assistant_reply = response.choices[0].message["content"]
        return jsonify({"response": assistant_reply})
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    app.run(port=5001, debug=True)
