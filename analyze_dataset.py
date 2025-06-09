# Take file path to dataset as input
# Make a new temp file that includes the first 70 lines of the dataset

# Prompt a small LLM to find the cols and get a short description of this

# Export this as a dictionary (print it but also return it)
# with the 
import pandas as pd
import os
import json
from get_overture_data import get_overture_data

## TO DO

## Fow now: default names of database cols

# Parameters
#if lat_lon is combined lat_lon paramter will be [col_name, 0] if it is in format lat, lon 
#                                                [col_name, 1] if it is in format lon, lat 
#if they are different cols, lat will come first

# address_col will either be one col or a few. 
# If it is a few the cols will be in order of a proper address: 

def generate_descriptions(df, num):
    if num == 1:
        descriptions = {
    "camis": "Unique identifier for each restaurant/food establishment in the system",
    "dba": "Doing Business As name; the operating name of the restaurant or food establishment",
    "boro": "Borough where the establishment is located (Manhattan, Brooklyn, Queens, Bronx, Staten Island)",
    "building": "Street number/building address",
    "street": "Street name where the establishment is located",
    "zipcode": "ZIP code of the establishment's location",
    "phone": "Contact phone number for the establishment",
    "cuisine_description": "Type of cuisine served (e.g., American, Chinese, Pizza, Thai)",
    "inspection_date": "Date when the health inspection was conducted",
    "action": "Result/action taken during inspection (e.g., 'Violations were cited', 'No violations recorded')",
    "violation_code": "Specific code identifying the type of health violation found",
    "violation_description": "Detailed description of the health violation",
    "critical_flag": "Indicates whether the violation is considered 'Critical' or 'Not Critical'",
    "score": "Numerical inspection score (higher scores indicate more violations)",
    "grade": "Letter grade assigned based on inspection (A, B, C, etc.)",
    "grade_date": "Date when the grade was assigned",
    "record_date": "Date when this record was entered into the system",
    "inspection_type": "Type of inspection conducted (e.g., 'Cycle Inspection', 'Pre-permit')",
    "latitude": "Geographic latitude coordinate of the establishment",
    "longitude": "Geographic longitude coordinate of the establishment",
    "community_board": "NYC community board district number",
    "council_district": "NYC council district number",
    "census_tract": "Census tract identifier",
    "bin": "Building Identification Number",
    "bbl": "Borough, Block, and Lot identifier",
    "nta": "Neighborhood Tabulation Area code",
    "location_point1": "Additional location reference point"
        }
    
    else:
        descriptions = {
    "account_number": "Unique identifier assigned to each vendor/contractor account in the system",
    "vendor_formal_name": "Official legal business name of the vendor or contracting company",
    "vendor_dba": "Doing Business As name - the trade name or brand name used by the vendor",
    "first_name": "First name of the primary contact person or business owner",
    "last_name": "Last name of the primary contact person or business owner",
    "telephone": "Primary phone number for contacting the vendor",
    "business_description": "Detailed description of the company's services, products, and business activities",
    "certification": "Type of business certification (e.g., MBE=Minority Business Enterprise, WBE=Women Business Enterprise)",
    "cert_renewal_date": "Date when the business certification expires and needs to be renewed",
    "ethnicity": "Ethnicity classification of the business owner (ASIAN, HISPANIC, BLACK, NON-MINORITY)",
    "address1": "Primary street address line 1 of the business location",
    "address2": "Secondary address line (apartment, suite, floor number, etc.)",
    "city": "City where the business is physically located",
    "state": "State abbreviation where the business is located",
    "zip": "ZIP postal code of the business location",
    "mailingaddress1": "Mailing address line 1 (may differ from physical address)",
    "mailingaddress2": "Mailing address line 2 (apartment, suite, P.O. Box, etc.)",
    "mailingcity": "City for mailing correspondence",
    "mailingstate": "State for mailing correspondence",
    "mailingzip": "ZIP code for mailing correspondence",
    "website": "Company's official website URL",
    "date_of_establishment": "Date when the business was officially established or incorporated",
    "aggregate_bonding_limit": "Maximum dollar amount of bonding capacity available to the contractor",
    "signatory_to_union_contracts": "Indicates whether the company is bound by union labor agreements",
    "id6_digit_naics_code": "6-digit North American Industry Classification System code identifying the business type",
    "naics_sector": "Broad industry sector classification from NAICS",
    "naics_subsector": "More specific industry subsector within the NAICS classification",
    "naics_title": "Descriptive title of the NAICS industry classification",
    "types_of_construction_projects_performed": "Categories or types of construction work the contractor performs",
    "nigp_codes": "National Institute of Governmental Purchasing commodity codes for products/services",
    "name_of_client_job_exp_1": "Client name for the first job experience reference",
    "largest_value_of_contract": "Dollar value of the largest contract completed (from job experience 1)",
    "percent_self_performed_job_exp_1": "Percentage of work performed by own employees vs subcontractors for job 1",
    "date_of_work_job_exp_1": "Date when the first referenced job was completed",
    "description_of_work_job_exp_1": "Detailed description of services provided for the first job reference",
    "name_of_client_job_exp_2": "Client name for the second job experience reference",
    "value_of_contract_job_exp_2": "Dollar value of the contract for the second job reference",
    "percent_self_performed_job_exp_2": "Percentage of work self-performed vs subcontracted for job reference 2",
    "date_of_work_job_exp_2": "Completion date for the second job reference",
    "description_of_work_job_exp_2": "Description of services provided for the second job reference",
    "name_of_client_job_exp_3": "Client name for the third job experience reference",
    "value_of_contract_job_exp_3": "Dollar value of the contract for the third job reference",
    "percent_self_performed_job_exp_3": "Percentage of work self-performed vs subcontracted for job reference 3",
    "date_of_work_job_exp_3": "Completion date for the third job reference",
    "description_of_work_job_exp_3": "Description of services provided for the third job reference",
    "capacity_building_programs": "Participation in business development or capacity building programs",
    "enrolled_in_passport": "Whether the vendor is enrolled in the NYC Passport program (Yes/No)",
    "borough": "NYC borough where the business is located (Manhattan, Brooklyn, Bronx, Queens, Staten Island)",
    "latitude": "Geographic latitude coordinate of the business location",
    "longitude": "Geographic longitude coordinate of the business location",
    "community_board": "NYC Community Board district number where the business is located",
    "council_district": "NYC City Council district number for the business location",
    "bin": "Building Identification Number - unique identifier for NYC buildings",
    "bbl": "Borough, Block, and Lot number - NYC property identification system",
    "census_tract_2020_": "US Census tract number from the 2020 census for demographic analysis",
    "neighborhood_tabulation_area_nta_2020_": "NYC Neighborhood Tabulation Area code from 2020 for statistical reporting"
    }


    return descriptions

def make_standard_cols(df, dataset_name, num, name_col='dba', address_col=['building', 'street', 'zipcode'], lat_lon=['latitude', 'longitude']):
    if num == 1:
        name_col='dba'
        address_col=['building', 'street', 'zipcode']
        lat_lon=['latitude', 'longitude']
    else:
        name_col='vendor_formal_name'
        address_col=['address1', 'zip']
        lat_lon=['latitude', 'longitude']

    # Rename name_col to unique_name
    df['unique_name'] = df[name_col]

    # Combine address columns into one string column if multiple provided
    if len(address_col) > 1:
        df['unique_address'] = df[address_col].astype(str).agg(' '.join, axis=1)
    elif len(address_col) == 1:
        df['unique_address'] = df[address_col[0]]
    else:
        raise ValueError("address_col must have at least one column name.")

    # Process lat/lon and build unique_lon_lat as dict {x: lon, y: lat}
    lat_vals = []
    lon_vals = []

    if len(lat_lon) == 2 and isinstance(lat_lon[0], list):
        # lat_lon is in format [[combined_col_name, order]]
        combined_col, order = lat_lon[0]
        split_coords = df[combined_col].astype(str).str.split(",", expand=True)
        if order == 0:  # lat, lon
            lat = split_coords[0].astype(float)
            lon = split_coords[1].astype(float)
        elif order == 1:  # lon, lat
            lon = split_coords[0].astype(float)
            lat = split_coords[1].astype(float)
        else:
            raise ValueError("lat_lon order must be 0 (lat, lon) or 1 (lon, lat)")
    elif len(lat_lon) == 2:
        # Separate lat and lon columns provided
        lat = df[lat_lon[0]].astype(float)
        lon = df[lat_lon[1]].astype(float)
    else:
        raise ValueError("lat_lon must be a list of two separate columns or a list of one [col_name, order].")

    df['unique_lon_lat'] = [{"x": x, "y": y} for x, y in zip(lon, lat)]

    # Filter out invalid lat/lon: non-numeric, NaN, or (0, 0)
    valid_mask = (~lat.isna()) & (~lon.isna()) & ~((lat == 0) & (lon == 0))
    lat_valid = lat[valid_mask]
    lon_valid = lon[valid_mask]

    df.loc[valid_mask, 'unique_lon_lat'] = [{"x": x, "y": y} for x, y in zip(lon_valid, lat_valid)]
    df.loc[~valid_mask, 'unique_lon_lat'] = None  # Set invalid ones to None

    # Calculate bounding box only for valid coordinates
    bounds = {
        "xmin": lon_valid.min(),
        "xmax": lon_valid.max(),
        "ymin": lat_valid.min(),
        "ymax": lat_valid.max(),
    }
    
    edited_path = f"{dataset_name}_edited.csv" 

    os.makedirs(f"./tmp/{dataset_name}/", exist_ok=True)
    df.to_csv(f"./tmp/{dataset_name}/{edited_path}", index=False)
    with open(f"./tmp/{dataset_name}/bounds.json", "w") as f:
        json.dump(bounds, f, indent=2)

    descriptions = generate_descriptions(df=df,num=num)
    with open(f"./tmp/{dataset_name}/descriptions.json", "w") as f:
        json.dump(descriptions, f, indent=2)

    return bounds

# if __name__ == "__main__":

#     bounds, folder_name = make_standard_cols(file_path="./tmp/sample_nyc.csv")

#     #Call get_overture_data for given bbox
#     bbox = (bounds['xmin'], bounds['ymin'], bounds['xmax'], bounds['ymax'])

#     # bbox format should be (west, south, east, north)
#     # translates to         (lon_min, lat_min, lon_max, lat_max)
#     # translates to         (xmin, ymin, xmax, ymax)
#     get_overture_data(bbox, folder_name)


    # add call get_overture_data.py
    #print(bounds)


