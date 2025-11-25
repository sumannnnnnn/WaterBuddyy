"""
AI helper for WaterBuddy
This module provides AI responses for the WaterBuddy chatbot using Google's Gemini API
"""
from datetime import datetime
from gemini_api import generate, configure_genai

def set_api_key(api_key):
    """
    Configure the Gemini API with the provided API key
    
    Args:
        api_key: The API key for Google's Gemini API
    """
    try:
        configure_genai(api_key)
        return True
    except Exception as e:
        print(f"Error configuring Gemini API: {str(e)}")
        return False

def generate_response(user_input, user_data=None, water_data=None):
    """
    Generate an AI response based on user input and context using Gemini API.
    
    Args:
        user_input: The user's message
        user_data: Dictionary containing user profile information
        water_data: Dictionary containing water intake information
    
    Returns:
        Generated text response
    """
    # Extract user and water data
    user_name = user_data.get('name', 'there') if user_data else 'there'
    current_amount = water_data.get('current_amount', 0) if water_data else 0
    goal_amount = water_data.get('goal', 2500) if water_data else 2500
    percentage = water_data.get('percentage', 0) if water_data else 0
    remaining = water_data.get('remaining', 0) if water_data else 0

    # Check if the user just wanted to add water (simple command processing)
    water_keywords = ['add', 'water', 'glass', 'cup', 'ml', 'bottle', 'drink']
    if any(keyword in user_input.lower() for keyword in water_keywords) and len(user_input.split()) <= 4:
        # If it's just an add water command, give a simple response about the update
        if percentage >= 100:
            return f"Great job! I've updated your water intake. You've reached {percentage:.0f}% of your daily goal!"
        elif percentage >= 75:
            return f"Almost there! I've updated your water intake. You're at {percentage:.0f}% of your daily goal."
        elif percentage >= 50:
            return f"Halfway there! I've updated your water intake. You're at {percentage:.0f}% of your daily goal."
        elif percentage >= 25:
            return f"Good start! I've updated your water intake. You're at {percentage:.0f}% of your daily goal."
        else:
            return f"I've updated your water intake. You're at {percentage:.0f}% of your daily goal."
    
    # Create a prompt for the Gemini API based on user's query and water data
    prompt = f"""
You are a helpful water intake assistant named WaterBuddy, helping a user track their hydration. 
Be friendly, supportive, and provide useful information about hydration. Keep your responses concise and natural.

Respond to the user's message below. Here's some context:
- User's name: {user_name}
- Current water intake: {current_amount}ml
- Daily goal: {goal_amount}ml
- Current progress: {percentage:.0f}%
- Remaining water needed: {remaining}ml

User's message: {user_input}

Note: If the user is asking about water intake progress, be specific with the numbers. 
If they're asking about hydration tips or benefits, provide valuable information.
DO NOT mention that you're an AI or language model.
"""
    
    # Get response from the API
    try:
        return generate(prompt)
    except Exception as e:
        # Fallback responses in case of API failure
        current_hour = datetime.now().hour
        time_greeting = "morning" if 5 <= current_hour < 12 else "afternoon" if 12 <= current_hour < 18 else "evening"
        
        fallback = f"Good {time_greeting}, {user_name}! I'm here to help you track your water intake. Currently you're at {percentage:.0f}% of your daily goal."
        print(f"API Error: {str(e)}")
        return fallback 