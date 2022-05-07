import unittest

import bbc  # type: ignore
import pandas as pd  # type: ignore

# TODO I dont really know how to write unit tests


class TestBBCFuncs(unittest.TestCase):
    def test_get_bbc_search_pages_return(self):
        search_term = "crossrail"
        pages = [1]
        result = bbc.get_bbc_search_pages(search_term, pages)
        self.assertIsInstance(result, list)

    def test_get_bbc_search_pages_error(self):
        search_term = "crossrail"
        pages = [0]
        with self.assertRaises(bbc.PageOutOfRangeError):
            bbc.get_bbc_search_pages(search_term, pages)


class TestBBCArticle(unittest.TestCase):
    pass


class TestMain(unittest.TestCase):
    def test_build_article_dict_(self):
        search_term = "crossrail"
        pages = [1]
        result = bbc.build_article_results_dict(search_term, pages)
        assert len(result) > 0
        self.assertIsInstance(result, dict)


if __name__ == "__main__":
    unittest.main()
