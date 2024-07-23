import os

os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
from fastapi import FastAPI, HTTPException, Query
import uvicorn
from contextlib import asynccontextmanager
from Classification.classification import SentimentAnalysis
from Scrapping.datascrapping import (
    scrape_bbc_news,
)
from Classification.classifynews import classify_news, get_articles_by_category


from DataSchemas.BBC import BBCModel
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.memory import MemoryJobStore
from typing import List, Optional
from dotenv import load_dotenv

load_dotenv()

jobstores = {"default": MemoryJobStore()}
scheduler = AsyncIOScheduler(jobstores=jobstores, timezone="Asia/Kolkata")


@asynccontextmanager
async def app_lifespan(app: FastAPI):
    scheduler.start()

    yield
    scheduler.shutdown()


app = FastAPI(lifespan=app_lifespan)

###################################
#####################################
# Define paths to the saved model and tokenizer also added in constants
MODEL_PATH = "./MLmodel/gru_model.h5"
TOKENIZER_PATH = "./MLmodel/tokenizer.pkl"

# Load model and tokenizer
sentiment_analysis = SentimentAnalysis()
model = sentiment_analysis.model
tokenizer = sentiment_analysis.tokenizer


# # Job running daily at 9:30:00
@scheduler.scheduled_job("cron", day_of_week="mon-sun", hour=9, minute=30, second=0)
@app.post("/scrape")
def trigger_scrape():
    scrape_bbc_news()
    return {"message": "Scraping completed and news articles updated"}


@app.post("/predict")
def predict(bbc_model: BBCModel):
    try:
        text = bbc_model.body
        if not text:
            raise HTTPException(
                status_code=400, detail="Text body is missing from the input"
            )
        sentiment = sentiment_analysis.predict(text)
        return {"sentiment": sentiment}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/classify-news")
def classify_news_endpoint():
    try:
        result = classify_news()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get(
    "/articles/{category}",
    response_model=List[BBCModel],
)
def get_articles_by_category_endpoint(category: Optional[str] = None):
    try:
        if category is None:
            category = "Neutral News"
        result = get_articles_by_category(category)
        print(result)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e),
            headers={"X-Error": "There was an error processing the request."},
        )


if __name__ == "__main__":

    uvicorn.run(app, host="127.0.0.1", port=8000)
