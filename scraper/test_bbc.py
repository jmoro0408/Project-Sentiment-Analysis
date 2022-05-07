import unittest
import bbc

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

if __name__ == '__main__':
    unittest.main()
