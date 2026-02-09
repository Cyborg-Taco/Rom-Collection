#!/usr/bin/env python3
"""
Script to generate a JSON file containing all ROMs from the Rom-Collection repository.
This script fetches the directory structure from GitHub and creates a JSON file
that can be used by the ROM downloader script.
"""

import json
import requests
import sys
from urllib.parse import quote

GITHUB_API_BASE = "https://api.github.com/repos/Cyborg-Taco/Rom-Collection/contents"
RAW_BASE = "https://raw.githubusercontent.com/Cyborg-Taco/Rom-Collection/main"

def get_directory_contents(path=""):
    """Fetch directory contents from GitHub API"""
    url = f"{GITHUB_API_BASE}/{path}" if path else GITHUB_API_BASE
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {path}: {e}", file=sys.stderr)
        return []

def scan_repository():
    """Scan the repository and build ROM database"""
    rom_data = {
        "systems": {}
    }
    
    print("Scanning repository root...")
    root_contents = get_directory_contents()
    
    if not root_contents:
        print("Failed to fetch root contents", file=sys.stderr)
        return rom_data
    
    # Filter for directories only (these are the systems)
    systems = [item for item in root_contents if item['type'] == 'dir']
    
    print(f"Found {len(systems)} systems")
    
    for system in systems:
        system_name = system['name']
        print(f"Processing system: {system_name}")
        
        # Get contents of the system directory
        system_contents = get_directory_contents(system_name)
        
        # Filter for ROM files (common extensions)
        rom_extensions = ['.zip', '.7z', '.rar', '.nes', '.snes', '.sfc', 
                         '.gb', '.gbc', '.gba', '.n64', '.z64', '.v64',
                         '.smd', '.gen', '.md', '.bin', '.iso', '.cue',
                         '.chd', '.cdi', '.gdi', '.nds', '.3ds', '.cia']
        
        games = []
        for item in system_contents:
            if item['type'] == 'file':
                # Check if file has a ROM extension
                if any(item['name'].lower().endswith(ext) for ext in rom_extensions):
                    game_entry = {
                        "name": item['name'],
                        "size": item['size'],
                        "download_url": item['download_url'],
                        "path": item['path']
                    }
                    games.append(game_entry)
        
        if games:
            # Use the folder name as-is for the retropie directory
            retropie_dir = system_name
            
            rom_data['systems'][system_name] = {
                "display_name": system_name,
                "retropie_directory": retropie_dir,
                "rom_count": len(games),
                "games": games
            }
            
            print(f"  Found {len(games)} ROMs for {system_name}")
    
    return rom_data

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
    print("ROM Collection JSON Generator")
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
    
    # Scan repository for new data
    new_data = scan_repository()
    
    # Merge new data with existing data
    # This will update existing systems and add new ones
    existing_data['systems'].update(new_data['systems'])
    
    print()
    print(f"Writing data to {output_file}...")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(existing_data, f, indent=2, ensure_ascii=False)
    
    print(f"Successfully updated {output_file}")
    print(f"Total systems: {len(existing_data['systems'])}")
    
    total_roms = sum(system['rom_count'] for system in existing_data['systems'].values())
    print(f"Total ROMs: {total_roms}")
    print()
    print("You can now use this JSON file with the rom_downloader.sh script")

if __name__ == "__main__":
    main()
