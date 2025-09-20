from app import db
from app.extensions import db
from datetime import datetime

class ReviewSavedHistory(db.Model):
    __tablename__ = 'review_saved_history'

    id = db.Column(db.Integer, primary_key=True)
    airline = db.Column(db.String(100))
    sentiment = db.Column(db.String(20))
    description = db.Column(db.Text)
    date = db.Column(db.DateTime, default=datetime.utcnow)

class ReviewFull(db.Model):
    __tablename__ = 'review_full'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    airline = db.Column(db.String(100))
    sentiment = db.Column(db.String(20))
    review = db.Column(db.Text)
    date_flown = db.Column(db.DateTime)  # Wajib pakai DateTime

class SavedChart(db.Model):
    __tablename__ = 'saved_charts'
    id = db.Column(db.Integer, primary_key=True)
    chart_name = db.Column(db.String(100), nullable=False)
    airline = db.Column(db.String(100), nullable=False)
    sentiment = db.Column(db.String(20), nullable=False)
    chart_type = db.Column(db.String(50), nullable=False)
    generated_on = db.Column(db.DateTime, default=datetime.utcnow)
    image_data = db.Column(db.Text)

class DetailedVisualization(db.Model):
    __tablename__ = 'detailed_visualizations'
    id = db.Column(db.Integer, primary_key=True)
    airline = db.Column(db.String(100), nullable=False)
    name_of_visualization = db.Column(db.Text, nullable=False)
    saved_at = db.Column(db.DateTime, default=datetime.utcnow)
    image_data = db.Column(db.Text, nullable=False)

