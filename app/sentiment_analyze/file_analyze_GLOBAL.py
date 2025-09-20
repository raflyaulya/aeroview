import string
import re
from bs4 import BeautifulSoup  # For web scraping and HTML parsing
import pandas as pd  # For data manipulation and analysis
import numpy as np  # For numerical computations
import matplotlib
matplotlib.use('Agg')  # Ensures plots are created without a GUI (useful for servers)
import matplotlib.pyplot as plt  # For creating visualizations
import io  # For in-memory file operations
import base64  # For encoding image data into base64 for rendering in web apps
import seaborn as sns  # For advanced visualization (used for bar plots)
import requests  # For making HTTP requests to scrape web pages
from app.models import *
from app.extensions import db
# from datetime import datetime

import nltk  # For natural language processing
from nltk.corpus import stopwords  # For accessing stopword lists
from nltk.probability import FreqDist  # For frequency distribution analysis
from textblob import TextBlob  # For sentiment analysis and text processing

# Uncomment these lines to download NLTK data if not already done
# nltk.download('punkt')
# nltk.download('averaged_perceptron_tagger')
# nltk.download('wordnet')
# nltk.download('stopwords')


#==========================     web-scraping BEGIN     ============================ 

# Function to scrape airline reviews and perform analysis
def airline_func(airline_name, selectSentiment):
    # Format the airline name to match the URL structure
    formatted_name = '-'.join(airline_name.split())
    base_url = f"https://www.airlinequality.com/airline-reviews/{formatted_name}"
    
    pages = 10  # Number of pages to scrape
    page_size = 100  # Reviews per page (default: 100)
    reviews = []  # List to store extracted reviews
    dates_flown = []  # List to store date flown
    ratings = []  # List to store ratings
    titles = []  # List to store review titles

    # Scrape reviews from multiple pages
    for i in range(1, pages + 1):
        url = f"{base_url}/page/{i}/?sortby=post_date%3ADesc&pagesize={page_size}"
        response = requests.get(url)  # Send GET request to the page
        content = response.content  # Extract page content
        parsed_content = BeautifulSoup(content, 'html.parser')  # Parse the HTML
        
        # Extract review text and additional information
        for review in parsed_content.find_all("article", class_="comp_media-review-rated"):
            # Extract review text
            review_text = review.find("div", {"class": "text_content"}).get_text()
            reviews.append(review_text)
            
            # Extract date flown
            date_flown = None
            for row in review.find_all("tr"):
                header = row.find("td", class_="review-rating-header")
                if header and "Date Flown" in header.text:
                    date_flown = row.find("td", class_="review-value").text.strip()
                    break
            dates_flown.append(date_flown)
            
            # Extract rating
            rating = review.find("span", itemprop="ratingValue")
            ratings.append(rating.text.strip() if rating else None)
            
            # Extract title
            title = review.find("h2", class_="text_header")
            titles.append(title.text.strip() if title else None)

    # Create a DataFrame to organize and clean the data
    df = pd.DataFrame({
        "reviews": reviews,
        "date_flown": dates_flown,
        "rating": ratings,
        "title": titles
    })

    # ============================   data cleaning start / ОБРАБОТАТЬ ДАННЫЕ   ====================
    # Create a DataFrame to organize and clean the data
    df.index = range(1, len(df) + 1)  # Reset index to start from 1

    # Remove unnecessary prefixes from the reviews
    unnecessary_statements = ['✅ Trip Verified | ', 'Not Verified | ', '✅ Verified Review | ']
    for statement in unnecessary_statements:
        df.reviews = df.reviews.str.replace(statement, '')
    # ==============================      data cleaning stop / ОБРАБОТАТЬ ДАННЫЕ    ============================= 

    # ==============        data analyze/analyzing sentiment start      =====================
    # Function to analyze sentiment of reviews
    def analyze_sentiment(reviews):
        tokens = nltk.word_tokenize(reviews)  # Tokenize text into words
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
    df[['sentiment', 'polarity']] = df['reviews'].apply(analyze_sentiment).apply(pd.Series)
    # ============================        data analyze/analyzing sentiment stop      =====================


    # ============================        analyzing sentiment choice start      =====================
    # Function to select a random review based on sentiment choice
    def func_selectSentiment(selectSentiment):
        positive_values = ['Positive', 'positive']
        negative_values = ['Negative', 'negative']

        if selectSentiment in positive_values:
            positive_reviews = df[df['sentiment'] == 'Positive']
            return np.random.choice(positive_reviews['reviews'])
        elif selectSentiment in negative_values:
            negative_reviews = df[df['sentiment'] == 'Negative']
            return np.random.choice(negative_reviews['reviews'])
        return None

    res_sentiment = func_selectSentiment(selectSentiment)  # Get random review of selected sentiment

    # ==============        analyzing sentiment choice stop      =====================


    # ==============        Saving Scraped Data   START     =====================
    def save_scraped_data(airline_name, df):
        for index, row in df.iterrows():
            date_flown_raw = row.get('date_flown', None)
            try:
                date_flown = pd.to_datetime(date_flown_raw)
            except Exception:
                date_flown = None

            history = ReviewFull(
                airline=airline_name,
                sentiment=row.get('sentiment', None),
                review=row.get('reviews', None),
                date_flown=date_flown
            )
            db.session.add(history)
        db.session.commit()
    # Save scraped data to database
    save_scraped_data(airline_name, df)

    plots = []
    most_common_words = []
    words = []
    frequencies = []
    
    # Function to generate WORD FREQUENCY chart
    def generate_word_freq_chart(sentiment_filter):
        nonlocal most_common_words, words, frequencies

        sentiment_reviews = ' '.join(df[df['sentiment'] == sentiment_filter]['reviews'].tolist())
        sentiment_reviews = re.sub(r'\d+', '', sentiment_reviews.lower())  # Lowercase and remove numbers
        sentiment_reviews = sentiment_reviews.translate(str.maketrans('', '', string.punctuation))  # Remove punctuation

        tokens = sentiment_reviews.split()
        custom_stopwords = stopwords.words('english')
        clean_tokens = [token for token in tokens if token not in custom_stopwords]

        freq_dist = FreqDist(clean_tokens)  # Compute word frequencies
        most_common_words = freq_dist.most_common(20)  # Get top 20 frequent words
        words, frequencies = zip(*most_common_words)

        # Plot and save the bar chart
        plt.bar(words, frequencies)
        plt.xlabel('Words')
        plt.ylabel('Frequency')
        plt.title(f'Word Frequency Plot ({sentiment_filter} Reviews)')
        plt.xticks(rotation=45)

        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        plots.append(base64.b64encode(buffer.getvalue()).decode())
        buffer.close()
        plt.clf()

    # Generate chart for selected sentiment
    # plots = []
    # most_common_words = []
    # words = []
    # frequencies = []

    if selectSentiment.lower() == 'positive':
        generate_word_freq_chart('Positive')
    elif selectSentiment.lower() == 'negative':
        generate_word_freq_chart('Negative')

    # Create and save a PIE chart for sentiment distribution
    pie_sentiment_counts = df.groupby('sentiment')['reviews'].count()
    plt.pie(pie_sentiment_counts.values, labels=pie_sentiment_counts.index, autopct='%1.2f%%')
    plt.title(f'Результаты анализа настроений {airline_name}')

    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plots.append(base64.b64encode(buffer.getvalue()).decode())
    buffer.close()
    plt.clf()

    return plots, res_sentiment, most_common_words, words, frequencies



# airline_name= 'Etihad Airways'
# selectSentiment = 'Positive'
# plots, res_sentiment, most_common_words, words, frequencies = airline_func(airline_name=airline_name,
#                                                                             selectSentiment=selectSentiment)
# # Simpan gambar visualisasi ke database
# print(f"deskripsi sentiment {selectSentiment} dari maskapai {airline_name} adalah berikut dibawah ini:") 
# print(res_sentiment)
# print()
# print('dan juga berikut adalah gambar2 yg dihasilkan didalam plots')

# # Simpan setiap plot ke file
# for i, plot in enumerate(plots):
#     with open(f"plot_{i}.png", "wb") as img_file:
#         img_file.write(base64.b64decode(plot))
#     print(f"Plot {i} disimpan sebagai plot_{i}.png")