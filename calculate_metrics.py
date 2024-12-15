import json
from utils.useful_utilities import (read_claims,
                                    read_reverts,
                                    calculate_metrics)

input_path = 'input_data/unzipped'
output_path = 'output_data'

def main():
    
    # Reading Claims and Reverts from input_data folder
    claims = read_claims(f'{input_path}/claims')
    reverts = read_reverts(f'{input_path}/reverts')
    
    metrics = calculate_metrics(claims, reverts)

    with open(f'{output_path}/metrics.json', 'w') as outfile:
        json.dump(metrics, outfile, indent=4)

    for metric in metrics:
        print(f"npi: {metric['npi']}, ndc: {metric['ndc']}, fills: {metric['fills']}, reverted: {metric['reverted']}, avg price: ${metric['avg_price']:.2f}, total price: ${metric['total_price']:.2f}")

if __name__ == '__main__':
    main()