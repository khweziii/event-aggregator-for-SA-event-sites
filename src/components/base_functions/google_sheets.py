import os
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from dotenv import load_dotenv

def get_google_sheet_data(spreadsheet_id: str, sheet_name: str, api_key: str):
    """
    Fetch data from a Google Sheets spreadsheet.
    
    Args:
        spreadsheet_id: The ID of the Google Sheets spreadsheet
        sheet_name: The name of the sheet to read from
        api_key: Google Sheets API key
    
    Returns:
        Dictionary containing the sheet data
    """
    load_dotenv()
    
    try:
        # Build the Sheets API service
        service = build('sheets', 'v4', developerKey=api_key)
        sheet = service.spreadsheets()
        
        # Get the data from the specified range
        range_name = f"{sheet_name}!A:Z"  # Get all columns
        result = sheet.values().get(spreadsheetId=spreadsheet_id, range=range_name).execute()
        
        return result
        
    except Exception as e:
        print(f"Error fetching Google Sheets data: {e}")
        return {'values': []}
