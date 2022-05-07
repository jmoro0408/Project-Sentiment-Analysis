import unittest
import bbc

class TestBBC(unittest.TestCase):

    def test_get_bbc_search_pages(self):
        search_term  = "crossrail"

        pages = [1]
        result = bbc.get_bbc_search_pages(search_term, pages)
        self.assertIsInstance(result,list)

if __name__ == '__main__':
    unittest.main()

