"""
1. scrape website
2. perform sentiment analysis
3. write to db

"""
from scraping.scraper import read_search_config
from scraping import guardian, bbc
import sentiment_analysis
import db_wrangling as dbw

def scrape_site(news_source: str, search_term: str):
    #match case is better but only available in python 3.10+
    if news_source == "bbc":
        return bbc.main(search_term =search_term)
    if news_source == "guardian":
        return guardian.main(search_term =search_term)

def perform_sentiment_analysis(news_source: str, search_term: str):
    return sentiment_analysis.main(news_source, search_term)

def write_to_db(news_source: str, search_term: str):
    connection_params = dbw.read_config()
    conn = dbw.connect(connection_params)
    db = dbw.DataBase(_conn=conn)
    return db.send_csv_to_psql(
        search_term=search_term, news_source=news_source, table=search_term
    )

def main():
    input_config = read_search_config()
    SEARCH_TERM = input_config["search_term"]
    NEWS_SOURCE = input_config["news_source"]
    scrape_site(NEWS_SOURCE, SEARCH_TERM)
    perform_sentiment_analysis(NEWS_SOURCE, SEARCH_TERM)
    write_to_db(NEWS_SOURCE, SEARCH_TERM)

if __name__ == "__main__":
    main()