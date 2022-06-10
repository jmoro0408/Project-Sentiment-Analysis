"""
1. scrape website
2. perform sentiment analysis
3. write to db

"""
from scraping.scraper import read_search_config
from scraping import guardian, bbc

def scrape_site(news_source: str, search_term: str):
    match news_source:
        case "bbc":
            return bbc.main(search_term =search_term)
        case "guardian":
            return guardian.main(search_term =search_term)

def main():
    input_config = read_search_config()
    SEARCH_TERM = input_config["search_term"]
    NEWS_SOURCE = input_config["news_source"]
    print(f"Scraping {NEWS_SOURCE} site for {SEARCH_TERM} results")
    scrape_site(NEWS_SOURCE, SEARCH_TERM)


if __name__ == "__main__":
    main()