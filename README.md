# sparkify-cloud-analytics

### Business Requirements

#### Analytical requirements

---

### Technical requirements

#### Database choice
The OLAP database choice is the colunar database Redshift. This type of database allows us to have a denormalized schema, thus speeding up OLAP operations.

#### Facts and Dimensions tables design (Physical data model)

Facts table design:

Our fact table is `songplays` and the business event metric we're tracking is `start_time`, which is a semi-additive fact since it would not make sense to SUM all `start_time` values. However, getting the AVG, MIN, or MAX would give us some useful data to analyze.
asd
The type of `songplays` fact table is `Transactional` as each record represents one event at a single instant.


- Business process: Song play
- Grain: Each record represents the moment that a song started playing
- Dimensions: This fact table associates with the following dimensions: User, Song, Artist, Time;
- Facts: start_time

#### DDL, DML, DQL

- Data Definition Language file: sql_queries.py
- Data Modeling Language file: sql_queries.py
- Data Query Language file: sql_queries.py

#### Distribution key strategies
TODO: Organize order of primary key attributes in DDL, DML and DQL;
EVEN, ALL, AUTO, KEY

#### Sorting keys strategies

#### Available data
We have `log_data` which contains business events from sparkify app, and `song_data` with music metadata.

`log_data` example:
```json
{
    "artist": null,
    "auth": "Logged In",
    "firstName": "Walter",
    "gender": "M",
    "itemInSession": 0,
    "lastName": "Frye",
    "length": null,
    "level": "free",
    "location": "San Francisco-Oakland-Hayward, CA",
    "method": "GET",
    "page": "Home",
    "registration": 1540919166796.0,
    "sessionId": 38,
    "song": null,
    "status": 200,
    "ts": 1541105830796,
    "userAgent": "\"Mozilla\/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit\/537.36 (KHTML, like Gecko) Chrome\/36.0.1985.143 Safari\/537.36\"",
    "userId": "39"
}
```

`song_data` example:
```json
{
    "artist_id": "ARJNIUY12298900C91",
    "artist_latitude": null,
    "artist_location": "",
    "artist_longitude": null,
    "artist_name": "Adelitas Way",
    "duration": 213.9424,
    "num_songs": 1,
    "song_id": "SOBLFFE12AF72AA5BA",
    "title": "Scream",
    "year": 2009
}
```

#### DW architecture

Kimball's Bus X Independent Data Marts X Inmon's Corporate Information Factory X Hybrid Kimball's Bus and Imon's CIF (Using this)

Staging area

#### Server sizing and capacity planning

#### Data quality check

---

## Execution

### Creation of facts and dimensions tables (Physical model)

### ETL to S3

### ETL from S3 to Redshift (DW)

## Redshift config
- IAM user: Create an IAM user with permissions
- Security group: 

## Heads up
When performing the `COPY` command from a S3 bucket into a redshift table, and there is no match between the json attribute names and column names, we should use a jsonpath file. The jsonpath file should be declared in the same order the attributes are set in `CREATE TABLE` statement. The order of attributes in `json` data does not make difference. When the columns and attributes have the same name, we can use `json 'auto'` in `COPY` command.

log_json_path.json
```json
{
    "jsonpaths": [
        "$['artist']",
        "$['auth']",
        "$['firstName']",
        "$['gender']",
        "$['itemInSession']",
        "$['lastName']",
        "$['length']",
        "$['level']",
        "$['location']",
        "$['method']",
        "$['page']",
        "$['registration']",
        "$['sessionId']",
        "$['song']",
        "$['status']",
        "$['ts']",
        "$['userAgent']",
        "$['userId']"
    ]
}
```
maps to:
```sql
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
    page VARCHAR(50),
    registration DECIMAL(18, 3),
    session_id INTEGER,
    song VARCHAR,
    status INTEGER,
    ts BIGINT,
    user_agent VARCHAR,
    user_id VARCHAR(255)
)
```

### Insertion order on tables
The first two tables to be loaded were staging_events_table and staging_songs_table, then I analyzed which attributes from final tables were required to our analysis. The ETL from stagin tables into final tables should consider data that would be meaningful only.

- staging_events_table
- staging_songs_table
- user_table
- song_table
- time_table:
```sql
INSERT INTO dimDate (date_key, date, year, quarter, month, day, week, is_weekend)
SELECT DISTINCT(TO_CHAR(payment_date :: DATE, 'yyyyMMDD')::integer) AS date_key,
       date(payment_date)                                           AS date,
       EXTRACT(year FROM payment_date)                              AS year,
       EXTRACT(quarter FROM payment_date)                           AS quarter,
       EXTRACT(month FROM payment_date)                             AS month,
       EXTRACT(day FROM payment_date)                               AS day,
       EXTRACT(week FROM payment_date)                              AS week,
       CASE WHEN EXTRACT(ISODOW FROM payment_date) IN (6, 7) THEN true ELSE false END AS is_weekend
FROM payment;
```
- 

### AWS CLI
Upload files to s3:
```shell
aws-vault exec sparkify-dw -- aws s3 cp log_data s3://victor-nano-sparkify-raw-data/log_data --recursive
```

---

## References

- https://www.zentut.com/data-warehouse/fact-table/
- https://dwgeek.com/types-of-fact-tables-data-warehouse.html/
- http://www.datamartist.com/dimensional-tables-and-fact-tables
