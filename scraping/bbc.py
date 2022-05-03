"""
Module to scrap bbc news articles.
Module will provide article title, text, date, and url
"""
# TO DO add func to get all bbc articles from search
# run through all articles from search func and get title/body
# add capability to get datetime of article

from typing import Iterable, List

import requests  # type: ignore
from bs4 import BeautifulSoup as bs  # type: ignore


def get_bbc_search_urls(search_term: str, pages: Iterable = [1]) -> List:
    """
    constructs the bbs search urls for a given search term.
    pages is an iterable that represents the page range to get.
    i.e pages = ranges(1,4) will return the first 3 search pages.
    """
    search_url = f"https://www.bbc.co.uk/search?q={search_term}&page="
    urls = []
    for page in pages:
        page = str(page)
        search_with_page = search_url + page
        urls.append(search_with_page)
    return urls


class BBC:
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

    def get_title(self) -> str:
        """
        get the article title
        """
        title_class = "ssrcss-15xko80-StyledHeading e1fj1fc10"
        return self.soup.find(class_=title_class).text


if __name__ == "__main__":
    URL = "https://www.bbc.com/news/uk-england-london-61093756"
    parsed = BBC(URL)
    article_body = parsed.body
    article_title = parsed.title
    pages = range(1, 3)
    print(get_bbc_search_urls("crossrail", pages))
