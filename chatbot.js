/**
 * WaterBuddy Chatbot Functionality
 * Handles user interactions with the water intake chatbot
 * Provides intelligent responses based on context
 */

class WaterChatbot {
    constructor(chatContainerId, messageInputId, sendButtonId) {
        this.chatContainer = document.getElementById(chatContainerId);
        this.messageInput = document.getElementById(messageInputId);
        this.sendButton = document.getElementById(sendButtonId);
        
        this.initEventListeners();
        this.addWelcomeMessage();
    }
    
    initEventListeners() {
        this.sendButton.addEventListener('click', () => this.sendMessage());
        
        this.messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                this.sendMessage();
            }
        });
    }
    
    addWelcomeMessage() {
        // Add a welcome message when the chat is initialized
        const welcomeMessage = "👋 Hello! I'm your WaterBuddy AI assistant. I can help you track your water intake, provide hydration tips, and answer your questions. How can I help you today?";
        this.addBotMessage(welcomeMessage);
    }
    
    formatMessage(message) {
        // Convert URLs to clickable links
        message = message.replace(/(https?:\/\/[^\s]+)/g, '<a href="$1" target="_blank" class="text-blue-600 hover:underline">$1</a>');
        
        // Convert newlines to <br>
        message = message.replace(/\n/g, '<br>');
        
        // Make API key note a bit more distinct if present
        if (message.includes("(Note: For more advanced AI responses")) {
            const noteParts = message.split("(Note: For more advanced AI responses");
            message = noteParts[0] + '<span class="block mt-2 text-xs text-yellow-700 italic">(Note: For more advanced AI responses' + noteParts[1] + '</span>';
        }
        
        return message;
    }
    
    async sendMessage() {
        const message = this.messageInput.value.trim();
        
        if (!message) return;
        
        // Add user message to chat
        this.addUserMessage(message);
        this.messageInput.value = '';

        // Show typing indicator
        this.showTypingIndicator();
        
        try {
            const response = await fetch('/chatbot_message', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message: message }),
            });
            
            // Add a small delay to simulate typing
            await new Promise(resolve => setTimeout(resolve, Math.random() * 1000 + 1000));
            
            // Hide typing indicator
            this.hideTypingIndicator();
            
            const data = await response.json();
            if (data.success) {
                // Add bot response to chat
                this.addBotMessage(data.message);
                
                // Update water amount if changed
                if (data.current_amount !== window.currentAmount) {
                    window.currentAmount = data.current_amount;
                    window.goalAmount = data.goal;
                    window.updateWaterFill();
                    
                    // Update calendar for today
                    const today = new Date().toISOString().split('T')[0];
                    window.calendarData[today] = {
                        amount: data.current_amount,
                        goal: data.goal,
                        achieved: data.current_amount >= data.goal
                    };
                    
                    // Refresh calendar
                    window.renderCalendar(window.currentDate);
                    window.updateStreaks();
                }
                
                // Update API status note if needed
                if (data.api_key_set === false) {
                    const apiStatusNote = document.querySelector('.bg-yellow-800\\/30');
                    if (apiStatusNote && apiStatusNote.classList.contains('hidden')) {
                        apiStatusNote.classList.remove('hidden');
                    }
                }
            }
        } catch (error) {
            console.error('Error sending message:', error);
            this.hideTypingIndicator();
            this.addBotMessage("I'm sorry, I couldn't process your message. Please try again later.");
        }
    }
    
    addUserMessage(message) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'flex mb-4 justify-end';
        messageDiv.innerHTML = `
            <div class="bg-blue-500 p-3 rounded-lg rounded-tr-none max-w-xs">
                <p class="text-white">${this.formatMessage(message)}</p>
            </div>
            <div class="flex-shrink-0 ml-3">
                <div class="w-10 h-10 rounded-full bg-blue-700 flex items-center justify-center">
                    <i class="fas fa-user text-white"></i>
                </div>
            </div>
        `;
        
        this.chatContainer.appendChild(messageDiv);
        this.scrollToBottom();
    }
    
    addBotMessage(message) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'flex mb-4';
        messageDiv.innerHTML = `
            <div class="flex-shrink-0 mr-3">
                <div class="w-10 h-10 rounded-full bg-blue-500 flex items-center justify-center">
                    <i class="fas fa-robot text-white"></i>
                </div>
            </div>
            <div class="bg-blue-100 p-3 rounded-lg rounded-tl-none max-w-xs">
                <p class="text-gray-800">${this.formatMessage(message)}</p>
            </div>
        `;
        
        this.chatContainer.appendChild(messageDiv);
        this.scrollToBottom();
    }
    
    showTypingIndicator() {
        document.getElementById('typingIndicator').classList.remove('hidden');
        this.scrollToBottom();
    }
    
    hideTypingIndicator() {
        document.getElementById('typingIndicator').classList.add('hidden');
    }
    
    scrollToBottom() {
        this.chatContainer.scrollTop = this.chatContainer.scrollHeight;
    }
}

// Initialize chatbot when the document is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.chatbot = new WaterChatbot('chatContainer', 'messageInput', 'sendMessage');
});