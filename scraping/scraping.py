"""
Module to hold scraping functions that can be used across various news scraping files.
"""
import datetime
from pathlib import Path
from typing import List, Optional, Union

import bs4  # type: ignore
import pandas as pd  # type: ignore


class Scraper:
    """
    Scraper methods that can be used across multiple news scraping sites
    """

    body: str
    soup: bs4.BeautifulSoup
    article_date: Union[str, datetime.date]

    def clean_date(self) -> datetime.date:
        """
        takes a typical HTML date string and returns the date as a datetime.date object.
        Time is discarded.
        example input: 2022-04-03T13:14:11
        """
        date_string = str(self.article_date).split("T", maxsplit=1)[0]
        return datetime.date.fromisoformat(date_string)

    def clean_article(self, strings_to_remove: Optional[List] = None) -> Optional[str]:
        """
        Cleans the text retrieved from the article body.
        """
        if strings_to_remove is None:
            return self.body.strip()
        for string_to_remove in strings_to_remove:
            if string_to_remove in self.body:
                cleaned_text = self.body.replace(string_to_remove, " ")
                return cleaned_text.strip()
            return self.body.strip()
        return None


def save_results_csv(results_df: pd.DataFrame, fname: str):
    """
    save results df to csv
    """
    save_dir = Path(Path(Path.cwd(), "scraping/results"), fname + ".csv")
    results_df.to_csv(save_dir)
