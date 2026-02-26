import os

# import blob
from dotenv import load_dotenv
import requests
import re
import pandas as pd
from bs4 import BeautifulSoup
from src.components.base_scrapers.places_function import get_place_id
from firebase_admin import credentials, firestore,initialize_app, storage
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from src.logger import logging
from datetime import datetime, timezone, timedelta



def quicket_event_extractor(event_link, email):

    load_dotenv()
    logging.info("Starting quicket extractor function")
    # Initialize Firebase Admin
    # cred = credentials.Certificate("wtp.json")
    #
    # initialize_app(cred, {
    #     "storageBucket": "whatstheplan-ab453.firebasestorage.app"
    # })
    #
    # db = firestore.client()
    # bucket = storage.bucket()
    #
    # # Google Sheets API Setup
    # # SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive.file"]
    #
    # SERVICE_ACCOUNT_FILE = "wtp_service_account2.json"
    # credentials = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)

    # Define your spreadsheet and range
    # SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
    # RANGE = os.getenv("RANGE")  # Adjust as needed
    #
    # service = build("sheets", "v4", credentials=credentials)
    # sheet = service.spreadsheets()

    # ##------------------------------Manually inputted event links from several websites
    # quicket_event_links = ["https://www.quicket.co.za/events/296038-soke-celebrate-africa-cpt-8-march-2025/?ref=events-list#/",
    #                        "https://www.quicket.co.za/events/296929-feel-good-series-presents-umi-our-music-festival/?ref=events-list",
    #                        "https://www.quicket.co.za/events/302433-meji-meji-joburg-takeover/?ref=events-list",
    #                        "https://www.quicket.co.za/events/298674-zethe-breathe-album-launch-johannesburg/?ref=events-list",
    #                        "https://www.quicket.co.za/events/301903-one-park-x-kalashnikovv-gallery-art-fair-after-party/?ref=events-list"
    #                ]
    #
    #
    # ##------------------------------Manually inputted event links from several websites
    #

    api_key = os.environ.get("QUICKET_API_KEY")

    # defining parameters for the header
    param_list = {

        'api_key': api_key
    }


    ##------------------Extracting the event ids from the event urls
    # for full_url in event_link:

    # Search for the pattern in the URL
    # Regex pattern to extract the 6 digits after '/events/'
    pattern = r"/events/(\d{6})"

    match = re.search(pattern, event_link)

    if match:
        # event_id.append(match.group(1)) # Extract the first (and only) capturing group
        event_id = match.group(1)

        ##------------------Extracting the event ids from the event urls
        the_events_df = pd.DataFrame(columns=['event_id', 'name', 'description', 'start_date', 'end_date','event_url', 'imageURL', 'venueName', 'address_line1','address_line2','town', 'province', 'country', 'organiser_url', 'cheapest_ticket_price'])



        # Define quicket api url to get an event given its id
        quicket_url = f"https://api.quicket.co.za/api/Events/{event_id}"

        # Making a get request to obtain event information for the given event id
        r = requests.get(url=quicket_url, params=param_list)

        # Ensuring that the response's output is in json format
        response_json = r.json()
        #
        # print(response_json["name"])
        #
        description_soup = BeautifulSoup(response_json["description"], "html.parser")
        cleaned_description = description_soup.get_text(separator="\n")
        cleaned_text = cleaned_description.replace("\xa0", " ").strip()

        # print(cleaned_text)
        #
        price = [dict.get('price') for dict in response_json["tickets"] if dict.get('soldOut') is False]

        #
        address_line1 = response_json['venue'].get('addressLine1') if response_json['venue'] else ""
        address_line2 = response_json['venue'].get('addressLine2') if response_json['venue'] else ""
        town = response_json['locality'].get('levelThree') if response_json['venue'] else ""
        province = response_json['locality'].get('levelTwo') if response_json['venue'] else ""
        country = response_json['locality'].get('levelOne') if response_json['venue'] else ""
        venue_name = response_json['venue'].get('name') if response_json['venue'] else ""

        places_api_key = os.environ.get("PLACES_API")
        place_info = get_place_id(venue_name, api_key=places_api_key)
        #
        if place_info is not None:
            establishment_details = {
            "id" : place_info["candidates"][0]['place_id'],
            "formattedAddress" : place_info["candidates"][0]['formatted_address'],
            "location" : place_info["candidates"][0]['geometry']['location'],
            "displayName" : place_info["candidates"][0]['name'],
            "managerAccount": 'testAddEventEndpoint'

            }


        else:
            establishment_details = None

        datetime_endDate = datetime.strptime(response_json["endDate"], "%Y-%m-%dT%H:%M:%S")

        # Original ISO string (in UTC)
        datetime_startDate = datetime.strptime(response_json["startDate"], "%Y-%m-%dT%H:%M:%S")

        new_row_firestore = {
            'ageRestriction': '18 and older',
            'artistNames': [],
            'artists': [],
            'description': cleaned_text,
            'endDate': datetime(datetime_endDate.year, datetime_endDate.month, datetime_endDate.day,
                                datetime_endDate.hour, datetime_endDate.minute,
                                tzinfo=timezone(timedelta(hours=2))),
            'genres': [],
            'managerAccount': email,
            'name': response_json["name"],
            'paymentPortal': response_json["url"],
            'price': min(price) if price else "Unknown",
            'startDate': datetime(datetime_startDate.year, datetime_startDate.month, datetime_startDate.day,
                                  datetime_startDate.hour, datetime_startDate.minute,
                                  tzinfo=timezone(timedelta(hours=2))),
            'venue': "",
            'venueId': "",
            'whatstheplace': "",
            'eventImageUrl': f"https:{response_json["imageUrl"]}"
            # should be the venue id

            # 'venue': venue_name+", "+address_line1+", "+address_line2+", "+town+", "+province # should be the venue id
        }

        # venue_info = {
        #     "venueId": venue_id,
        #     "managerAccount": email
        # }
        # venue_info = {
        #     "venueId": "",
        #     "managerAccount": email
        # }
        # print(new_row_firestore)
        logging.info("Successfully extracted quicket event information")

        return new_row_firestore, establishment_details
        # new_row_sheets = [
        #     response_json['id'],
        #     response_json["name"],
        #     cleaned_text,
        #     response_json["startDate"],
        #     response_json["endDate"],
        #     response_json["url"],
        #     f"https:{response_json["imageUrl"]}" if response_json["imageUrl"] else "Unknown",
        #     response_json['venue'].get('name') if response_json['venue'] else "Unknown",
        #     response_json['venue'].get('addressLine1') if response_json['venue'] else "Unknown",
        #     response_json['venue'].get('addressLine2') if response_json['venue'] else "Unknown",
        #     response_json['locality'].get('levelThree') if response_json['venue'] else "Unknown",
        #     response_json['locality'].get('levelTwo') if response_json['venue'] else "Unknown",
        #     response_json['locality'].get('levelOne') if response_json['venue'] else "Unknown",
        #     response_json['organiser'].get('organiserPageUrl') if response_json['venue'] else "Unknown",
        #     min(price) if price else "Unknown"
        # ]
        #

        # print(new_row_sheets)
        # # Append the row to the sheet
        # response = sheet.values().append(
        #     spreadsheetId=SPREADSHEET_ID,
        #     range=RANGE,  # Use an empty range or specify a range like 'Sheet1!A1'
        #     valueInputOption="RAW",  # 'RAW' to enter data as-is, 'USER_ENTERED' for formulas
        #     insertDataOption="INSERT_ROWS",  # Automatically inserts new rows if necessary
        #     body={
        #         "values": [new_row_sheets]
        #     }
        # ).execute()

        # print("#----------------------------------------#")
        # print(f"Added event number to Google Sheets: {id}")
        # print("#----------------------------------------#")

        # db.collection("events").add(new_row_firestore)
        #
        # print("#----------------------------------------#")
        # print(f"Added event number to Firestore: {id}")
        # print("#----------------------------------------#")

    else:
        # print('#--------------------------------------------------------#')
        # print(f'Could not retrieve event id from event link: {event_link}')
        # print('#--------------------------------------------------------#')
        #
        return f'Could not retrieve event id from event link: {event_link}'















