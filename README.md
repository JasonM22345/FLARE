# Author: Jason Mensah-Homiah - jm2jy@virginia.edu 12/07/2024

Here’s the updated **README** with sample commands and file structure details included:

```markdown
# FLARE: Fuzzing Lifecycle Automation & Reporting Environment

## Description

FLARE (Fuzzing Lifecycle Automation \& Reporting Environment) is an automated platform designed to simplify the fuzzing process for users with minimal technical expertise. By leveraging a chatbot powered by a large language model (LLM), FLARE automates key tasks in fuzzing campaigns, including target setup, seed generation, code instrumentation, and execution. It also provides real-time monitoring and reporting on the fuzzing progress. 

The system enables users to initiate fuzzing operations by simply providing a GitHub repository URL, making fuzzing more accessible without requiring in-depth knowledge of the underlying processes.

## How It Works

1. **User Input**: The user provides a GitHub repository URL (e.g., `Fuzz https://github.com/fuzzstati0n/fuzzgoat.git`).
2. **Preprocessing**: FLARE checks for the presence of a README and Makefile in the repository and adds them to the LLM’s prompt for additional context.
3. **Playbook Integration**: Playbooks with setup instructions, LLM restrictions, tips, and resources are referenced.
4. **Code Compilation & Instrumentation**: FLARE generates bash scripts to compile and instrument the code.
5. **Fuzzing**: The fuzzing process is automatically started using AFL, and FLARE monitors the progress in real-time.
6. **Status & Reporting**: Users can request fuzzing status updates, and FLARE will generate detailed reports, including crash information and fuzzing metrics.

## Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/flare.git
cd flare
```

### 2. Make `setups.sh` Executable

```bash
chmod +x setups.sh
```

### 3. Install FLARE Dependencies

Run the setup script to install FLARE's dependencies:

```bash
./setups.sh
```

**Note**: AFL (American Fuzzy Lop) is **not** installed via the setup script. You must install it manually from [AFL+ Documentation](https://aflplus.plus/docs/install/).

### 4. ChatGPT API Key Configuration

- The provided ChatGPT API key in `config.py` will be deactivated on 12/20/2024. After that, you'll need to replace it with your own API key.

## Folder Structure

- **www/**: Contains `web_server.py`, which serves as the web-based interface using Flask. This is the main user interface for interacting with FLARE.
- **chat_server.py**: Contains the chatbot logic and communicates with the LLM to process user input and return the required output.
- **www/FLARE_playbook**: Contains the playbooks used to guide FLARE in setting up fuzzing environments, LLM restrictions, and fuzzing tips.

## Sample Commands

Here are a few sample commands that you can use with the FLARE chatbot:

1. **Start Fuzzing a Repository**:
    To start fuzzing a repository, simply provide the GitHub URL and use the `[flare-execute]` tag to indicate that the command should be executed by FLARE:
    
    ```bash
    fuzz this "https://github.com/fuzzstati0n/fuzzgoat.git" [flare-execute]
    ```
    
    FLARE will preprocess the request, check for the README and Makefile, generate necessary scripts, compile the code, instrument it, and begin fuzzing automatically.

2. **Check Fuzzing Status**:
    To check the status of a fuzzing process, simply ask FLARE for the status of the current target, e.g., "fuzzgoat":
    
    ```bash
    what is the status of "fuzzgoat" I am currently fuzzing.
    ```

    FLARE will provide real-time status, including the number of crashes, runtime, speeds, coverage, and any other relevant information.

## Future Work

FLARE is designed with modularity and flexibility, allowing for future improvements:

- **Crash Triage**: The integration of automated crash triage tools will allow FLARE to categorize and handle crashes more effectively.
- **Seed Generation & Harnessing**: Future versions will complete seed generation and harness creation functionality to further optimize fuzzing.
- **Integration with More Fuzzing Tools**: Adding additional fuzzing tools to provide users with multiple fuzzing options.
- **Offline LLM Support**: The ability to use offline models will be explored for environments where network connectivity is restricted.

## Conclusion

FLARE demonstrates the potential of using LLMs to automate and simplify the fuzzing process. While some features like crash triage and advanced seed generation are not yet fully implemented, FLARE provides a solid foundation for future developments. Its open architecture allows for easy integration of additional fuzzing tools and techniques, making it a powerful tool for simplifying software security testing.

