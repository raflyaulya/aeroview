import string
import re
from bs4 import BeautifulSoup  # For web scraping and HTML parsing
import random  # For generating random choices
import pandas as pd  # For data manipulation and analysis
import numpy as np  # For numerical computations
# import matplotlib
# matplotlib.use('Agg')  # Ensures plots are created without a GUI (useful for servers)
import matplotlib.pyplot as plt  # For creating visualizations
import io  # For in-memory file operations
import base64  # For encoding image data into base64 for rendering in web apps
import seaborn as sns  # For advanced visualization (used for bar plots)
import requests  # For making HTTP requests to scrape web pages
import nltk  # For natural language processing
from nltk.corpus import stopwords  # For accessing stopword lists
from nltk.probability import FreqDist  # For frequency distribution analysis
from textblob import TextBlob  # For sentiment analysis and text processing
import random

nltk.download('punkt_tab')
nltk.download('averaged_perceptron_tagger')
nltk.download('wordnet')
nltk.download('stopwords')
# Download the missing resource
nltk.download('averaged_perceptron_tagger_eng')



def airline_func(airline_name):
    # Format the airline name to match the URL structure
    formatted_name = '-'.join(airline_name.split())
    base_url = f"https://www.airlinequality.com/airline-reviews/{formatted_name}"

    pages = 10  # Number of pages to scrape
    page_size = 100  # Reviews per page (default: 100)
    reviews = []  # List to store extracted reviews

    # Scrape reviews from multiple pages
    for i in range(1, pages + 1):
        url = f"{base_url}/page/{i}/?sortby=post_date%3ADesc&pagesize={page_size}"
        response = requests.get(url)  # Send GET request to the page
        content = response.content  # Extract page content
        parsed_content = BeautifulSoup(content, 'html.parser')  # Parse the HTML
        reviews.append(parsed_content)

        # Extract review text from specific HTML elements
        # for para in parsed_content.find_all("div", {"class": "text_content"}):
        #     reviews.append(para.get_text())

    return reviews
    # return parsed_content

# . !!!!  THE AIRLINE NAME HERE !!!!!
airline_name = 'Air France'
res_func = airline_func(airline_name)
# print(res_func)

# Extract all review articles
reviews = []
# Assuming 'soup' is a list containing a single BeautifulSoup object
for item in res_func[0].find_all("article", class_="comp_media-review-rated"):
    reviews.append(item)  # Kumpulin semua review ke dalam list

# ... (rest of your code remains the same)
# List untuk menyimpan data ekstrak
data = []

# Iterasi setiap review untuk ekstrak detailnya
for review in reviews:
    date = review.find("meta", itemprop="datePublished")["content"] if review.find("meta", itemprop="datePublished") else None
    rating = review.find("span", itemprop="ratingValue").text.strip() if review.find("span", itemprop="ratingValue") else None
    title = review.find("h2", class_="text_header").text.strip() if review.find("h2", class_="text_header") else None
    # author = review.find("span", itemprop="author").text.strip() if review.find("span", itemprop="author") else None
    content = review.find("div", class_="text_content").text.strip() if review.find("div", class_="text_content") else None

    # Cari date_flown dari tabel yang ada di review
    date_flown = None
    for row in review.find_all("tr"):
        header = row.find("td", class_="review-rating-header date_flown")
        value = row.find("td", class_="review-value")
        if header and value:
            date_flown = value.text.strip()
            break  # Ambil satu aja, terus keluar dari loop

    # Simpan ke list data
    data.append([date, date_flown, rating, title,
                #  author,
                 content])

# Buat DataFrame
columns = ["date_published", "date_flown", "rating", "title",
          #  "author",
           "review"]
df = pd.DataFrame(data, columns=columns)
# print(df.head())

# ===================================================================================================
def analyze_sentiment(review): # Changed from reviews to review
    # reviews = df['review'] # Removed this redundant line
    tokens = nltk.word_tokenize(review)  # Tokenize text into words
    tagged_tokens = nltk.pos_tag(tokens)  # Perform part-of-speech tagging

    lemmatizer = nltk.WordNetLemmatizer()
    lemmatized_words = [
        lemmatizer.lemmatize(word_analyze, tag[0].lower() if tag[0].lower() in ['a', 'r', 'n', 'v'] else 'n')
        for word_analyze, tag in tagged_tokens
    ]

    # Remove stopwords
    cust_stopwords = stopwords.words('english')
    clean_words = [word_analyze for word_analyze in lemmatized_words if word_analyze.lower() not in cust_stopwords]

    clean_text = ' '.join(clean_words)  # Recreate text after cleaning

    # Perform sentiment analysis using TextBlob
    blob = TextBlob(clean_text)
    polarity = blob.sentiment.polarity

    # Classify sentiment based on polarity
    if polarity > 0:
        sentiment = 'Positive'
    else: 
        sentiment = 'Negative'

    return sentiment, polarity

    # Apply sentiment analysis to each review and store results in new columns
df[['sentiment', 'polarity']] = df['review'].apply(analyze_sentiment).apply(pd.Series) # Changed from df['reviews'] to df['review']
# ===================================================================================================

# ===================================================================================================
# Pastikan kolom date_flown bersih dari NaN/null values
df_cleaned = df.dropna(subset=["date_flown"])

# Konversi date_flown jadi format datetime (jika hanya bulan & tahun, kita set default ke tanggal 1)
df_cleaned["date_flown"] = pd.to_datetime(df_cleaned["date_flown"], format="%B %Y")

# Grouping data berdasarkan bulan/tahun penerbangan
df_grouped = df_cleaned.groupby(df_cleaned["date_flown"].dt.to_period("M")).size().reset_index(name="count")

# Plot
plt.figure(figsize=(12, 6))
sns.lineplot(x=df_grouped["date_flown"].astype(str), y=df_grouped["count"], marker="o", linestyle="-", color="b")

# Formatting plot
plt.xticks(rotation=45)
plt.xlabel("Bulan & Tahun Penerbangan")
plt.ylabel("Jumlah Review")
plt.title(f"Tren Jumlah Review Berdasarkan Bulan pada maskapai {airline_name}")
plt.grid(True)

# Show plot
plt.show()
# plt.savefig("review_trend.png", dpi=300, bbox_inches='tight')  # Simpan gambar dengan kualitas tinggi
# print("Grafik telah disimpan sebagai review_trend.png")  # Beri tahu user

# ===================================================================================================

# Convert rating to numeric and categorize into 'positive' and 'negative'
df["rating"] = pd.to_numeric(df["rating"], errors="coerce")
# df["sentiment"] = df["rating"].apply(lambda x: "positive" if x >= 6 else "negative")

# Convert date to datetime format and extract year & month
df_dateflown = df[df['date_flown'].notna()]
df_dateflown["date"] = pd.to_datetime(df_dateflown["date_flown"], format="%B %Y", errors="coerce")
df_dateflown["year"] = df_dateflown["date"].dt.year
df_dateflown["month"] = df_dateflown["date"].dt.month

# Drop any rows with missing essential values
df_cleaned = df_dateflown.dropna(subset=["date", "rating",])
# Reorder and select relevant columns to match airline_data.csv format
df_final = df_cleaned[["date", "year", "month", "rating", "review"]]
# Display processed DataFrame
# print(df_final.head())

df_res = pd.merge(df, df_final, on='review', how='outer')
print(df_res)

# ===================================================================================================

# Filter data untuk tahun 2024
year_to_analyze = 2024
df_year = df_res[df_res['year'] == year_to_analyze]

# Hitung jumlah sentiment positif dan negatif per bulan
sentiment_counts = df_year.groupby(['month', 'sentiment']).size().unstack(fill_value=0)

# Hitung persentase
sentiment_percentage = sentiment_counts.div(sentiment_counts.sum(axis=1), axis=0) * 100

# Data untuk grouped bar chart
months = sentiment_percentage.index
positive = sentiment_percentage['Positive']
negative = sentiment_percentage['Negative']

# Lebar setiap bar
bar_width = 0.35

# Posisi bar untuk setiap bulan
r1 = np.arange(len(months))  # Posisi bar untuk Positive
r2 = [x + bar_width for x in r1]  # Posisi bar untuk Negative

# Plot grouped bar chart
plt.figure(figsize=(10, 6))
plt.bar(r1, positive, color='green', width=bar_width, label='Positive')
plt.bar(r2, negative, color='red', width=bar_width, label='Negative')

# Tambahkan label dan judul
plt.title('Persentase Sentiment Positif dan Negatif per Bulan (2024)', fontsize=16)
plt.xlabel('Bulan', fontsize=14)
plt.ylabel('Persentase', fontsize=14)
plt.xticks([r + bar_width / 2 for r in range(len(months))], months, rotation=0)
plt.legend(title='Sentiment', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.grid(axis='y', linestyle='--', alpha=0.7)

# Tampilkan plot
plt.show()

# ===================================================================================================
# Plot bar chart dengan warna custom
# sentiment_percentage.plot(kind='bar', stacked=True, figsize=(10, 6), color=['#1f77b4', '#d62728'])
# plt.title('Persentase Sentiment Positif dan Negatif per Bulan (2024)', fontsize=16)
# plt.xlabel('Bulan', fontsize=14)
# plt.ylabel('Persentase', fontsize=14)
# plt.xticks(rotation=0)
# plt.legend(title='Sentiment', bbox_to_anchor=(1.05, 1), loc='upper left')
# plt.grid(axis='y', linestyle='--', alpha=0.7)
# plt.show()

# ===================================================================================================
# PIE CHART in 1 year = contoh 2024
# Hitung total sentiment positif dan negatif untuk tahun 2024
total_sentiment = df_year['sentiment'].value_counts()
# Plot pie chart
plt.figure(figsize=(6, 6))
plt.pie(total_sentiment, labels=total_sentiment.index, autopct='%1.1f%%', colors=['green', 'red'])
plt.title(f'Persentase Sentiment Positif dan Negatif selama {year_to_analyze}')
plt.show()

# ===================================================================================================
# Filter data untuk 3 BULAN PERTAMA
df_3_months = df_year[df_year['month'].isin([1, 2, 3])]

# Hitung total sentiment
total_sentiment_3_months = df_3_months['sentiment'].value_counts()

# Plot pie chart
plt.figure(figsize=(6, 6))
plt.pie(total_sentiment_3_months, labels=total_sentiment_3_months.index, autopct='%1.1f%%', colors=['green', 'red'])
plt.title(f'Persentase Sentiment Positif dan Negatif (Januari - Maret {year_to_analyze})')
plt.show()

# ===================================================================================================
# Filter data untuk KUARTAL AWAL
df_4_months = df_year[df_year['month'].isin([1, 2, 3,4])]

# Hitung total sentiment
total_sentiment_4_months = df_4_months['sentiment'].value_counts()

# Plot pie chart
plt.figure(figsize=(6, 6))
plt.pie(total_sentiment_4_months, labels=total_sentiment_4_months.index, autopct='%1.1f%%', colors=['green', 'red'])
plt.title(f'Persentase Sentiment Positif dan Negatif pada Kuartal awal {year_to_analyze}')
plt.show()

# ===================================================================================================
# Filter data untuk KUARTAL AKHIR
df_4_months = df_year[df_year['month'].isin([9,10,11,12])]

# Hitung total sentiment
total_sentiment_4_months = df_4_months['sentiment'].value_counts()

# Plot pie chart
plt.figure(figsize=(6, 6))
plt.pie(total_sentiment_4_months, labels=total_sentiment_4_months.index, autopct='%1.1f%%', colors=['green', 'red'])
plt.title(f'Persentase Sentiment Positif dan Negatif pada Kuartal akhir {year_to_analyze}')
plt.show()