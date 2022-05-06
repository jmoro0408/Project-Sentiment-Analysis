"""
Module to hold scraping functions that can be used across various news scraping files.
"""
import datetime
from typing import List, Optional

import bs4  # type: ignore
from bs4 import BeautifulSoup as bs  # type: ignore


class Scraper:
    """
    Scraper methods that can be used across multiple news scraping sites
    """

    body: str
    soup: bs4.BeautifulSoup

    def get_date(self) -> datetime.date:
        """
        returns the date of the published article in datetime format
        """
        datetime_string = self.soup.time.attrs["datetime"]
        date_string = datetime_string.split("T")[0]
        return datetime.date.fromisoformat(date_string)

    def clean_article(self, strings_to_remove: List) -> Optional[str]:
        """
        Cleans the text retrieved from the article body.
        """

        for string_to_remove in strings_to_remove:
            if string_to_remove in self.body:
                cleaned_text = self.body.replace(string_to_remove, " ")
                return cleaned_text.strip()
            else:
                return self.body.strip()
        return None
