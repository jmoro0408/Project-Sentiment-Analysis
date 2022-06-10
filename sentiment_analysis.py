"""
Uses huggingface transformers to generate
sentiment analysis on article titles
"""

# pylint: disable=line-too-long,invalid-name
import pandas as pd  # type: ignore
import transformers  # type: ignore
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from typing_extensions import TypeAlias
from scraping.scraper import read_search_config

TokenizerType: TypeAlias = (
    transformers.models.distilbert.tokenization_distilbert_fast.DistilBertTokenizerFast
)
ModelType: TypeAlias = (
    transformers.models.distilbert.modeling_distilbert.DistilBertForSequenceClassification
)


def load_model(model_name: str) -> tuple[TokenizerType, ModelType]:
    """
    loads in the pretrained model for use.
    """
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(model_name)
    return tokenizer, model


def predict_sentiment(text: str, model: ModelType, tokenizer: TokenizerType) -> tuple:
    """
    makes predictions on inputted text
    returns tuple with [%negative, %positive] results
    """

    inputs = tokenizer(text, return_tensors="pt")
    outputs = model(**inputs)
    return tuple(outputs.logits.softmax(dim=-1).tolist())[0]


def read_csv(search_term: str, news_source: str) -> pd.DataFrame:
    """
    reads in results csv and returns a pandas df
    """
    csv_dir = f"scraping/results/{search_term}_{news_source}.csv"
    return pd.read_csv(csv_dir, sep="|")


def write_csv(df: pd.DataFrame, search_term: str, news_source: str):
    """writes a pandas dataframe to csv

    Args:
        df (pd.DataFrame): pandas df to write
        search_term (str): search term corresponding to this specific df
        news_source (str): new source used to gather articles"""
    csv_dir = f"scraping/results/sentiment_analysis_results/{search_term}_{news_source}_sentiment.csv"
    return df.to_csv(csv_dir, sep="|", index = False)

def combine_sentiment_df(
    article_df: pd.DataFrame, sentiment_results: pd.Series
) -> pd.DataFrame:
    """Combines the sentiment analysis results with the original article df

    Args:
        article_df (pd.DataFrame): df containing the article text, title, date etc
        sentiment_results (pd.Series): pd series containing the negative/positive results of the article sentiment

    Returns:
        pd.DataFrame: df wih sentiment results merged with article df
    """
    temp_df = pd.DataFrame(
        sentiment_results.to_list(), columns=["negative", "positive"]
    )
    combined_df = pd.concat([article_df, temp_df], axis=1, join="inner")
    del temp_df
    return combined_df


def main():
    """
    main function to call predictions
    """
    input_config = read_search_config()
    SEARCH_TERM = input_config["search_term"]
    NEWS_SOURCE = input_config["news_source"]
    MODEL_NAME = "distilbert-base-uncased-finetuned-sst-2-english"
    df = read_csv(search_term=SEARCH_TERM, news_source=NEWS_SOURCE)
    tokenizer, model = load_model(MODEL_NAME)
    sentiment_results = df["article_title"].apply(
        predict_sentiment, args=(model, tokenizer)
    )
    combined_df = combine_sentiment_df(
        article_df=df, sentiment_results=sentiment_results
    )
    write_csv(combined_df, search_term=SEARCH_TERM, news_source=NEWS_SOURCE)


if __name__ == "__main__":
    main()
