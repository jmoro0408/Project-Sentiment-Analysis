"""

"""
import db_wrangling as dbw
import sentiment_analysis
from scraping import bbc, guardian
from scraping.scraper import read_search_config


def scrape_site(news_source: str, search_term: str) -> None:
    """scrapes the site specified by news_source.
    Currently bbc news and guardian news implemented.
    The results are saved as csv files in scraping/results as
    {search_term}_{news_source}.csv.

    Args:
        news_source (str): news source to be scraped
        search_term (str): term to be searched and scraped

    Returns:
        _type_: bbc or guardian object
    """
    # match case is better but only available in python 3.10+
    if news_source == "bbc":
        bbc.main(search_term=search_term)
    if news_source == "guardian":
        guardian.main(search_term=search_term)
    print("Only bbc and guardian news sources are currently implemented.")
    return None


def perform_sentiment_analysis(news_source: str, search_term: str) -> None:
    """undertakes sentiment analysis of the article titles provided by
    the search term and news source csv file specified.
    results are saved in scraping/results/sentiment_analysis_results
    as {search_term}_{news_source}_{sentiment}.csv

    Args:
        news_source (str): news source to be scraped
        search_term (str): term to be searched and scraped

    Returns:
        None
    """
    sentiment_analysis.main(news_source, search_term)
    return None


def write_to_db(news_source: str, search_term: str) -> None:
    """Writes the full csv file with sentiment analysis into
    the postgres database.
    Data is writted to table corresponding to the search_term.

    Args:
        news_source (str): news source to be scraped
        search_term (str): term to be searched and scraped

    Returns:
       None
    """
    connection_params = dbw.read_config()
    conn = dbw.connect(connection_params)
    db = dbw.DataBase(_conn=conn)
    db.send_csv_to_psql(
        search_term=search_term, news_source=news_source, table=search_term
    )
    return None


def main():
    """Runs the full program.
    1. Scrape site specified by "news_source" for term "search_term" and
        save results as csv.
    2. undertake sentiment analysis of the article titles included in the csv
    3. writes the full csv with sentiment to postgres db.
    """
    input_config = read_search_config()
    SEARCH_TERM = input_config["search_term"]
    NEWS_SOURCE = input_config["news_source"]
    scrape_site(NEWS_SOURCE, SEARCH_TERM)
    perform_sentiment_analysis(NEWS_SOURCE, SEARCH_TERM)
    write_to_db(NEWS_SOURCE, SEARCH_TERM)


if __name__ == "__main__":
    main()
