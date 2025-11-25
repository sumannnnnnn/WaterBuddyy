from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import os
import json
from datetime import datetime, timedelta
import random

# Import database and models
from database import db, User, WaterIntake, DailyGoal, WaterReminder
# Import local response generator
from gemini_helper import generate_response, set_api_key

# Create Flask app
app = Flask(__name__)

# Configure the app
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///water_tracker.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'water_intake_tracker_secret_key'

# Initialize the database with the app
db.init_app(app)

# Create database tables
with app.app_context():
    db.create_all()

# Try to load Gemini API key from environment variable
gemini_api_key = os.environ.get('GEMINI_API_KEY')
if gemini_api_key:
    try:
        if set_api_key(gemini_api_key):
            print("Gemini API key loaded from environment variable")
    except Exception as e:
        print(f"Error loading Gemini API key from environment: {str(e)}")

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if request.method == 'POST':
        data = request.form
        
        # Check if user exists
        user = None
        if 'user_id' in session:
            user = User.query.get(session['user_id'])
        
        if not user:
            # Create new user
            user = User(
                name=data['name'],
                age=int(data['age']),
                weight=float(data['weight']),
                height=float(data['height']),
                profession=data['profession'],
                email=data.get('email', '')
            )
            db.session.add(user)
            db.session.commit()
            session['user_id'] = user.id
        else:
            # Update existing user
            user.name = data['name']
            user.age = int(data['age'])
            user.weight = float(data['weight'])
            user.height = float(data['height'])
            user.profession = data['profession']
            user.email = data.get('email', user.email)
            db.session.commit()
        
        # Calculate recommended water intake
        calculate_water_goal(user)
        
        return redirect(url_for('dashboard'))
    
    user = None
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
    
    return render_template('profile.html', user=user)

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    
    user = User.query.get(session['user_id'])
    if not user:
        return redirect(url_for('index'))
    
    # Get today's water intake
    today = datetime.now().date()
    today_intake = WaterIntake.query.filter_by(
        user_id=user.id, 
        date=today
    ).first()
    
    if not today_intake:
        today_intake = WaterIntake(user_id=user.id, date=today, amount=0)
        db.session.add(today_intake)
        db.session.commit()
    
    # Get daily goal
    daily_goal = DailyGoal.query.filter_by(user_id=user.id).first()
    if not daily_goal:
        daily_goal = calculate_water_goal(user)
    
    # Get intake history for the last 30 days
    thirty_days_ago = today - timedelta(days=30)
    intake_history = WaterIntake.query.filter(
        WaterIntake.user_id == user.id,
        WaterIntake.date >= thirty_days_ago
    ).all()
    
    # Format history for calendar
    calendar_data = {}
    for intake in intake_history:
        date_str = intake.date.strftime('%Y-%m-%d')
        goal_achieved = intake.amount >= daily_goal.amount
        calendar_data[date_str] = {
            'amount': intake.amount,
            'goal': daily_goal.amount,
            'achieved': goal_achieved
        }
    
    # Prepare calendar days for template
    now = datetime.now()
    current_month_days = []
    
    # Get the first day of the month and the number of days in the month
    first_day = datetime(now.year, now.month, 1)
    if now.month == 12:
        next_month = datetime(now.year + 1, 1, 1)
    else:
        next_month = datetime(now.year, now.month + 1, 1)
    
    num_days = (next_month - first_day).days
    
    # Add empty days for the beginning of the month
    weekday = first_day.weekday()
    for _ in range((weekday + 1) % 7):  # Convert to Sunday-based week
        current_month_days.append({'empty': True})
    
    # Add the days of the month
    for day in range(1, num_days + 1):
        date_obj = datetime(now.year, now.month, day).date()
        date_str = date_obj.strftime('%Y-%m-%d')
        
        water_intake = WaterIntake.query.filter_by(
            user_id=user.id, 
            date=date_obj
        ).first()
        
        achieved = False
        if water_intake and daily_goal:
            achieved = water_intake.amount >= daily_goal.amount
        
        current_month_days.append({
            'day': day,
            'empty': False,
            'achieved': achieved,
            'today': date_obj == today
        })
    
    # Get percentage of water consumed
    percentage = min(100, int((today_intake.amount / daily_goal.amount) * 100)) if daily_goal.amount > 0 else 0
    
    # Calculate streak
    streak = 0
    check_date = today - timedelta(days=1)
    
    while True:
        intake = WaterIntake.query.filter_by(
            user_id=user.id, 
            date=check_date
        ).first()
        
        if intake and intake.amount >= daily_goal.amount:
            streak += 1
            check_date -= timedelta(days=1)
        else:
            break
    
    # Add today if goal achieved
    if today_intake.amount >= daily_goal.amount:
        streak += 1
    
    # Get a random hydration tip
    tips = [
        "Drinking water before meals can help with weight management.",
        "Herbal teas count towards your daily water intake.",
        "Eat water-rich fruits and vegetables to boost hydration.",
        "Keep a water bottle with you at all times as a visual reminder.",
        "Try infusing your water with fruits for added flavor.",
        "Drinking cold water can help burn more calories.",
        "Proper hydration can help reduce headaches.",
        "Replace sugary drinks with water to reduce calorie intake.",
        "Drinking water can help improve your mood and cognitive function."
    ]
    tip = random.choice(tips)
    
    # Check if Gemini API key is set
    gemini_api_key_set = session.get('gemini_api_key_set', False)
    
    return render_template(
        'dashboard.html', 
        user=user,
        intake=today_intake.amount,
        target=daily_goal.amount,
        percentage=percentage,
        streak=streak,
        streak_percentage=min(100, streak * 10),  # 10 days is 100%
        calendar_days=current_month_days,
        current_date=today.strftime('%B %d, %Y'),
        tip=tip,
        gemini_api_key_set=gemini_api_key_set
    )

@app.route('/insights')
def insights():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    
    user = User.query.get(session['user_id'])
    if not user:
        return redirect(url_for('index'))
    
    # Get water intake history for the last 30 days
    today = datetime.now().date()
    thirty_days_ago = today - timedelta(days=30)
    intake_history = WaterIntake.query.filter(
        WaterIntake.user_id == user.id,
        WaterIntake.date >= thirty_days_ago
    ).order_by(WaterIntake.date).all()
    
    # Get daily goal
    daily_goal = DailyGoal.query.filter_by(user_id=user.id).first()
    
    # Calculate current streak
    streak = 0
    check_date = today - timedelta(days=1)
    
    while True:
        intake = WaterIntake.query.filter_by(
            user_id=user.id, 
            date=check_date
        ).first()
        
        if intake and intake.amount >= daily_goal.amount:
            streak += 1
            check_date -= timedelta(days=1)
        else:
            break
    
    # Add today if goal achieved
    today_intake = WaterIntake.query.filter_by(
        user_id=user.id, 
        date=today
    ).first()
    
    if today_intake and today_intake.amount >= daily_goal.amount:
        streak += 1
    
    # Get all historical data for badge calculation
    all_history = WaterIntake.query.filter_by(user_id=user.id).order_by(WaterIntake.date).all()
    
    # Calculate badges
    badges = {
        'first_day': len(all_history) > 0,
        'week_streak': streak >= 7,
        'month_perfect': False,  # Will calculate below
        'overachiever': False,   # Will calculate below
        'early_bird': False,     # Placeholder for tracking early logs
        'night_owl': False,      # Placeholder for tracking late logs
        'consistency': False,    # Placeholder for tracking multiple logs per day
        'goal_setter': False     # Placeholder - would need to track goal changes
    }
    
    # Check for perfect month (30 days)
    if streak >= 30:
        badges['month_perfect'] = True
    
    # Check for overachiever (exceeding goal by 50% for a week)
    overachiever_days = 0
    for i in range(min(7, len(all_history))):
        if i >= len(all_history):
            break
        intake_record = all_history[-(i+1)]  # Get most recent days
        if intake_record.amount >= daily_goal.amount * 1.5:
            overachiever_days += 1
    
    badges['overachiever'] = overachiever_days >= 7
    
    # For now, simulate some more badges based on streak
    if streak >= 5:
        badges['early_bird'] = True
        badges['night_owl'] = True
    
    if streak >= 10:
        badges['consistency'] = True
        badges['goal_setter'] = True
    
    # Prepare calendar days for template
    now = datetime.now()
    current_month_days = []
    current_month = now.strftime('%B %Y')
    
    # Get the first day of the month and the number of days in the month
    first_day = datetime(now.year, now.month, 1)
    if now.month == 12:
        next_month = datetime(now.year + 1, 1, 1)
    else:
        next_month = datetime(now.year, now.month + 1, 1)
    
    num_days = (next_month - first_day).days
    
    # Add empty days for the beginning of the month
    weekday = first_day.weekday()
    for _ in range((weekday + 1) % 7):  # Convert to Sunday-based week
        current_month_days.append({'empty': True})
    
    # Add the days of the month
    for day in range(1, num_days + 1):
        date_obj = datetime(now.year, now.month, day).date()
        date_str = date_obj.strftime('%Y-%m-%d')
        
        water_intake = WaterIntake.query.filter_by(
            user_id=user.id, 
            date=date_obj
        ).first()
        
        streak_day = False
        if water_intake and daily_goal:
            streak_day = water_intake.amount >= daily_goal.amount
        
        current_month_days.append({
            'day': day,
            'empty': False,
            'streak': streak_day,
            'today': date_obj == today
        })
    
    return render_template(
        'insights.html',
        user=user,
        streak=streak,
        calendar_days=current_month_days,
        current_month=current_month,
        badges=badges
    )

@app.route('/settings')
def settings():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    
    user = User.query.get(session['user_id'])
    if not user:
        return redirect(url_for('index'))
    
    # Get the user's reminder settings
    reminder = WaterReminder.query.filter_by(user_id=user.id).first()
    if not reminder:
        reminder = WaterReminder(user_id=user.id)
        db.session.add(reminder)
        db.session.commit()
    
    # Check if Gemini API key is set
    gemini_api_key_set = session.get('gemini_api_key_set', False)
    
    # For now, redirect to profile page where users can modify their information
    # In a future update, create a dedicated settings.html template
    return render_template('settings.html', 
                          user=user, 
                          reminder=reminder,
                          gemini_api_key_set=gemini_api_key_set)

@app.route('/add_water', methods=['POST'])
def add_water():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'})
    
    data = request.json
    amount = data.get('amount', 0)
    
    today = datetime.now().date()
    intake = WaterIntake.query.filter_by(
        user_id=session['user_id'], 
        date=today
    ).first()
    
    if not intake:
        intake = WaterIntake(
            user_id=session['user_id'],
            date=today,
            amount=amount
        )
        db.session.add(intake)
    else:
        intake.amount += amount
    
    db.session.commit()
    
    # Get daily goal
    daily_goal = DailyGoal.query.filter_by(user_id=session['user_id']).first()
    goal_achieved = intake.amount >= daily_goal.amount if daily_goal else False
    
    # Calculate percentage for the water fill display
    percentage = min(100, int((intake.amount / daily_goal.amount) * 100)) if daily_goal and daily_goal.amount > 0 else 0
    
    return jsonify({
        'success': True, 
        'current_amount': intake.amount,
        'goal': daily_goal.amount if daily_goal else 0,
        'goal_achieved': goal_achieved,
        'percentage': percentage
    })

@app.route('/chatbot_message', methods=['POST'])
def chatbot_message():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'})
    
    data = request.json
    user_message = data.get('message', '').lower()
    
    user = User.query.get(session['user_id'])
    today = datetime.now().date()
    intake = WaterIntake.query.filter_by(user_id=user.id, date=today).first()
    daily_goal = DailyGoal.query.filter_by(user_id=user.id).first()
    
    if not intake:
        intake = WaterIntake(user_id=user.id, date=today, amount=0)
        db.session.add(intake)
        db.session.commit()

    # Extract water amount if present in the message
    amount = 0
    water_added = False
    
    # Check for direct water commands
    if user_message.strip() == "add":
        # Default amount for simple "add" command
        amount = 250  # Default to one glass (250ml)
        water_added = True
    # Check for direct numbers (e.g., "300" to add 300ml)
    elif user_message.strip().isdigit():
        amount = int(user_message.strip())
        water_added = True
    # Check for "add X" patterns (e.g., "add 300ml")
    elif 'add' in user_message and ('water' in user_message or 'glass' in user_message or 'cup' in user_message or 'ml' in user_message or 'bottle' in user_message or len(user_message.split()) <= 3):
        words = user_message.split()
        for i, word in enumerate(words):
            try:
                # Remove any non-digit characters (e.g., "300ml" -> "300")
                cleaned_word = ''.join(c for c in word if c.isdigit())
                if cleaned_word:
                    num = int(cleaned_word)
                    if i + 1 < len(words):
                        if any(unit in words[i + 1] for unit in ['glass', 'glasses', 'cup', 'cups']):
                            amount = num * 250
                        elif any(unit in words[i + 1] for unit in ['bottle', 'bottles']):
                            amount = num * 500
                        elif any(unit in words[i + 1] for unit in ['ml', 'milliliters', 'millilitres']):
                            amount = num
                        else:
                            amount = num  # Assume ml if no unit specified
                    else:
                        amount = num  # Assume ml if no unit specified
                    break
            except ValueError:
                continue
    
    if amount > 0:
        intake.amount += amount
        db.session.commit()
        water_added = True

    # Prepare user and water data for AI model
    goal_percentage = (intake.amount / daily_goal.amount) * 100 if daily_goal else 0
    
    user_data = {
        'name': user.name,
        'age': user.age,
        'weight': user.weight,
        'height': user.height,
        'profession': user.profession
    }
    
    water_data = {
        'current_amount': intake.amount,
        'goal': daily_goal.amount if daily_goal else 0,
        'percentage': goal_percentage,
        'remaining': (daily_goal.amount - intake.amount) if daily_goal else 0
    }
    
    # Check if Gemini API key is configured
    api_key_set = session.get('gemini_api_key_set', False)
    
    # Use Gemini to generate a response
    response = generate_response(user_message, user_data, water_data)
    
    # If API key isn't set, add a note to the response
    if not api_key_set and 'api' not in user_message.lower() and 'gemini' not in user_message.lower():
        response += "\n\n(Note: For more advanced AI responses, ask your admin to set up the Gemini API key in Settings.)"

    # Calculate percentage for the water fill display
    percentage = min(100, int((intake.amount / daily_goal.amount) * 100)) if daily_goal and daily_goal.amount > 0 else 0
    
    return jsonify({
        'success': True,
        'message': response,
        'current_amount': intake.amount,
        'goal': daily_goal.amount if daily_goal else 0,
        'percentage': percentage,
        'water_added': water_added,
        'api_key_set': api_key_set
    })

@app.route('/check_water_reminder', methods=['GET'])
def check_water_reminder():
    """Check if it's time to send a water reminder to the user"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'})
    
    user_id = session['user_id']
    
    # Get the user's reminder settings
    reminder = WaterReminder.query.filter_by(user_id=user_id).first()
    
    # If no reminder exists, create one
    if not reminder:
        reminder = WaterReminder(user_id=user_id)
        db.session.add(reminder)
        db.session.commit()
    
    # Check if reminders are enabled
    if not reminder.is_enabled:
        return jsonify({'success': True, 'should_remind': False})
    
    # Get the current time
    now = datetime.now()
    
    # Calculate the time difference since the last reminder
    time_diff = now - reminder.last_reminder_time
    minutes_passed = time_diff.total_seconds() / 60
    
    # Check if it's time for a reminder (1.5 hours = 90 minutes)
    should_remind = minutes_passed >= reminder.reminder_interval
    
    # If it's time for a reminder, update the last reminder time
    if should_remind:
        reminder.last_reminder_time = now
        db.session.commit()
        
        # Get personalized reminder message
        user = User.query.get(user_id)
        today = datetime.now().date()
        intake = WaterIntake.query.filter_by(user_id=user_id, date=today).first()
        daily_goal = DailyGoal.query.filter_by(user_id=user_id).first()
        
        if not intake:
            intake = WaterIntake(user_id=user_id, date=today, amount=0)
            db.session.add(intake)
            db.session.commit()
        
        # Calculate remaining water needed
        remaining = (daily_goal.amount - intake.amount) if daily_goal else 2500
        
        # Generate a personalized reminder message
        reminder_messages = [
            f"Hi {user.name}! It's been 1.5 hours since your last water break. Time to hydrate!",
            f"Water break time! You still need {remaining}ml to reach your daily goal.",
            f"Remember to stay hydrated, {user.name}! How about drinking some water now?",
            "Hydration reminder! A glass of water will help you stay focused and energized.",
            "Your body needs water to function properly. Take a moment to hydrate now!"
        ]
        
        message = random.choice(reminder_messages)
        
        return jsonify({
            'success': True,
            'should_remind': True,
            'message': message,
            'current_amount': intake.amount,
            'goal': daily_goal.amount if daily_goal else 2500
        })
    
    return jsonify({
        'success': True,
        'should_remind': False
    })

@app.route('/toggle_water_reminders', methods=['POST'])
def toggle_water_reminders():
    """Enable or disable water reminders for the user"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'})
    
    user_id = session['user_id']
    data = request.json
    enabled = data.get('enabled', True)
    
    # Get the user's reminder settings
    reminder = WaterReminder.query.filter_by(user_id=user_id).first()
    
    # If no reminder exists, create one
    if not reminder:
        reminder = WaterReminder(user_id=user_id, is_enabled=enabled)
        db.session.add(reminder)
    else:
        reminder.is_enabled = enabled
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'is_enabled': reminder.is_enabled
    })

@app.route('/set_reminder_interval', methods=['POST'])
def set_reminder_interval():
    """Set the interval for water reminders in minutes"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'})
    
    user_id = session['user_id']
    data = request.json
    interval = data.get('interval', 90)  # Default to 90 minutes (1.5 hours)
    
    # Validate the interval (minimum 30 minutes, maximum 240 minutes)
    interval = max(30, min(240, interval))
    
    # Get the user's reminder settings
    reminder = WaterReminder.query.filter_by(user_id=user_id).first()
    
    # If no reminder exists, create one
    if not reminder:
        reminder = WaterReminder(user_id=user_id, reminder_interval=interval)
        db.session.add(reminder)
    else:
        reminder.reminder_interval = interval
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'interval': reminder.reminder_interval
    })

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))

@app.route('/set_gemini_api_key', methods=['POST'])
def set_gemini_api_key():
    """Set the Gemini API key for the chatbot"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'})
    
    data = request.json
    api_key = data.get('api_key', '').strip()
    
    if not api_key:
        return jsonify({'success': False, 'message': 'API key cannot be empty'})
    
    try:
        result = set_api_key(api_key)
        if result:
            # If successful, store the API key in the session
            session['gemini_api_key_set'] = True
            return jsonify({'success': True, 'message': 'Gemini API key set successfully'})
        else:
            return jsonify({'success': False, 'message': 'Invalid API key'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error setting API key: {str(e)}'})

@app.route('/test_gemini', methods=['GET', 'POST'])
def test_gemini():
    """Test route for Gemini API integration"""
    from gemini_api import generate
    
    api_key_set = session.get('gemini_api_key_set', False)
    
    if request.method == 'POST':
        if 'set_api_key' in request.form:
            api_key = request.form.get('api_key', '').strip()
            if api_key:
                try:
                    result = set_api_key(api_key)
                    if result:
                        session['gemini_api_key_set'] = True
                        return render_template('test_gemini.html', 
                                              api_key_set=True, 
                                              message="API key set successfully")
                    else:
                        return render_template('test_gemini.html', 
                                              api_key_set=False, 
                                              message="Invalid API key")
                except Exception as e:
                    return render_template('test_gemini.html', 
                                          api_key_set=False, 
                                          message=f"Error: {str(e)}")
            else:
                return render_template('test_gemini.html', 
                                      api_key_set=False, 
                                      message="API key cannot be empty")
        else:
            prompt = request.form.get('prompt', 'Tell me about the importance of hydration')
            try:
                response = generate(prompt)
                return render_template('test_gemini.html', 
                                      prompt=prompt, 
                                      response=response, 
                                      api_key_set=api_key_set)
            except Exception as e:
                return render_template('test_gemini.html', 
                                      prompt=prompt, 
                                      error=str(e), 
                                      api_key_set=api_key_set)
    
    return render_template('test_gemini.html', api_key_set=api_key_set)

def calculate_water_goal(user):
    """Calculate recommended water intake based on user metrics"""
    # Base calculation: 35ml per kg of body weight
    base_amount = user.weight * 35
    
    # Adjustments based on age
    if user.age > 65:
        base_amount *= 0.9  # Slightly less for elderly
    elif user.age < 18:
        base_amount *= 1.1  # Slightly more for younger people
    
    # Adjustments based on profession (simplified)
    active_professions = ['athlete', 'construction', 'fitness', 'trainer', 'labor', 'worker']
    sedentary_professions = ['office', 'desk', 'computer', 'programmer', 'developer']
    
    for term in active_professions:
        if term in user.profession.lower():
            base_amount *= 1.3  # More water for active professions
            break
    
    for term in sedentary_professions:
        if term in user.profession.lower():
            base_amount *= 0.9  # Less water for sedentary professions
            break
    
    # Round to nearest 100ml
    recommended_amount = round(base_amount / 100) * 100
    
    # Ensure minimum amount
    if recommended_amount < 1500:
        recommended_amount = 1500
    
    # Save or update daily goal
    daily_goal = DailyGoal.query.filter_by(user_id=user.id).first()
    if not daily_goal:
        daily_goal = DailyGoal(user_id=user.id, amount=recommended_amount)
        db.session.add(daily_goal)
    else:
        daily_goal.amount = recommended_amount
    
    db.session.commit()
    return daily_goal

if __name__ == '__main__':
    app.run(debug=True)