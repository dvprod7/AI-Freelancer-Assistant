from duckduckgo_search import DDGS
from pathlib import Path
import re

OUTPUT_FILE = "data/profiles.txt"

MAX_LEADS_PER_KEYWORD = 3
MAX_TOTAL_LEADS = 10


# ==========================
# LOAD KEYWORDS
# ==========================

def load_keywords():
    with open("data/keywords.txt", "r", encoding="utf-8") as f:
        return [k.strip() for k in f if k.strip()]


# ==========================
# SEARCH WEB
# ==========================

def search_instagram_profiles(keyword):
    results = []

    query = f"{keyword} instagram"

    with DDGS() as ddgs:
        search_results = ddgs.text(query, max_results=15)

        for r in search_results:
            url = r.get("href", "")

            if "instagram.com" in url:
                username = extract_username(url)

                if username:
                    profile = f"{username} | negocio local | sin sitio web"
                    results.append(profile)

    return results[:MAX_LEADS_PER_KEYWORD]


# ==========================
# EXTRACT USERNAME
# ==========================

def extract_username(url):
    match = re.search(r"instagram\.com/([^/?]+)", url)
    if match:
        return match.group(1)
    return None


# ==========================
# SAVE PROFILES
# ==========================

def save_profiles(profiles):
    Path("data").mkdir(exist_ok=True)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for p in profiles:
            f.write(p + "\n")


# ==========================
# RUN FINDER
# ==========================

def run():
    keywords = load_keywords()
    all_profiles = []

    for keyword in keywords:

        if len(all_profiles) >= MAX_TOTAL_LEADS:
            break

        print(f"🔎 Searching real leads: {keyword}")

        results = search_instagram_profiles(keyword)

        all_profiles.extend(results)

    all_profiles = all_profiles[:MAX_TOTAL_LEADS]

    save_profiles(all_profiles)

    print("✅ Real profiles.txt generated")


if __name__ == "__main__":
    run()