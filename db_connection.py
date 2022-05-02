from configparser import ConfigParser
from typing import Optional

import psycopg2
from psycopg2 import Error


def config(filename: str = "database.ini", section: str = "postgresql") -> dict:
    """
    reads the database.ini configuration file for database connection.
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


def query_db(query: Optional[str] = None) -> None:
    """
    Opens a connection to the database and runs a provided query.
    """
    conn = None
    try:
        # read connection parameters
        params = config()

        # connect to the PostgreSQL server
        print("Connecting to the PostgreSQL database...")
        conn = psycopg2.connect(**params)

        # Create a cursor to perform database operations
        cursor = conn.cursor()
        cursor.execute(query)
        results = cursor.fetchall()
        print(results)

        conn.commit()
        conn.close()

    except (Exception, Error) as error:
        print("Error while connecting to PostgreSQL", error)
    finally:
        if conn:
            cursor.close()
            conn.close()
            print("PostgreSQL connection is closed")


if __name__ == "__main__":
    query = """SELECT * from news_source"""
    query_db(query=query)
