import os

import requests
from dotenv import load_dotenv


class GuardianArticle:
    def __init__(self, search_term: str, api_key: str):
        self.search_term = search_term
        self.api_key = api_key
        self.query = self.build_api_query()
        self.response = self.get_api_response(self.query)

    def build_api_query(self) -> str:
        """
        create a string suitable for querying the guardian api
        """
        search_term = self.search_term.replace(" ", "%20")
        return f"https://content.guardianapis.com/search?q={search_term}&api-key={self.api_key}"

    def get_api_response(self, api_query_url: str) -> requests.models.Response:
        """
        get response from guardian api
        """
        print(type(requests.get(api_query_url)))
        return requests.get(api_query_url)


if __name__ == "__main__":
    load_dotenv()
    api_key = str(os.getenv("GUARDIAN_API_KEY"))
    guardian = GuardianArticle("crossrail", api_key)
    print(guardian.response.text)
