# app/scraping.py
import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
import random
from DataSchemas.BBC import BBC
import os
from constants import user_agents
from Database.dbconnection import get_db_connection
import dotenv

dotenv.load_dotenv()

MONGO_DB_KEY = os.getenv("MONGO_DB_KEY")


db = get_db_connection()
collection = db.articles


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

    for link in links:
        Article = BBC(link)
        articles.append(Article.to_json())

    collection.delete_many({})
    if articles:
        collection.insert_many(articles)
