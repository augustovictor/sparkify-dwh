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
    songplay_id IDENTITY(0, 1),
    start_time INTEGER,
    user_id INTEGER,
    level VARCHAR(20),
    song_id INTEGER,
    artist_id INTEGER,
    session_id INTEGER,
    location VARCHAR(255),
    user_agent VARCHAR
)
""")

staging_songs_table_create = ("""
CREATE TABLE IF NOT EXISTS staging_songs_table (
    song_id VARCHAR(80),
    title VARCHAR(255),
    artist_id INTEGER,
    year SMALLINT(4),
    duration INTEGER
)
""")

songplay_table_create = ("""
CREATE TABLE IF NOT EXISTS songplay_table (
    songplay_id IDENTITY(0, 1),
    start_time INTEGER,
    user_id INTEGER,
    level VARCHAR(20),
    song_id INTEGER,
    artist_id INTEGER,
    session_id INTEGER,
    location VARCHAR(255),
    user_agent VARCHAR
)
""")

user_table_create = ("""
CREATE TABLE IF NOT EXISTS user_table (
    user_id VARCHAR(80),
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    gender CHAR,
    level VARCHAR(20)
)
""")

song_table_create = ("""
CREATE TABLE IF NOT EXISTS song_table (
    song_id VARCHAR(80),
    title VARCHAR(255),
    artist_id INTEGER,
    year SMALLINT(4),
    duration INTEGER
)
""")

artist_table_create = ("""
CREATE TABLE IF NOT EXISTS artist_table (
    artist_id VARCHAR(80),
    name VARCHAR(255),
    location VARCHAR(20),
    lattitude VARCHAR(20),
    longitude VARCHAR(20)
)
""")

time_table_create = ("""
CREATE TABLE IF NOT EXISTS time_table (
    start_time DATETIME,
    hour SMALLINT(2),
    day SMALLINT(2),
    week SMALLINT(2),
    month SMALLINT(2),
    year SMALLINT(4),
    weekday SMALLINT(1)
)
""")

# STAGING TABLES

staging_events_copy = ("""
COPY staging_events_table FROM '%s' CREDENTIALS 'aws_iam_role=arn:aws:iam::%s:role/%s' REGION '%s'
""").format(config['S3']['LOG_DATA'], config['AWS']['ACC_NUMBER'], config['AWS']['ROLE_NAME'], config['AWS']['REGION'])

staging_songs_copy = ("""
COPY staging_songs_table FROM '%s' CREDENTIALS 'aws_iam_role=arn:aws:iam::%s:role/%s' REGION '%s'
""").format(config['S3']['SONG_DATA'], config['AWS']['ACC_NUMBER'], config['AWS']['ROLE_NAME'], config['AWS']['REGION'])

# FINAL TABLES

songplay_table_insert = ("""
INSERT INTO songplay_table (
    songplay_id,
    start_time,
    user_id,
    level,
    song_id,
    artist_id,
    session_id,
    location,
    user_agent,
)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
""")

user_table_insert = ("""
INSERT INTO user_table (
    user_id,
    first_name,
    last_name,
    gender,
    level
)
VALUES (%s,%s,%s,%s,%s)
""")

song_table_insert = ("""
INSERT INTO song_table (
    song_id,
    title,
    artist_id,
    year,
    duration
)
VALUES (%s,%s,%s,%s,%s)
""")

artist_table_insert = ("""
INSERT INTO artist_table (
    artist_id,
    name,
    location,
    lattitude,
    longitude,
)
VALUES (%s,%s,%s,%s,%s)
""")

time_table_insert = ("""
INSERT INTO time_table (
    start_time,
    hour,
    day,
    week,
    month,
    year,
    weekday,
)
VALUES (%s,%s,%s,%s,%s,%s,%s)
""")

# QUERY LISTS

create_table_queries = [staging_events_table_create, staging_songs_table_create, songplay_table_create, user_table_create, song_table_create, artist_table_create, time_table_create]
drop_table_queries = [staging_events_table_drop, staging_songs_table_drop, songplay_table_drop, user_table_drop, song_table_drop, artist_table_drop, time_table_drop]
copy_table_queries = [staging_events_copy, staging_songs_copy]
insert_table_queries = [songplay_table_insert, user_table_insert, song_table_insert, artist_table_insert, time_table_insert]
