import pandas as pd
import re
import ast
from rapidfuzz import fuzz

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

    # Create a map from (number, street) to row for other_df (the smaller dataset)
    other_address_map = {}
    for _, row in other_df.iterrows():
        unique_address = row['unique_address']
        number, street = parse_address1(unique_address)
        if number and street:
            key = (number, street)
            other_address_map[key] = row

    # Output containers
    matched_names_overture = []
    matched_names_other = []

    overture_discrepancy_rows = []
    other_discrepancy_rows = []

    # Process overture_df
    for _, row in overture_df.iterrows():
        try:
            address_list = ast.literal_eval(row['addresses'])  # Safe parsing
            if isinstance(address_list, list) and len(address_list) > 0:
                freeform_address = address_list[0]['freeform']
        except Exception:
            continue  # skip malformed rows

        if freeform_address:
            number, street = parse_address1(freeform_address)
            if number and street:
                key = (number, street)
                if key in other_address_map:
                    other_row = other_address_map[key]
                    # Parse name field
                    name_dict = ast.literal_eval(row['names']) if isinstance(row['names'], str) else row['names']
                    overture_name = name_dict.get('primary', 'Unknown')
                    other_name = other_row['unique_name']

                    # Semantic comparison
                    similarity = fuzz.token_sort_ratio(overture_name, other_name)

                    if similarity >= 80:
                        matched_names_overture.append(overture_name)
                        matched_names_other.append(other_name)
                    else:
                        overture_discrepancy_rows.append({
                            'address': freeform_address,
                            'name': overture_name,
                            'similarity': similarity
                        })
                        other_discrepancy_rows.append({
                            'address': other_row['unique_address'],
                            'name': other_name,
                            'similarity': similarity
                        })

    print("\n✅ Matched Names:")
    for o, r in zip(matched_names_overture, matched_names_other):
        print(f" - Overture: {o}")
        print(f" - Other:    {r}\n")

    return {
        'overture_discrepancy_rows': overture_discrepancy_rows,
        'other_dataset_discrepancy_rows': other_discrepancy_rows
    }

# Example usage
if __name__ == "__main__":
    result = compare_n('./tmp/sample_nyc/overture_data.csv', './tmp/sample_nyc/sample_nyc_edited.csv')

    # Optional: export discrepancies to a CSV or JSON for Streamlit use
    pd.DataFrame(result['overture_discrepancy_rows']).to_csv("overture_discrepancies.csv", index=False)
    pd.DataFrame(result['other_dataset_discrepancy_rows']).to_csv("other_discrepancies.csv", index=False)
