
# compares the data from overture and other dataset. Saves all the differences in a file to be displayed on streamlit.  
# dictionary {overture_discrepency_rows: [overture data], other_dataset_discrepency_rows: [otherdataset data],}

import pandas as pd
import re
import ast


def compare_based_on_address(overture_dataset_path, other_dataset_path):

    # Names
    # overture_df['names']['primary']
    # other_df['unique_name']

    # Address
    # overture_df['addresses']['freeform'] Parse: number, street name
    # overture_df['addresses'][locality] - City/Boro
    # overture_df['addresses'][postcode] - zipcode
    # overture_df['addresses'][region] - State
    # overture_df['addresses'][country] - Country

    # other_df['unique_address']. Parse: number, street name, zip code, city, state, country

    return
    #return {'Overture': overture_diff_df, f"{base}": other_dataset_diff_df,}


def parse_address1(address):
    """Extract number and lowercase street name from a freeform address."""
    match = re.match(r'(\d+)\s+(.*)', address)
    if match:
        number = match.group(1)
        street = match.group(2).lower().strip()
        return number, street
    return None, None

def compare_n(overture_dataset_path, other_dataset_path):
    # Load datasets
    overture_df = pd.read_csv(overture_dataset_path)
    other_df = pd.read_csv(other_dataset_path)

    # print(overture_df.head())
    # print(other_df.head())

    # count = 0
    # for _, row in overture_df.iterrows():
    #     count += 1
    #     print(row)
    #     print(row['addresses'])
    #     print(type(row['addresses']))
    #     address_list = ast.literal_eval(row['addresses'])  # Safe parsing
    #     print(address_list)
    #     print(type(address_list))
    #     print(address_list[0]['freeform'])
    #     print(type(address_list[0]['freeform']))
    #     print("\n")

    #     if count > 10:
    #         return 

    # return
    # Create a map from (number, street) to name for other_df (the smaller dataset)
    other_address_map = {}
    for _, row in other_df.iterrows():
        unique_address = row['unique_address']
        number, street = parse_address1(unique_address)
        if number and street:
            key = street
            other_address_map[key] = row['unique_name']

    # Lists to store matched names
    matched_names_overture = []
    matched_names_other = []

    count = 0
    # Process overture_df
    for _, row in overture_df.iterrows():
        try:
            address_list = ast.literal_eval(row['addresses'])  # Safe parsing
            if isinstance(address_list, list) and len(address_list) > 0:
                freeform_address = address_list[0]['freeform']
        except Exception as e:
            print("Exception raised this row was skipped\n")
            continue  # skip malformed rows

        if freeform_address:
            count += 1
            if count < 10:
                print("freeform_address", freeform_address, type(freeform_address))

            number, street = parse_address1(freeform_address)
            if number and street:
                key = street
                if key in other_address_map:
                    # Parse name field (similar stringified dict assumption)
                    name_dict = ast.literal_eval(row['names']) if isinstance(row['names'], str) else row['names']
                    overture_name = name_dict.get('primary', 'Unknown')
                    other_name = other_address_map[key]

                    print(f"Match found:")
                    print(f" - Overture: {overture_name}")
                    print(f" - Other: {other_name}\n")

                    matched_names_overture.append(overture_name)
                    matched_names_other.append(other_name)

    # Final matched name lists
    print("\nMatched names from overture_df:")
    print(matched_names_overture)

    print("\nMatched names from other_df:")
    print(matched_names_other)
if __name__ == "__main__":
    compare_n('./tmp/sample_nyc/overture_data.csv', './tmp/sample_nyc/sample_nyc_edited.csv')


