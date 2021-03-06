"""
Module docstring to keep pylint happy
"""

import datetime
from typing import Dict, Iterable, Union

import requests
from bs4 import BeautifulSoup as bs  # type: ignore
from tqdm import tqdm  # type: ignore

from scraping.scraper import df_from_article_dict  # type: ignore
from scraping.scraper import Scraper, read_config_yaml, save_results_csv

SEARCH_PAGES: Iterable = range(1, 10)
NEWS_SOURCE_ID = 1


class GuardianAPI:
    """
    class to handle the querying of the guardian api
    """

    def __init__(self, search_term: str, api_key: str, search_page: int):
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
            text_list.append((element.findAll(string=True)))
        text = " ".join(text_list[0])
        self.body = text
        return self.body


def build_article_results_dict(
    search_term: str,
    api_key: str,
    search_pages: Iterable,
    result_nums: Iterable = range(0, 9),
) -> Dict:
    """
    main function #to write
    """

    titles = []
    bodies = []
    dates = []
    urls = []
    for page in tqdm(search_pages):
        guardian_api = GuardianAPI(
            search_term=search_term, api_key=api_key, search_page=page
        )
        for result in tqdm(result_nums):
            try:
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
            except IndexError:
                print("List of articles available exceeded, breaking...")
                break
    guardian_articles_dict = {
        "article_title": titles,
        "article_text": bodies,
        "source_url": urls,
        "article_date": dates,
    }
    guardian_articles_dict["news_source_id"] = NEWS_SOURCE_ID  # type: ignore
    return guardian_articles_dict


def main(search_term: str):
    API_KEY = read_config_yaml("secrets.yml")["guardian_api"]
    print(f"Scraping guardian site for {search_term} results")
    article_dict = build_article_results_dict(
        search_term=search_term, api_key=API_KEY, search_pages=SEARCH_PAGES
    )
    results = df_from_article_dict(article_dict)
    save_results_csv(results, fname=f"{search_term}_guardian")
    return None
