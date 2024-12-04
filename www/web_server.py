from flask import Flask, render_template, request, jsonify
import requests
import subprocess
import os
import re  # Import regex module for extracting Markdown blocks

app = Flask(__name__, static_folder='resources', template_folder='.')

# Ensure /tmp/flare_ws exists
FLARE_WORKSPACE = '/tmp/flare_ws'
os.makedirs(FLARE_WORKSPACE, exist_ok=True)


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
        chatbot_response = response.json()

        # Check for "flare-execute" command
        if "flare-execute" in user_input:
            try:
                # Extract Markdown blocks with commands
                markdown_blocks = re.findall(r'```(?:\w+)?\n([\s\S]*?)```', chatbot_response.get("response", ""))
                execution_outputs = []

                # Execute each block
                for block in markdown_blocks:
                    command = block.strip()
                    if command:  # Ensure the block isn't empty
                        result = subprocess.run(
                            command,
                            shell=True,
                            executable='/bin/bash',  # Use bash for execution
                            capture_output=True,
                            text=True,
                            cwd=FLARE_WORKSPACE
                        )
                        # Capture stdout or stderr based on the result
                        execution_output = result.stdout if result.returncode == 0 else result.stderr
                        execution_outputs.append(f"Command: {command}\nOutput:\n{execution_output.strip()}")

                # Add execution output to the chatbot response
                if execution_outputs:
                    chatbot_response["flare_execute_output"] = "\n\n".join(execution_outputs)

            except Exception as e:
                chatbot_response["flare_execute_output"] = f"Error during execution: {str(e)}"

        return jsonify(chatbot_response)
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Failed to connect to chat server: {str(e)}"})


@app.route('/resources/<path:filename>')
def serve_static(filename):
    return send_from_directory(os.path.join(os.getcwd(), 'resources'), filename)


if __name__ == '__main__':
    app.run(debug=True)
