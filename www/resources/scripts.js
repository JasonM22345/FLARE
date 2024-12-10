document.addEventListener('DOMContentLoaded', () => {
    console.log('scripts.js loaded');
    console.log('Marked.js:', typeof marked); // Debugging: Should output 'function'

    function sendMessage() {
        const message = document.getElementById('chat-input').value;
        const chatMessages = document.getElementById('chat-messages');

        if (!message.trim()) {
            alert('Please enter a message!');
            return;
        }

        // Display user message
        const userMessage = document.createElement('div');
        userMessage.className = 'message user-message';
        userMessage.textContent = message;
        chatMessages.appendChild(userMessage);

        // Clear input
        document.getElementById('chat-input').value = '';

        // Fetch chatbot response
        fetch('/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message }),
        })
            .then((response) => response.json())
            .then((data) => {
                const botMessage = document.createElement('div');
                botMessage.className = 'message bot-message';

                if (data.response) {
                    // Extract Markdown enclosed in triple backticks (```), removing programming language
                    const markdownBlocks = [];
                    const regex = /```(\w+)?\n([\s\S]*?)```/g; // Captures optional language and content
                    let match;

                    while ((match = regex.exec(data.response)) !== null) {
                        markdownBlocks.push(match[2]); // Extract only the content, ignoring the language
                    }

                    // Render entire response without Markdown blocks as normal text
                    const cleanResponse = data.response.replace(regex, '').trim();
                    if (cleanResponse) {
                        const cleanTextDiv = document.createElement('div');
                        cleanTextDiv.textContent = cleanResponse;
                        botMessage.appendChild(cleanTextDiv);
                    }

                    // Render each Markdown block with a copy button
                    markdownBlocks.forEach((block) => {
                        const botMessageContent = document.createElement('div');
                        botMessageContent.className = 'markdown-content';
                        if (typeof marked === 'function') {
                            botMessageContent.innerHTML = marked(block);
                        } else {
                            console.error('Marked.js not loaded properly.');
                            botMessageContent.textContent = block;
                        }

                        const copyButton = document.createElement('button');
                        copyButton.className = 'copy-button';
                        copyButton.textContent = 'Copy';
                        copyButton.onclick = () => {
                            navigator.clipboard.writeText(block).then(() => {
                                alert('Markdown copied to clipboard!');
                            });
                        };

                        botMessage.appendChild(botMessageContent);
                        botMessage.appendChild(copyButton);
                    });
                } else {
                    botMessage.textContent = 'Sorry, I encountered an error.';
                }

                // Add flare-execute output and interpretation if present
                if (data.flare_execute_output) {
                    const executeOutput = document.createElement('div');
                    executeOutput.className = 'flare-execute-output';
                    executeOutput.textContent = data.flare_execute_output;
                    chatMessages.appendChild(executeOutput);
                }

                if (data.flare_execute_interpretation) {
                    const interpretationOutput = document.createElement('div');
                    interpretationOutput.className = 'flare-execute-interpretation';
                    interpretationOutput.textContent = `Interpretation: ${data.flare_execute_interpretation}`;
                    chatMessages.appendChild(interpretationOutput);
                }

                chatMessages.appendChild(botMessage);

                // Scroll to the bottom of the chat
                chatMessages.scrollTop = chatMessages.scrollHeight;
            })
            .catch((error) => {
                console.error('Error:', error);
                const errorMessage = document.createElement('div');
                errorMessage.className = 'message bot-message';
                errorMessage.textContent = 'An error occurred while communicating with the chatbot.';
                chatMessages.appendChild(errorMessage);
            });
    }

    // Expose the function globally if needed
    window.sendMessage = sendMessage;
});
