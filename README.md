# Water Intake Tracking Website with Personalized Chatbot

This web application helps users track their daily water intake with a personalized chatbot that provides reminders and recommendations based on individual metrics.

## Features

- **Personalized Profile**: Collects user data (height, weight, age, profession) to calculate optimal water intake
- **Interactive Dashboard**: Features a chatbot interface for water intake tracking
- **Visual Tracking**: Graphical representation of water intake using glass icons
- **Streak Calendar**: Calendar to mark and track daily water intake completion streaks
- **Personalized Recommendations**: Custom water intake goals based on user metrics
- **Reminder System**: Timely notifications to complete water intake goals

## Water Intake Calculation Parameters

The application uses several key parameters to calculate personalized daily water intake recommendations:

- **Body Weight**: Base calculation of 30-35 ml per kg of body weight
- **Activity Level**: 
  - Sedentary: Base recommendation
  - Moderately Active: Add 350-500 ml
  - Very Active: Add 500-1000 ml
- **Climate**: 
  - Hot/Humid: Additional 500-1000 ml
  - Normal: Base recommendation
- **Age**: Adjusted based on age groups:
  - 18-30: 100% of base recommendation
  - 31-55: 90-95% of base recommendation
  - 55+: 85-90% of base recommendation
- **Health Conditions**: Adjustments for specific conditions (if any)
- **Profession**: Additional intake for:
  - Physical labor: 500-1000 ml extra
  - Office work: Base recommendation
  - Outdoor work: Additional 500 ml

Note: These parameters are guidelines and may be adjusted based on individual needs and medical advice.

## Tech Stack

- **Frontend**: HTML, JavaScript, Tailwind CSS
- **Backend**: Python (Flask)
- **Database**: SQLite

## Project Structure

```
chatbotwater/
├── static/
│   ├── css/
│   │   └── styles.css
│   ├── js/
│   │   ├── chatbot.js
│   │   ├── dashboard.js
│   │   └── profile.js
│   └── images/
├── templates/
│   ├── index.html
│   ├── profile.html
│   └── dashboard.html
├── app.py
├── database.py
└── README.md
```

## Setup Instructions

1. Install required dependencies:
   ```
   pip install flask flask-sqlalchemy
   ```

2. Initialize the database:
   ```
   python database.py
   ```

3. Run the application:
   ```
   python app.py
   ```

4. Open your browser and navigate to `http://localhost:5000`

## Usage

1. Create a profile with your personal information
2. Navigate to the dashboard to interact with the chatbot
3. Track your water intake using the interface
4. View your progress and streaks on the calendar