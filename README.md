# Building an AI-Powered Dashboard for Sentiment Analysis of Amazon.in Sale Event Products Using Reddit Feedback

## Problem Statement

To develop a dashboard powered by an AI language model that provides actionable insights from Reddit comments about products sold during specific Amazon.in sale events. By scraping sale-specific Reddit discussions, the system will classify sentiment, extract user feedback, and recommend improvements to enhance product quality, increase customer satisfaction, and boost future sales performance.

## 🔧 PHASE 1: Define Scope & Requirements

### Identify Target Sale Events
- **Example:** "Amazon Fab TV Sale (June 1–10)"
- Note sale names, dates, and product categories

### Define Product List per Sale
- Use Amazon's official sale pages (manually or via web scraping) to get products sold during each event

## 📥 PHASE 2: Data Collection

### Reddit Data Scraping (PRAW)
- Use **PRAW** to scrape posts and comments from subreddits like:
  - r/IndianGaming
  - r/IndiaDeals
  - r/AmazonIndia
  - r/AskIndia, etc.

- Filter posts/comments by:
  - Sale dates (e.g., June 1–10)
  - Keywords: ["Amazon", "Fab TV Sale", product names, etc.]

### Store Raw Data
- Save scraped data into a database or CSV (include timestamp, username, comment body, post title, subreddit, etc.)

## 🧠 PHASE 3: Preprocess & Clean the Data

### Data Cleaning (Python)
- Remove spam, bot comments, emojis, URLs, non-English comments
- Normalize text (lowercase, punctuation removal, etc.)

### Label or Annotate Sentiment (Optional)
- If training your own model: Use tools like Prodigy or label manually
- Or skip if using OpenAI/Gemini API for zero-shot/few-shot classification

## 🤖 PHASE 4: AI/LLM Integration

### Using OpenAI for Sentiment & Insight Extraction
- Use **Chat Completion API** via Python or curl to:
  - Classify sentiment (positive/negative/neutral)
  - Extract complaints/suggestions/praise
  - Tag product names and issues (e.g., "Remote not working", "Delivery delay")

### Example Prompt (for ChatGPT API):
*[Note: The specific prompt example would be included in the original presentation but isn't fully visible in the provided content]*

## 📊 PHASE 5: Dashboard Development

### Backend (Python FastAPI)
- Serve processed data (JSON API with product names, sentiments, feedback, suggestions)

### Frontend (React.js or Dash/Streamlit)
Build visual dashboard with:
- Sentiment trends per product
- Common complaints/praises (word cloud, tags)
- Suggested improvements
- Filter by product, date, sentiment, category

## Example Reddit Discussion Links

Here are some example Reddit discussions related to Amazon sales that could be used for data collection:

1. [Great savings on Amazon Republic Day sale](https://www.reddit.com/r/indiasocial/comments/198x3cd/great_savings_on_amazon_republic_day_sale/?utm_source=share&utm_medium=web3x&utm_name=web3xcss&utm_term=1&utm_content=share_button)

2. [Great India Sale by Amazon](https://www.reddit.com/r/IndiaTech/comments/1fkjcp7/great_india_sale_by_amazon/?utm_source=share&utm_medium=web3x&utm_name=web3xcss&utm_term=1&utm_content=share_button)

3. [Is Amazon fooling us with Republic Day sale?](https://www.reddit.com/r/IndiaPS5/comments/1hzugqr/is_amazon_fooling_us_with_republic_day_sale/?utm_source=share&utm_medium=web3x&utm_name=web3xcss&utm_term=1&utm_content=share_button)

4. [Best gaming laptops to buy during the Republic Day sale](https://www.reddit.com/r/IndianGaming/comments/195ml77/best_gaming_laptops_to_buy_during_the_republic/?utm_source=share&utm_medium=web3x&utm_name=web3xcss&utm_term=1&utm_content=share_button)

5. [How does Amazon pay insane joining bonus?](https://www.reddit.com/r/developersIndia/comments/1atae2b/how_does_amazon_pay_insane_joining_bonus/?utm_source=share&utm_medium=web3x&utm_name=web3xcss&utm_term=1&utm_content=share_button)

***
