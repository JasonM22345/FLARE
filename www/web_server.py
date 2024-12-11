from flask import Flask, render_template, request, jsonify, send_from_directory
import requests
import subprocess
import os
import re
import yaml
import git  # GitPython for handling Git repositories

app = Flask(__name__, static_folder='resources', template_folder='.')

# Ensure /tmp/flare_ws exists
FLARE_WORKSPACE = '/tmp/flare_ws'
os.makedirs(FLARE_WORKSPACE, exist_ok=True)

# Path to the default playbook
DEFAULT_PLAYBOOK_PATH = './FLARE_playbook/default.yaml'


def get_default_playbook():
    """Read and return the content of the default playbook as a string."""
    try:
        with open(DEFAULT_PLAYBOOK_PATH, 'r') as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        print(f"Default playbook not found at {DEFAULT_PLAYBOOK_PATH}.")
        return None
    except Exception as e:
        print(f"Error reading default playbook: {e}")
        return None


def get_repo_tree(repo_dir):
    """Generate a directory tree of the Git repository."""
    tree_output = []
    for root, dirs, files in os.walk(repo_dir):
        for name in dirs + files:
            tree_output.append(os.path.relpath(os.path.join(root, name), repo_dir))
    return "\n".join(tree_output)


def get_git_repo_details(git_url):
    """Get the details (README, Makefile, Tree) of the Git repo."""
    try:
        repo_dir = os.path.join(FLARE_WORKSPACE, 'repo')
        if os.path.exists(repo_dir):
            subprocess.run(['rm', '-rf', repo_dir], check=True)  # Clean up previous clone
        print(f"Cloning repository from {git_url}")
        repo = git.Repo.clone_from(git_url, repo_dir)

        # Check for README files
        readme_files = ['README.md', 'readme.md', 'README.rst', 'readme.rst', 'readme.txt', 'README.txt']
        readme_content = ''
        for readme in readme_files:
            readme_path = os.path.join(repo_dir, readme)
            if os.path.isfile(readme_path):
                with open(readme_path, 'r') as readme_file:
                    readme_content = readme_file.read()
                break  # Stop after the first README file is found

        # Check for Makefile
        makefile_content = ''
        makefile_path = os.path.join(repo_dir, 'Makefile')
        if os.path.isfile(makefile_path):
            with open(makefile_path, 'r') as makefile_file:
                makefile_content = makefile_file.read()

        # Get the file structure (tree) of the repository
        tree_output = get_repo_tree(repo_dir)

        # Prepare the content to be added to the user prompt
        repo_details = ""
        if readme_content:
            repo_details += f"{{README}}:\n{readme_content}\n"
        if makefile_content:
            repo_details += f"{{Makefile}}:\n{makefile_content}\n"
        repo_details += f"{{Tree}}:\n{tree_output}\n"

        return repo_details

    except git.exc.GitCommandError as e:
        return f"Error cloning repository: {str(e)}"
    except Exception as e:
        return f"Error processing Git repository: {str(e)}"



def get_fuzzing_status(target_path):
    """Check the status of the fuzzing process for the given target."""
    try:
        # Running afl-whatsup to get the status of the fuzzing process
        output = subprocess.check_output(
            ['afl-whatsup', '-s', os.path.join(FLARE_WORKSPACE, target_path, 'out')],
            text=True
        )
        return output
    except subprocess.CalledProcessError as e:
        return f"Error retrieving fuzzing status: {str(e)}"


def find_target_program(target_path):
    """Extract the target program name from the target path."""
    # Extract the last part of the target path
    target_exec_name = os.path.basename(target_path) # Target Executable name
    target_program = os.path.join(FLARE_WORKSPACE, target_path, target_exec_name)
    
    # Verify the extracted name is valid
    if target_program:
        return target_program
    return None



def generate_crash_report(target_path):
    """Generate a report of any crashes encountered during fuzzing."""
    crash_report = ""
    crashes_dir = os.path.join(FLARE_WORKSPACE, target_path, 'out', 'default', 'crashes')

    try:
        # Check if the crashes directory exists
        if os.path.isdir(crashes_dir):
            for crash_file in os.listdir(crashes_dir):
                crash_path = os.path.join(crashes_dir, crash_file)
                if os.path.isfile(crash_path):
                    crash_report += f"### Crash Input: {crash_file}\n"
                    crash_report += f"Path: {crash_path}\n"

                    # Dynamically find the target program
                    target_program = find_target_program(target_path)
                    if target_program:
                        # Replaying the crash using the found target program
                        replay_output = ""
                        try:
                            result = subprocess.run(
                                [target_program, crash_path],
                                text=True,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                check=False  # Don't raise an exception on non-zero exit
                            )
                            replay_output = (
                                f"Replay Output (stdout):\n{result.stdout}\n"
                                f"Replay Error (stderr):\n{result.stderr}\n"
                                f"Exit Code: {result.returncode}\n"
                            )
                        except Exception as e:
                            replay_output = f"Error running target program: {str(e)}\n"

                        crash_report += replay_output
                    else:
                        crash_report += "Error: No target program found for replay.\n"

                    # Generate crash explanation using the chatbot
                    try:
                        message_to_send = {
                            "prompt": "A crash from a fuzzer was replayed with the original executable. Explain the crash, what it could possibly be, in one to three sentences. Output below:",
                            "crash_input": crash_file,
                            "stdout": result.stdout,
                            "stderr": result.stderr,
                            "exit_code": result.returncode
                        }

                        response = requests.post('http://localhost:5001/chat', json={"message": message_to_send})
                        response.raise_for_status()  # Ensure HTTP errors are caught
                        chatbot_response = response.json().get("response", "Not enough context, review manually.")

                        crash_report += f"### Crash Explanation:\n{chatbot_response}\n\n"
                    except Exception as e:
                        crash_report += f"### Crash Explanation:\nNot enough context, review manually. (Error: {str(e)})\n\n"
        else:
            # If the crashes directory does not exist
            crash_report = f"Error: Crashes directory not found at {crashes_dir}"

    except Exception as e:
        # Catch any exception that occurs and return the error message
        crash_report = f"Error accessing or processing the crashes directory: {str(e)}"

    return crash_report



@app.route('/')
def home():
    return render_template('index.html')


@app.route('/tests', methods=['GET', 'POST'])
def tests():
    if request.method == 'POST':
        target_name = request.form.get('target-name', '').strip()

        if target_name:
            # Generate the full path to the target in the workspace directory
            target_path = os.path.join(FLARE_WORKSPACE, target_name)

            # Generate fuzzing status report
            fuzzing_status = get_fuzzing_status(target_path)
            crash_report = generate_crash_report(target_path)

            # Send fuzzing status to chatbot for explanation
            explanation_request = f"explain the fuzzing status for the target {target_name}:\n{fuzzing_status}. Also explain fuzzing results in terms of what kind of bug it probably is. help triage it."
            explanation_request += f" Do not explain menial things like file system, etc."
            explanation_response = requests.post('http://localhost:5001/chat', json={"message": explanation_request}).json()
            fuzzing_explanation = explanation_response.get("response", "No explanation available.")

            # Send crash report to chatbot for each crash explanation
            crash_explanations = ""
            crashes_dir = os.path.join(FLARE_WORKSPACE, target_path, 'out', 'default', 'crashes')
            for crash_file in os.listdir(crashes_dir):
                crash_path = os.path.join(crashes_dir, crash_file)
                if os.path.isfile(crash_path):
                    crash_explanation_request = f"Please explain the following crash for the target {target_name} with input file {crash_file}:\n{crash_path}"
                    crash_explanation_response = requests.post('http://localhost:5001/chat', json={"message": crash_explanation_request}).json()
                    crash_explanations += f"### Crash Explanation for {crash_file}:\n{crash_explanation_response.get('response', 'No explanation available.')}\n\n"

            # Combine the results
            full_report = f"### Fuzzing Status for {target_name}:\n\n{fuzzing_status}\n\n### Fuzzing Explanation:\n{fuzzing_explanation}\n\n### Crash Report:\n\n{crash_report}\n\n### Crash Explanations:\n{crash_explanations}"

            return render_template('tests.html', target_name=target_name, fuzzing_report=full_report)
        else:
            return render_template('tests.html', error="Please provide a valid target name.")

    return render_template('tests.html')


@app.route('/tests/<test_id>')
def test_details(test_id):
    return render_template('test_details.html', test_id=test_id)


@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get('message', '')
    git_repo_url = None
    if 'git' in user_input.lower():  # Check if the user provided a Git repo URL
        # Extract the Git repository URL from the user input
        match = re.search(r'(https?://[^\s]+\.git)', user_input)
        if match:
            git_repo_url = match.group(1)

    # If a Git repo URL is provided, fetch details (README, Makefile, Tree)
    repo_details = ""
    if git_repo_url:
        repo_details = get_git_repo_details(git_repo_url)

    # Read the default playbook content
    default_playbook = get_default_playbook()
    playbook_content = ""
    if default_playbook:
        # Convert YAML to a readable string format
        playbook_content = yaml.dump(default_playbook)

    # Prepare the message to send to the chatbot
    message_to_send = user_input

    # If "playbook:" is not already included in the user input, prepend the playbook content
    if "playbook:" not in user_input.lower() and playbook_content:
        message_to_send = f"Answer {user_input} based on these guidelines {playbook_content}"

    # If Git repo details are found, append them to the message
    if repo_details:
        message_to_send = f"{message_to_send} This is the git repo {repo_details}"

    try:
        # Call the chatbot backend
        response = requests.post('http://localhost:5001/chat', json={"message": message_to_send})
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

                # Request interpretation of the execution output from the chatbot, along with the original user input
                interpretation_request = f"Given the following user prompt:\n{user_input}\n\nAnd the following execution output:\n{execution_outputs[-1]}\n\nPlease interpret the results and explain what happened."
                interpretation_response = requests.post('http://localhost:5001/chat', json={"message": interpretation_request}).json()
                chatbot_response["flare_execute_interpretation"] = interpretation_response.get("response", "No interpretation available.")

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
