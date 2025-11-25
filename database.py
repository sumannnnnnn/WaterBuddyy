from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Initialize SQLAlchemy
db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=True)
    age = db.Column(db.Integer, nullable=False)
    weight = db.Column(db.Float, nullable=False)  # in kg
    height = db.Column(db.Float, nullable=False)  # in cm
    profession = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    # Relationships
    water_intakes = db.relationship('WaterIntake', backref='user', lazy=True)
    daily_goal = db.relationship('DailyGoal', backref='user', lazy=True, uselist=False)
    water_reminder = db.relationship('WaterReminder', backref='user', lazy=True, uselist=False)
    
    def __repr__(self):
        return f'<User {self.name}>'

class WaterIntake(db.Model):
    __tablename__ = 'water_intakes'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    amount = db.Column(db.Integer, nullable=False)  # in milliliters
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    def __repr__(self):
        return f'<WaterIntake {self.date}: {self.amount}ml>'

class DailyGoal(db.Model):
    __tablename__ = 'daily_goals'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    amount = db.Column(db.Integer, nullable=False)  # in milliliters
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    def __repr__(self):
        return f'<DailyGoal {self.amount}ml>'

class WaterReminder(db.Model):
    __tablename__ = 'water_reminders'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    last_reminder_time = db.Column(db.DateTime, default=datetime.now)
    reminder_interval = db.Column(db.Integer, default=90)  # in minutes (1.5 hours = 90 minutes)
    is_enabled = db.Column(db.Boolean, default=True)
    
    def __repr__(self):
        return f'<WaterReminder for user {self.user_id}, last sent: {self.last_reminder_time}>'