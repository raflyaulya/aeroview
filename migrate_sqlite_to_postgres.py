import sqlite3
from app import create_app, db
from app.models import ReviewHistory
from dateutil import parser as dateparse

app = create_app()

# Buka koneksi ke SQLite
sqlite_conn = sqlite3.connect("airline_reviews.db")
sqlite_cursor = sqlite_conn.cursor()
sqlite_cursor.execute("SELECT airline, sentiment, review, date_flown FROM reviews")
rows = sqlite_cursor.fetchall()

with app.app_context():
    for row in rows:
        raw_date = row[3]
        parsed_date = None

        # Coba parsing tanggal
        if raw_date:
            try:
                parsed_date = dateparse.parse(raw_date, fuzzy=True)
            except Exception as e:
                print(f"[⚠] Gagal parsing date: '{raw_date}' → NULL | Error: {e}")

        # Tambahkan data ke PostgreSQL
        review = ReviewHistory(
            airline=row[0],
            sentiment=row[1],
            review=row[2],
            date_flown=parsed_date
        )
        db.session.add(review)

    db.session.commit()

sqlite_conn.close()
print("✅ Migrasi selesai!")
