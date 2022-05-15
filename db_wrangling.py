"""
Main module for database functions, including connection querying, inserting etc.
"""

import csv
from configparser import ConfigParser
from mimetypes import init
from typing import Optional

import psycopg2  # type: ignore
from psycopg2 import Error  # type: ignore


def read_config(filename: str = "database.ini", section: str = "postgresql") -> dict:
    """
    reads the database.ini configuration file for database connection and returns a
    dictionary of the connection configurationd details.
    """
    # create a parser
    parser = ConfigParser()
    # read config file
    parser.read(filename)

    # get section, default to postgresql
    _db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            _db[param[0]] = param[1]
    else:
        raise Exception(f"Section {section} not found in the {filename} file")

    return _db


def connect(params: dict) -> psycopg2.extensions.connection:
    """
    creates a connection to the database.
    IMPORTANT: Does not automatically close the database connection. This should
    be handled by subsequent db tools (query, insert, create etc) or by calling the close
    method of the DataBase class.
    """
    _conn = None
    try:
        # read connection parameters
        params = read_config()
        # connect to the PostgreSQL server
        _conn = psycopg2.connect(**params)
        return _conn
    except (Exception, Error) as error:
        print("Error while connecting to PostgreSQL", error)
        return error


class DataBase:
    """
    Main database class that handles all querying, inserting, etc
    """

    def __init__(self, _conn: psycopg2.extensions.connection) -> None:
        self.init = init
        self._conn = _conn
        self.cursor = _conn.cursor()

    def print_tables(self):
        """
        prints all tables from active connection
        """
        self.cursor.execute(
            """
        SELECT table_name FROM information_schema.tables
        WHERE table_schema = 'public'
        """
        )
        for table in self.cursor.fetchall():
            print(table)

    def query(self, query: Optional[str] = None) -> None:
        """
        runs and prints a given SQL query on the provided database connection
        """
        try:
            self.cursor.execute(query)
            results = self.cursor.fetchall()
            print(results)

        except (Exception, Error) as error:
            print("Error while connecting to PostgreSQL", error)
        finally:
            if conn:
                self.cursor.close()
                conn.close()
                print("PostgreSQL connection is closed")

    def close(self):
        """
        Manually closes the database connection. Not typically required as closing should
        be handled by any querying/inserting/creating etc method.
        """
        try:
            self.cursor.close()
            conn.close()
            print("PostgreSQL connection is closed")
        except (Exception, Error) as error:
            print("Error while connecting to PostgreSQL", error)

    def copy_from_csv(self, search_term: str, news_source: str, table: str) -> None:
        """
        Writing a saved csv file to database using copy_from()
        """
        csv_dir = f"scraping/results/{search_term}_{news_source}.csv"
        with open(csv_dir, "r", encoding="UTF-8") as f:
            try:
                self.cursor.copy_from(f, table, sep="|")
                self._conn.commit()
            except (Exception, psycopg2.DatabaseError) as error:
                print(f"Error: {error}")
                self._conn.rollback()
                self.close()
                return None
            print("copy_from_file() done")
            self.close()
            return None


if __name__ == "__main__":
    QUERY = """SELECT * FROM HS2;"""
    connection_params = read_config()
    conn = connect(connection_params)
    db = DataBase(_conn=conn)
    # db.query(query=QUERY)
    news_source_ = "guardian"
    search_term_ = "HS2"
    db.copy_from_csv(search_term=search_term_, news_source=news_source_, table="hs2")
