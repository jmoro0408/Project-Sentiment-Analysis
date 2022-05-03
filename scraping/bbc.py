"""
Module to scrap bbc news articles.
Module will provide article title, text, date, and url
"""

import requests  # type: ignore
from bs4 import BeautifulSoup as bs  # type: ignore


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
    print(article_body)
