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
        search_results = ddgs.text(query, max_results=20)

        for r in search_results:
            url = r.get("href", "")
            title = r.get("title", "")

            if "instagram.com" in url:
                username = extract_username(url)

                if username:

                    description_hint = clean_title(title)

                    print(f"🔍 Checking website for {username}...")

                    have_web = detect_website(username)
                    
                    print(f"FOUND PROFILE: {username} | website={have_web}")
                    
                    # SOLO leads sin web
                    if have_web == "no website":
                        profile = f"{username} | {description_hint} | {have_web}"
                        results.append(profile)
                    else:
                        print(f"⛔ Skipped {username} (has website)")

    return results[:MAX_LEADS_PER_KEYWORD]

def detect_website(username):
    query = f'"{username}"'

    with DDGS() as ddgs:
        results = ddgs.text(query, max_results=5)

        for r in results:
            url = r.get("href", "")

            # ignoramos redes sociales
            if any(domain in url for domain in [
                "instagram.com",
                "facebook.com",
                "tiktok.com",
                "youtube.com",
                "linkedin.com"
            ]):
                continue

            # si encontramos dominio externo → tiene web
            if "." in url:
                return "has website"

    return "no website"

def clean_title(title):
    title = title.lower()

    # quitar texto típico de resultados IG
    title = title.replace("• instagram photos and videos", "")
    title = re.sub(r"\(@.*?\)", "", title)

    # limpiar símbolos raros
    title = re.sub(r"[^a-zA-Záéíóúñ0-9\s]", " ", title)

    # espacios múltiples
    title = re.sub(r"\s+", " ", title).strip()

    return title


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