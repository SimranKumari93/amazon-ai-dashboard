# Amazon Sale Sentiment Analysis & LLM Training Pipeline

## Project Overview

This project automates the **collection, cleaning, and sentiment analysis** of Reddit discussions related to **Amazon sales**.
It extracts customer opinions, identifies trending products, and prepares structured datasets for **training a custom LLM** specialized in e-commerce discussions.

---

## Problem Statement

Large-scale e-commerce events (e.g., Amazon Great Indian Festival, Prime Day) generate **thousands of customer comments** daily on online forums.
Manually tracking and analyzing them is **slow and error-prone**.

This project solves that problem by:

* Automating Reddit data collection from sale-related discussions.
* Cleaning and filtering data for **only relevant insights**.
* Applying **AI sentiment analysis** to gauge public opinion.
* Producing datasets ready for **LLM fine-tuning** in retail-specific contexts.

---

## Features

* Automatic Reddit comment scraping via **PRAW API**.
* Text cleaning & relevance filtering.
* AI-powered **sentiment classification**.
* Raw and processed data saved in CSV format.
* Ready-to-train datasets for custom LLMs.

---

## Project Structure

```
project-root/
│
├── data/
│   ├── raw/                # Raw Reddit comments
│   └── processed/          # Cleaned + sentiment-tagged data
│
├── scraper/
│   ├── reddit_scraper.py   # Step 1: Data scraping
│   ├── subreddits.txt      # Target subreddits list
│
├── processor/
│   ├── sentiment_cleaner.py # Step 2: Cleaning + Sentiment
│   ├── utils.py             # Helper functions
│
├── .env                     # Reddit API credentials
├── requirements.txt         # Dependencies
└── README.md                # Documentation
```

---

## Workflow

1. **Scraping** → Collect Reddit posts & comments from target subreddits.
2. **Processing** → Clean, filter, and analyze sentiment.
3. **Output** → Store final dataset in `data/processed/` for LLM training.

---

## Here is the notion
link: https://www.notion.so/chatbot-lab-228cccd15a1a800a857df5346d4fe3d3
In this template, I have added all the bugs that I got during this project and how I resolved them. Each and every step is written, also what the dependencies, resources, and APIs.
Install all with:

```bash
pip install -r requirements.txt
```

---

## APIs Used

* **Reddit API** (via PRAW) – Fetch posts/comments.
* **Custom AI API** – Sentiment classification.
---

## Known Issues

* “No comments found” if keywords are missing in posts.
* API rate limits may interrupt long scrapes.
* Sarcasm/mixed sentiment can cause misclassification.
---

## Resources

* [PRAW Docs](https://praw.readthedocs.io/)
* [Reddit API Reference](https://www.reddit.com/dev/api/)
* [Pandas Docs](https://pandas.pydata.org/)
* [Requests Docs](https://requests.readthedocs.io/)

---

## Real-World Applications

* **Market research** for e-commerce trends.
* Tracking **customer sentiment** during big sales.
* Building **domain-specific chatbots** for retail.

---
Feel free to reach out to simrankumaribodhgaya93@gmail.com if you have any queries 
