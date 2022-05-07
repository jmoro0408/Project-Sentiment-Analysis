import unittest
from sys import api_version

import requests

from scraper.guardian import API_KEY, GuardianAPI, GuardianArticle


class TestGuardianAPI(unittest.TestCase):
    def setUp(self):
        search_term = "search with  spaces "
        search_page = 1
        self.guardian_api = GuardianAPI(
            search_term=search_term, api_key=API_KEY, search_page=search_page
        )

    def test_build_api_query_spaces(self):
        assert " " not in self.guardian_api.build_api_query()

    def test_get_api_response(self):
        _query = self.guardian_api.build_api_query()
        api_response = requests.get(_query)
        assert api_response.status_code == 200


class TestGuardianArticle(unittest.TestCase):
    def setUp(self):
        url = "https://www.theguardian.com/uk-news/2022/may/04/crossrail-much-delayed-elizabeth-line-to-open-on-24-may"
        self.article = GuardianArticle(url=url)

    def test_body(self):
        self.body = self.article.get_body()
        assert len(self.body) > 0
        self.assertIsInstance(self.body, str)


if __name__ == "__main__":
    unittest.main()
