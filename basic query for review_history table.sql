SELECT * FROM review_saved_history
SELECT * FROM review_full
select * from detailed_visualizations
SELECT * FROM saved_charts;

-- to get the data which is how many airline we have
select distinct airline from review_history

SELECT * FROM review where airline = 'Singapore Airlines'
SELECT * FROM review_history where airline = 'Singapore Airlines'
SELECT * FROM saved_charts where id =1

SELECT * FROM review LIMIT 10;

-- MENGHAPUS DATA yg sama, eg: data philippine airlines ada triple sama, maka gw menghapus semua data nya 
-- dan menyisakannya menjadi 1 row data saja 
DELETE FROM review
WHERE ctid IN (
    SELECT ctid
    FROM review
    WHERE airline = 'Philippine Airlines'
      AND sentiment = 'Positive'
      AND description = 'Flew Brisbane to Manila with Philippine Airlines. Flight was in 2 legs because of stop in Darwin to refuel. Good to be able to stretch your legs in the Darwin departure area but no business lounge access. A320 which did not have space for top-standard long-haul seats but was, nevertheless, reasonably comfortable. Lunch served on the first leg and dinner on the second - good standard. Service was very friendly.'
    ORDER BY ctid
    OFFSET 1
);


-- !! HATI2 !! MENGHAPUS semua Data di table ini
DELETE FROM review_history;

-- untuk melihat/mengecek apakah ada value yg kosong didalam column "date_flown" 
-- SELECT * FROM review_history WHERE date_flown IS NULL OR TRIM(date_flown) = '[null]';

-- Reset ID auto increment:
ALTER SEQUENCE review_history_id_seq RESTART WITH 1;


ALTER TABLE review RENAME TO review_saved_history;
ALTER TABLE review_history RENAME TO review_full;


-- HAPUS TABLE  review_history
delete from saved_charts;
delete from review_analysis_links
DROP TABLE IF EXISTS review_history;
DROP TABLE IF EXISTS review_analysis_links;


ALTER TABLE saved_charts ADD COLUMN image_data TEXT;


-- untuk mengecek berapa banyak value [null] didalam COLUMN date_flown
SELECT COUNT(*) AS jumlah_null
FROM review_history
WHERE date_flown IS NULL;

 -- berapa persen data yang null dari total:
 SELECT 
  COUNT(*) FILTER (WHERE date_flown IS NULL) AS jumlah_null,
  COUNT(*) AS total_data,
  ROUND(100.0 * COUNT(*) FILTER (WHERE date_flown IS NULL) / COUNT(*), 2) AS persen_null
FROM review_history;


-- SELECT column_name, data_type
-- FROM information_schema.columns
-- WHERE table_name = 'review_history';

-- Table: review_history
CREATE TABLE review_history (
    id SERIAL PRIMARY KEY,
    airline VARCHAR(100),
    sentiment VARCHAR(20),
    review TEXT,
    date_flown TIMESTAMP WITHOUT TIME ZONE
);


-- Table: saved_charts
CREATE TABLE saved_charts (
    id SERIAL PRIMARY KEY,
    chart_name VARCHAR(100) NOT NULL,
    airline VARCHAR(100) NOT NULL,
    sentiment VARCHAR(20) NOT NULL,
    chart_type VARCHAR(50) NOT NULL,
    generated_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    image_path TEXT
);

-- Table: review_analysis_links
CREATE TABLE review_analysis_links (
    id SERIAL PRIMARY KEY,
    airline VARCHAR(100) NOT NULL,
    sentiment VARCHAR(20) NOT NULL,
    analysis_url TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE detailed_visualizations (
    id SERIAL PRIMARY KEY,
    airline VARCHAR(100),
    name_of_visualization TEXT,
    saved_at TIMESTAMP,
    image_data TEXT
);

