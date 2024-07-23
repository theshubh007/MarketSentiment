from pymongo import MongoClient
from typing import List
from DataSchemas.BBC import BBCModel
from Classification.classification import SentimentAnalysis

from datetime import datetime
import os


# Initialize MongoDB connection
client = MongoClient(os.environ["MONGO_DB_KEY"])
db = client.news_db
collection = db.articles

# Initialize Sentiment Analysis
sentiment_analysis = SentimentAnalysis()


def classify_news():
    try:
        # Fetch all articles from MongoDB
        articles = list(collection.find({}))

        if not articles:
            print("No articles found to classify.")
            return {"message": "No articles found to classify."}

        updated_articles = []

        for article in articles:
            # Convert MongoDB document to BBCModel
            bbc_article = BBCModel(**article)
            text = bbc_article.body

            if not text:
                continue

            # Predict sentiment
            sentiment = sentiment_analysis.predict(text)

            # Update category based on sentiment
            sentiment_category_mapping = {
                "Positive": "Positive News",
                "Neutral": "Neutral News",
                "Negative": "Negative News",
            }
            new_category = sentiment_category_mapping.get(sentiment, "General")

            # Update article with new category
            collection.update_one(
                {"url": bbc_article.url}, {"$set": {"category": new_category}}
            )

            updated_articles.append(
                {
                    "url": bbc_article.url,
                    "old_category": bbc_article.category,
                    "new_category": new_category,
                }
            )

        return {"updated_articles": updated_articles}

    except Exception as e:
        print(f"An error occurred: {e}")
        return {"error": str(e)}


def get_articles_by_category(category: str):
    """
    Fetch articles from MongoDB by category.

    :param category: The category to filter by (e.g., 'Positive News', 'Negative News', 'Neutral News').
    :return: List of articles in the specified category.
    """
    try:
        # Validate category
        valid_categories = ["Positive News", "Negative News", "Neutral News"]
        if category not in valid_categories:
            raise ValueError(
                f"Invalid category. Valid categories are {valid_categories}."
            )

        # Fetch articles from MongoDB
        articles = list(collection.find({"category": category}, {"_id": 0}))
        print("Flag 1s")
        if not articles:
            print(f"No articles found for category: {category}.")
            return {"message": f"No articles found for category: {category}."}

        return articles

    except Exception as e:
        print(f"An error occurred: {e}")
        return {"error": str(e)}
