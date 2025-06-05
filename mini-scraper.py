import json
import os
from pathlib import Path

# This is a tool for scraping game art for retro games using the screenscraper api.

def load_credentials():
    """Load ScreenScraper API credentials from config file."""
    config_file = Path(__file__).parent / 'config.json'
    
    if not config_file.exists():
        # Create template config file
        template = {
            "screenscraper": {
                "username": "your_username_here",
                "password": "your_password_here",
                "dev_id": "your_dev_id_here",
                "dev_password": "your_dev_password_here"
            }
        }
        with open(config_file, 'w') as f:
            json.dump(template, f, indent=4)
        print(f"Created config template at {config_file}")
        print("Please fill in your ScreenScraper credentials in the config.json and run again.")
        return None
    
    with open(config_file, 'r') as f:
        config = json.load(f)
    
    return config['screenscraper']

def connect_to_screenscraper():
    """Connect to ScreenScraper API with stored credentials."""
    creds = load_credentials()
    if not creds:
        return None
    
    # Base URL for ScreenScraper API
    base_url = "https://www.screenscraper.fr/api2"
    
    # Test connection
    test_url = f"{base_url}/ssuserInfos.php"
    params = {
        'devid': creds['dev_id'],
        'devpassword': creds['dev_password'],
        'softname': 'mini-scraper',
        'output': 'json',
        'ssid': creds['username'],
        'sspassword': creds['password']
    }
    
    try:
        response = requests.get(test_url, params=params)
        response.raise_for_status()
        return creds
    except requests.RequestException as e:
        print(f"Failed to connect to ScreenScraper: {e}")
        return None

if __name__ == "__main__":
    credentials = connect_to_screenscraper()
    if credentials:
        print("Successfully connected to ScreenScraper API")
