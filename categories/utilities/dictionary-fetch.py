uv run --with requests --with pandas - << 'EOF'
import pandas as pd, requests, time

df = pd.read_csv("words.csv")  # column named "word"

def get_def(word):
    try:
        r = requests.get(f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}", timeout=5)
        if r.status_code == 200:
            return r.json()[0]["meanings"][0]["definitions"][0]["definition"]
    except: pass
    return ""

df["definition"] = df["word"].apply(lambda w: (time.sleep(0.1) or get_def(w)))
df.to_csv("words_with_definitions.csv", index=False)
print("Done!")
EOF