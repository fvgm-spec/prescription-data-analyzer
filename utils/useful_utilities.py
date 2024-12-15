import csv
import ijson
import json
from collections import defaultdict, Counter
import os
    
def read_pharmacies(pharmacies_dir: str) -> list:
    """
    Reads pharmacy data from CSV files in the provided directory.

    Args:
        pharmacies_dir (str): The directory containing the pharmacy CSV files.

    Returns:
        dict: A dictionary mapping NPI to pharmacy chain.
    """
    pharmacy_chains = {}
    for filename in os.listdir(pharmacies_dir):
        if filename.endswith('.csv'):
            with open(os.path.join(pharmacies_dir, filename), 'r') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    pharmacy_chains[row['npi']] = row['chain']
                    
    return pharmacy_chains

def read_claims(claims_dir: str) -> list:
    """
    Reads claim data from JSON files in the provided directory.

    Args:
        claims_dir (str): The directory containing the claim JSON files.

    Returns:
        list: A list of claim dictionaries.
    """
    claims = []
    for filename in os.listdir(claims_dir):
        if filename.endswith('.json'):
            with open(os.path.join(claims_dir, filename), 'rb') as jsonfile:
                parser = ijson.parse(jsonfile)
                for prefix, event, value in parser:
                    if prefix == 'item' and event == 'start_map':
                        claim = {}
                    elif prefix == 'item.id' and event == 'string':
                        claim['id'] = value
                    elif prefix == 'item.npi' and event == 'string':
                        claim['npi'] = value
                    elif prefix == 'item.ndc' and event == 'string':
                        claim['ndc'] = value
                    elif prefix == 'item.price' and event == 'number':
                        claim['price'] = float(value)
                    elif prefix == 'item.quantity' and event == 'number':
                        claim['quantity'] = float(value)
                    elif prefix == 'item.timestamp' and event == 'string':
                        claim['timestamp'] = value
                    elif prefix == 'item' and event == 'end_map':
                        
                        claims.append(claim)
                        
    return claims

def read_reverts(reverts_dir: str) -> list:
    """
    Reads revert data from JSON files in the provided directory.

    Args:
        reverts_dir (str): The directory containing the revert JSON files.

    Returns:
        list: A list of revert dictionaries.
    """
    reverts = []
    for filename in os.listdir(reverts_dir):
        if filename.endswith('.json'):
            with open(os.path.join(reverts_dir, filename), 'rb') as jsonfile:
                parser = ijson.parse(jsonfile)
                for prefix, event, value in parser:
                    if prefix == 'item' and event == 'start_map':
                        revert = {}
                    elif prefix == 'item.id' and event == 'string':
                        revert['id'] = value
                    elif prefix == 'item.claim_id' and event == 'string':
                        revert['claim_id'] = value
                    elif prefix == 'item.timestamp' and event == 'string':
                        revert['timestamp'] = value
                    elif prefix == 'item' and event == 'end_map':
                        reverts.append(revert)
                        
    return reverts

def process_data(pharmacy_chains: list, claims: list, reverts: list) -> list:
    """
    Processes the claim data and calculates the total revenue for each pharmacy chain.

    Args:
        pharmacy_chains (dict): A dictionary mapping NPI to pharmacy chain.
        claims (list): A list of claim dictionaries.
        reverts (list): A list of revert dictionaries.

    Returns:
        list: A list of tuples, where each tuple contains the pharmacy chain name and the total revenue.
    """
    reverted_claims = set(revert['claim_id'] for revert in reverts)
    pharmacy_revenues = defaultdict(float)

    for claim in claims:
        if claim['npi'] in pharmacy_chains:
            if claim['id'] not in reverted_claims:
                pharmacy_revenues[pharmacy_chains[claim['npi']]] += claim['price']

    return sorted(pharmacy_revenues.items(), key=lambda x: x[1], reverse=True)

def calculate_metrics(claims: list, reverts: list) -> list:
    """
    Calculates various metrics for each (NPI, NDC) combination.

    Args:
        claims (list): A list of claim dictionaries.
        reverts (list): A list of revert dictionaries.

    Returns:
        list: A list of dictionaries, where each dictionary contains the calculated metrics for a (NPI, NDC) combination.
    """
    reverted_claims = set(revert['claim_id'] for revert in reverts)
    metrics = defaultdict(lambda: {'fills': 0, 'reverted': 0, 'total_price': 0.0})

    for claim in claims:
        key = (claim['npi'], claim['ndc'])
        metrics[key]['fills'] += 1
        metrics[key]['total_price'] += claim['price']
        if claim['id'] in reverted_claims:
            metrics[key]['reverted'] += 1

    return [
        {
            'npi': npi,
            'ndc': ndc,
            'fills': metric['fills'],
            'reverted': metric['reverted'],
            'avg_price': metric['total_price'] / metric['fills'] if metric['fills'] else 0,
            'total_price': metric['total_price']
        }
        for (npi, ndc), metric in metrics.items()
    ]
    
    
def recommendations(claims: list, reverts: list, pharmacy_chains: list) -> list:
    """
    Generates recommendations for the top 2 pharmacy chains with the lowest average price for each NDC.

    Args:
        claims (list): A list of claim dictionaries.
        reverts (list): A list of revert dictionaries.
        pharmacy_chains (dict): A dictionary mapping NPI to pharmacy chain.

    Returns:
        list: A list of dictionaries, where each dictionary contains the NDC and the top 2 pharmacy chains with the lowest average price.
    """
    reverted_claims = set(revert['claim_id'] for revert in reverts)
    ndc_metrics = defaultdict(lambda: defaultdict(list))

    for claim in claims:
        npi = claim['npi']
        ndc = claim['ndc']
        chain = pharmacy_chains.get(npi, 'Unknown')
        price = claim['price']

        ndc_metrics[ndc][chain].append(price)

        if claim['id'] in reverted_claims:
            ndc_metrics[ndc][chain].append(-price)  # Append negative price for reverted claims

    ndc_recommendations = []
    for ndc, chain_metrics in ndc_metrics.items():
        chain_recommendations = []
        for chain, prices in chain_metrics.items():
            avg_price = sum(prices) / len(prices)
            chain_recommendations.append({'name': chain, 'avg_price': avg_price})

        chain_recommendations.sort(key=lambda x: x['avg_price'])
        ndc_recommendations.append({'ndc': ndc, 'chain': chain_recommendations[:2]})

    return ndc_recommendations


def most_prescribed(claims: list, reverts: list) -> list:
    """
    Identifies the most commonly prescribed quantities for each NDC.

    Args:
        claims (list): A list of claim dictionaries.
        reverts (list): A list of revert dictionaries.

    Returns:
        list: A list of dictionaries, where each dictionary contains the NDC and the most commonly prescribed quantities.
    """
    reverted_claims = set(revert['claim_id'] for revert in reverts)
    ndc_quantities = defaultdict(list)

    for claim in claims:
        npi = claim['npi']
        ndc = claim['ndc']
        quantity = claim.get('quantity', 0.0)

        if claim['id'] not in reverted_claims:
            ndc_quantities[ndc].append(quantity)

    ndc_most_prescribed = []
    for ndc, quantities in ndc_quantities.items():
        most_prescribed = Counter(quantities).most_common()
        ndc_most_prescribed.append({"ndc": ndc, "most_prescribed_quantity": [q[0] for q in most_prescribed]})

    return ndc_most_prescribed
