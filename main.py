from fastapi import FastAPI, HTTPException, Query
import uvicorn
from contextlib import asynccontextmanager
from pydantic import BaseModel
from typing import List, Optional
import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
import random
import os
from DataModels.BBC import BBC
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.memory import MemoryJobStore
import pickle
import re
import tensorflow as tf


# Disable oneDNN custom operations
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"

import numpy as np


###################################
#####################################
# Define paths to the saved model and tokenizer
MODEL_PATH = "./MLmodel/gru_model.h5"
TOKENIZER_PATH = "./MLmodel/tokenizer.pkl"


@asynccontextmanager
async def app_lifespan(app: FastAPI):
    scheduler.start()

    yield
    scheduler.shutdown()


app = FastAPI(lifespan=app_lifespan)
from dotenv import load_dotenv

load_dotenv()

jobstores = {"default": MemoryJobStore()}
# Initialize an AsyncIOScheduler with the jobstore
scheduler = AsyncIOScheduler(jobstores=jobstores, timezone="Asia/Kolkata")

# MongoDB Atlas connection
uri = os.environ["MONGO_DB_KEY"]
client = MongoClient(uri)
db = client.news_db
collection = db.articles

# User-agents list
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.78 Safari/537.36 OPR/47.0.2631.39",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; AS; rv:11.0) like Gecko",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/603.2.4 (KHTML, like Gecko) Version/10.1.1 Safari/603.2.4",
    "My User Agent 1.0",
]


class Article(BaseModel):
    title: str
    link: str
    category: str


# Job running daily at 9:30:00
@scheduler.scheduled_job("cron", day_of_week="mon-sun", hour=9, minute=30, second=0)
def scrape_bbc_news():
    print("Scraping BBC News...")
    url = "https://www.bbc.com/news"
    headers = {"User-Agent": random.choice(user_agents)}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")
    articles = []
    links = set()
    for item in soup.find_all("a", {"data-testid": "internal-link"}):
        link = item.get("href")
        if link and link.startswith("/news/articles/"):
            full_link = "https://www.bbc.com" + link
            links.add(full_link)
            print(full_link)

        #  return links
        if link and not link.startswith("http"):
            link = "https://www.bbc.com" + link

    for link in links:
        Article = BBC(link)
        articles.append(Article.to_json())

    # Store articles in MongoDB
    collection.delete_many({})  # Clear existing articles
    if articles:
        for article in articles:
            print(article)
        collection.insert_many(articles)


@app.get("/news", response_model=List[Article])
def get_news(
    category: Optional[str] = Query(None, description="Category of news to filter by")
):
    if category:
        filtered_articles = list(collection.find({"category": category}, {"_id": 0}))
        return filtered_articles
    return list(collection.find({}, {"_id": 0}))


@app.get("/search", response_model=List[Article])
def search_news(query: str):
    search_query = {"title": {"$regex": query, "$options": "i"}}
    result = list(collection.find(search_query, {"_id": 0}))
    if not result:
        raise HTTPException(
            status_code=404, detail="No articles found for the given query"
        )
    return result


@app.post("/scrape")
def trigger_scrape():
    scrape_bbc_news()
    # scrape_bbc_Artical("https://www.bbc.com/news/articles/cv2gpx7pnwdo")
    return {"message": "Scraping completed and news articles updated"}


# Load the trained model and tokenizer
def load_model_and_tokenizer(model_path, tokenizer_path):
    model = tf.keras.models.load_model(model_path)
    with open(tokenizer_path, "rb") as handle:
        tokenizer = pickle.load(handle)
    return model, tokenizer


# model, tokenizer = load_model_and_tokenizer(MODEL_PATH, TOKENIZER_PATH)


# Define the input format using Pydantic
class TextInput(BaseModel):
    text: str


# Define the text preprocessing function
def preprocess_text(text):
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)
    return text


# Define the prediction function
def predict_sentiment(text, tokenizer, model):
    text = preprocess_text(text)
    sequence = tokenizer.texts_to_sequences([text])
    sequence = [
        seq for seq in sequence if len(seq) > 0
    ]  # Filter out empty sequences if any
    # Handle the case where the sequence might be empty
    if len(sequence) == 0:
        return "Unable to process input text."

    prediction = model.predict(sequence)[0]
    predicted_class = np.argmax(prediction)
    sentiment_labels = ["Positive", "Neutral", "Negative"]
    sentiment = sentiment_labels[predicted_class]
    return sentiment


# Define the API endpoint
@app.post("/predict")
def predict(text_input: TextInput):
    try:
        text = text_input.text
        print(text)
        print("flag1")
        model, tokenizer = load_model_and_tokenizer(MODEL_PATH, TOKENIZER_PATH)
        print("flag2")
        sentiment = predict_sentiment(text, tokenizer, model)
        return {"sentiment": sentiment}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":

    uvicorn.run(app, host="127.0.0.1", port=8000)
