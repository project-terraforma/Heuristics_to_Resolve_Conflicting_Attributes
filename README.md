## Problem Statement: How can we improve the consistency and quality of place data over time by developing heuristics that detect and resolve conflicting or incomplete attributes across similar entities?

### Objective: Improve quality of place data over time by using heuristics to resolve conflicting or incomplete attributes across similar entities.

#### Key Result: Define 5 heuristics that help assess entity trust or stability (e.g., age, edit frequency, source reliability), to support long-term maintenance.

#### Key Result: Build 2 tools to go through database and ensure data quality using these heuristics. 

#### Key Result: Use these tools to clean 5 datasets.

### Project Scope: New York City
#### Databases and Descriptions
https://data.cityofnewyork.us/Business/SBS-Certified-Business-List/ci93-uc8s/about_data SBS Certified Business List
- Features in Data that we're interested: Vendor_Formal_Name(Formal Name of the Company), Vendor_DBA(Name the Company goes by), telephone, Address_Line_1, Address_Line_2, City, State, Postcode

https://data.cityofnewyork.us/City-Government/Points-of-Interest/rxuy-2muj Points of Interest Data Set by NYC Open Data

https://data.cityofnewyork.us/Health/DOHMH-New-York-City-Restaurant-Inspection-Results/43nn-pn8j/about_data New York City Restaurant Inspection Results
- Mostly interested in the date to ensure place still exists

#### Code to explore this database: https://colab.research.google.com/drive/1KqM0r1ZVTOtAm-yUaEZyrNQagDc9Q0Xj?authuser=1#scrollTo=TLTMbwQqrJ7K 
