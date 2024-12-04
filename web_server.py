# Flare Web Server (web_server.py)
from flask import Flask, render_template, request, jsonify
import requests
import subprocess

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/tests')
def tests():
    return render_template('tests.html')

@app.route('/tests/<test_id>')
def test_details(test_id):
    return render_template('test_details.html', test_id=test_id)

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get('message', '')
    response = requests.post('http://localhost:5001/chat', json={"message": user_input})
    return jsonify(response.json())

@app.route('/execute', methods=['POST'])
def execute():
    commands = request.json.get('commands', [])
    for command in commands:
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            if result.returncode != 0:
                error_output = result.stderr
                # Send error back to ChatGPT for correction
                chat_response = requests.post('http://localhost:5001/chat', 
                                              json={"message": f"The command {command} failed with error: {error_output}. Fix it."})
                suggestions = chat_response.json().get('response', '')
                return jsonify({"error": error_output, "suggestions": suggestions})
        except Exception as e:
            return jsonify({"error": str(e)})
    return jsonify({"status": "Execution completed successfully."})

if __name__ == '__main__':
    app.run(debug=True)
