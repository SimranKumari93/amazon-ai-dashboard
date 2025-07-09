def get_subreddits(filepath="scraper/subreddits.txt"):
    with open(filepath, "r") as file:
        return [line.strip() for line in file.readlines() if line.strip()]

# Example usage
subreddits = get_subreddits()
print(subreddits)