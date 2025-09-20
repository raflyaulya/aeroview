import time
import requests 
import numpy as np
import string 
import pandas as pd
import re
import random
from bs4 import BeautifulSoup
import io
import base64
import seaborn as sn
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import spacy
import nltk
from nltk.probability import FreqDist  # For frequency distribution analysis
from nltk.corpus import stopwords
# from textstat.textstat import textstatistics #, legacy_round
from textblob import TextBlob
from urllib.parse import quote as url_quote
from concurrent.futures import ThreadPoolExecutor
import warnings 
warnings.filterwarnings('ignore')

# Uncomment these lines to download NLTK data if not already done
# nltk.download('punkt_tab')
# nltk.download('averaged_perceptron_tagger')
# nltk.download('wordnet')
# nltk.download('stopwords')
# # Download the missing resource
# nltk.download('averaged_perceptron_tagger_eng')   

class CaptchaBlockedError(Exception):
    pass

# def detect_captcha(soup):
#     """Deteksi halaman CAPTCHA berdasarkan elemen spesifik"""
#     captcha_indicator = soup.find("div", {"class": "captcha"}) or soup.find(text=re.compile("captcha", re.I))
#     return captcha_indicator is not None
russian_airlines = {
    "Aeroflot": "aeroflot",
    "Aurora": "aviakompaniya-avrora-aurora",
    "Nordstar": "nord-star-airlines-aviakompaniya-taimyr",
    "Ikar": "ikar-ikar-airlines",
    "Red Wings Airlines": "red-wings",
    "Rossiya": "rossiya-rossiiskie-avialinii",
    "S7 Airlines": "s7-airlines-oao-aviakompaniya-sibir",
    "Utair": "utair",
    "Ural Airlines": "uralskie-avialinii",
    "Yakutia Airlines": "yakutiya",
    "Yamal Airlines": "yamal",
    "Alrosa Mirny Air Enterprise": "alrosa-alrosa-airlines",
    "Azimuth": "azimut",
    "IrAero": "iraero-0",
    "Izhavia": "izhavia",
    "RusLine": "ruslain",
    "Severstal Air Company": "severstal-avia",
    "UVT Aero": "yuvt-aero-uvt-aero",
    "Pobeda": "pobeda-0",
    "SmartAvia": "smartavia-3",
    "Azur air": "azurair-katekavia",
    "I-Fly": "i-fly",
    "Nordwind Airlines": "nordwind-airlines"
}

def airline_func_rus(airline_name, selectSentiment):
    try:
        # ========  KALO KENAPA2 , COBA DI UN-COMMENT AJA, SOALNYA headers yg dibawah ini udh BENAR  ===================================
        headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
        }

        # rus_airline_name = russian_airlines['Azur air']
        rus_airline_name = airline_name
        base_url = f"https://irecommend.ru/content/{rus_airline_name}"

        response = requests.get(base_url, headers=headers, verify=False, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')

        # ========  KALO KENAPA2 , COBA DI UN-COMMENT AJA, soalnya RESPONSE & SOUP yg dibawah ini udh BENAR  ===================================
        # response = requests.get(base_url, headers=headers, verify=False) 
        # soup = BeautifulSoup(response.content, 'html.parser')


        # ===============   CLEANING SOME HTML ELEMENTS =======================
        # Menghapus elemen-elemen yang tidak diperlukan
        ads = soup.find_all("div", {"class": ["show-on-desktop", "show-on-tablet", "adfox_block"]})
        for ad in ads:
            ad.decompose()

        unnecessary_ids = ["b_middle1", "b_mobmiddle1"]
        for id_ in unnecessary_ids:
            element = soup.find(id=id_)
            if element:
                element.decompose()

        # Menghapus elemen "Смотрите также" (block-seealso)
        seealso = soup.find("div", {"class": "block-seealso"})
        if seealso:
            seealso.decompose()

        # Membersihkan elemen lain jika diperlukan
        unnecessary_classes = ["clear"]
        for cls in unnecessary_classes:
            elements = soup.find_all("div", {"class": cls})
            for element in elements:
                element.decompose()

        # =====================    GET THE SUB-TITLE PER REVIEWS  ======================
        result_list = []

        # Cari elemen dengan class 'reviewTextSnippet'
        review_snippets = soup.find_all("a", class_="reviewTextSnippet")

        # Iterasi untuk mengambil nilai href
        for snippet in review_snippets:
            href = snippet.get("href")
            if href:
                # Simpan hanya bagian terakhir dari URL
                cleaned_href = href.split("/")[-1]
                result_list.append(cleaned_href)

        # =====================    TO GET THE STAR RATING PER CUST REVIEW ======================
        # Inisialisasi list untuk menyimpan hasil rating
        ratings = []
        # Cari semua elemen rating
        rating_elements = soup.find_all("div", class_="fivestarWidgetStatic")

        # Iterasi untuk menghitung jumlah "on" di dalam rating
        for rating_element in rating_elements:
            stars_on = rating_element.find_all("div", class_="on")
            stars_count = len(stars_on)  # Hitung jumlah bintang aktif
            ratings.append(stars_count)
        # # Cetak hasil
        ratings.pop(0)

        # =====================    STARTING to Prepare & Analyze data ======================
        list_sub_title = result_list
        lis1 = list_sub_title
        lis2 = ratings

        data = list(zip(lis1, lis2))

        # determine the number of reviews text 
        num_lis = 50
        random_lis = random.sample(data, num_lis)
        df_rand = pd.DataFrame(random_lis, columns=['sub_title', 'count_ratings'])
        df_rand['index'] = range(1, len(df_rand) + 1)
        df_rand = df_rand[['index'] + list(df_rand.columns[:-1])]

        # ini adalah list dari data kolom "sub_title" yg isinya adalah 50 rows
        df_rand_subTitle = df_rand['sub_title'].tolist()

        # =====================    STARTING to Analyze data ======================
        lis_url = df_rand_subTitle
        temporary_save = []

        # ========  KALO KENAPA2 , COBA DI UN-COMMENT AJA, soalnya for i in lis_url yg dibawah ini udh BENAR  ===================================
        # ========  to get the CUST REVIEW TEXT IN DETAIL AND MORE INFORMATION (by using sub_title)   ===================================
        for i in lis_url:
            base_url = f"https://irecommend.ru/content/{i}"
                
                # Tambahkan delay acak antara 2-5 detik
            time.sleep(random.uniform(2, 5))

            try:
                response = requests.get(base_url, headers=headers, timeout=10)
                response.raise_for_status()
            except requests.exceptions.RequestException as e:
                continue  # Lanjut ke review berikutnya jika error                
            soup = BeautifulSoup(response.content, 'html.parser')

            temporary_save.append(soup)

        # Lanjutkan dengan parsing data
        for soup in temporary_save:
            for tag in soup.find_all(['script', 'style']):
                tag.decompose()

        all_text = []
        for soup in temporary_save:
            all_text.append(' '.join(soup.stripped_strings))

        text = ' '.join(all_text)
        text = text.lower()
        text = re.sub(r'\d+', '', text)

        # ====== FINAL CUST REVIEW TEXT  HAS ALREADY GOTTEN !!!   ===============  
        df = pd.DataFrame()
        df["reviews"] = all_text
        # ====== FINAL CUST REVIEW TEXT  HAS ALREADY GOTTEN !!!   ===============  

        # Muat model bahasa Rusia dari spacy = for RUS STOPWORDS USAGE !!!
        stopwordsRus_preprocessing = spacy.load("ru_core_news_sm")
        
        # =======================       HAPUS tanpa metode stopwords??? 
        # ==============        data analyze/analyzing sentiment start      =====================
        # ===================                       "»" , "«"       ======================================
        def analyze_sentiment(reviews):
            # Tokenisasi dengan NLTK
            tokens = nltk.word_tokenize(reviews)
            tagged_tokens = nltk.pos_tag(tokens)
            # Lemmatisasi dengan NLTK
            lemmatized_words = []
            lemmatizer = nltk.WordNetLemmatizer()
            for word, tag in tagged_tokens:
                tag = tag[0].lower() if tag[0].lower() in ['a', 'r', 'n', 'v'] else 'n'
                lemmatized_words.append(lemmatizer.lemmatize(word, tag))
            
            stopwordsRus_preprocessing = spacy.load("ru_core_news_sm")
            # Hapus stopwords dengan spacy
            doc = stopwordsRus_preprocessing(" ".join(lemmatized_words))  # Gabungkan lemmatized words untuk diproses oleh spacy
            clean_words = [token.text for token in doc if not token.is_stop]  # Hapus stopwords
            # Gabungkan kembali kata-kata yang tersisa
            clean_text = ' '.join(clean_words)   
                     
            # Analisis sentimen dengan TextBlob
            blob = TextBlob(clean_text)
            polarity = blob.sentiment.polarity

            if polarity > 0:
                sentiment = 'Positive'
            else:
                sentiment = 'Negative'
            
            return sentiment, polarity

        df[['sentiment', 'polarity']] = df['reviews'].apply(analyze_sentiment).apply(pd.Series)
        # print(df)

        df1 = df
        dfnew = df_rand

        df = pd.merge(df1, dfnew, left_index=True, right_index=True)

        # =========================================================================================
        # BAGIAN YG DI (UN)COMMENT
        # Remove the 'polarity' column
        # if 'polarity' in df.columns:
        #     df = df.drop('polarity', axis=1)

        # # Update 'sentiment' column based on 'count_ratings'
        # def update_sentiment(row):
        #     if row['count_ratings'] in (4, 5):
        #         return 'Positive'
        #     elif row['count_ratings'] == 3:
        #         return 'Neutral'
        #     elif row['count_ratings'] in (1, 2):
        #         return 'Negative'
        #     else:
        #         return row['sentiment'] # Keep original sentiment if count_rating is not in specified range.

        # df['sentiment'] = df.apply(update_sentiment, axis=1)
        # BAGIAN YG DI (UN)COMMENT
        # =========================================================================================

        df = df[df['reviews'] != 'Irecommend']
        df = df[['index', 'reviews', 'sub_title', 'sentiment', 'count_ratings']]
        # df2 = df2.reset_index()
        # print(df2)

        # ====================================  starting to Final Step of DATA CLEANING   =======================================
        cust_rev_list= df['reviews']

        # Fungsi untuk memodifikasi setiap review
        def clean_review(review):
            # Cari bagian "Опубликовано"
            start_idx = review.find('Опубликовано')
            # Cari bagian "рекомендует сообщить о нарушении"
            end_idx = review.find('рекомендует сообщить о нарушении Читать все отзывы')
            
            # Jika kedua teks ditemukan, potong teks di antaranya
            if start_idx != -1 and end_idx != -1:
                return review[start_idx:end_idx + len('рекомендует сообщить о нарушении Читать все отзывы')]
            return review  # Jika salah satu tidak ditemukan, kembalikan teks asli

        # Terapkan fungsi ke setiap elemen dalam list
        cleaned_reviews = [clean_review(review) for review in cust_rev_list]
        cust_rev2 = cleaned_reviews
        # df['cust_rev_liss'] = cleaned_reviews


        # Fungsi untuk membersihkan teks
        def clean_review(review):
            # Hapus bagian "Опубликовано date month, year - hh:mm"
            review = re.sub(r'Опубликовано \d{1,2} \w+, \d{4} - \d{2}:\d{2}', '', review)
            # Hapus kalimat "рекомендует сообщить о нарушении Читать все отзывы"
            review = review.replace('рекомендует сообщить о нарушении Читать все отзывы', '')
            # Hapus spasi yang tidak perlu di awal dan akhir
            return review.strip()

        # Terapkan fungsi ke setiap elemen dalam daftar
        cleaned_reviews1 = [clean_review(review) for review in cust_rev2]

        df['reviews'] = cleaned_reviews1

        # ====================================  stop to  Final Step of DATA CLEANING   =======================================


        # ====================================  starting to Classificate the analyze sentiment choice =======================================
        # Store the sentiment analysis review text into 2 kind of Classification,  Positive or Negative 
        #  function to select a random review based on sentiment choice 
        # ==================     NEUTRAL  ???????
        def func_selectSentiment(selectSentiment):
            positive_values = ['Positive', 'positive']
            negative_values = ['Negative', 'negative']

            if selectSentiment in positive_values:
                positive_reviews = df[df["sentiment"] == 'Positive']
                return np.random.choice(positive_reviews['reviews'])
            elif selectSentiment in negative_values:
                negative_reviews = df[df["sentiment"] == 'Negative']
                return np.random.choice(negative_reviews['reviews'])
            return None 
        
        res_sentiment = func_selectSentiment(selectSentiment)
            

        # ==============        visualizing data START     =====================
        plots = []  # List to store visualizations
        most_common_words = []  # Store word frequencies for returning later
        words = []
        # words = word_freq
        frequencies = []  # Store frequencies

        def generate_word_freq_chart(sentiment_filter):
            nonlocal most_common_words, words, frequencies

            # Gabungkan review berdasarkan sentimen
            sentiment_reviews = ' '.join(df[df['sentiment'] == sentiment_filter]['reviews'].tolist())
            
            # Preprocessing teks secara menyeluruh
            sentiment_reviews = (
                sentiment_reviews.lower()  # Convert ke lowercase
                .translate(str.maketrans('', '', string.punctuation + '«»—–'))  # Hapus tanda baca + karakter khusus Rusia
                .replace("’", "").replace("‘", "")  # Hapus tanda kutip khusus
            )
            
            # Tokenisasi dan hapus stopwords dengan spaCy
            doc = stopwordsRus_preprocessing(sentiment_reviews)
            clean_tokens = [
                token.text 
                for token in doc 
                if not token.is_stop 
                and not token.is_punct  # Pastikan tanda baca terfilter
                and token.text.strip()  # Hapus token kosong
            ]

            # Hitung frekuensi kata
            freq_dist = FreqDist(clean_tokens)
            most_common_words = freq_dist.most_common(20)
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
        if selectSentiment.lower() == 'positive':
            generate_word_freq_chart('Positive')
        elif selectSentiment.lower() == 'negative':
            generate_word_freq_chart('Negative')

        # Create and save a bar chart for sentiment counts
        bar_sentiment_counts = df.groupby('sentiment')['reviews'].count()
        sn.barplot(x=bar_sentiment_counts.index, y=bar_sentiment_counts.values)
        plt.title(f'Sentiment Analysis Results of {rus_airline_name}')
        plt.xlabel('Sentiment')
        plt.ylabel('Number of Reviews')

        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        plots.append(base64.b64encode(buffer.getvalue()).decode())
        buffer.close()
        plt.clf()

        # Create and save a pie chart for sentiment distribution
        pie_sentiment_counts = df.groupby('sentiment')['reviews'].count()
        plt.pie(pie_sentiment_counts.values, labels=pie_sentiment_counts.index, autopct='%1.2f%%')
        plt.title(f'Sentiment Analysis Results of {rus_airline_name}')


        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        plots.append(base64.b64encode(buffer.getvalue()).decode())
        buffer.close()
        plt.clf()

        return plots , res_sentiment, most_common_words, words, frequencies 

    except CaptchaBlockedError as e:
        print(f"ERROR CAPTCHA: {str(e)}")
        return [], "Blocked by CAPTCHA", [], [], []
    
    except Exception as e:
        print(f"ERROR UNKNOWN: {str(e)}")
        return [], "Scraping Error", [], [], []

    # ==============        visualizing data stop      =====================