import pandas as pd , re, os, openai
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# ⬇️ Change this to your event slug (match your CSV file)
slug = "fab_tv_sale"

# Load data
input_path = f"data/raw/{slug}_reddit_comments.csv"
output_path = f"data/processed/{slug}_sentiment.csv"

df = pd.read_csv(input_path)

# Clean comment text
def clean_comment(text):
    text = re.sub(r"http\S+", "", text)          # remove URLs
    text = re.sub(r"[^A-Za-z0-9\s]", "", text)   # remove symbols
    text = re.sub(r"\s+", " ", text).strip()     # normalize spaces
    return text

df["cleaned_comment"] = df["comment"].astype(str).apply(clean_comment)

# Analyze sentiment using OpenAI
def get_sentiment(comment):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # or "gpt-4"
            messages=[{
                "role": "user",
                "content": f"Classify the sentiment of this comment as Positive, Negative, or Neutral:\n\n\"{comment}\""
            }],
            temperature=0
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return "Error"

df["sentiment"] = df["cleaned_comment"].apply(get_sentiment)

# Save processed output
os.makedirs("data/processed", exist_ok=True)
df.to_csv(output_path, index=False)
print(f"✅ Sentiment file saved to {output_path}")

# import re
# import os 
# import openai
# import pandas as pd
# from dotenv import load_dotenv
# from textblob import TextBlob

# load_dotenv() 
# openai.api_key = os.getenv("OPENAI_API_KEY")


# # Load data
# df = pd.read_csv("data/raw/fab_tv_sale_reddit_comments.csv")

# # Clean function
# def clean_text(text):
#     text = re.sub(r"http\S+|www\S+|https\S+", "", text)  # remove URLs
#     text = re.sub(r"[^A-Za-z0-9\s]", "", text)  # remove special chars
#     text = re.sub(r"\s+", " ", text)  # collapse whitespace
#     return text.strip().lower()

# # Apply cleaning
# df["cleaned_comment"] = df["comment"].astype(str).apply(clean_text)

# # Sentiment tagging
# def get_sentiment(text):
#     polarity = TextBlob(text).sentiment.polarity
#     if polarity > 0.1:
#         return "positive"
#     elif polarity < -0.1:
#         return "negative"
#     else:
#         return "neutral"

# df["sentiment"] = df["cleaned_comment"].apply(get_sentiment)

# # Ensure the output directory exists
# os.makedirs("data/processed", exist_ok=True)

# # Save final sentiment dataframe
# df.to_csv("data/processed/fab_tv_sale_sentiment.csv", index=False)
# print("✅ Sentiment analysis complete. Data saved.")