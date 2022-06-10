"""
Module to scrap bbc news articles.
The get_bbs_search_urls function can get a list of bbc search page results for
a given search term and number of pages. This is just the URL of the actual results
page, not the article urls.

The parse_search_results function can then take this search results page url to
get the actual article urls we are interested in.

Module will provide article title, text, date, and url
"""

import datetime  # type: ignore
from typing import Dict, Iterable, List, Union

import requests  # type: ignore
from bs4 import BeautifulSoup as bs  # type: ignore
from scraping.scraper import df_from_article_dict  # type: ignore
from scraping.scraper import Scraper, save_results_csv
from tqdm import tqdm  # type: ignore

SEARCH_PAGES = range(1, 10)
NEWS_SOURCE_ID = 2  # news source value for postgres db


class PageOutOfRangeError(Exception):
    """Raised when the the provided search range is out of range"""

    pass


def get_bbc_search_pages(search_term: str, pages: Iterable) -> List:
    """
    constructs the bbc search urls for a given search term.
    pages is an iterable that represents the page range to get.
    i.e pages = ranges(1,4) will return the first 3 search pages.
    """
    if 0 in pages:
        raise PageOutOfRangeError("Search page range starts at 1")
    search_url = f"https://www.bbc.co.uk/search?q={search_term}&page="
    urls = []
    for page in pages:
        page = str(page)
        search_with_page = search_url + page
        urls.append(search_with_page)
    return urls


def get_article_urls_from_search(search_results_urls: List) -> List:
    """
    returns links to actual articles from the bbc search page.
    First gets all the anchor tags for each search results page. It then filters out the most likely
    articles using the substring.
    Returns a list of all the article urls.
    """
    substring = "bbc.co.uk/news/uk"
    links = []
    for search_url in search_results_urls:
        search_results_content = requests.get(search_url).content
        soup = bs(search_results_content, "html.parser")
        for link in soup.find_all("a"):
            links.append(link.get("href"))
        links_with_substring = [string for string in links if substring in string]
    return links_with_substring


class BBCArticle(Scraper):
    """
    main scraping class for BBC articles
    """

    def __init__(self, url: str):
        article = requests.get(url)
        self.soup = bs(article.content, "html.parser")
        self.title: Union[str, float]
        self.article_date: Union[str, datetime.date]
        self.body: str

    def get_date(self) -> str:
        """
        returns the date of the published article in datetime format
        """
        self.article_date = str(self.soup.time.attrs["datetime"])
        return self.article_date

    def get_body(self) -> str:
        """
        get the main article text from the article body
        """
        text_blocks = self.soup.findAll("div", attrs={"data-component": "text-block"})
        text_list = []
        for item in text_blocks:
            for p in item.p:
                if p.name is None:
                    text_list.append(p)
        text = " ".join(text_list)
        self.body = text
        return self.body

    def get_title(self) -> Union[str, float]:
        """
        get the article title
        """
        title_class = "ssrcss-15xko80-StyledHeading e1fj1fc10"
        try:
            self.title = str(self.soup.find(class_=title_class).text)
        except AttributeError:
            self.title = float("nan")
        return float("nan")  # Return nan so that it can be dropped by df.dropna()


def build_article_results_dict(search_term: str, pages: Iterable) -> Dict:
    """
    Run through the bbc news article pipeline.
    1. gets the search page results from the search term and num of pages
    2. gets the individual article urls from the search page
    3. for each article, gets the title and text body
    4. returns a dataframe of title, text body, and url
    """
    article_strings_to_remove = [
        "Follow BBC London on  ,  and  . Send your story ideas to ",
    ]
    search_results_pages = get_bbc_search_pages(search_term=search_term, pages=pages)
    article_urls = get_article_urls_from_search(search_results_pages)
    titles = []
    bodies = []
    dates = []
    for article_url in tqdm(article_urls):
        bbc_article = BBCArticle(url=article_url)
        bbc_article.get_title()
        bbc_article.get_body()
        bbc_article.get_date()
        bbc_article.clean_article(strings_to_remove=article_strings_to_remove)
        bbc_article.clean_date()

        titles.append(bbc_article.title)
        bodies.append(bbc_article.body)
        dates.append(bbc_article.article_date)
    bbc_articles_dict = {
        "article_title": titles,
        "article_text": bodies,
        "source_url": article_urls,
        "article_date": dates,
    }
    bbc_articles_dict["news_source_id"] = NEWS_SOURCE_ID
    return bbc_articles_dict

def main(search_term: str, ):
    print(f"Scraping bbc site for {search_term} results")
    article_results_dict = build_article_results_dict(
    search_term=search_term, pages=SEARCH_PAGES
)
    results = df_from_article_dict(article_results_dict)
    save_results_csv(results, fname=f"{search_term}_bbc")
    return None



