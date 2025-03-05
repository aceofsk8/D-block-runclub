from app import db

class Profile(db.Model):
    __tablename__ = 'profile'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)

class Run(db.Model):
    __tablename__ = 'run'
    id = db.Column(db.Integer, primary_key=True)
    profile_id = db.Column(db.Integer, db.ForeignKey('profile.id'), nullable=False)
    date = db.Column(db.String(10), nullable=False)
    distance = db.Column(db.Float, nullable=False)
    run_time = db.Column(db.String(10), nullable=False)  # Format MM:SS
    heart_rate = db.Column(db.Integer, nullable=False)

Profile.runs = db.relationship('Run', backref='profile', lazy=True)
