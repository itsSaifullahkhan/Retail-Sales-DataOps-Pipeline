import json
from pathlib import Path

import requests


API_URL = "https://dummyjson.com/carts"
RAW_DATA_PATH = Path("data/raw/carts.json")


def fetch_carts_data():
    """
    Fetch carts data from the API.
    """
    response = requests.get(API_URL, timeout=30)
    response.raise_for_status()
    return response.json()


def save_raw_data(data, output_path):
    """
    Save API response into a raw JSON file.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)


def main():
    print("Fetching carts data from API...")

    data = fetch_carts_data()

    print("Saving raw data into data/raw/carts.json...")

    save_raw_data(data, RAW_DATA_PATH)

    print("Raw API data saved successfully.")


if __name__ == "__main__":
    main()