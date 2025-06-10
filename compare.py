import pandas as pd
import re
import ast
import openai
from dotenv import load_dotenv
import os
from sentence_transformers import SentenceTransformer, util

load_dotenv()
OPEN_AI_KEY = os.getenv("OPENAI_API_KEY")
model = SentenceTransformer('all-MiniLM-L6-v2')

def llm_verify_name_match(overture_name, other_name):
    prompt = f"""
    Are the following two business names likely referring to the same place?
    1. \"{overture_name}\"
    2. \"{other_name}\"
    Reply only \"Yes\" or \"No\".
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
    match = re.match(r"^(\d+)\s+([a-zA-Z\s]+)", address)
    if match:
        number = match.group(1)
        street = match.group(2).lower().strip()
        return number, street
    return None, None

def compare_n(overture_dataset_path, other_dataset_path, save_path):
    overture_df = pd.read_csv(overture_dataset_path)
    other_df = pd.read_csv(other_dataset_path)

    overture_discrepancy_rows = []
    other_discrepancy_rows = []

    # # bbox too big overture data is empty
    # if overture_df.empty:
    #     pd.DataFrame(overture_discrepancy_rows).to_csv(save_path + '/discrepancies_from_overture.csv', index=False)
    #     pd.DataFrame(other_discrepancy_rows).to_csv(save_path + '/discrepancies_from_other.csv', index=False)
    #     return

    other_address_map = {}
    for _, row in other_df.iterrows():
        unique_address = row['unique_address']
        number, street = parse_address1(unique_address)
        if number and street:
            key = (number, street)
            other_address_map.setdefault(key, []).append(row)


    for _, row in overture_df.iterrows():
        try:
            address_list = ast.literal_eval(row['addresses'])
            freeform_address = address_list[0]['freeform'] if address_list else None
        except Exception:
            continue

        if freeform_address:
            number, street = parse_address1(freeform_address)
            if number and street:
                key = (number, street)
                if key in other_address_map:
                    candidates = other_address_map[key]
                    name_dict = ast.literal_eval(row['names']) if isinstance(row['names'], str) else row['names']
                    overture_name = name_dict.get('primary', 'Unknown')

                    best_match, best_score = None, 0
                    for other_row in candidates:
                        other_name = other_row['unique_name']
                        embeddings = model.encode([overture_name.lower(), other_name.lower()])
                        score = util.cos_sim(embeddings[0], embeddings[1]).item() * 100

                        if score > best_score:
                            best_match, best_score = other_row, score

                    if best_score >= 80 or (60 <= best_score < 80 and llm_verify_name_match(overture_name, best_match['unique_name'])):
                        continue
                    else:
                        overture_discrepancy_rows.append({
                            'address': freeform_address,
                            'name': overture_name,
                            'similarity': best_score
                        })
                        other_discrepancy_rows.append({
                            'address': best_match['unique_address'] if best_match is not None else '(no match)',
                            'name': best_match['unique_name'] if best_match is not None else '(no match)',
                            'similarity': best_score
                        })

    pd.DataFrame(overture_discrepancy_rows).to_csv(save_path + '/discrepancies_from_overture.csv', index=False)
    pd.DataFrame(other_discrepancy_rows).to_csv(save_path + '/discrepancies_from_other.csv', index=False)

    return {
        'overture_discrepancy_rows': overture_discrepancy_rows,
        'other_dataset_discrepancy_rows': other_discrepancy_rows
    }

# if __name__ == "__main__":
#     result = compare_n('./tmp/sample_nyc/overture_data.csv', './tmp/sample_nyc/sample_nyc_edited.csv', "./tmp/sample_nyc/")

#     pd.DataFrame(result['overture_discrepancy_rows']).to_csv('overture_discrepancy_rows.csv', index=False)
#     pd.DataFrame(result['other_dataset_discrepancy_rows']).to_csv('other_dataset_discrepancy_rows.csv', index=False)


