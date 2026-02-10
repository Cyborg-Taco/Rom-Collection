#!/usr/bin/env python3
"""
Script to generate a JSON file by scanning local ROM directories.
Run this script in the root directory of your Rom-Collection folder.
It will scan all subdirectories (systems) and catalog the ROM files.
"""

import json
import os
import sys
from pathlib import Path

# Common ROM file extensions
ROM_EXTENSIONS = [
    '.zip', '.7z', '.rar', '.gz', '.tar',  # Archives
    '.nes', '.smc', '.sfc', '.fig',  # Nintendo
    '.gb', '.gbc', '.gba',  # Game Boy
    '.n64', '.z64', '.v64',  # N64
    '.smd', '.gen', '.md', '.bin',  # Genesis/Mega Drive
    '.iso', '.cue', '.chd', '.cdi', '.gdi',  # CD-based
    '.nds', '.3ds', '.cia',  # DS/3DS
    '.a26', '.a52', '.a78',  # Atari
    '.pce',  # PC Engine
    '.ngp', '.ngc',  # Neo Geo Pocket
    '.ws', '.wsc',  # WonderSwan
    '.col',  # ColecoVision
    '.int',  # Intellivision
    '.vec',  # Vectrex
    '.lnx',  # Atari Lynx
    '.min',  # Pokemon Mini
    '.32x',  # Sega 32X
    '.gg',  # Game Gear
    '.psx', '.pbp',  # PlayStation
]

def get_file_size(filepath):
    """Get file size in bytes"""
    try:
        return os.path.getsize(filepath)
    except OSError:
        return 0

def scan_directory(base_path):
    """Scan directory and build ROM database"""
    base_path = Path(base_path)
    
    if not base_path.exists() or not base_path.is_dir():
        print(f"Error: {base_path} is not a valid directory", file=sys.stderr)
        return None
    
    rom_data = {
        "systems": {}
    }
    
    print(f"Scanning directory: {base_path}")
    print()
    
    # Get all subdirectories (each is a system)
    subdirs = [d for d in base_path.iterdir() if d.is_dir() and not d.name.startswith('.')]
    
    print(f"Found {len(subdirs)} system directories")
    print()
    
    for system_dir in sorted(subdirs):
        system_name = system_dir.name
        print(f"Processing system: {system_name}")
        
        games = []
        
        # Scan for ROM files in this system directory
        for item in system_dir.iterdir():
            if item.is_file():
                # Check if file has a ROM extension
                if any(item.name.lower().endswith(ext) for ext in ROM_EXTENSIONS):
                    # Get relative path from base directory
                    relative_path = item.relative_to(base_path)
                    
                    game_entry = {
                        "name": item.name,
                        "size": get_file_size(item),
                        "path": str(relative_path).replace('\\', '/')  # Ensure forward slashes
                    }
                    games.append(game_entry)
        
        if games:
            # Sort games by name
            games.sort(key=lambda x: x['name'].lower())
            
            # Use the folder name as-is for the retropie directory
            rom_data['systems'][system_name] = {
                "display_name": system_name,
                "retropie_directory": system_name,
                "rom_count": len(games),
                "games": games
            }
            
            print(f"  Found {len(games)} ROMs")
        else:
            print(f"  No ROMs found")
    
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
    
    # Get the directory to scan (current directory by default)
    if len(sys.argv) > 1:
        scan_path = sys.argv[1]
    else:
        scan_path = "."
    
    output_file = "roms.json"
    
    # Load existing data
    print(f"Checking for existing {output_file}...")
    existing_data = load_existing_json(output_file)
    
    if existing_data.get('systems'):
        print(f"Found existing database with {len(existing_data['systems'])} systems")
        print("Will update with newly scanned data...")
    else:
        print("No existing database found. Creating new one...")
    
    print()
    
    # Scan directory for ROM files
    new_data = scan_directory(scan_path)
    
    if new_data is None:
        print("Failed to scan directory.", file=sys.stderr)
        sys.exit(1)
    
    # Merge new data with existing data
    # This will update existing systems and add new ones
    existing_data['systems'].update(new_data['systems'])
    
    print()
    print(f"Writing data to {output_file}...")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(existing_data, f, indent=2, ensure_ascii=False)
    
    print(f"Successfully created/updated {output_file}")
    print(f"Total systems: {len(existing_data['systems'])}")
    
    total_roms = sum(system['rom_count'] for system in existing_data['systems'].values())
    print(f"Total ROMs: {total_roms}")
    print()
    print("You can now commit this JSON file to your GitHub repository")
    print("Then use the rom_downloader.sh script to download ROMs")

if __name__ == "__main__":
    main()