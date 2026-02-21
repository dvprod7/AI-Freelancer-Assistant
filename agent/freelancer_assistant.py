import requests
import json
import time

# ==============================
# CONFIG
# ==============================

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3"

INPUT_FILE = "data/profiles.txt"
OUTPUT_FILE = "data/leads.json"


# ==============================
# READ PROFILES
# ==============================

def load_profiles(filename):
    profiles = []

    with open(filename, "r", encoding="utf-8") as file:
        for line in file:
            if line.strip():
                parts = [p.strip() for p in line.split("|")]

                if len(parts) == 3:
                    profiles.append(parts)
                else:
                    print(f"⚠️ Línea ignorada (formato incorrecto): {line}")

    return profiles


# ==============================
# ASK MODEL
# ==============================

def ask_model(profile_data):
    username, description, signals = profile_data

    prompt = f"""
        You are an assistant helping a freelance web developer find clients.

        Analyze this Instagram business:

        Username: {username}
        Description: {description}
        Signals: {signals}

        Your goal:
        Create a SHORT personalized outreach message proposing a website solution.
        
        Return raw JSON only.
        Do not include explanations, markdown, or code blocks.

        Rules:
        - outreach_angle MUST be a ready-to-send DM message
        - Friendly and human tone
        - Max 2 sentences
        - Mention a website benefit
        - Do NOT sound robotic
        - Do NOT explain analysis

        Format:

        {{
        "business_type": "",
        "website_need": "Low | Medium | High",
        "outreach_angle": ""
        }}
        """

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.4
            }
        }
    )

    data = response.json()
    return data["response"]


# ==============================
# PARSE JSON SAFELY
# ==============================

def fix_json_with_ai(bad_output):
    fix_prompt = f"""
        The following response should be valid JSON but is broken.

        Fix it and return ONLY valid JSON.
        Do not explain anything.

        Broken response:
        {bad_output}
        """

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL,
            "prompt": fix_prompt,
            "stream": False,
            "options": {"temperature": 0}
        }
    )

    data = response.json()
    return data["response"]

def parse_analysis(response_text):
    try:
        start = response_text.find("{")
        end = response_text.rfind("}") + 1
        json_str = response_text[start:end]

        return json.loads(json_str)

    except Exception:
        print("⚠️ JSON broken — attempting self-heal...")

        fixed = fix_json_with_ai(response_text)

        try:
            start = fixed.find("{")
            end = fixed.rfind("}") + 1
            json_str = fixed[start:end]

            return json.loads(json_str)

        except Exception:
            print("❌ Self-heal failed.")

            return {
                "business_type": "Unknown",
                "website_need": "Unknown",
                "outreach_angle": "Failed after retry"
            }


# ==============================
# SAVE RESULTS
# ==============================

def save_results(results, filename):
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(results, file, indent=2, ensure_ascii=False)


# ==============================
# MAIN AGENT LOOP
# ==============================

def run_agent():
    profiles = load_profiles(INPUT_FILE)

    print(f"\n🚀 Profiles loaded: {len(profiles)}\n")

    results = []

    for profile in profiles:
        print(f"🔎 Processing: {profile[0]}")

        analysis_text = ask_model(profile)
        analysis_json = parse_analysis(analysis_text)

        result = {
            "username": profile[0],
            "analysis": analysis_json
        }

        results.append(result)

        # pequeña pausa para estabilidad
        time.sleep(1)

    save_results(results, OUTPUT_FILE)

    print("\n✅ Analysis complete!")
    print(f"📁 Results saved in {OUTPUT_FILE}")


# ==============================
# RUN
# ==============================

if __name__ == "__main__":
    run_agent()