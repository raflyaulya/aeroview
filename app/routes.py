import sqlite3
from flask import jsonify, render_template, url_for
from flask import flash, redirect, session, request
from urllib.parse import quote as url_quote
from app import db
from flask import current_app as app
# from app.models import 
from sqlalchemy import extract, text
from datetime import datetime

from app.sentiment_analyze.file_analyze_GLOBAL import * 
from app.sentiment_analyze.file_analyze_RUS import * 
from app.visualization.timeline_visualization import *
from app.visualization.timeline_visualization_1airline import *
from app.models import * 
from app.extensions import db
from flask import Blueprint


main = Blueprint('main', __name__)

@main.route("/")
#================    NEXT PAGE MASUK KE PAGE ANALISA    ========================  methods=['GET', 'POST']
# @app.route('/index', methods=['GET', 'POST']) 
@main.route('/index', methods=['GET', 'POST']) 
def index():  # next_page index
    if 'username' in session: 
        return render_template('login')  # NEXT PAGE MASUK KE PAGE ANALISA 
    return render_template('index.html')  # redirect(url_for('index'))


# =======================           RUSSIAN VERSION   
# @app.route('/index_rus', methods=['GET', 'POST']) 
@main.route('/russian-main-page', methods=['GET', 'POST']) 
def index_rus():  # next_page index
    if 'username' in session:
        return render_template('login')  # NEXT PAGE MASUK KE PAGE ANALISA 
    return render_template('index_rus.html')  # redirect(url_for('index'))
    

# =======================           UPDATE CODE untuk ERROR HANDLE, AFFECTED: [FINALRESULT] + SAVE ==============================================   
# # =======================           RUSSIAN VERSION = INI YANG BENER  BARUU !!!  
@main.route('/final-result-global-analysis', methods=['GET', 'POST'])
def finalResult():
    try:
        res_airlineName = request.form['airlineName']
        selectSentiment = request.form['selectSentiment']
            
            # Panggil fungsi analisis
        plots, res_sentiment, most_common_words, words, frequencies = airline_func(res_airlineName, selectSentiment)
            
        return render_template('finalResult.html', 
                                res_airlineName=res_airlineName, 
                            selectSentiment=selectSentiment,
                            plots=plots, 
                            res_sentiment=res_sentiment, 
                            most_common_words=most_common_words,
                            words=words, 
                            frequencies=frequencies,
                            )
    
    except KeyError:
        flash('Please fill out all required fields!', 'error')
        return redirect(url_for('main.index'))
    
    except Exception as e:
        app.logger.error(f"Error during analysis: {str(e)}")
        flash('Oops! Something went wrong during analysis. Please try again.', 'error')
        return redirect(url_for('main.index'))

# ================================================================================================

# =======================           RUSSIAN VERSION  IMPROVED !!!! 
# @app.route('/finalResult_rus', methods=['POST'])
@main.route('/final-result-russian-analysis', methods=['POST'])
def finalResult_rus():
    # try:
    res_airlineName = request.form['airlineName']
    selectSentiment = request.form['selectSentiment']
    try:
        plots, res_sentiment, most_common_words, words, frequencies = airline_func_rus(res_airlineName, selectSentiment)
        
        # handle CAPTCHA error
        if res_sentiment == 'Blocked by CAPTCHA':   #"CAPTCHA detected":
            flash('Website irecommend.ru memblokir akses karena CAPTCHA. Silakan coba lagi setelah beberapa menit.', 'error')
            return redirect(url_for('main.index_rus'))
        # handle General Error
        # elif res_sentiment == "Scraping error":
        if res_sentiment == "Scraping error":
            flash('Terjadi kesalahan saat mengambil data. Silakan coba lagi.', 'error')
            return redirect(url_for('main.index_rus'))
        
        return render_template('finalResult_rus.html', res_airlineName=res_airlineName, 
                               selectSentiment=selectSentiment,plots=plots, 
                             res_sentiment=res_sentiment, most_common_words=most_common_words,
                             words=words, frequencies=frequencies)
    
    except Exception as e:
        # app.logger.error(f"Unexpected error: {str(e)}")
        flash('Terjadi kesalahan tak terduga. Silakan coba lagi nanti.', 'error')
        return redirect(url_for('main.index_rus'))    

# ===========================       SAVING DATA         ====================

# =======================           UPDATE CODE untuk ERROR HANDLE, AFFECTED: FINALRESULT + [SAVE] ==============================================   

# @app.route('/save', methods=['POST'])
@main.route('/save-history', methods=['POST'])
def save_data():
    try:
        airline = request.form['airline']
        sentiment = request.form['sentiment']
        review = request.form['review']
            
        if not airline or not review:
            flash('Please fill out all required fields!', 'error')
            return redirect(url_for('history'))

        review = ReviewSavedHistory(airline=airline, sentiment=sentiment, 
                        description=review, date=datetime.utcnow())
        db.session.add(review)
        db.session.commit()

        flash('Data saved successfully!', 'success')
        return redirect(url_for('main.history'))
    
    except sqlite3.Error as e:
        app.logger.error(f"Database error: {str(e)}")
        flash('Database error occurred. Please try again later.', 'error')
        return redirect(url_for('history'))
    except Exception as e:
        app.logger.error(f"Unexpected error: {str(e)}")
        flash('Oops! Something went wrong. Please try again.', 'error')
        return redirect(url_for('history'))
    

# @main.route('/history', methods=['GET','POST'])
# def history():
#     rows = Review.query.order_by(Review.date.asc()).all()
#     return render_template('history.html', submissions=rows)


@main.route('/history', methods=['GET', 'POST'])
def history():
    filter_airline = request.args.get('filter_airline', '').lower()
    if filter_airline:
        rows = ReviewSavedHistory.query.filter(ReviewSavedHistory.airline.ilike(f"%{filter_airline}%")).order_by(ReviewSavedHistory.date.asc()).all()
    else:
        rows = ReviewSavedHistory.query.order_by(ReviewSavedHistory.date.asc()).all()
    
    return render_template('history.html', submissions=rows)


@main.route('/delete_review/<int:review_id>', methods=['POST'])
def delete_review(review_id):
    review = ReviewSavedHistory.query.get(review_id)
    if review:
        db.session.delete(review)
        db.session.commit()
        flash(f'Review ID {review_id} deleted successfully!', 'success')
    else:
        flash(f'Review ID {review_id} not found.', 'error')
    return redirect(url_for('main.history'))

# =========================    TEST TIMELINE untuk Data Visualization di page history.html / Saving history    ==================================      
@main.route('/timeline')
def timeline():
    image_base64 = generate_timeline_visualization()
    review_counts = get_review_counts_by_airline()

    return render_template('timeline.html', image=image_base64, review_counts=review_counts)

# =============================================    ==================================      
# =============================================  DETAIL TIMELINE VISUALIZATION (6 GAMBAR data visual)    ==================================      
# @app.route('/timeline/<airline>')
@main.route('/timeline/<airline>')
def airline_timeline(airline):
    # Ambil tahun, periode, dan kuartal yang dipilih dari query parameter
    selected_year = request.args.get('year', type=int)
    selected_period = request.args.get('period')
    selected_quarter = request.args.get('quarter')
    start_month = request.args.get('start_month')  # Tambahkan parameter baru
    end_month = request.args.get('end_month')      # Tambahkan parameter baru
    
    # Ambil daftar tahun yang tersedia dari database
    available_years = db.session.query(
        extract('year', ReviewFull.date_flown).label('year')
    ).filter(ReviewFull.airline == airline).distinct().order_by(text('year DESC')).all()

    available_years = [int(year.year) for year in available_years if year.year]
    
    # Jika tidak ada tahun yang tersedia, tambahkan tahun default (2022, 2023, 2024, 2025)
    if not available_years:
        available_years = [2021, 2022, 2023, 2024, 2025]
    
    # Jika tahun, periode, atau kuartal tidak dipilih, tampilkan form tanpa grafik
    if not selected_year or not selected_period or not selected_quarter:
        return render_template('airline_timeline.html', airline=airline, available_years=available_years)
    
    # Panggil fungsi visualisasi untuk airline tertentu
    plots = generate_airline_specific_visualization(airline, selected_year, selected_period, selected_quarter,
                                                    start_month, end_month)
    
    if plots is None:
        flash(f"No data found for airline: {airline}", "error")
        return redirect(url_for('main.history'))
    
    period_label_map = {
        "jan-apr": "Januari - April",
        "may-aug": "May - August",
        "sep-dec": "September -  Desember",
    }
    quarter_label_map = {
        "q1": "Kuartal 1",
        "q2": "Kuartal 2",
        "q3": "Kuartal 3",
        "q4": "Kuartal 4"
    }
    
    selected_period_label = period_label_map.get(selected_period, "Unknown Period")
    selected_quarter_label = quarter_label_map.get(selected_quarter, "Unknown Quarter")
    
    return render_template(
        'airline_timeline.html',
        plots=plots,
        airline=airline,
        available_years=available_years,
        selected_year=selected_year,
        selected_period=selected_period,
        selected_quarter=selected_quarter,
        selected_period_label=selected_period_label,
        selected_quarter_label=selected_quarter_label,
        start_month=start_month,
        end_month=end_month)

# ======================    Rules & About us    ======================      
# @app.route('/rules', methods=['POST'])
@main.route('/rules', methods=['POST'])
def rules():
    if request.method == 'POST':
        return render_template('rules.html')     # redirect(url_for('rules'))
    

# @app.route('/aboutUs', methods=['POST'])
@main.route('/aboutUs', methods=['POST'])
def aboutUs():
    if request.method == 'POST':
        return render_template('aboutUs.html')     #redirect(url_for('aboutUs')) 
    
# ======================    Rules & About us    ======================      

# ======================    here below is everythin about save chart     ======================      
@main.route('/save_chart', methods=['POST'])
def save_chart():
    chart_name = request.form['chart_name']
    airline = request.form['airline']
    sentiment = request.form['sentiment']
    chart_type = request.form['chart_type']
    image_data = request.form['image_data']  # base64 string dikirim dari form

    new_chart = SavedChart(
        chart_name=chart_name,
        airline=airline,
        sentiment=sentiment,
        chart_type=chart_type,
        image_data=image_data
    )
    db.session.add(new_chart)
    db.session.commit()

    return redirect(url_for('main.view_saved_charts'))

@main.route('/view-saved-charts')  # for view the saved charts  
def view_saved_charts():
    # saved_charts = SavedChart.query.order_by(SavedChart.generated_on.desc()).all()
    saved_charts = SavedChart.query.order_by(SavedChart.id).all()
    return render_template('view_saved_charts.html', saved_charts=saved_charts)

@main.route('/delete-chart/<int:chart_id>', methods=['POST'])
def delete_chart(chart_id):
    chart_to_delete = SavedChart.query.get_or_404(chart_id)
    db.session.delete(chart_to_delete)
    db.session.commit()
    flash(f"Chart ID {chart_id} berhasil dihapus.", 'success')
    return redirect(url_for('main.view_saved_charts'))


# ===================  here below is everything about Timeline Visualization in detail (6 gambar data visual)    ==========================
@main.route('/save_detailed_visualization', methods=['POST'])
def save_detailed_visualization():
    airline = request.form['airline']
    name = request.form['name_of_visualization']
    image_data = request.form['image_data']  # base64
    saved_at = datetime.utcnow()

    vis = DetailedVisualization(
        airline=airline,
        name_of_visualization=name,
        image_data=image_data,
        saved_at=saved_at
    )
    db.session.add(vis)
    db.session.commit()

    flash(f"Visualization '{name}' berhasil disimpan!", 'success')
    return redirect(request.referrer)

@main.route('/view_detailed_visualizations')
def view_detailed_visualizations():
    visualizations = DetailedVisualization.query.order_by(DetailedVisualization.id).all()
    return render_template('view_detailed_visualizations.html', visualizations=visualizations)


@main.route('/delete_detailed_visualization/<int:viz_id>', methods=['POST'])
def delete_detailed_visualization(viz_id):
    viz = DetailedVisualization.query.get_or_404(viz_id)
    db.session.delete(viz)
    db.session.commit()
    flash('Visualization deleted successfully!', 'success')
    return redirect(url_for('main.view_detailed_visualizations'))

