"""
Module docstring to keep pylint happy
"""

import os

import requests
from dotenv import load_dotenv


class GuardianAPI:
    """
    class to handle the querying of the guardian api
    """

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
        response = requests.get(
            _query
        )  # should add some exception handling for invalid status codes
        return response

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


def guardian_api_pipeline(search_term: str, api_key: str):
    guardian_api = GuardianAPI("crossrail", API_KEY)
    results = guardian_api.parse_api_response(0)
    print(results)


if __name__ == "__main__":
    load_dotenv()
    API_KEY = str(os.getenv("GUARDIAN_API_KEY"))
    guardian_api_pipeline("crossrail", API_KEY)
