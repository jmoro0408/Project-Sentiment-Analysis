"""
Module docstring to keep pylint happy
"""

import os

import requests
from dotenv import load_dotenv


class GuardianArticle:
    """
    Main guardian class.
    """

    def __init__(self, search_term: str, api_key: str):
        self.search_term = search_term
        self.api_key = api_key
        self.query = self.build_api_query()
        self.response = self.get_api_response()

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
        return requests.get(self.query)


if __name__ == "__main__":
    load_dotenv()
    API_KEY = str(os.getenv("GUARDIAN_API_KEY"))
    guardian = GuardianArticle("crossrail", API_KEY)
    print(guardian.response.text)
