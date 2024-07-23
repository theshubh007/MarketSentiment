import tensorflow as tf
import pickle
import numpy as np
import re


class SentimentAnalysis:
    def __init__(self):
        self.model_path = "./MLmodel/gru_model.h5"
        self.tokenizer_path = "./MLmodel/tokenizer.pkl"
        self.model, self.tokenizer = self.load_model_and_tokenizer()

    def load_model_and_tokenizer(self):
        model = tf.keras.models.load_model(self.model_path)
        with open(self.tokenizer_path, "rb") as handle:
            tokenizer = pickle.load(handle)
        return model, tokenizer

    def preprocess_text(self, text):
        text = text.lower()
        text = re.sub(r"[^\w\s]", "", text)
        return text

    def predict(self, text):
        text = self.preprocess_text(text)
        sequence = self.tokenizer.texts_to_sequences([text])
        sequence = [seq for seq in sequence if len(seq) > 0]
        if len(sequence) == 0:
            return "Unable to process input text."
        prediction = self.model.predict(sequence)[0]
        predicted_class = np.argmax(prediction)
        sentiment_labels = ["Positive", "Neutral", "Negative"]
        sentiment = sentiment_labels[predicted_class]
        return sentiment
