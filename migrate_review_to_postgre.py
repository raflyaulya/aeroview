import pandas as pd
import sqlite3
from sqlalchemy import create_engine

# 1. Buka koneksi ke database SQLite
sqlite_conn = sqlite3.connect("database.db")
submissions_df = pd.read_sql_query("SELECT * FROM submissions", sqlite_conn)
submissions_df["timestamp"] = pd.to_datetime(submissions_df["timestamp"])
sqlite_conn.close()

# 2. Siapkan DataFrame untuk PostgreSQL
review_df = submissions_df.rename(columns={
    "timestamp": "date",
    "review": "description"  # FIX INI PENTING
})
review_df = review_df[["airline", "sentiment", "description", "date"]]

# 3. Hubungkan ke PostgreSQL
engine = create_engine("postgresql+psycopg2://postgres:12345@localhost:5432/airline_reviews")

# 4. Masukkan ke tabel 'review'
review_df.to_sql("review", engine, if_exists="append", index=False)

print(f"{len(review_df)} rows successfully inserted into PostgreSQL!")
