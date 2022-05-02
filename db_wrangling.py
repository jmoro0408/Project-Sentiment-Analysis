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
    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception(
            "Section {0} not found in the {1} file".format(section, filename)
        )

    return db


def connect(params: dict) -> psycopg2.extensions.connection:
    """
    creates a connection to the database.
    IMPORTANT: Does not automatically close the database connection. This should
    be handled by subsequent db tools (query, insert, create etc) or by calling the close
    method of the DataBase class.
    """
    conn = None
    try:
        # read connection parameters
        params = read_config()
        # connect to the PostgreSQL server
        conn = psycopg2.connect(**params)
        return conn
    except (Exception, Error) as error:
        print("Error while connecting to PostgreSQL", error)


class DataBase:
    """
    Main database class that handles all querying, inserting, etc
    """

    def __init__(self, conn: psycopg2.extensions.connection) -> None:
        self.init = init
        self.conn = conn
        self.cursor = conn.cursor()

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


if __name__ == "__main__":
    query = """SELECT * from news_source"""
    connection_params = read_config()

    conn = connect(connection_params)
    db = DataBase(conn=conn)
    db.query(query=query)
