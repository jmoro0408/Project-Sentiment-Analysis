"""
Module docstring to keep pylint happy
"""
# TODO Move the creation of the results df from here and bbc into scraping.py
# Possibly return a dict of lists from and results then build df from there?

# TODO Guardian api response only includes 9 responses. Figure out how to get more.

import datetime
import os
from typing import Dict, Iterable, Union

import pandas as pd  # type: ignore
import requests
from bs4 import BeautifulSoup as bs  # type: ignore
from dotenv import load_dotenv

from scraping import Scraper, save_results_csv

load_dotenv()
API_KEY = str(os.getenv("GUARDIAN_API_KEY"))
SEARCH_TERM = "crossrail"
SEARCH_PAGES = [1,2]
SAVE = False


class GuardianAPI:
    """
    class to handle the querying of the guardian api
    """

    def __init__(self, search_term: str, api_key: str, search_page:int):
        self.search_term = search_term
        self.api_key = api_key
        self.search_page = search_page
        self.results: Dict


    def build_api_query(self) -> str:
        """
        create a string suitable for querying the guardian api
        """
        search_term = self.search_term.replace(" ", "%20")
        return f"https://content.guardianapis.com/search?page={self.search_page}&q={search_term}&api-key={self.api_key}"

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
        article, and generally clean, I'm making this grab only one result at a time,
        corresponding to the "result_number" argument.
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
            "title": article_results[result_number]["webTitle"],
            "url": article_results[result_number]["webUrl"],
            "date": article_results[result_number]["webPublicationDate"],
        }
        return result_dict


class GuardianArticle(Scraper):
    """
    class to handle the parsing of individial guardian articles
    """

    def __init__(self, url: str):
        article = requests.get(url)
        self.soup = bs(article.content, "html.parser")
        self.article_date: Union[str, datetime.date]
        self.body: str

    def get_body(self) -> str:
        """
        get the main article text from the article body
        """
        text_blocks = self.soup.findAll("div", attrs={"data-gu-name": "body"})
        text_list = []
        for element in text_blocks:
            text_list.append((element.findAll(text=True)))
        text = " ".join(text_list[0])
        self.body = text
        return self.body


def main(search_term: str, api_key: str,search_pages: Iterable,  result_nums: Iterable = range(0,9)):
    """
    main function #to write
    """

    titles = []
    bodies = []
    dates = []
    urls = []
    for page in search_pages:
        guardian_api = GuardianAPI(search_term=search_term, api_key=api_key, search_page=page)
        for result in result_nums:
            api_response = guardian_api.parse_api_response(result_number=result)
            titles.append(api_response["title"])
            urls.append(api_response["url"])

            guardian_article = GuardianArticle(api_response["url"])
            guardian_article.get_body()
            guardian_article.clean_article(strings_to_remove=None)
            guardian_article.article_date = api_response["date"]
            guardian_article.clean_date()

            bodies.append(guardian_article.body)
            dates.append(guardian_article.article_date)

    results_df = pd.DataFrame(
        list(zip(titles, bodies, urls, dates)),
        columns=["Title", "Body", "URL", "Date"],
    ).dropna()
    results_df = results_df.reset_index(drop=True)
    return results_df


if __name__ == "__main__":
    results = main(search_term=SEARCH_TERM, api_key=API_KEY, search_pages = SEARCH_PAGES)
    print(results.head())
    print(f"dataframe has {len(results)} rows)")
    if SAVE:
        save_results_csv(results, fname=f"{SEARCH_TERM}_guardian")
