import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64
import numpy as np
from nltk.corpus import stopwords
from nltk.probability import FreqDist
import re
import string
from app.models import *
from app import db

# plots = []

def generate_airline_specific_visualization(airline_name, year=None, selected_period=None, selected_quarter=None,
                                            start_month=None, end_month=None):

    # Ambil data dari database untuk airline tertentu
    reviews = ReviewFull.query.filter_by(airline=airline_name).all()
    if not reviews:
        return ''
    
    # convert to dataFrame
    df = pd.DataFrame([{
    'airline': r.airline, 
    'sentiment': r.sentiment, 
    'date_flown': r.date_flown
    } for r in reviews])

    
    if df.empty:
        return ""  # Jika tidak ada data
    
    # Konversi date_flown ke datetime
    df['date_flown'] = pd.to_datetime(df['date_flown'], format="%B %Y", errors="coerce")
    
    # Drop rows dengan date_flown yang tidak valid
    df = df.dropna(subset=["date_flown"])
    
    # Filter data berdasarkan tahun jika tahun diberikan
    if year:
        df = df[df['date_flown'].dt.year == year]
    
    # List untuk menyimpan plot base64
    plots = []
    
    # Fungsi untuk generate plot dan menyimpannya ke dalam list plots
    def generate_plot(plot_func, *args, **kwargs):
        plt.figure(figsize=(12, 6))
        plot_func(*args, **kwargs)
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        plots.append(base64.b64encode(buf.getvalue()).decode('utf-8'))
        plt.close()

    
    # ================================================================================
    # GAMBAR DATA VISUALISASI NO 1: Tren Jumlah Review Berdasarkan Bulan  ||  PLOTS1 [0]
    df_grouped = df.groupby(df["date_flown"].dt.to_period("M")).size().reset_index(name="count")
    df_grouped["date_flown_formatted"] = df_grouped["date_flown"].dt.strftime("%b %Y")

    generate_plot(
        sns.lineplot, x=df_grouped["date_flown_formatted"], y=df_grouped["count"], marker="o", linestyle="-", color="b"
    )

    plt.title(f"Tren Jumlah Review Berdasarkan Bulan pada maskapai {airline_name} ({year if year else 'All Time'})")
    plt.xlabel("Bulan & Tahun Penerbangan")
    plt.ylabel("Jumlah Review")
    plt.xticks(rotation=45)
    plt.grid(True)
    
    # ================================================================================
    # GAMBAR DATA VISUALISASI NO 2: Persentase Sentiment Positif dan Negatif per Bulan  ||  PLOTS1 [1]
    sentiment_counts = df.groupby([df["date_flown"].dt.to_period("M"), 'sentiment']).size().unstack(fill_value=0)
    sentiment_percentage = sentiment_counts.div(sentiment_counts.sum(axis=1), axis=0) * 100
    months = sentiment_percentage.index

    # Format bulan ke "MMM YYYY" (contoh: "Feb 2023")
    months_formatted = [month.strftime("%b %Y") for month in months]

    positive = sentiment_percentage['Positive']
    negative = sentiment_percentage['Negative']
    bar_width = 0.35
    r1 = np.arange(len(months))
    r2 = [x + bar_width for x in r1]

    def bar_chart_visual2():
        plt.bar(r1, positive, color='green', width=bar_width, label='Positive')
        plt.bar(r2, negative, color='red', width=bar_width, label='Negative')
        plt.title(f'Процент позитивных и негативных настроений каждый месяц ({year if year else "All Time"})')
        plt.xlabel('Bulan')
        plt.ylabel('Persentase')
        plt.xticks([r + bar_width / 2 for r in range(len(months))], months_formatted, rotation=45)
        plt.legend(title='Sentiment', bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.grid(axis='y', linestyle='--', alpha=0.7)

    generate_plot(bar_chart_visual2)
    
    # ================================================================================
    # GAMBAR DATA VISUALISASI NO 3: Pie Chart Sentiment Positif dan Negatif  ||  PLOTS2 [0]
    total_sentiment = df['sentiment'].value_counts()
    plt.title(f'Persentase Sentiment Positif dan Negatif ({year if year else "All Time"})')
    
    generate_plot(
        plt.pie, total_sentiment, labels=total_sentiment.index, autopct='%1.1f%%', colors=['green', 'red']
    )
    
    # ================================================================================
    # GAMBAR DATA VISUALISASI NO 4: Pie Chart Sentiment untuk Periode Tertentu  ||  PLOTS2 [1]
    if selected_period:
        if selected_period == "jan-apr":
            df_period = df[df['date_flown'].dt.month.isin([1, 2, 3,4])]
            period_label = "Januari - April"
        elif selected_period == "may-aug":
            df_period = df[df['date_flown'].dt.month.isin([5, 6,7,8])]
            period_label = "May - August"
        elif selected_period == "sep-dec":
            df_period = df[df['date_flown'].dt.month.isin([9,10,11,12])]
            period_label = "September - Desember"
        
        total_sentiment_period = df_period['sentiment'].value_counts()
        
        generate_plot(
            plt.pie, total_sentiment_period, labels=total_sentiment_period.index, autopct='%1.1f%%', colors=['green', 'red']
        )
        plt.title(f'Persentase Sentiment Positif dan Negatif ({period_label} {year if year else ""})')
    
    # ================================================================================
    # GAMBAR DATA VISUALISASI NO 5: Pie Chart Sentiment untuk Kuartal Tertentu  ||  PLOTS2 [2]
    if selected_quarter:
        if selected_quarter == "q1":
            df_quarter = df[df['date_flown'].dt.month.isin([1, 2, 3])]
            quarter_label = "Kuartal 1"
        elif selected_quarter == "q2":
            df_quarter = df[df['date_flown'].dt.month.isin([4, 5, 6])]
            quarter_label = "Kuartal 2"
        elif selected_quarter == "q3":
            df_quarter = df[df['date_flown'].dt.month.isin([7, 8, 9])]
            quarter_label = "Kuartal 3"
        elif selected_quarter == "q4":
            df_quarter = df[df['date_flown'].dt.month.isin([10, 11, 12])]
            quarter_label = "Kuartal 4"
        
        total_sentiment_quarter = df_quarter['sentiment'].value_counts()
        
        generate_plot(
            plt.pie, total_sentiment_quarter, labels=total_sentiment_quarter.index, autopct='%1.1f%%', colors=['green', 'red']
        )
        plt.title(f'Persentase Sentiment Positif dan Negatif ({quarter_label} {year if year else ""})')

    # ================================================================================
    # GAMBAR DATA VISUALISASI NO 6: Persentase Sentiment Positif dan Negatif dari Bulan X ke Y
# ================================================================================
# GAMBAR DATA VISUALISASI NO 6: Persentase Sentiment Positif dan Negatif per Bulan (Range X-Y)   ||  PLOTS1 [2]
    if start_month and end_month:
        # Konversi nama bulan ke angka (Jan=1, Dec=12)
        month_map = {month.lower(): idx for idx, month in enumerate(
            ['January', 'February', 'March', 'April', 'May', 'June', 
            'July', 'August', 'September', 'October', 'November', 'December'], 1)}
        start_num = month_map.get(start_month.lower())
        end_num = month_map.get(end_month.lower())
        
        if start_num and end_num:
            # Filter data berdasarkan range bulan
            df_range = df[(df['date_flown'].dt.month >= start_num) & 
                        (df['date_flown'].dt.month <= end_num)]
            
            if not df_range.empty:
                # Hitung persentase sentiment per bulan
                sentiment_counts = df_range.groupby(
                    [df_range['date_flown'].dt.to_period("M"), 'sentiment']
                ).size().unstack(fill_value=0)
                
                sentiment_percentage = sentiment_counts.div(
                    sentiment_counts.sum(axis=1), axis=0
                ) * 100
                
                # Format bulan ke "MMM" (contoh: "Jan")
                months = [period.strftime("%b") for period in sentiment_percentage.index]

                def bar_chart_visual6():
                    bar_width = 0.35
                    r1 = np.arange(len(months))
                    r2 = [x + bar_width for x in r1]
                    plt.bar(
                        r1, 
                        sentiment_percentage['Positive'], 
                        color='green', 
                        width=bar_width, 
                        label='Positive'
                    )
                    plt.bar(
                        r2, 
                        sentiment_percentage['Negative'], 
                        color='red', 
                        width=bar_width, 
                        label='Negative'
                    )
                    plt.title(
                        f'Процент позитивных и негативных настроений в месяц\n'
                        f'{start_month} - {end_month} {year if year else ""}'
                    )
                    plt.xlabel('Месяц')
                    plt.ylabel('Процент (%)')
                    plt.xticks(
                        [r + bar_width / 2 for r in range(len(months))], 
                        months, 
                        rotation=45
                    )
                    plt.legend(title='Sentiment', bbox_to_anchor=(1.05, 1), loc='upper left')
                    plt.grid(axis='y', linestyle='--', alpha=0.7)

                generate_plot(bar_chart_visual6)
    
    return plots #plots1, plots2
    
    # return plots

