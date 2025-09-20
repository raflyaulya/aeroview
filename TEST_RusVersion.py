'''
                                !!!  PROGRESS ON GOING   !!!

    TAMBAHAN BEBERAPA METODE:
    - Handling error (untuk mencegah berganti VPN berkali2)
    - data preparation (menghapus value "Irecommend", dan menyusun rapi kolom)
    - METODE Scraping PROXY LIST (supaya mencegah error/ban dari situs irecommend.ru)

'''

import requests 
import string 
import pandas as pd
import re
import random
from bs4 import BeautifulSoup
import nltk
from nltk.corpus import stopwords
from textstat.textstat import textstatistics #, legacy_round
from textblob import TextBlob
from urllib.parse import quote as url_quote
from fake_useragent import *
from check_proxy import *
import warnings 
warnings.filterwarnings('ignore')

nltk.download('punkt_tab')
nltk.download('averaged_perceptron_tagger')
nltk.download('wordnet')
nltk.download('stopwords')
# Download the missing resource
nltk.download('averaged_perceptron_tagger_eng')


# ===========================   METODE (USER AGENT) to AVOID mengganti VPN berkali2    part I =======================
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
}

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

# ===========================   METODE (USER AGENT) to AVOID mengganti VPN berkali2    part II =======================
# ua = UserAgent()
# user_agent = ua.random
# headers = {"User-Agent": user_agent}

# ===========================   METODE (USER AGENT) to AVOID mengganti VPN berkali2    part II =======================

# output_name = 'aeroflot_airlines'
# output_name = 'aeroflot'
# https://irecommend.ru/content/aeroflot
rus_airline_name = russian_airlines['Pobeda']

base_url = f"https://irecommend.ru/content/{rus_airline_name}"
proxy = random.choice(valid_proxies)
response = requests.get(base_url, headers=headers, 
                        # proxies={"http":proxy, 'https':proxy}  # ========  penambahan METODE PROXY
                        ) 
soup = BeautifulSoup(response.content, 'html.parser')
# print(soup)
# print('=========================================================\n')


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

# Cetak hasil HTML yang sudah disederhanakan
# print(soup.prettify())

# =====================    TO GET THE SUB-TITLE PER REVIEWS  ======================
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
# # Cetak hasil
print('sub-title reviews result:',result_list)
print('length of the sub-title list',len(result_list))
print('==================================\n')

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
print('Star rating result list:',ratings)
print('lenth of the rating star list:',len(ratings))
print('\n====================================================\n')


# =====================    STARTING to Prepare & Analyze data ======================
list_sub_title = result_list
lis1 = list_sub_title
lis2 = ratings

data = list(zip(lis1, lis2))
df_kol = pd.DataFrame(data, columns=['sub_title', 'count_ratings'])

# determine the number of reviews text 
num_lis = 50
random_lis = random.sample(data, num_lis)
df_rand = pd.DataFrame(random_lis, columns=['sub_title', 'count_ratings'])
df_rand['index'] = range(1, len(df_rand) + 1)
df_rand = df_rand[['index'] + list(df_rand.columns[:-1])]

# ini adalah list dari data kolom "sub_title" yg isinya adalah 30 rows
df_rand_subTitle = df_rand['sub_title'].tolist()
# df_rand_subTitle

lis_url = df_rand_subTitle
temporary_save = []


for i in lis_url:
    base_url = f"https://irecommend.ru/content/{i}"
    proxy = random.choice(valid_proxies)
    response = requests.get(base_url, headers=headers, 
                            # proxies={"http":proxy, 'https':proxy}  #===================    penambahan METODE PROXY
                            )
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
# print(text)

df = pd.DataFrame()
df["reviews"] = all_text

def analyze_sentiment(reviews):
    tokens = nltk.word_tokenize(reviews)

    tagged_tokens = nltk.pos_tag(tokens)

    lemmatized_words = []
    lemmatizer = nltk.WordNetLemmatizer()
    for word, tag in tagged_tokens:
        tag = tag[0].lower() if tag[0].lower() in ['a', 'r', 'n', 'v'] else 'n'
        lemmatized_words.append(lemmatizer.lemmatize(word, tag))

    stopwords = nltk.corpus.stopwords.words('russian')
    clean_words = [word for word in lemmatized_words if word.lower() not in stopwords]

    clean_text = ' '.join(clean_words)

    blob = TextBlob(clean_text)
    polarity = blob.sentiment.polarity
    # subjectivity = blob.sentiment.subjectivity

    if polarity > 0:
        sentiment = 'Positive'
    else:
        sentiment = 'Negative'

    return sentiment, polarity

df[['sentiment', 'polarity']] = df['reviews'].apply(analyze_sentiment).apply(pd.Series)

df1 = df
# dfnew = df_kol[:30]
dfnew = df_rand

df2 = pd.merge(df1, dfnew, left_index=True, right_index=True)
# df2 = pd.concat([df1, dfnew], axis=1
# df2

# Remove the 'polarity' column
if 'polarity' in df2.columns:
    df2 = df2.drop('polarity', axis=1)

# Update 'sentiment' column based on 'count_ratings'
def update_sentiment(row):
    if row['count_ratings'] in (4, 5):
        return 'Positive'
    elif row['count_ratings'] == 3:
        return 'Neutral'
    elif row['count_ratings'] in (1, 2):
        return 'Negative'
    else:
        return row['sentiment'] # Keep original sentiment if count_rating is not in specified range.

df2['sentiment'] = df2.apply(update_sentiment, axis=1)


df2 = df2[df2['reviews'] != 'Irecommend']
df2 = df2[['index', 'reviews', 'sub_title', 'sentiment', 'count_ratings']]
# df2 = df2.reset_index()

print(df2)
print('===========================================================================')

# get the airline name by link name / REVERSED Dict rus airline name
reversed_airlines = {value: key for key, value in russian_airlines.items()}
# input_link = 's7-airlines-oao-aviakompaniya-sibir'
rus_airline_name = reversed_airlines.get(rus_airline_name, "Maskapai tidak ditemukan")

df.to_excel(f'data_df_{rus_airline_name}2.xlsx', index=False)
df2.to_excel(f'data_df2_{rus_airline_name}2.xlsx', index=False)

if result_list == 0:
    print('There\'s something error in your program!')
elif result_list == num_lis:
    print(f'data DF & DF2 - {rus_airline_name} has been saved successfully!!')


    # num_lis = 50