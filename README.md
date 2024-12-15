# Prescription Data Analyzer

This Python application analyzes prescription data, including claims, reverts, and pharmacy information, to provide insights and recommendations for the business team.

## Prerequisites

- Python 3.11
- Required Python packages: `csv`, `ijson`, `json`, `collections`

## Setup

1. Clone the repository:

```bash
git clone https://github.com/your-username/prescription-data-analyzer.git
```

2. Navigate to the project directory:

```bash
cd prescription-data-analyzer
```

3. Ensure you have the required Python packages installed. You can install them using pip:

```bash
pip install -r requirements.txt
```

## Usage

1. You are provided with JSON files corresponding to Claims, Reverts, and Pharmacies, they are located inside the folder `input_data` with corresponding subdirectories for each of the file types.
   
2. Run the following scripts to generate the desired outputs:

a. **Calculate Metrics**:
   ```
   python calculate_metrics.py
   ```
   This script will generate a `metrics.json` file in the `output_data/` directory, containing the calculated metrics for each (`npi`, `ndc`) combination.

b. **Make Recommendations**:
   ```
   python recommendations.py
   ```
   This script will generate a `recommendations.json` file in the `output_data/` directory, containing the top 2 pharmacy chains with the lowest average price for each `ndc`.

c. **Identify Most Prescribed Quantities**:
   ```
   python most_prescribed.py
   ```
   This script will generate a `most_prescribed.json` file in the `output_data/` directory, containing the most commonly prescribed quantities for each `ndc`.

## Deployment

The application is designed to run on a single instance with 10 CPU cores. This configuration allows the scripts to process the data efficiently and take advantage of the available hardware resources.

For efficiently parsing data from JSON directories, the application uses `ijson` library, for example, in the `read_claims` function below, provides several benefits especially when handling large JSON files read from the `input_data` directory. 

```python
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
                ...
```

### Main benefits:

1. **Memory Efficiency**: Traditional JSON parsing libraries, such as the built-in `json` module, load the entire JSON file into memory before parsing. This can be problematic when dealing with large JSON files, as it can quickly consume a significant amount of system memory. In contrast, ijson uses a streaming approach, parsing the JSON file incrementally and only loading a small portion of the data into memory at a time. This reduces the memory footprint of the application, making it more scalable and efficient, especially when processing large datasets.
   
2. **Faster Processing**: By parsing the JSON file incrementally, `ijson` can start processing the data much sooner than a traditional JSON parsing approach. This is particularly beneficial when the JSON files are large, as the application can start working on the data without having to wait for the entire file to be loaded into memory.

3. **Reduced Resource Consumption**: The memory-efficient nature of `ijson` also means that the application will consume fewer system resources, such as CPU and memory, when processing the data. This can be crucial when running the application on a single instance with a limited number of CPU cores, as specified by the DevOps team.

4. **Handling Large Files**: When dealing with very large JSON files, the traditional json module may encounter issues or even fail to load the entire file into memory. ijson, on the other hand, is designed to handle large JSON files without running into such limitations, making it a more robust and reliable choice for this application.

5. **Flexibility**: The `ijson` library allows for more fine-grained control over the parsing process, enabling the developer to extract only the necessary data elements from the JSON file. This can lead to further optimizations and reduced processing overhead, as the application doesn't need to handle unnecessary data.