Amazon Sale Sentiment Analysis & LLM Training Pipeline
Project Overview
This project automates the collection, cleaning, and sentiment analysis of Reddit discussions related to Amazon sales. It is designed to extract customer
opinions in real time, identify trending products, and prepare structured datasets for training a custom language model (LLM) focused on e-commerce 
discussions.

Problem Statement
Large-scale e-commerce events, such as Amazon sales, generate thousands of customer comments daily across online forums. Manually tracking and analyzing
these insights is inefficient and prone to error. This project addresses the challenge by:

Automating data collection from relevant Reddit threads.

Cleaning and filtering the data for better usability.

Applying sentiment analysis to gauge public opinion.

Producing a ready-to-train dataset for fine-tuning LLMs on retail-specific language.

Features
Automated scraping of Amazon sale–related posts and comments from Reddit using PRAW API.

Text cleaning and keyword-based filtering for relevance.

AI-powered sentiment analysis of customer feedback.

Storage of both raw and processed datasets in CSV format.

Data preparation for LLM training.

Project Structure
project-root/
│
├── data/
│   ├── raw/                # Raw Reddit comments from scraping
│   └── processed/          # Cleaned and sentiment-tagged data
│
├── scraper/
│   ├── reddit_scraper.py   # Step 1: Reddit data scraping script
│   ├── subreddits.txt      # List of target subreddits
│
├── processor/
│   ├── sentiment_cleaner.py # Step 2: Data cleaning and sentiment processing
│   ├── utils.py             # Helper functions for text cleaning and prompts
│
├── .env                     # Reddit API credentials
├── requirements.txt         # Python dependencies
└── README.md                # Project documentation
Workflow
Scraping – Collects posts and comments from relevant subreddits using PRAW API and stores them in data/raw/.

Processing – Cleans the text, removes unwanted content, applies keyword-based filtering, and runs sentiment analysis through an AI model.

Output – Saves processed, sentiment-tagged data to data/processed/, ready for LLM fine-tuning or analysis.

Here is the notion link for a better understanding of the bugs I fixed, dependencies installed, API used (how it was created, like PRAW), resources used also 
the next enhancements in my project Link: https://www.notion.so/chatbot-lab-228cccd15a1a800a857df5346d4fe3d3  

Real-World Applications
Market research for e-commerce trends.

Tracking customer sentiment during major sales events.

Building domain-specific chatbots for retail.

You can reach out to me if you find any difficulty in this repo 
