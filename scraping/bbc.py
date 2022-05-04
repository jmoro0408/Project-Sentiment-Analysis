"""
Module to scrap bbc news articles.
The get_bbs_search_urls function can get a list of bbc search page results for
a given search term and number of pages. This is just the URL of the actual results
page, not the article urls.

The parse_search_results function can then take this search results page url to
get the actual article urls we are interested in.

Module will provide article title, text, date, and url
"""
# TO DO  add capability to get datetime of article

from pathlib import Path
from typing import Iterable, List, Union

import pandas as pd  # type: ignore
import requests  # type: ignore
from bs4 import BeautifulSoup as bs  # type: ignore


class PageOutOfRangeError(Exception):
    """Raised when the the provided search range is out of range"""

    pass


def get_bbc_search_pages(search_term: str, pages: Iterable = [1]) -> List:
    """
    constructs the bbs search urls for a given search term.
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


class BBCArticle:
    """
    main scraping class for BBC articles
    """

    def __init__(self, url: str):
        article = requests.get(url)
        self.soup = bs(article.content, "html.parser")
        self.body = self.get_body()
        self.title = self.get_title()

    def get_body(self) -> str:
        """
        get the main article text from the article body
        """
        body_class = "ssrcss-pv1rh6-ArticleWrapper e1nh2i2l6"
        table = self.soup.findAll("article", attrs={"class": body_class})
        text = " ".join([p.text for p in table])
        return text

    def get_title(self) -> Union[float, str]:
        """
        get the article title
        """
        title_class = "ssrcss-15xko80-StyledHeading e1fj1fc10"
        try:
            return self.soup.find(class_=title_class).text
        except AttributeError:
            return float("nan")


def bbc_article_pipeline(search_term: str, pages: Iterable = [1]) -> pd.DataFrame:
    """
    Run through the bbc news article pipeline.
    1. gets the search page results from the search term and num of pages
    2. gets the individual article urls from the search page
    3. for each article, gets the title and text body
    4. returns a dataframe of title, text body, and url
    """
    search_results_pages = get_bbc_search_pages(search_term=search_term, pages=pages)
    article_urls = get_article_urls_from_search(search_results_pages)
    titles = []
    bodies = []
    for article_url in article_urls:
        bbc_article = BBCArticle(url=article_url)
        titles.append(bbc_article.title)
        bodies.append(bbc_article.body)
    results = pd.DataFrame(
        list(zip(titles, bodies, article_urls)), columns=["Title", "Body", "URL"]
    ).dropna()
    results = results.reset_index(drop=True)
    return results


def save_results_csv(results_df: pd.DataFrame, fname: str):
    save_dir = Path(Path(Path.cwd(), "scraping/results"), fname + ".csv")
    results_df.to_csv(save_dir)


if __name__ == "__main__":
    search_term = "crossrail"
    results = bbc_article_pipeline(search_term=search_term, pages=range(1, 4))
    save_results_csv(results, fname=f"{search_term}_bbc")
