#!/usr/bin/env python3
"""
Main script that reads event URLs from Google Sheets, scrapes event details
using the unified scraper architecture, and uploads to Firebase collections.
"""
from src.logger import logging 
from src.components.base_functions.get_event_urls import get_event_urls_from_users
from src.components.base_functions.identify_platform import identify_platform
from src.components.base_functions.initialize_firebase import initialize_firebase
from src.components.base_functions.process_event_urls import process_event_url
from firebase_admin import storage
from googleapiclient.http import MediaFileUpload
# from google.oauth2.credentials import Credentials
from src.logger import LOG_FILE, LOG_FILE_PATH
from src.components.base_functions.get_drive_service import get_drive_service_uri, DRIVE_ID
# from src.components.base_functions.get_drive_service
import os 
from dotenv import load_dotenv

load_dotenv()



def main():
    """Main function to process all events from Google Sheets."""
    print("=== Event Scraper - Main Process ===")
    logging.info("=== Event Scraper - Main Process ===")
    # Initialize Firebase
    print("Initializing Firebase...")
    db = initialize_firebase()
    
    # Get event URLs from Google Sheets
    # print("Fetching event URLs from Google Sheets...")
    # event_urls = get_event_urls_from_sheets()

    # Get event URLs from user 
    print("Fetching event URLs from User....")
    event_urls = get_event_urls_from_users()
    
    if not event_urls:
        print("⚠️  No event URLs found or missing environment variables.")
        logging.info("⚠️  No event URLs found or missing environment variables.")
    
    # Process each event URL
    print(f"Processing {len(event_urls)} events...")
    logging.info(f"Processing {len(event_urls)} events...")
    success_count = 0
    total_count = len(event_urls)
    
    for index, url in enumerate(event_urls, 1):
        print(f"\n--- Event {index}/{total_count} ---")
        logging.info(f"\n--- Event {index}/{total_count} ---")
        
        # Identify platform using regex patterns (similar to your original logic)
        platform = identify_platform(url)
        print(f"Platform identified: {platform}")
        
        # Process the event
        if process_event_url(url, db):
            success_count += 1
    
    print(f"\n=== Processing Complete ===")
    print(f"Successfully processed: {success_count}/{total_count} events")
    print(f"Failed: {total_count - success_count} events")
    logging.info(f"\n=== Processing Complete ===")
    logging.info(f"Successfully processed: {success_count}/{total_count} events")
    logging.info(f"Failed: {total_count - success_count} events")

    try:
        # initialize_firebase(credentials_path, bucket_name)
        destination_folder="logs"
        bucket = storage.bucket()
        destination_blob = f"{destination_folder}/{LOG_FILE}"
        blob = bucket.blob(destination_blob)

        blob.upload_from_filename(LOG_FILE_PATH)
        print(f"Log file '{LOG_FILE}' uploaded to Firebase Storage at '{destination_blob}'.")

    except Exception as e:
        logging.error(f"Failed to upload log file to Firebase Storage: {e}")
        raise

    try:

        service = get_drive_service_uri()

        file_metadata = {
            "name": LOG_FILE,
            "parents": [DRIVE_ID]
        }
        media = MediaFileUpload(LOG_FILE_PATH, mimetype="text/plain")

        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields="id"
        ).execute()

        print(f"Log '{LOG_FILE}' uploaded to Google Drive. File ID: {file.get('id')}")

    except Exception as e:
        logging.error(f"Failed to upload log to Google Drive: {e}")
        raise


# if __name__ == "__main__":
#     main()
