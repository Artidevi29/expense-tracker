from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from datetime import datetime
import calendar

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# ------------------- Database Models -------------------
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)  # plain for demo; hash in real
    monthly_budget = db.Column(db.Float, default=0.0)
    transactions = db.relationship('Transaction', backref='user', lazy=True)

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(200))
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# Create tables
with app.app_context():
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ------------------- Helper Functions -------------------
def get_current_month_range():
    today = datetime.utcnow()
    start = today.replace(day=1)
    next_month = start.replace(month=start.month+1) if start.month < 12 else start.replace(year=start.year+1, month=1)
    end = next_month - timedelta(days=1)
    return start, end

from datetime import timedelta

def get_monthly_stats(user):
    today = datetime.utcnow()
    start = today.replace(day=1, hour=0, minute=0, second=0)
    end = (start.replace(month=start.month+1) - timedelta(days=1)) if start.month < 12 else start.replace(year=start.year+1, month=1) - timedelta(days=1)
    expenses = Transaction.query.filter(
        Transaction.user_id == user.id,
        Transaction.date >= start,
        Transaction.date <= end
    ).all()
    total_spent = sum(t.amount for t in expenses)
    budget = user.monthly_budget
    remaining = budget - total_spent
    savings = max(0, remaining)   # if positive, else 0 (or you can show negative as overspent)
    overspent = remaining < 0
    return {
        'budget': budget,
        'total_spent': total_spent,
        'remaining': remaining,
        'savings': savings if not overspent else 0,
        'overspent': -remaining if overspent else 0,
        'expenses': expenses,
        'start_date': start,
        'end_date': end
    }

# ------------------- Routes -------------------
@app.route('/')
def home():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return redirect(url_for('register'))
        user = User(username=username, password=password)  # store plain, but better hash
        db.session.add(user)
        db.session.commit()
        flash('Registration successful! Please login.')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Invalid credentials')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    stats = get_monthly_stats(current_user)
    # Get category totals for chart
    category_totals = {}
    for t in stats['expenses']:
        category_totals[t.category] = category_totals.get(t.category, 0) + t.amount
    return render_template('index.html', stats=stats, category_totals=category_totals, now=datetime.utcnow())

@app.route('/set_budget', methods=['POST'])
@login_required
def set_budget():
    new_budget = float(request.form['budget'])
    current_user.monthly_budget = new_budget
    db.session.commit()
    flash(f'Monthly budget set to ₹{new_budget:.2f}')
    return redirect(url_for('dashboard'))

@app.route('/add_expense', methods=['GET', 'POST'])
@login_required
def add_expense():
    if request.method == 'POST':
        amount = float(request.form['amount'])
        category = request.form['category']
        description = request.form.get('description', '')
        date_str = request.form.get('date')
        if date_str:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
        else:
            date = datetime.utcnow().date()
        transaction = Transaction(amount=amount, category=category, description=description, date=date, user_id=current_user.id)
        db.session.add(transaction)
        db.session.commit()
        flash('Expense added')
        return redirect(url_for('dashboard'))
    return render_template('add_expense.html', now=datetime.utcnow())

@app.route('/edit_expense/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_expense(id):
    t = Transaction.query.get_or_404(id)
    if t.user_id != current_user.id:
        flash('Unauthorized')
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        t.amount = float(request.form['amount'])
        t.category = request.form['category']
        t.description = request.form.get('description', '')
        t.date = datetime.strptime(request.form['date'], '%Y-%m-%d').date()
        db.session.commit()
        flash('Expense updated')
        return redirect(url_for('dashboard'))
    return render_template('edit_expense.html', expense=t)

@app.route('/delete_expense/<int:id>')
@login_required
def delete_expense(id):
    t = Transaction.query.get_or_404(id)
    if t.user_id == current_user.id:
        db.session.delete(t)
        db.session.commit()
        flash('Expense deleted')
    else:
        flash('Unauthorized')
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(debug=True)
