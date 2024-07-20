import requests
from bs4 import BeautifulSoup
import random
from constants import user_agents
from datetime import date,datetime
import json


class BBC:

    def __init__(self, url, category="General"):
        self.url = url
        self.category = category
        self.date = date.today()
        self.header = None
        self.body = None
        self.soup = None
        self.scrape()

    def scrape(self):
        headers = {"User-Agent": random.choice(user_agents)}

        response = requests.get(self.url, headers=headers)
        self.soup = BeautifulSoup(response.content, "html.parser")
        self.header = self.get_header(self.soup)
        self.body = self.get_body(self.soup)

    def get_header(self, soup):
        # Adjust the CSS selector according to the actual HTML structure
        header_tag = soup.find("h1")
        if header_tag:
            return header_tag.get_text().strip()
        return None

    def get_body(self, soup):
        text_block_div = soup.find("div", {"data-component": "text-block"})
        if text_block_div:
            paragraphs = text_block_div.find_all("p")
            return " ".join([p.get_text().strip() for p in paragraphs])
        return None

    def get_url(self):
        return self.url

    def get_category(self):
        return self.category

    def to_json(self):
        date_datetime = datetime(self.date.year, self.date.month, self.date.day)
        return {
            "url": self.get_url(),
            "category": self.get_category(),
            "date": date_datetime,
            "header": self.get_header(self.soup),
            "body": self.get_body(self.soup),
        }
