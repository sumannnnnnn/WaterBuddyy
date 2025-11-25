"""
Google Gemini AI integration for WaterBuddy
This module provides API access to Google's Gemini for hydration-related queries
"""
import os
import google.generativeai as genai
from datetime import datetime
import random

# Configure the Gemini API with the API key
def configure_genai(api_key=None):
    """Configure the Gemini API with the provided API key"""
    if api_key is None:
        api_key = os.getenv("GEMINI_API_KEY")
        
    if not api_key:
        raise ValueError("Gemini API key is required. Set it as GEMINI_API_KEY environment variable or pass it directly.")
    
    genai.configure(api_key=api_key)

# Hydration facts to supplement responses
hydration_facts = [
    "Your brain is approximately 75% water, which is why staying hydrated is crucial for cognitive function.",
    "Even mild dehydration (1-2% of body weight) can impair cognitive performance and mood.",
    "Proper hydration can reduce the risk of kidney stones by diluting stone-forming substances in urine.",
    "Drinking enough water helps maintain electrolyte balance, which is essential for nerve and muscle function.",
    "Water helps transport oxygen and nutrients to your cells, supporting overall cellular health.",
    "Hydration supports your immune system by helping your body naturally eliminate toxins and waste.",
    "Studies show that proper hydration can improve physical performance by as much as 25%.",
    "Your body's thirst mechanism becomes less effective as you age, which is why older adults need to be more mindful about drinking water.",
    "Drinking water before meals can help with weight management by creating a sense of fullness.",
    "Water helps regulate body temperature through sweating and respiration.",
    "Approximately 60% of an adult human body is water, highlighting its importance for overall health.",
    "Chronic dehydration can contribute to headaches, fatigue, and difficulty concentrating.",
    "Dark-colored urine often indicates that you need to drink more water.",
    "The Institute of Medicine recommends about 3.7 liters (125 ounces) of total water intake for men and 2.7 liters (91 ounces) for women daily.",
    "Exercise increases your water needs - you should drink about 17-20 oz of water 2-3 hours before exercise, and 7-10 oz every 10-20 minutes during activity."
]

# Hydration tips to supplement responses
hydration_tips = [
    "Keep a reusable water bottle with you at all times. Studies show visual reminders can increase water consumption by up to 25%.",
    "Set specific hydration goals for different parts of your day - like 500ml by lunch and another 500ml by dinner.",
    "Try the 8x8 rule: eight 8-ounce glasses of water throughout the day (about 2 liters total).",
    "Add natural flavors to your water with fruits like lemon, berries, cucumber, or herbs like mint or basil.",
    "Use a marked water bottle with time indicators to pace your drinking throughout the day.",
    "Download a water tracking app that sends you regular reminders to drink up.",
    "Create a routine by drinking a full glass of water after specific daily activities like brushing your teeth or checking email.",
    "Start your day with a full glass of water before your morning coffee or tea to kickstart hydration.",
    "Keep a glass of water on your desk while working and take sips between tasks.",
    "Eat water-rich foods like cucumber (96% water), zucchini (95%), watermelon (92%), and strawberries (91%).",
    "Set up water-drinking 'triggers' - like drinking water every time you check your phone or after each bathroom break.",
    "Try drinking through a straw, which can help increase your water consumption without even noticing.",
    "Make it a habit to drink a full glass of water before and after each meal.",
    "Replace at least one sugary beverage each day with water to improve both hydration and overall health.",
    "Use a smart water bottle that tracks your intake and glows when it's time to drink more water."
]

def get_gemini_model():
    """Get the Gemini model to use for generation"""
    try:
        # Try to use Gemini 1.5 Pro if available
        return genai.GenerativeModel('gemini-1.5-pro')
    except:
        try:
            # Fall back to Gemini 1.0 Pro
            return genai.GenerativeModel('gemini-1.0-pro')
        except:
            # Final fallback to whatever model is available
            available_models = genai.list_models()
            for model in available_models:
                if 'gemini' in model.name:
                    return genai.GenerativeModel(model.name)
            
            raise ValueError("No Gemini models available with your API key")

def generate(prompt):
    """
    Generate a response using Google's Gemini API based on the user's query and context
    
    Args:
        prompt: The text prompt containing the user's query and context
    
    Returns:
        A response from the Gemini model
    """
    # Extract context information from the prompt if available
    user_name = "there"
    current_amount = 0
    goal_amount = 2500
    percentage = 0
    remaining = 0
    
    try:
        # Extract user info from the prompt
        if "User's name:" in prompt:
            for line in prompt.split('\n'):
                if "User's name:" in line:
                    user_name = line.split(':')[1].strip()
                elif "Current water intake:" in line:
                    current_amount = int(line.split(':')[1].strip().replace('ml', ''))
                elif "Daily goal:" in line:
                    goal_amount = int(line.split(':')[1].strip().replace('ml', ''))
                elif "Current progress:" in line:
                    percentage = float(line.split(':')[1].strip().replace('%', ''))
                elif "Remaining water needed:" in line:
                    remaining = int(line.split(':')[1].strip().replace('ml', ''))
    except:
        # If extraction fails, calculate remaining
        remaining = goal_amount - current_amount
    
    # Determine the user's query from the prompt
    user_query = ""
    if "User's message:" in prompt:
        message_parts = prompt.split("User's message:")
        if len(message_parts) > 1:
            user_query = message_parts[1].strip()
    else:
        user_query = prompt
    
    try:
        # Try to use the Gemini API
        model = get_gemini_model()
        
        # Enhance the prompt with additional hydration information
        enhanced_prompt = f"""{prompt}

Additional hydration information to consider:
1. Did you know? {random.choice(hydration_facts)}
2. Helpful tip: {random.choice(hydration_tips)}

Please provide a helpful, friendly response to the user about their water intake or hydration question.
Keep your response concise (1-3 sentences) and focused on helping them stay hydrated.
"""
        
        response = model.generate_content(enhanced_prompt)
        return response.text
        
    except Exception as e:
        # Fallback in case of API errors
        print(f"Gemini API Error: {str(e)}")
        
        # Calculate some useful values for the fallback response
        glasses_remaining = round(remaining / 250)
        glasses_total = round(goal_amount / 250)
        current_hour = datetime.now().hour
        time_of_day = "morning" if 5 <= current_hour < 12 else "afternoon" if 12 <= current_hour < 18 else "evening"
        
        # Create simple fallback responses based on query type
        if any(x in user_query.lower() for x in ['how much', 'progress', 'water intake', 'hydration level']):
            if percentage >= 80:
                return f"You're doing great, {user_name}! You've had {current_amount}ml, which is {round(percentage)}% of your {goal_amount}ml goal."
            else:
                return f"You're currently at {round(percentage)}% of your daily goal with {current_amount}ml. You still need {remaining}ml to reach your {goal_amount}ml target. That's about {glasses_remaining} more glasses."
        
        elif any(x in user_query.lower() for x in ['tip', 'advice', 'suggest']):
            return f"Here's a hydration tip: {random.choice(hydration_tips)}"
        
        elif any(x in user_query.lower() for x in ['fact', 'benefit', 'health', 'importance']):
            return f"Hydration fact: {random.choice(hydration_facts)}"
        
        else:
            return f"Good {time_of_day}, {user_name}! I'm here to help you track your water intake. Currently you're at {round(percentage)}% of your daily goal."

# Initialize the API if environment variable is available
try:
    configure_genai()
except:
    # Will configure later when API key is provided
    pass

# Test function if this file is run directly
if __name__ == "__main__":
    test_prompt = """
You are a helpful water intake assistant named WaterBuddy, helping a user track their hydration. 
Be friendly, supportive, and provide useful information about hydration. Keep your responses concise and natural.

Respond to the user's message below. Here's some context:
- User's name: John
- Current water intake: 750ml
- Daily goal: 3000ml
- Current progress: 25%
- Remaining water needed: 2250ml

User's message: Why is staying hydrated important?
"""
    print(f"Testing with prompt...")
    result = generate(test_prompt)
    print(f"Response: {result}") 