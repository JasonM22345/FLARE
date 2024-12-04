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
            botMessage.textContent = data.response || 'Sorry, I encountered an error.';
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

