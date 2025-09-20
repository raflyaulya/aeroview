from app import db
from app.models import *
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64
from app.models import *
from sqlalchemy import func

def generate_timeline_visualization():
    # Ambil data dari PostgreSQL via SQLAlchemy
    data = ReviewFull.query.with_entities(
        ReviewFull.airline,
        ReviewFull.sentiment,
        ReviewFull.date_flown
    ).all()

    # Ubah ke DataFrame
    df = pd.DataFrame(data, columns=['airline', 'sentiment', 'timestamp'])

    # Jika tidak ada data, balikin kosong
    if df.empty:
        return ""

    df['sentiment'] = df['sentiment'].str.lower()
    df['timestamp'] = pd.to_datetime(df['timestamp'])

    # Urutkan data
    df_sorted = df.sort_values('airline')

    # Buat plot
    plt.figure(figsize=(10, 6))
    sns.stripplot(
        x='timestamp', 
        y='airline', 
        hue='sentiment', 
        data=df_sorted, 
        jitter=True, 
        dodge=True, 
        palette={'positive': 'green', 'negative': 'red'}
    )
    plt.xlabel('Date')
    plt.ylabel('Airline')
    plt.title('Airline Sentiment Trends Over Time')
    plt.xticks(rotation=45)

    handles, labels = plt.gca().get_legend_handles_labels()
    plt.legend(handles[:2], ['Positive', 'Negative'], 
               title='Sentiment', 
               bbox_to_anchor=(1.05, 1), 
               loc='upper left')
    plt.tight_layout()
    plt.grid()

    # Convert ke base64
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    plt.close()

    return image_base64


def get_review_counts_by_airline():
    # Query jumlah review per airline
    results = db.session.query(
        ReviewFull.airline,
        func.count().label('total_reviews')
    ).group_by(ReviewFull.airline).order_by(func.count().desc()).all()

    return results
