from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
from dotenv import load_dotenv
from flask_migrate import Migrate

#load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

map_months = {
    1: ["January", 31],
    2: ["February", 28],
    3: ["March", 31],
    4: ["April", 30],
    5: ["May", 31],
    6: ["June", 30],
    7: ["July", 31],
    8: ["August", 31],
    9: ["September", 30],
    10:["October", 31],
    11:["November", 30],
    12:["December", 31]
}

week_map = {
    1: "Sunday",
    2: "Monday",
    3: "Tuesday",
    4: "Wednesday",
    5: "Thursday",
    6: "Friday",
    7: "Saturday"
}

# Database Models
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
    
class Calendar(db.Model):
    date = db.Column(db.String, primary_key=True)
    day_week = db.Column(db.Integer)
    day_month = db.Column(db.Integer)
    month = db.Column(db.Integer)
    year = db.Column(db.Integer)
    events = db.Column(db.JSON, nullable=True)     ## Dictionary of event IDs

class SpecialDate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    wishlist_items = db.relationship('WishlistItem', backref='special_date', lazy=True)

class WishlistItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    url = db.Column(db.String(500))
    price = db.Column(db.Float)
    special_date_id = db.Column(db.Integer, db.ForeignKey('special_date.id'), nullable=False)

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

# Routes
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

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

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('dashboard'))
        
        flash('Invalid username or password')
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    dates = SpecialDate.query.filter_by(user_id=current_user.id).order_by(SpecialDate.date).all()
    return render_template('dashboard.html', dates=dates)

@app.route('/add_date', methods=['GET', 'POST'])
@login_required
def add_date():
    if request.method == 'POST':
        title = request.form.get('title')
        date_str = request.form.get('date')
        description = request.form.get('description')
        category = request.form.get('category')
        
        date = datetime.strptime(date_str, '%Y-%m-%d')
        date_array = date_str.split('-')
        year = int(date_array[0])
        month = int(date_array[1])
        day = int(date_array[2])
        
        special_date = SpecialDate(
            title=title,
            date=date,
            description=description,
            category=category,
            user_id=current_user.id
        )

        weekday = datetime(year, month, day).weekday() + 1
        new_event = Calendar(
            date = date,
            day_week = weekday,
            day_month = day,
            year = year,
            month = month,
            events = {
                'title': title,
                'date': date,
                'description': description,
                'category': category,
                'user_id': current_user.id
            }
        )

        db.session.add(special_date)
        db.session.commit()
        
        flash('Special date added successfully')
        return redirect(url_for('dashboard'))
    
    return render_template('add_date.html')

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

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)