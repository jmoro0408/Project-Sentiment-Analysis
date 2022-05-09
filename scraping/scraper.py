"""
Module to hold scraping functions that can be used across various news scraping files.
"""
import datetime
from configparser import ConfigParser
from pathlib import Path
from typing import Dict, List, Optional, Union

import pandas as pd  # type: ignore
import yaml  # type: ignore


class Scraper:
    """
    Scraper methods that can be used across multiple news scraping sites
    """

    def __init__(self):
        self.body: str
        self.article_date: Union[datetime.date, str]

    """named article_date vs date to
    avoid confusion with datetime.date or "from datetime import date"""

    def clean_date(self) -> datetime.date:
        """
        takes a typical HTML date string and returns the date as a datetime.date object.
        Time is discarded.
        example input: 2022-04-03T13:14:11
        """
        date_string = str(self.article_date).split("T", maxsplit=1)[0]
        self.article_date = datetime.date.fromisoformat(date_string)
        return self.article_date

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


def df_from_article_dict(article_results_dict: Dict) -> pd.DataFrame:
    results_df = pd.DataFrame.from_dict(article_results_dict)
    results_df = results_df.dropna().reset_index(drop=True)
    return results_df


def save_results_csv(results_df: pd.DataFrame, fname: str):
    """
    save results df to csv
    """
    print(f"Saving {len(results_df)} rows")
    save_dir = Path(Path.cwd(), "scraping", "results", fname + ".csv")
    results_df.to_csv(save_dir)
    print("Saved")


def read_search_config() -> Dict:
    parser = ConfigParser()
    parser.read(r"scraping/searching.ini")

    save_str = parser["searching_params"]["save"]
    if save_str == "True":
        save = True
    elif save_str == "False":
        save = False
    else:
        raise ValueError(f"Cannot covert {save_str} to a bool")
    config_dict = {
        "search_term": parser["searching_params"]["search_term"],
        "save": save,
    }
    return config_dict


def read_api_key(yml_file: str) -> Dict:
    with open(yml_file) as f:
        config = yaml.load(f, Loader=yaml.SafeLoader)
    return config
