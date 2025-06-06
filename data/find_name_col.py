import pandas as pd
import spacy
import re

# Load spaCy's small English model
nlp = spacy.load("en_core_web_sm")

# Heuristic keywords for column names
PLACE_KEYWORDS = [
    "place", "location", "venue", "name", "store",
    "business", "site", "landmark", "institution", "building", "library"
]

# Entity labels that suggest place-like names
PLACE_ENTITY_LABELS = {"ORG", "FAC"}

def is_mostly_digits(s):
    return len(re.sub(r'\D', '', s)) > len(s) * 0.5

def score_column(col_name, col_values):
    score = 0

    # Skip numeric columns
    if pd.api.types.is_numeric_dtype(col_values):
        return 0

    # Clean
    clean_values = col_values.dropna().astype(str)
    clean_values = clean_values[clean_values.str.strip() != ""]

    # If empty after cleaning, skip
    if len(clean_values) == 0:
        return 0

    # Skip if most values are numeric-looking
    mostly_digits_ratio = clean_values.map(is_mostly_digits).mean()
    if mostly_digits_ratio > 0.8:
        return 0

    # Heuristic 1: Column name contains keyword
    if any(keyword in col_name.lower() for keyword in PLACE_KEYWORDS):
        score += 1.5  # slightly stronger boost

    # Filter long phrases (likely descriptions)
    avg_word_count = clean_values.map(lambda x: len(x.split())).mean()
    if avg_word_count > 6:
        return 0  # too verbose

    # Sample values
    sample = clean_values.sample(min(10, len(clean_values)), random_state=42)

    # Heuristic 2: NER
    entity_hits = 0
    capitalized_hits = 0
    for val in sample:
        doc = nlp(val)
        entity_hits += sum(ent.label_ in PLACE_ENTITY_LABELS for ent in doc.ents)

        if val == val.upper() or val.istitle() or re.search(r'[A-Z]{2,}', val):
            capitalized_hits += 1

    score += entity_hits / len(sample)
    score += 0.5 * (capitalized_hits / len(sample))  # modest boost for all caps/title case

    return score


def find_place_name_column(df: pd.DataFrame) -> str | None:
    best_col = None
    best_score = 0.0  # Require a positive score to return something

    for col in df.columns:
        score = score_column(col, df[col])
        if score > best_score:
            best_score = score
            best_col = col

    return best_col if best_score > 0 else None

def load_datasets(datasets):
    """
    Load datasets from the provided URLs.
    """
    lst = []
    for name, url in datasets.items():
        try:
            lst.append(pd.read_csv(url))
            print(f"Loaded {name} with {len(datasets[name])} rows.")
        except Exception as e:
            print(f"Failed to load {name}: {e}")
    
    return lst

if __name__ == "__main__":

    # datasets = {
    # "sbs_businesses": "https://data.cityofnewyork.us/resource/ci93-uc8s.csv",
    # "nyc_pois": "https://data.cityofnewyork.us/api/views/t95h-5fsr/rows.csv?date=20250523&accessType=DOWNLOAD",
    # "nyc_restaurants": "https://data.cityofnewyork.us/resource/43nn-pn8j.csv"
    # }

    #dfs = load_datasets(datasets)

    df = pd.read_csv("https://data.cityofnewyork.us/resource/43nn-pn8j.csv")
    print(df.head())
    best_col = find_place_name_column(df)
    print(best_col)  # Should output 'business_name'

    """
    ## Ex Usage
    data = {
        "id": [1, 2, 3],
        "business name": ["Taco Bell", "UT Austin Library", "Starbucks"],
        "first name": ["Githika A", "Ryan O", "Jack B"],
        "zip": [73301, 94103, 60616]
    }
    df = pd.DataFrame(data)

    best_col = find_place_name_column(df)
    print(best_col)  # Should output 'business_name'
    """

