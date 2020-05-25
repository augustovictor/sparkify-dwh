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
EVEN, ALL, AUTO, KEY

#### Sorting keys strategies


#### DW architecture

Kimball's Bus X Independent Data Marts X Inmon's Corporate Information Factory X Hybrid Kimball's Bus and Imon's CIF

Staging area

#### Server sizing and capacity planning

#### Data quality check

---

## Execution

### Creation of facts and dimensions tables (Physical model)

### ETL to S3

### ETL from S3 to Redshift (DW)

---

## References

- https://www.zentut.com/data-warehouse/fact-table/
- https://dwgeek.com/types-of-fact-tables-data-warehouse.html/
- http://www.datamartist.com/dimensional-tables-and-fact-tables