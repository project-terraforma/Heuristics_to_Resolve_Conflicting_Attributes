import pandas as pd
import re
import ast
from rapidfuzz import fuzz
import openai
from dotenv import load_dotenv
import os

load_dotenv()
OPEN_AI_KEY = os.getenv("OPENAI_API_KEY")

def llm_verify_name_match(overture_name, other_name):
    """Ask LLM if two names refer to the same place."""
    prompt = f"""
        Are the following two business names likely referring to the same place?
        1. "{overture_name}"
        2. "{other_name}"
        Reply only "Yes" or "No".
        """

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0125",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            max_tokens=5
        )
        reply = response.choices[0].message['content'].strip().lower()
        return "yes" in reply
    except Exception as e:
        print("LLM verification failed:", e)
        return False
    
def parse_address1(address):
    """Extract number and lowercase street name from a freeform address."""
    match = re.match(r"^(\d+)\s+([a-zA-Z\s]+)", address)
    if match:
        number = match.group(1)
        street = match.group(2).lower().strip()
        return number, street
    return None, None

def compare_n(overture_dataset_path, other_dataset_path):
    # Load datasets
    overture_df = pd.read_csv(overture_dataset_path)
    other_df = pd.read_csv(other_dataset_path)

    # Create a map from (number, street) to list of businesses for other_df
    other_address_map = {}
    for _, row in other_df.iterrows():
        unique_address = row['unique_address']
        number, street = parse_address1(unique_address)
        if number and street:
            key = (number, street)
            other_address_map.setdefault(key, []).append(row)

    # Output containers
    matched_names_overture = []
    matched_names_other = []
    overture_discrepancy_rows = []
    other_discrepancy_rows = []

    # Process overture_df
    for _, row in overture_df.iterrows():
        try:
            address_list = ast.literal_eval(row['addresses'])
            if isinstance(address_list, list) and len(address_list) > 0:
                freeform_address = address_list[0]['freeform']
        except Exception:
            continue  # Skip malformed rows

        if freeform_address:
            number, street = parse_address1(freeform_address)
            if number and street:
                key = (number, street)
                if key in other_address_map:
                    candidates = other_address_map[key]

                    name_dict = ast.literal_eval(row['names']) if isinstance(row['names'], str) else row['names']
                    overture_name = name_dict.get('primary', 'Unknown')

                    # Find best match
                    best_match = None
                    best_score = 0
                    for other_row in candidates:
                        other_name = other_row['unique_name']
                        score = fuzz.token_sort_ratio(overture_name.lower(), other_name.lower())
                        if score > best_score:
                            best_score = score
                            best_match = other_row

                    if best_match is not None and best_score >= 80:
                        matched_names_overture.append(overture_name)
                        matched_names_other.append(best_match['unique_name'])
                    elif best_match is not None and best_score >= 60:
                        is_llm_match = llm_verify_name_match(overture_name, best_match['unique_name'])
                        if is_llm_match:
                            matched_names_overture.append(overture_name)
                            matched_names_other.append(best_match['unique_name'])
                        else:
                            overture_discrepancy_rows.append({
                                'address': freeform_address,
                                'name': overture_name,
                                'similarity': best_score
                            })
                            other_discrepancy_rows.append({
                                'address': best_match['unique_address'],
                                'name': best_match['unique_name'],
                                'similarity': best_score
                            })
                    elif best_match is not None:
                        overture_discrepancy_rows.append({
                            'address': freeform_address,
                            'name': overture_name,
                            'similarity': best_score
                        })
                        other_discrepancy_rows.append({
                            'address': best_match['unique_address'],
                            'name': best_match['unique_name'],
                            'similarity': best_score
                        })
                    else:
                        # fallback if no valid candidate was found
                        overture_discrepancy_rows.append({
                            'address': freeform_address,
                            'name': overture_name,
                            'similarity': 0
                         })
                        other_discrepancy_rows.append({
                            'address': '(no match)',
                            'name': '(no match)',
                            'similarity': 0
                        })


    return {
        'overture_discrepancy_rows': overture_discrepancy_rows,
        'other_dataset_discrepancy_rows': other_discrepancy_rows
    }

def recheck_other_discrepancies(overture_df, other_discrepancy_rows):
    print("\n🔁 Rechecking discrepancies...")

    # Build overture map
    overture_address_map = {}
    for _, row in overture_df.iterrows():
        try:
            address_list = ast.literal_eval(row['addresses'])
            if isinstance(address_list, list) and len(address_list) > 0:
                freeform = address_list[0]['freeform']
                number, street = parse_address1(freeform)
                if number and street:
                    key = (number, street)
                    overture_address_map.setdefault(key, []).append(row)
        except:
            continue

    rechecked_matches = []

    for row in other_discrepancy_rows:
        other_address = row['address']
        other_name = row['name']

        number, street = parse_address1(other_address)
        if number and street:
            key = (number, street)
            candidates = overture_address_map.get(key, [])
            for overture_row in candidates:
                try:
                    name_dict = ast.literal_eval(overture_row['names']) if isinstance(overture_row['names'], str) else overture_row['names']
                    overture_name = name_dict.get('primary', 'Unknown')

                    if not isinstance(overture_name, str) or not isinstance(other_name, str):
                        continue

                    score = fuzz.token_sort_ratio(overture_name.lower(), other_name.lower())

                    if score >= 80:
                        rechecked_matches.append((other_name, overture_name, key, score, "fuzzy"))
                        break
                    elif score >= 60:
                        if llm_verify_name_match(other_name, overture_name):
                            rechecked_matches.append((other_name, overture_name, key, score, "llm"))
                            break
                except:
                    continue

    # print("\n✅ Matches found on recheck:")
    # for other_name, overture_name, key, score, method in rechecked_matches:
    #     print(f" - Address: {key}")
    #     print(f" - Other:   {other_name}")
    #     print(f" - Overture:{overture_name}")
    #     print(f" - Score:   {score} ({method})\n")

    return rechecked_matches


if __name__ == "__main__":
    result = compare_n('./tmp/sample_nyc/overture_data.csv', './tmp/sample_nyc/sample_nyc_edited.csv')

    overture_df = pd.read_csv('./tmp/sample_nyc/overture_data.csv')
    recheck_other_discrepancies(overture_df, result['other_dataset_discrepancy_rows'])

    pd.DataFrame(result['overture_discrepancy_rows']).to_csv('discrepancies_from_overture.csv', index=False)
    pd.DataFrame(result['other_dataset_discrepancy_rows']).to_csv('discrepancies_from_other.csv', index=False)

