# Calls Analyze Dataset
# Calls Get Overture Data
import io
import pandas as pd

from get_overture_data import get_overture_data
# from analyze_dataset import get_col_names
from analyze_dataset import make_standard_cols

# Call first to get bounds.json
# make_standard_cols(df, dataset_name) --> 
    # saves col descriptions as a .json in tmp/name/descriptions.json
    # makes unique_name, unique_address, unique_lon_lat files 
    # saves this new edited file in tmp/name/named_edited.csv
    # saves bounds in tmp/name/bounds.json

# get_overture_data(bbox, file_path)
    # file_path is ./tmp/name
    # load bbox from ./tmp/name/bounds.json
    # bbox = (bounds['xmin'], bounds['ymin'], bounds['xmax'], bounds['ymax'])


def process_dataset(file_obj, dataset_name):
    print("called with ", dataset_name)
    df = pd.read_csv(file_obj)
    bounds = make_standard_cols(df, dataset_name, num=2)
    bbox = (bounds['xmin'], bounds['ymin'], bounds['xmax'], bounds['ymax'])
    get_overture_data(bbox, f"./tmp/{dataset_name}")
    return 


# if __name__ == "__main__":
#     with open('./tmp/sbs_businesses.csv', 'rb') as f:
#         uploaded_file_like = io.BytesIO(f.read())
#         process_dataset(uploaded_file_like, dataset_name='nyc_restaurants')
    
