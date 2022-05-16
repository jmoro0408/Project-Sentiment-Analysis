import pandas as pd  # type: ignore
import transformers  # type: ignore
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from typing_extensions import TypeAlias

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


def predict_sentiment(model: ModelType, tokenizer: TokenizerType, text: str) -> list:
    """
    makes predictions on inputted text
    returns list with [%negative, %positive] results
    """

    inputs = tokenizer(text, return_tensors="pt")
    outputs = model(**inputs)
    return outputs.logits.softmax(dim=-1).tolist()


def read_csv(search_term: str, news_source: str) -> pd.DataFrame:
    """
    reads in results csv and returns a pandas df
    """
    csv_dir = f"scraping/results/{search_term}_{news_source}.csv"
    return pd.read_csv(csv_dir, sep="|")


def main():
    """
    main function to call predictions
    """
    SEARCH_TERM = "crossrail"
    NEWS_SOURCE = "bbc"
    MODEL_NAME = "distilbert-base-uncased-finetuned-sst-2-english"
    tokenizer, model = load_model(MODEL_NAME)
    df = read_csv(search_term=SEARCH_TERM, news_source=NEWS_SOURCE)
    test_title = df.iloc[1]["article_title"]
    results = predict_sentiment(model=model, tokenizer=tokenizer, text=test_title)[0]
    print(
        f"Article title: {test_title} is {results[0]:.4f} negative and {results[1]:.4f} positive"
    )


if __name__ == "__main__":
    main()
