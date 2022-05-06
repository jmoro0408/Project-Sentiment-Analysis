"""
Module to hold scraping functions that can be used across various news scraping files.
"""
import datetime
from typing import List, Optional
from pathlib import Path
import pandas as pd

import bs4  # type: ignore
from bs4 import BeautifulSoup as bs  # type: ignore


class Scraper:
    """
    Scraper methods that can be used across multiple news scraping sites
    """

    body: str
    soup: bs4.BeautifulSoup

    def clean_date(self) -> datetime.date:
        date_string = self.date.split("T")[0]
        return datetime.date.fromisoformat(date_string)

    def clean_article(self, strings_to_remove: Optional[List] = None) -> Optional[str]:
        """
        Cleans the text retrieved from the article body.
        """
        if strings_to_remove is None:
            return self.body.strip()
        else:
            for string_to_remove in strings_to_remove:
                if string_to_remove in self.body:
                    cleaned_text = self.body.replace(string_to_remove, " ")
                    return cleaned_text.strip()
                else:
                    return self.body.strip()
        return None

def save_results_csv(results_df: pd.DataFrame, fname: str):
    save_dir = Path(Path(Path.cwd(), "scraping/results"), fname + ".csv")
    results_df.to_csv(save_dir)