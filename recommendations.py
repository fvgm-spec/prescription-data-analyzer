import json
from utils.useful_utilities import (read_pharmacies,
                                    read_claims,
                                    read_reverts,
                                    recommendations)

input_path = 'input_data/unzipped'
output_path = 'output_data'

def main():
    
    # Reading Claims, Reverts, and Pharmacy Chains from input_data folder
    pharmacy_chains = read_pharmacies(f'{input_path}/pharmacies')
    claims = read_claims(f'{input_path}/claims')
    reverts = read_reverts(f'{input_path}/reverts')
    
    recs = recommendations(claims, reverts, pharmacy_chains)

    with open(f'{output_path}/recommendations.json', 'w') as outfile:
        json.dump(recs, outfile, indent=4)

    for rec in recs:
        print(f"NDC: {rec['ndc']}")
        for chain in rec['chain']:
            print(f"  Chain: {chain['name']}, Avg Price: ${chain['avg_price']:.2f}")
        print()

if __name__ == '__main__':
    main()