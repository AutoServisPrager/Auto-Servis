from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///autoservis.db'  # SQLite databáze
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'supersecretkey'

db = SQLAlchemy(app)

# Model pro zákazníky
class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False, unique=True)
    email = db.Column(db.String(100), unique=True)
    vehicles = db.relationship('Vehicle', backref='owner', lazy=True)

# Model pro vozidla
class Vehicle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    license_plate = db.Column(db.String(10), nullable=False, unique=True)
    vin = db.Column(db.String(17), unique=True)
    brand = db.Column(db.String(50), nullable=False)
    model = db.Column(db.String(50), nullable=False)
    year = db.Column(db.Integer)
    owner_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    last_service_date = db.Column(db.DateTime, default=datetime.utcnow)
    next_stk_date = db.Column(db.DateTime, nullable=False)
    diagnostics = db.relationship('Diagnostic', backref='vehicle', lazy=True)

# Model pro diagnostiku vozidla
class Diagnostic(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicle.id'), nullable=False)
    error_code = db.Column(db.String(10), nullable=False)
    description = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Model pro zakázkové listy
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicle.id'), nullable=False)
    description = db.Column(db.Text, nullable=False)
    parts_used = db.Column(db.Text)
    labor_hours = db.Column(db.Float, nullable=False)
    total_cost = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

@app.route('/')
def index():
    vehicles = Vehicle.query.all()
    return render_template('index.html', vehicles=vehicles)

@app.route('/add_vehicle', methods=['POST'])
def add_vehicle():
    license_plate = request.form['license_plate']
    vin = request.form['vin']
    brand = request.form['brand']
    model = request.form['model']
    year = request.form['year']
    owner_id = request.form['owner_id']
    next_stk_date = request.form['next_stk_date']
    
    new_vehicle = Vehicle(
        license_plate=license_plate, vin=vin, brand=brand,
        model=model, year=int(year), owner_id=int(owner_id),
        next_stk_date=datetime.strptime(next_stk_date, '%Y-%m-%d')
    )
    db.session.add(new_vehicle)
    db.session.commit()
    flash('Vozidlo bylo přidáno!')
    return redirect(url_for('index'))

# Spuštění aplikace
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Vytvoření databáze, pokud neexistuje
    app.run(debug=True)

