"""
Module docstring to keep pylint happy
"""

import os
from typing import Dict

import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = str(os.getenv("GUARDIAN_API_KEY"))


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


class GuardianArticle:
    """
    class to handle the parsing of individial guardian articles
    """

    pass


def main(search_term: str, api_key: str, result_num: int):
    guardian_api = GuardianAPI("crossrail", api_key)
    guardian_api.results = guardian_api.parse_api_response(result_num)
    print(guardian_api.results)


if __name__ == "__main__":
    main(search_term="crossrail", api_key=API_KEY, result_num=0)
