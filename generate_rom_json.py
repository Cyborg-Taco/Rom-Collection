#!/usr/bin/env python3
"""
Script to download the roms.json file from the Rom-Collection repository.
This script fetches the pre-generated JSON file that contains all ROMs.
"""

import json
import requests
import sys

# Direct link to the JSON file in the repository
JSON_URL = "https://raw.githubusercontent.com/Cyborg-Taco/Rom-Collection/main/roms.json"
RAW_BASE = "https://raw.githubusercontent.com/Cyborg-Taco/Rom-Collection/main"

def download_json():
    """Download the roms.json file from the repository"""
    print("Downloading roms.json from repository...")
    try:
        response = requests.get(JSON_URL)
        response.raise_for_status()
        data = response.json()
        
        # Ensure all games have proper path for downloading
        # If they have download_url, convert it to path
        # If they have path, keep it
        if 'systems' in data:
            for system_name, system_data in data['systems'].items():
                if 'games' in system_data:
                    for game in system_data['games']:
                        # If no path field, try to construct it
                        if 'path' not in game or not game['path']:
                            if 'download_url' in game:
                                # Extract path from download_url
                                url = game['download_url']
                                if 'Rom-Collection' in url:
                                    path = url.split('Rom-Collection/main/')[-1]
                                    game['path'] = path
                            else:
                                # Construct path from system and game name
                                game['path'] = f"{system_name}/{game['name']}"
        
        return data
    except requests.exceptions.RequestException as e:
        print(f"Error downloading JSON file: {e}", file=sys.stderr)
        return None
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON file: {e}", file=sys.stderr)
        return None

def load_existing_json(filename):
    """Load existing JSON file if it exists"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"systems": {}}
    except json.JSONDecodeError:
        print(f"Warning: {filename} is corrupted. Creating new file.", file=sys.stderr)
        return {"systems": {}}

def main():
    print("=" * 60)
    print("ROM Collection JSON Downloader")
    print("=" * 60)
    print()
    
    output_file = "roms.json"
    
    # Load existing data
    print(f"Checking for existing {output_file}...")
    existing_data = load_existing_json(output_file)
    
    if existing_data.get('systems'):
        print(f"Found existing database with {len(existing_data['systems'])} systems")
        print("Updating with new data from repository...")
    else:
        print("No existing database found. Creating new one...")
    
    print()
    
    # Download new data from repository
    new_data = download_json()
    
    if new_data is None:
        print("Failed to download JSON file from repository.", file=sys.stderr)
        sys.exit(1)
    
    # Merge new data with existing data
    # This will update existing systems and add new ones
    if 'systems' in new_data:
        existing_data['systems'].update(new_data['systems'])
    else:
        print("Warning: Downloaded JSON doesn't have 'systems' key. Using as-is.", file=sys.stderr)
        existing_data = new_data
    
    print()
    print(f"Writing data to {output_file}...")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(existing_data, f, indent=2, ensure_ascii=False)
    
    print(f"Successfully updated {output_file}")
    
    if 'systems' in existing_data:
        print(f"Total systems: {len(existing_data['systems'])}")
        total_roms = sum(system.get('rom_count', 0) for system in existing_data['systems'].values())
        print(f"Total ROMs: {total_roms}")
    
    print()
    print("You can now use this JSON file with the rom_downloader.sh script")

if __name__ == "__main__":
    main()