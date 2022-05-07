import unittest
import os
from dotenv import load_dotenv
import requests

from scraper.guardian import API_KEY, GuardianAPI

class TestGuardianAPI(unittest.TestCase):
    load_dotenv()
    API_KEY = str(os.getenv("GUARDIAN_API_KEY"))

    def test_build_api_query_spaces(self):
        search_term = "search with  spaces "
        guardian_api = GuardianAPI(search_term=search_term, api_key=API_KEY)
        assert " " not in guardian_api.build_api_query()

    def test_get_api_response(self):
        search_term = "crossrail"
        guardian_api = GuardianAPI(search_term=search_term, api_key=API_KEY)
        _query = guardian_api.build_api_query()
        api_response = requests.get(_query)
        assert api_response.status_code == 200