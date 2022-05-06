"""
Module docstring to keep pylint happy
"""

import os
from re import A
from typing import Dict

from scraping import Scraper
import requests
from dotenv import load_dotenv
from bs4 import BeautifulSoup as bs  # type: ignore

load_dotenv()
API_KEY = str(os.getenv("GUARDIAN_API_KEY"))
SEARCH_TERM = "crossrail"


class GuardianAPI:
    """
    class to handle the querying of the guardian api
    """

    results: Dict

    def __init__(self, search_term: str, api_key: str):
        self.search_term = search_term
        self.api_key = api_key

    def build_api_query(self) -> str:
        """
        create a string suitable for querying the guardian api
        """
        search_term = self.search_term.replace(" ", "%20")
        return f"https://content.guardianapis.com/search?q={search_term}&api-key={self.api_key}"

    def get_api_response(self) -> requests.models.Response:
        """
        get response from guardian api
        """
        _query = self.build_api_query()
        api_response = requests.get(
            _query
        )  # should add some exception handling for invalid status codes
        return api_response

    def parse_api_response(self, result_number: int) -> dict:
        """
        parses the response from the api query. See link for examples:
        https://open-platform.theguardian.com/explore/
        the response typically returns a ton of web page results. To keep this similar to the bbc
        article, and generally clean, I'm making this grab only one result at a time, correspoding to the
        "result_number" argument.
        This method deliberately only parses one result at a time.
        The intention here is that this method is called in a loop, parsing each result as required.
        The argument result_number should be supplied, calling out which specific result is wanted.
        """
        _response = self.get_api_response()
        results_list = _response.json()["response"]["results"]
        article_results = [
            result for result in results_list if result["type"] == "article"
        ]
        result_dict = {
            "webTitle": article_results[result_number]["webTitle"],
            "webUrl": article_results[result_number]["webUrl"],
            "webPublicationDate": article_results[result_number]["webPublicationDate"],
        }
        return result_dict


class GuardianArticle(Scraper):
    """
    class to handle the parsing of individial guardian articles
    """
    body: str
    def __init__(self, url:str):
        article = requests.get(url)
        self.soup = bs(article.content, "html.parser")

    def get_body(self) -> str:
        """
        get the main article text from the article body
        """
        text_blocks = self.soup.findAll("div", attrs={"data-gu-name": "body"})
        text_list = []
        for element in text_blocks:
            text_list.append((element.findAll(text = True)))
        text = " ".join(text_list[0])
        return text


def main(search_term: str, api_key: str, result_num: int):
    """
    """
    guardian_api = GuardianAPI(search_term, api_key)
    guardian_api.results = guardian_api.parse_api_response(result_num)
    guardian_article = GuardianArticle(url = guardian_api.results["webUrl"])
    guardian_article.body = guardian_article.get_body()
    article_text = guardian_article.clean_article(strings_to_remove=None)
    return article_text




if __name__ == "__main__":
    print(main(search_term=SEARCH_TERM, api_key=API_KEY, result_num=0))
