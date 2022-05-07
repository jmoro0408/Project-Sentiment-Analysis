import unittest
import bbc
import pandas as pd

# TODO I dont really know how to write unit tests

class TestBBCFuncs(unittest.TestCase):

    def test_get_bbc_search_pages_return(self):
        search_term  = "crossrail"
        pages = [1]
        result = bbc.get_bbc_search_pages(search_term, pages)
        self.assertIsInstance(result,list)

    def test_get_bbc_search_pages_error(self):
        search_term  = "crossrail"
        pages = [0]
        with self.assertRaises(bbc.PageOutOfRangeError):
           bbc.get_bbc_search_pages(search_term, pages)


class TestBBCArticle(unittest.TestCase):
    pass

class TestMain(unittest.TestCase):
    def test_main_(self):
        search_term = "crossrail"
        pages = [1]
        result = bbc.main(search_term, pages)
        self.assertIsInstance(result, pd.DataFrame)




if __name__ == '__main__':
    unittest.main()
