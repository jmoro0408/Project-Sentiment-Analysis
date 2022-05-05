"""
Module to scrap bbc news articles.
The get_bbs_search_urls function can get a list of bbc search page results for
a given search term and number of pages. This is just the URL of the actual results
page, not the article urls.

The parse_search_results function can then take this search results page url to
get the actual article urls we are interested in.

Module will provide article title, text, date, and url
"""
# TODO Move body/title/date from class attribute to instance attribute

import datetime
from pathlib import Path
from typing import Iterable, List, Optional, Union

import pandas as pd  # type: ignore
import requests  # type: ignore
from bs4 import BeautifulSoup as bs  # type: ignore


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


class BBCArticle:
    """
    main scraping class for BBC articles
    """

    def __init__(self, url: str):
        article = requests.get(url)
        self.soup = bs(article.content, "html.parser")
        self.body = self.get_body() # I dont think these should be class attributes.
        self.title = self.get_title() #move them out
        self.date = self.get_date() # to instance attributes, like guardian.py

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
        return text

    def get_title(self) -> Union[float, str]:
        """
        get the article title
        """
        title_class = "ssrcss-15xko80-StyledHeading e1fj1fc10"
        try:
            return self.soup.find(class_=title_class).text
        except AttributeError:
            return float("nan")  # Return nan so that it can be dropped by df.dropna()

    def clean_article(self) -> Optional[str]:
        """
        Cleans the text retrieved from the article body.
        """
        string_to_removes = [
            "Follow BBC London on  ,  and  . Send your story ideas to ",
        ]
        for string_to_remove in string_to_removes:
            if string_to_remove in self.body:
                cleaned_text = self.body.replace(string_to_remove, " ")
                return cleaned_text.strip()
            else:
                return self.body.strip()
        return None

    def get_date(self) -> datetime.date:
        """
        returns the date of the published article in datetime format
        """
        datetime_string = self.soup.time.attrs["datetime"]
        date_string = datetime_string.split("T")[0]
        return datetime.date.fromisoformat(date_string)


def bbc_article_pipeline(search_term: str, pages: Iterable) -> pd.DataFrame:
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
    dates = []
    for article_url in article_urls:
        bbc_article = BBCArticle(url=article_url)
        titles.append(bbc_article.title)
        bodies.append(bbc_article.clean_article())
        dates.append(bbc_article.date)

    _results = pd.DataFrame(
        list(zip(titles, bodies, article_urls, dates)),
        columns=["Title", "Body", "URL", "Date"],
    ).dropna()
    _results = _results.reset_index(drop=True)
    return _results


def save_results_csv(results_df: pd.DataFrame, fname: str):
    save_dir = Path(Path(Path.cwd(), "scraping/results"), fname + ".csv")
    results_df.to_csv(save_dir)


if __name__ == "__main__":
    SAVE = False
    SEARCH_TERM = "HS2"
    SEARCH_PAGES = [1]
    results = bbc_article_pipeline(search_term=SEARCH_TERM, pages=SEARCH_PAGES)
    if SAVE:
        save_results_csv(results, fname=f"{SEARCH_TERM}_bbc")
