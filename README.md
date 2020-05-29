# sparkify-cloud-analytics

### Business Requirements

#### Analytical requirements

Analytics team wants to answer the following questions:

Question 1: How many plays each artist have?
OLAP Cube operation: Rollup
> A rollup operation is a higher level of aggregation to a larger grouping

Question 2: How many plays each artist have in each music?
OLAP Cube operation: Drill-down
> A drill-down operation is a detailed level on one dimension

Question 3: Which users have listened to the song 'All Hands Against His Own', and when?
OLAP Cube operation: Slice
> A slice operation is a filtering on dimensions when one of them has a fixed filtering value
```sql
SELECT artist, song, length FROM song_table WHERE session_id = 338 AND item_in_session = 4;
SELECT a.name, s.title, u.user_id, u.level, CONCAT(u.first_name, CONCAT(' ', u.last_name)) as user_name
FROM songplay_table sp
JOIN artist_table a ON (a.artist_id = sp.artist_id)
JOIN song_table s ON (s.song_id = sp.song_id)
JOIN user_table u ON (u.user_id = sp.user_id)
WHERE session_id = 338;
```

Question 4: How many users have listened to 'All Hands Against His Own', 'Get Into Yours', and 'Like A Rolling Stone' between '2018-11-01' and '2018-11-30'?
OLAP Cube operation: Dice
> A dice operation is a filtering on all dimensions with specific values/ranges

---

### Technical requirements

#### Database choice
The OLAP database choice is the colunar database Redshift. This type of database allows us to have a denormalized schema, thus speeding up OLAP operations.

#### Facts and Dimensions tables design (Physical data model)

Facts table design:

Our fact table is `songplays` and the business event metric we're tracking is `start_time`, which is a semi-additive fact since it would not make sense to run all types of aggregation on it. Ex: SUM all `start_time` values. However, getting the AVG, MIN, or MAX would give us some useful data to analyze.

The type of the fact table `songplays` is `Transactional` as each record represents one event at a single instant.

Fact table design process:
- Define a Business process: Song play
- Define the grain: Each record represents the moment that a song started playing
- Define the dimensions: This fact table associates with the following dimensions: User, Song, Artist, Time;
- Define the Facts: start_time

#### DDL, DML, DQL files

- Data Definition Language file: sql_queries.py
- Data Modeling Language file: sql_queries.py
- Data Query Language file: sql_queries.py

#### Distribution and Sorting key strategies
The dimension tables distribution key strategy chosen was `ALL` since they are small dimension tables;

However, the distribution key strategy for the facts table `songplays` was `EVEN`, since we have a lot more data and due to the `ALL` distribution key strategy of dimension tables, no `JOIN SHUFFLING` operations would be performed; The facts table's `SORTKEY` is `start_time` as it would be used to order the results, and present them in a chronological order;

Our type of queries do not envolve analyzing most recent data only. Although the `SORTKEY` for the facts table `songplay` is `start_time` this is not its main reason.
> Aws doc: Queries are more efficient because they can skip entire blocks that fall outside the time range

Our queries are more about ranges of `start_time` values.

#### Raw data
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

As we're providing an analytical base in atomic level with the staging tables, and the final fact table focused on the business process of music listening, which by exclusion is not focused on a specific department, the architectur of this Data Warehouse is the Hybrid Kimball's Bus and Imon's Corporate Information Factory (CIF).

- The Data Aquisition phase was performed by copying data from S3  into staging tables
- Staging tables are part of our Enterprise DW, with data in atomic level, in case any department needs it;
- The Data Delivery phase was performed by DML queries copying data from staging tables and filtering information that was compliant to our quality checks;
- The final tables are part of our final Enterprise DW bus in which applications can be plugged into. Ex: Data visualization applications, and BI applications.

Staging area

#### Server sizing and capacity planning

#### Data quality check
There was no quality check performed during Data Aquisition phase, since we wanted to have our Enterprise DW with atomic level data;

During Delivery Phase some attributes were filtered to ensure no NULL values that would affect analytical queries.

---

## Execution

### Creation of staging, facts, and dimensions tables (Physical model)
Our staging tables are:
- staging_events_table
- staging_songs_table

Our dimension tables are:
- user_table
- song_table
- artist_table
- time_table

Our fact tables are:
- songplay_table

### ETL to S3
Data was already loaded into s3

### ETL from S3 into Redshift (DW)
S3 data was loaded into Redshift staging tables through `COPY` command. Also, because the attributes from `log_data` files did not have an exact match between its schema and `staging_events_table` table in Redshift, we needded to use a `jsonpath` file to map one schema to the other;

When performing the `COPY` command from a S3 bucket into a redshift table, and there is no match between the json attribute names and column names, we should use a `jsonpath` file. The `jsonpath` file should be declared in the same order the attributes are set in `CREATE TABLE` statement. The order of attributes in `json` data does not make difference. When the columns and attributes have the same name, we can use `json 'auto'` in `COPY` command.

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

## Redshift config
- IAM user: Create an IAM user with permissions;
- Security group with inbound rule set to `My Ip` so it was possible to run python scripts locally;
- Redshift cluster with 1 node and backup retentio period of 1 day (required to allow me to pause the cluster)

### Informative errors section:

Errors regarding information loading can be found at Redshift's `stl_load_errors` table:
```sql
-- insertion
select * from stl_load_errors ORDER BY starttime DESC LIMIT 5;
```

When marking an attribute as `DISTKEY` we're setting this table to have a distribution key strategy of DISTKEY, thus we cannot set table's attribute `DISTSTYLE` neither to `NONE` nor `ALL`
```sql
-- ddl
Cannot specify DISTKEY for column "user_id" of table "user_table" when DISTSTYLE is NONE or EVEN
```

### AWS CLI
Helper command I used to Upload files to s3:
```shell
aws-vault exec sparkify-dw -- aws s3 cp log_data s3://victor-nano-sparkify-raw-data/log_data --recursive
```

Add new aws cli profile:
```shell
aws cli configure <PROFILE_NAME>
```

Command with specific profile:
```shell
aws cli --profile <PROFILE_NAME> <COMMAND>
```

Use specific profile in current session:
```shell
export AWS_PROFILE=<PROFILE_NAME>
```

---

## References

- https://www.zentut.com/data-warehouse/fact-table/
- https://dwgeek.com/types-of-fact-tables-data-warehouse.html/
- http://www.datamartist.com/dimensional-tables-and-fact-tables
- https://docs.aws.amazon.com/pt_br/redshift/latest/dg/r_Dateparts_for_datetime_functions.html
- https://docs.aws.amazon.com/pt_br/redshift/latest/dg/r_CREATE_TABLE_examples.html
- https://medium.com/@elliotchance/building-a-date-dimension-table-in-redshift-6474a7130658
- https://docs.aws.amazon.com/redshift/latest/dg/c_best-practices-sort-key.html
- https://hevodata.com/blog/redshift-sort-keys-choosing-best-sort-style/
- https://stackoverflow.com/questions/58513886/why-does-this-redshift-create-table-query-with-distkey-and-diststyle-not-work
- https://docs.aws.amazon.com/pt_br/redshift/latest/dg/r_STL_LOAD_ERRORS.html

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
