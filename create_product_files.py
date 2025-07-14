import os, json, pandas as pd

# Ensure the raw folder exists
os.makedirs("data/raw", exist_ok=True)

# Load all events you listed
with open("data/raw/sale_events.json", "r", encoding="utf-8") as f:
    events = json.load(f)

# Create an empty template CSV for every event
for ev in events:
    slug = ev["name"].lower().replace(" ", "_").replace("’", "").replace("'", "")
    path = f"data/raw/products_{slug}.csv"
    if not os.path.exists(path):
        pd.DataFrame(columns=["product_name"]).to_csv(path, index=False)
        print(f"✅ Created {path}")
    else:
        print(f"ℹ️ {path} already exists")
