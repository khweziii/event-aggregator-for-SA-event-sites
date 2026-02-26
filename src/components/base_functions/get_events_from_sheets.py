
import os
from dotenv import load_dotenv
from google.cloud.firestore import FieldFilter
from src.components.base_functions.google_sheets import get_google_sheet_data

def get_event_urls_from_sheets():
    """Fetch event URLs from Google Sheets."""
    load_dotenv()
    
    # Check required environment variables
    required_vars = {
        'SPREADSHEET_ID_EVENTS': os.environ.get("SPREADSHEET_ID_EVENTS"),
        'SHEET_NAME': os.environ.get("SHEET_NAME"),
        'SHEETS_API': os.environ.get("SHEETS_API")
    }
    
    missing_vars = [var for var, value in required_vars.items() if not value]
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        print("Please add these to your .env file:")
        for var in missing_vars:
            print(f"   {var}=your_{var.lower()}_here")
        return []
    
    sheets_data = get_google_sheet_data(
        spreadsheet_id=required_vars['SPREADSHEET_ID_EVENTS'],
        sheet_name=required_vars['SHEET_NAME'],
        api_key=required_vars['SHEETS_API']
    )
    
    event_urls = []
    
    # Skip header row and extract URLs from column B (index 1)
    for index, row in enumerate(sheets_data.get('values', [])):
        if index > 0 and len(row) > 1:  # Skip header and ensure row has URL column
            event_urls.append(row[1])
    
    print(f"Found {len(event_urls)} event URLs in Google Sheets")
    return event_urls