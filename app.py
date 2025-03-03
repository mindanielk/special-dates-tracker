from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
from flask_migrate import Migrate
import json

#load environment variables
load_dotenv()

# App configurations
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)

database_url = os.getenv('DATABASE_URL')
if database_url:
    database_url = database_url.replace("postgres://", "postgresql://", 1)
else:
    database_url = "sqlite:///app.db"

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Database Models

## Model for storing user information
## A user has their own special dates and calendar
## Attaches their id to special dates for filtering
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    dates = db.relationship('SpecialDate', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
## Model for collapsing special dates into singular dates
## Mass storage for special dates for use in displaying
## in conjunction with the calendar GUI
class Calendar(db.Model):
    date = db.Column(db.String, primary_key=True, unique=True)
    events = db.Column(db.JSON, nullable=True)

## Model for storing special dates
## Stores all special dates to keep track
## of particular users and dates.
class SpecialDate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    wishlist_items = db.relationship(
        'WishlistItem',
        backref='special_date',
        lazy=True,
        cascade="all, delete",
        passive_deletes=True
    )

## Model for wishlists that a date may have
## Optional items that may be attached to a 
## special date for reminders
## Deleted when the date they are attached too is deleted
class WishlistItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    url = db.Column(db.String(500))
    price = db.Column(db.Float)
    special_date_id = db.Column(
        db.Integer,
        db.ForeignKey('special_date.id', ondelete='CASCADE'),
        nullable=False
    )

## Login method for flask
@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

# Routes

## Automatic redirect if logged in
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

## Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return redirect(url_for('register'))
        
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful')
        return redirect(url_for('login'))
    
    return render_template('register.html')

## Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = 'remember' in request.form
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user, remember=remember)
            session.permanent = remember
            return redirect(url_for('dashboard'))
        
        flash('Invalid username or password')
    return render_template('login.html')

## Main dashboard
## Add date
## Remove Date
## Calendar GUI
## Shows date cards and calendar for the currently logged in user
@app.route('/dashboard')
@login_required
def dashboard():
    dates = SpecialDate.query.filter_by(user_id=current_user.id).order_by(SpecialDate.date).all()
    return render_template('dashboard.html', dates=dates, calendar_dates=get_events())

## Add a date to keep track of
## Creates both a card and highlights
## the date in the calendar
@app.route('/add_date', methods=['GET', 'POST'])
@login_required
def add_date():
    if request.method == 'POST':
        title = request.form.get('title')
        date_str = request.form.get('date')
        description = request.form.get('description')
        category = request.form.get('category')
        
        date = datetime.strptime(date_str, '%Y-%m-%d')
        
        special_date = SpecialDate(
            title=title,
            date=date,
            description=description,
            category=category,
            user_id=current_user.id
        )

        update_entry('add', {
                    'title': title,
                    'date': date_str,
                })

        db.session.add(special_date)
        db.session.commit()
        
        flash('Special date added successfully')
        return redirect(url_for('dashboard'))
    
    return render_template('add_date.html')

## Remove a date
## Removes the card related to the date
## Removes highlight if no remaining events for given date
@app.route('/remove_date/<int:date_id>', methods=['POST'])
@login_required
def remove_date(date_id):
    special_date = SpecialDate.query.get_or_404(date_id)

    if special_date.user_id != current_user.id:
        print("Unauthorized deletion attempt")
        return jsonify({'error': 'Unauthorized'}), 403
    
    removed_date = special_date.date.strftime('%Y-%m-%d')

    update_entry('remove', {
        'title': special_date.title,
        'date': removed_date
    })

    db.session.delete(special_date)
    db.session.commit()

    print(f"Successfully removed event ID {date_id} from DB")
    return jsonify({'success': True, 'removed_date': removed_date})

## Helper function for adding and removing a date
## Deals with removing dates that have multiple events
## or adding events for dates that currently have none
def update_entry(operation, event):
    date = event['date']
    title = event['title']
    check_date = Calendar.query.filter_by(date=date).first()
    
    if operation == 'add':
        if check_date is None:
            new_entry = Calendar(
                date=date,
                events=json.dumps({title: event})
            )
            db.session.add(new_entry)
        else:
            if check_date.events:
                current_events = json.loads(check_date.events)
            else:
                current_events = {}

            current_events[title] = event
            check_date.events = json.dumps(current_events)

        db.session.commit()

    elif operation == 'remove':
        current_events = {}
        if check_date and check_date.events:
            try:
                current_events = json.loads(check_date.events)
            except json.JSONDecodeError:
                current_events = {}

            current_events.pop(title, None)

            if current_events:
                check_date.events = json.dumps(current_events)
            else:
                db.session.delete(check_date)

            db.session.commit()

## Gets a list of event date strings
## Filtered for current user
## Helper function for displaying the events for the current user
def get_events():
    user_special_dates = SpecialDate.query.filter_by(user_id=current_user.id).all()
    user_date_strings = {date.date.strftime('%Y-%m-%d') for date in user_special_dates}
    user_calendar_entries = Calendar.query.filter(Calendar.date.in_(user_date_strings)).all()
    return [entry.date for entry in user_calendar_entries if entry.events]

## Create a wishlist
## Attaches the wishlist to the given special date card
@app.route('/add_wishlist_item/<int:date_id>', methods=['POST'])
@login_required
def add_wishlist_item(date_id):
    special_date = SpecialDate.query.get_or_404(date_id)
    if special_date.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    item = WishlistItem(
        item_name=data['item_name'],
        description=data.get('description'),
        url=data.get('url'),
        price=data.get('price'),
        special_date_id=date_id
    )
    
    db.session.add(item)
    db.session.commit()
    
    return jsonify({
        'id': item.id,
        'item_name': item.item_name,
        'description': item.description,
        'url': item.url,
        'price': item.price
    })

## Logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
