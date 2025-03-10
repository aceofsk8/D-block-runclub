from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os

# Initialize Flask app
app = Flask(__name__)

# Configure database
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///runs.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False  # Avoids warnings

# Initialize database and migrations
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Import models AFTER initializing db
from models import Profile, Run

@app.route('/')
def home():
    """Homepage - Displays all profiles."""
    profiles = Profile.query.all()
    return render_template("index.html", profiles=profiles, selected_profile=None,
                           total_miles=0, avg_pace="--:--", avg_hr="--")

@app.route('/select_profile', methods=['POST'])
def select_profile():
    """Handles selecting a profile and displaying its run data."""
    profile_id = request.form.get('profile_id')
    selected_profile = Profile.query.get(profile_id)

    if selected_profile:
        runs = Run.query.filter_by(profile_id=selected_profile.id).all()
        
        total_miles = sum(run.distance for run in runs)
        total_time_seconds = sum(int(run.run_time.split(":")[0]) * 60 + int(run.run_time.split(":")[1]) for run in runs)
        total_hr = sum(run.heart_rate for run in runs)
        run_count = len(runs)

        avg_pace = "--:--"
        avg_hr = "--"

        if run_count > 0 and total_miles > 0:
            avg_pace_seconds = total_time_seconds / total_miles
            avg_pace = f"{int(avg_pace_seconds // 60)}:{int(avg_pace_seconds % 60):02d}"
            avg_hr = int(total_hr / run_count)

        return render_template("index.html", profiles=Profile.query.all(), selected_profile=selected_profile,
                               total_miles=round(total_miles, 2), avg_pace=avg_pace, avg_hr=avg_hr)
    
    return redirect(url_for('home'))

@app.route('/add_run', methods=['POST'])
def add_run():
    """Handles adding a new run to the database."""
    profile_name = request.form.get('profile_name')
    date = request.form.get('date')
    distance = request.form.get('distance')
    run_time = request.form.get('run_time')
    heart_rate = request.form.get('heart_rate')

    if not profile_name or not date or not distance or not run_time or not heart_rate:
        return redirect(url_for('home'))  # Prevent empty submissions

    # Get or create profile
    profile = Profile.query.filter_by(name=profile_name).first()
    if not profile:
        profile = Profile(name=profile_name)
        db.session.add(profile)
        db.session.commit()

    # Add run data
    new_run = Run(profile_id=profile.id, date=date, distance=float(distance), run_time=run_time, heart_rate=int(heart_rate))
    db.session.add(new_run)
    db.session.commit()

    return redirect(url_for('view_profile', profile_id=profile.id))

@app.route('/profile/<int:profile_id>')
def view_profile(profile_id):
    """Displays an individual profile and its run stats."""
    profiles = Profile.query.all()
    selected_profile = Profile.query.get_or_404(profile_id)
    runs = Run.query.filter_by(profile_id=selected_profile.id).all()

    total_miles = sum(run.distance for run in runs)
    total_time_seconds = sum(int(run.run_time.split(":")[0]) * 60 + int(run.run_time.split(":")[1]) for run in runs)
    total_hr = sum(run.heart_rate for run in runs)
    run_count = len(runs)

    avg_pace = "--:--"
    avg_hr = "--"

    if run_count > 0 and total_miles > 0:
        avg_pace_seconds = total_time_seconds / total_miles
        avg_pace = f"{int(avg_pace_seconds // 60)}:{int(avg_pace_seconds % 60):02d}"
        avg_hr = int(total_hr / run_count)

    return render_template("index.html", profiles=profiles, selected_profile=selected_profile,
                           total_miles=round(total_miles, 2), avg_pace=avg_pace, avg_hr=avg_hr)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Creates tables if they don't exist
    app.run(debug=True)
