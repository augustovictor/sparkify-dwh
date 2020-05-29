import configparser


# CONFIG
config = configparser.ConfigParser()
config.read('dwh.cfg')

# DROP TABLES

staging_events_table_drop = "DROP TABLE IF EXISTS staging_events_table"
staging_songs_table_drop = "DROP TABLE IF EXISTS staging_songs_table"
songplay_table_drop = "DROP TABLE IF EXISTS songplay_table"
user_table_drop = "DROP TABLE IF EXISTS user_table"
song_table_drop = "DROP TABLE IF EXISTS song_table"
artist_table_drop = "DROP TABLE IF EXISTS artist_table"
time_table_drop = "DROP TABLE IF EXISTS time_table"

# CREATE TABLES

staging_events_table_create= ("""
CREATE TABLE IF NOT EXISTS staging_events_table (
    songplay_id BIGINT IDENTITY(0, 1),
    artist VARCHAR(255),
    auth VARCHAR(255),
    first_name VARCHAR(255),
    gender CHAR,
    item_in_session INTEGER,
    last_name VARCHAR(255),
    length DECIMAL(11, 5),
    level VARCHAR(10),
    location VARCHAR(255),
    method VARCHAR(20),
    page VARCHAR(100),
    registration DECIMAL(18, 3),
    session_id INTEGER,
    song VARCHAR,
    status INTEGER,
    ts BIGINT,
    user_agent VARCHAR,
    user_id VARCHAR(255)
)
BACKUP NO
""")

staging_songs_table_create = ("""
CREATE TABLE IF NOT EXISTS staging_songs_table (
    artist_id VARCHAR(100),
    artist_latitude VARCHAR(100),
    artist_location VARCHAR(100),
    artist_longitude VARCHAR(100),
    artist_name VARCHAR(255),
    duration DECIMAL(11, 6),
    num_songs VARCHAR(100),
    song_id VARCHAR(100),
    title VARCHAR(255),
    year SMALLINT
)
BACKUP NO
""")

songplay_table_create = ("""
CREATE TABLE IF NOT EXISTS songplay_table (
    songplay_id BIGINT IDENTITY(0, 1) PRIMARY KEY,
    start_time DATE SORTKEY,
    user_id VARCHAR(80) REFERENCES user_table(user_id),
    level VARCHAR(100),
    song_id VARCHAR(90) REFERENCES song_table(song_id),
    artist_id VARCHAR(80) REFERENCES artist_table(artist_id),
    session_id VARCHAR(70),
    location VARCHAR(255),
    user_agent VARCHAR
)
BACKUP NO
DISTSTYLE EVEN
""")

user_table_create = ("""
CREATE TABLE IF NOT EXISTS user_table (
    user_id VARCHAR(80) PRIMARY KEY,
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    gender CHAR,
    level VARCHAR(100)
) BACKUP NO DISTSTYLE ALL COMPOUND SORTKEY(user_id, first_name)
""")

song_table_create = ("""
CREATE TABLE IF NOT EXISTS song_table (
    song_id VARCHAR(80) PRIMARY KEY,
    title VARCHAR(255),
    artist_id VARCHAR(100) REFERENCES artist_table(artist_id),
    year SMALLINT,
    duration DECIMAL(11, 5)
) BACKUP NO DISTSTYLE ALL COMPOUND SORTKEY(song_id, title)
""")

artist_table_create = ("""
CREATE TABLE IF NOT EXISTS artist_table (
    artist_id VARCHAR(80) PRIMARY KEY,
    name VARCHAR(255),
    location VARCHAR(100),
    lattitude VARCHAR(100),
    longitude VARCHAR(100)
) BACKUP NO DISTSTYLE ALL COMPOUND SORTKEY(artist_id, name)
""")

time_table_create = ("""
CREATE TABLE IF NOT EXISTS time_table (
    time_key BIGINT IDENTITY(0, 1),
    start_time DATE SORTKEY,
    hour SMALLINT,
    day SMALLINT,
    week SMALLINT,
    month SMALLINT,
    year SMALLINT,
    weekday SMALLINT) BACKUP NO DISTSTYLE ALL
""")

# STAGING TABLES

staging_events_copy = ("""
COPY staging_events_table FROM {} CREDENTIALS {} json {} REGION {}
""").format(config['S3']['LOG_DATA'], config['IAM_ROLE']['ARN'], config['S3']['LOG_JSONPATH'], config['AWS']['REGION'])

staging_songs_copy = ("""
COPY staging_songs_table FROM {} CREDENTIALS {} json 'auto' REGION {}
""").format(config['S3']['SONG_DATA'], config['IAM_ROLE']['ARN'], config['AWS']['REGION'])

# FINAL TABLES
# length, song, artist
songplay_table_insert = ("""
INSERT INTO songplay_table (
    start_time,
    user_id,
    level,
    song_id,
    artist_id,
    session_id,
    location,
    user_agent
)
(
    SELECT
        TIMESTAMP 'epoch' + se.ts/1000 * INTERVAL '1 second' AS start_time,
        se.user_id as user_id,
        se.level as level,
        s.song_id as song_id,
        a.artist_id as artist_id,
        se.session_id as session_id,
        a.location as location,
        se.user_agent as user_agent
    FROM staging_events_table se
    JOIN artist_table a ON (a.name = se.artist)
    JOIN song_table s ON (s.title = se.song AND s.duration = se.length)
)
""")

user_table_insert = ("""
INSERT INTO user_table (
    user_id,
    first_name,
    last_name,
    gender,
    level
)
(
    SELECT
        se.user_id AS user_id,
        se.first_name AS first_name,
        se.last_name AS last_name,
        se.gender AS gender,
        se.level AS level
    FROM staging_events_table se
    WHERE se.user_id IS NOT NULL
)
""")

song_table_insert = ("""
INSERT INTO song_table (
    song_id,
    title,
    artist_id,
    year,
    duration
)
(
    SELECT
        ss.song_id AS song_id,
        ss.title AS title,
        ss.artist_id AS artist_id,
        ss.year AS year,
        ss.duration AS duration
    FROM staging_songs_table ss
    WHERE song_id IS NOT NULL
    AND title IS NOT NULL
    AND duration IS NOT NULL
)
""")

artist_table_insert = ("""
INSERT INTO artist_table (
    artist_id,
    name,
    location,
    lattitude,
    longitude
)
(
    SELECT
        ss.artist_id AS artist_id,
        ss.artist_name AS name,
        ss.artist_location AS location,
        ss.artist_latitude AS latitude,
        ss.artist_longitude AS longitude
    FROM staging_songs_table ss
    WHERE artist_id IS NOT NULL
)
""")

time_table_insert = ("""
INSERT INTO time_table (
    start_time,
    hour,
    day,
    week,
    month,
    year,
    weekday
)
(
    SELECT
        TIMESTAMP 'epoch' + se.ts/1000 * INTERVAL '1 second' AS start_time,
        EXTRACT(hour FROM start_time) AS hour,
        EXTRACT(day FROM start_time) AS day,
        EXTRACT(week FROM start_time) AS week,
        EXTRACT(month FROM start_time) AS month,
        EXTRACT(year FROM start_time) AS year,
        EXTRACT(weekday FROM start_time) AS weekday
    FROM staging_events_table se
    WHERE se.ts IS NOT NULL
)
""")

# QUERY LISTS

create_table_queries = [staging_events_table_create, staging_songs_table_create, user_table_create, artist_table_create, song_table_create, time_table_create, songplay_table_create]
drop_table_queries = [staging_events_table_drop, staging_songs_table_drop, songplay_table_drop, user_table_drop, song_table_drop, artist_table_drop, time_table_drop]
copy_table_queries = [staging_events_copy, staging_songs_copy]
insert_table_queries = [user_table_insert, song_table_insert, artist_table_insert, time_table_insert, songplay_table_insert]
