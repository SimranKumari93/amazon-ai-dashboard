import pandas as pd
import openai
import os
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Load processed data
df = pd.read_csv("data/processed/fab_tv_sale_sentiment.csv")

# Group comments by product
grouped = df.groupby("product")

insights = []

for product, group in grouped:
    comments = "\n".join(group["cleaned_comment"].dropna().tolist())

    prompt = f"""
You are a product analyst. Analyze these customer comments for the product: {product}.

Comments:
{comments}

Based on the above, give:
1. Summary of what users like.
2. Summary of common complaints.
3. One actionable improvement to increase sales.
    """.strip()

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        summary = response.choices[0].message.content.strip()
    except Exception as e:
        summary = f"Error generating summary: {e}"

    insights.append({"product": product, "insight": summary})

# Save to CSV
output_df = pd.DataFrame(insights)
os.makedirs("data/insights", exist_ok=True)
output_df.to_csv("data/insights/fab_tv_insights.csv", index=False)

print("✅ Insights generated and saved.")
