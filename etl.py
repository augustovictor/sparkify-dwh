import configparser
import psycopg2
from sql_queries import copy_table_queries, insert_table_queries


def load_staging_tables(cur, conn):
    """
    Copies data from S3 to staging tables
    """

    for query in copy_table_queries:
        cur.execute(query)
        conn.commit()


def insert_tables(cur, conn):
    """
    Loads data from staging tables into final tables (facts table and dimensions tables)
    """

    for query in insert_table_queries:
        cur.execute(query)
        conn.commit()


def main():
    """
    Reads dwh.cfg config file
    Creates a connection with database
    Executes command to load staging tables
    Executes command to load data into final tables
    Closes connection with database 
    """

    config = configparser.ConfigParser()
    config.read('dwh.cfg')

    conn = psycopg2.connect("host={} dbname={} user={} password={} port={}".format(*config['CLUSTER'].values()))
    cur = conn.cursor()
    
    load_staging_tables(cur, conn)
    insert_tables(cur, conn)

    conn.close()


if __name__ == "__main__":
    main()