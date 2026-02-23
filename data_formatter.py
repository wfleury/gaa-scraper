"""
Data formatting and CSV export utilities
"""

import csv
import os
from datetime import datetime
from config import OUTPUT_DIR, CSV_FILENAME, FIELDS_TO_EXTRACT


def format_club_data(raw_data):
    """
    Clean and format raw club data
    
    Args:
        raw_data (dict): Raw data from scraper
        
    Returns:
        dict: Cleaned data
    """
    formatted = {}
    
    for field in FIELDS_TO_EXTRACT:
        value = raw_data.get(field, "")
        
        # Clean up common issues
        if isinstance(value, str):
            value = value.strip()
            # Remove extra whitespace
            value = ' '.join(value.split())
            # Handle "Click here" text in emails
            if field == "email" and "Click here" in value:
                continue
                
        formatted[field] = value
    
    # Add timestamp
    formatted['scraped_at'] = datetime.now().isoformat()
    
    return formatted


def save_to_csv(club_data_list, filename=None):
    """
    Save club data to CSV file
    
    Args:
        club_data_list (list): List of club data dictionaries
        filename (str): Optional custom filename
    """
    if not club_data_list:
        print("No data to save")
        return
    
    # Ensure output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Format all data
    formatted_data = [format_club_data(club) for club in club_data_list]
    
    # Determine filename
    if filename:
        output_path = os.path.join(OUTPUT_DIR, filename)
    else:
        output_path = os.path.join(OUTPUT_DIR, CSV_FILENAME)
    
    # Get all field names (including scraped_at)
    fieldnames = FIELDS_TO_EXTRACT + ['scraped_at']
    
    # Write to CSV
    with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(formatted_data)
    
    print(f"Data saved to: {output_path}")
    print(f"Total clubs: {len(formatted_data)}")
    
    return output_path


def load_existing_csv(filename=None):
    """
    Load existing CSV data
    
    Args:
        filename (str): Optional custom filename
        
    Returns:
        list: Existing data or None if file doesn't exist
    """
    if filename:
        file_path = os.path.join(OUTPUT_DIR, filename)
    else:
        file_path = os.path.join(OUTPUT_DIR, CSV_FILENAME)
    
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            return list(reader)
    return None
