import json
from utils.useful_utilities import (read_pharmacies,
                                    read_claims,
                                    read_reverts,
                                    most_prescribed)

input_path = 'input_data/unzipped'
output_path = 'output_data'

def main():
    
    # Reading Claims, Reverts, and Pharmacy Chains from input_data folder
    pharmacy_chains = read_pharmacies(f'{input_path}/pharmacies')
    claims = read_claims(f'{input_path}/claims')
    reverts = read_reverts(f'{input_path}/reverts')
    
    most_presc = most_prescribed(claims, reverts, pharmacy_chains)

    with open(f'{output_path}/most_prescribed.json', 'w') as outfile:
        json.dump(most_presc, outfile, indent=4)

    for prescription in most_presc:
        print(f"NDC: {prescription['ndc']}")
        print(f"Most Prescribed Quantities: {', '.join(map(str, prescription['most_prescribed_quantity']))}")
        print()

if __name__ == '__main__':
    main()