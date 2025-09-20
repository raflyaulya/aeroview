from app import create_app, db
from app.models import * 

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)


# ===========================================================================
# from app import app
# import sqlite3
# from app.models import Review, SavedChart, ReviewAnalysisLink, ReviewHistory

# # ==================      DATABASE        ==================================
# # ==================      ini DATABASE yg lama, kalo terjadi sesuatu tinggal di uncomment aja !         ==================================
# # Initialize the database if it doesn't exist
# def init_db():
#     conn = sqlite3.connect('database.db')
#     c = conn.cursor()
#     c.execute('''
#         CREATE TABLE IF NOT EXISTS submissions (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             airline TEXT NOT NULL,
#             sentiment TEXT NOT NULL,
#             review TEXT NOT NULL,
#             timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
#         )
#     ''')
#     conn.commit()
#     conn.close()

# # ==================      ini DATABASE yg BARU !!!         ==================================
# # def init_db():
# #     conn = sqlite3.connect('database.db')
# #     c = conn.cursor()
# #     c.execute('''
# #         CREATE TABLE IF NOT EXISTS submissions (
# #             id INTEGER PRIMARY KEY AUTOINCREMENT,
# #             airline TEXT NOT NULL,
# #             sentiment TEXT NOT NULL,
# #             review TEXT NOT NULL,
# #             date_flown TEXT,
# #             rating REAL,
# #             timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
# #         )
# #     ''')
# #     conn.commit()
# #     conn.close()


# if __name__ == '__main__':
#     init_db()  # Ensure database is created
#     # app.run(debug=True)  # INI YG BENAR! kalo terjadi something, lakukan UN-COMMENT
#     app.run(host='0.0.0.0', port=5000)  # Ganti ini!
    