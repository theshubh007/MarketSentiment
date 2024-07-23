# MarketSentiment

MarketSentiment is a powerful tool designed to analyze and classify financial and business news based on sentiment. By leveraging advanced natural language processing techniques, it provides insights into the sentiment of news articles, categorizing them as Positive, Neutral, or Negative. This enables investors, analysts, and decision-makers to quickly gauge market sentiment and make informed decisions.

## Problem It Solves

- In the fast-paced world of finance and business, staying updated with the latest news and understanding its impact is crucial. However, manually sifting through vast amounts of news to gauge sentiment is time-consuming and inefficient. MarketSentiment automates this process, providing quick and accurate sentiment analysis, thus saving time and offering valuable insights for better decision-making.


## Features

- **Automated Sentiment Analysis:** Automatically classify news articles into Positive, Neutral, or Negative categories.
- **Real-Time Analysis:** Fetch and analyze news articles from reliable sources in real-time.
- **Database Integration:** Store and retrieve news articles with sentiment classifications from MongoDB.
- **FastAPI Integration:** Easily access the sentiment analysis via API endpoints.
- **Scheduler:** Regularly scrape and update news articles for the latest sentiment analysis.

## Workflow Overview

#### 1. Scrape News Articles:
- Triggered automatically daily or manually via the /scrape endpoint.
- Scrapes articles from specified news sources (e.g., BBC News).
- Stores scraped articles in MongoDB.

#### 2.Classify Articles by Sentiment:
- Fetches all articles from MongoDB.
- Applies the sentiment analysis model to classify each article as Positive, Neutral, or Negative
- Updates the sentiment classification in MongoDB.

#### 3.Retrieve Classified Articles:
- Use the api endpoint to retrieve articles based on their sentiment.

#### 4.Predict Sentiment of Custom Text:
- Use the /predict endpoint to predict the sentiment of custom input text.
- The input text is processed and classified using the sentiment analysis model.




## Installation

#### Follow this commands to test this project

#### 1. Clone the repository:

```

```

#### 2. Install the required packages:

```
  pip install -r requirements.txt
```

#### 3. Set up MongoDB:
- Create a MongoDB Atlas account and get the connection URI.
- Set the connection URI in the environment variables.

#### 4. Run the application:
```
uvicorn main:app --reload
```

## Usage:



#### 1.Scrape and Update News Articles in MongoDB
- Method: POST
```
http://localhost:8000/scrape
```

#### 2. Get News Articles by Sentiment Category
- Method: GET
- categories = ["Positive News", "Negative News", "Neutral News"]

```
http://localhost:8000/articles/?{category}
```

#### 3. Predict Sentiment of a Text
- Method: POST

```
http://localhost:8000/predict
```
- Body format: Json
```
{
    "url": "https://www.bbc.com/news/article/12345",
    "category": "Politics",
    "date": "2024-07-22",
    "header": "Example Header",
    "body": "This is the body of the article that contains text to analyze."
}
```


## Contributing

Contributions are welcome! Please submit a pull request or open an issue to discuss improvements or features.