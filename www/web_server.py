from flask import Flask, render_template, request, jsonify
import requests
import subprocess
import os

app = Flask(__name__, static_folder='resources', template_folder='.')

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
    try:
        # Call the chatbot backend
        response = requests.post('http://localhost:5001/chat', json={"message": user_input})
        response.raise_for_status()  # Ensure HTTP errors are caught
        return jsonify(response.json())
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Failed to connect to chat server: {str(e)}"})

@app.route('/resources/<path:filename>')
def serve_static(filename):
    return send_from_directory(os.path.join(os.getcwd(), 'resources'), filename)

if __name__ == '__main__':
    app.run(debug=True)

