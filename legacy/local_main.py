# from .howler_function import howler_event_extractor
# from .quicket_function import quicket_event_extractor
# from .webtickets_function import webtickets_event_extractor
# from .computicket_function import computicket_event_extractor
# from firebase_admin import credentials, firestore,initialize_app, storage
# from google.cloud.firestore import FieldFilter
# from src.components.google_sheets import get_google_sheet_data
# import re
# from dotenv import load_dotenv
# import os


# cred = credentials.Certificate("wtp.json")

# initialize_app(cred, {
#     "storageBucket": "whatstheplan-ab453.firebasestorage.app"
# })

# db = firestore.client()

# load_dotenv()

# sheets_data = get_google_sheet_data(spreadsheet_id=os.environ.get("SPREADSHEET_ID_EVENTS"),
#                                     sheet_name=os.environ.get("SHEET_NAME"),
#                                     api_key=os.environ.get("SHEETS_API"))

# # print(sheets_data['values'][1][1])
# # print(len(sheets_data['values']))

# event_urls = []

# for index,value in enumerate(sheets_data['values']):

#     if index > 0:
#         # print(value[1])
#         event_urls.append(value[1])

# # print(event_urls)
# ##------------------------------Input-from-Frontend-which-will-be-an-array/will be a json object
# # list_input = []
# # input_from_frontend = input("Enter event url: ")
# # list_input.append(input_from_frontend)
# # ##------------------------------Input-from-Frontend-which-will-be-an-array/will be a json object
# #
# qkt_pattern = r"quicket"

# hwlr_pattern = r"howler"

# wbtckts_pattern = r"webtickets"

# cmptckt_pattern = r"computicket"

# # for index,value in enumerate(list_input):
# for index,value in enumerate(event_urls):

#     qkt_match = re.search(qkt_pattern, value, re.IGNORECASE)  # Case-insensitive

#     hwlr_match = re.search(hwlr_pattern, value, re.IGNORECASE) # Case-insensitive

#     wbtckts_match = re.search(wbtckts_pattern, value, re.IGNORECASE) # Case-insensitive

#     cmptckt_match = re.search(cmptckt_pattern, value, re.IGNORECASE) # Case-insensitive

#     if qkt_match:

#         print(f'---------Loading Event Details for Event {index}------------------------------')
#         event_info = quicket_event_extractor(event_link=value, email="kgalemakhwezi0@gmail.com") # change this to actual person's email
#         print(f'---------Done Loading Event Details for Event {index}-------------------------')

#         # add the event to the "events" collection in firestore (A NoSQL Database)
#         print(f'---------Adding Event {index} To Events Collection----------------------------')
#         if isinstance(event_info, tuple):
#             # print(event_info)

#             doc_ref = db.collection("whatstheplace")

#             events_ref = db.collection("events")
#             #
#             venue_query = (
#                 doc_ref
#                 .where(filter=FieldFilter("id", "==", event_info[1]['id']))
#             )


#             #
#             docs = list(venue_query.stream())

#             # print(venue_query.stream())

#             event_query = (
#                 events_ref
#                 .where(filter=FieldFilter("paymentPortal", "==", event_info[0]['paymentPortal']))
#             )
#             #
#             docs_event = list(event_query.stream())

#             '''
#             First condition is to check if a venue already exists in our collection:
#                 if the venue doesn't exist then check if the event exists, 
#                     if the event doesn't exist then add it to the events collection
#                     if the venue exists from our API then add it to the whatstheplace collection
#             '''
#             if not docs:
#                 # print("I'm inside if not docs conditional")
#                 '''
#                 Second condition is to check if an event already exists in our collection
#                 '''
#                 if event_info[1] is not None:
#                     venue_ref = db.collection("whatstheplace").add(event_info[1])
#                     # print(venue_ref[1].id)

#                     if not docs_event:
#                         new_row = event_info[0]
#                         new_row['venueId'] = str(venue_ref[1].id)

#                         db.collection("events").add(new_row)
#                         # print(new_row)
#                 # if not docs_event:
#                 #
#                 #     db.collection("events").add(event_info[0])
#                 #
#                 #     if event_info[1] is not None:
#                 #
#                 #         db.collection("whatstheplace").add(event_info[1])


#             else:
#                 query_results = venue_query.stream()

#                 venue_id = [doc.id for doc in query_results]

#                 if not docs_event:

#                     new_row = event_info[0]
#                     new_row['venueId'] = str(venue_id[0])
#                     db.collection("events").add(event_info[0])

#             print(f'---------Done Adding Event {index} To Events Collection--------------------')

#         else:

#             print(f'------Error loading event info into Events Collection----------------------')


#     if hwlr_match:
#         print(f'---------Loading Event Details for Event {index}------------------------------')
#         event_info = howler_event_extractor(event_link=value, email="kgalemakhwezi0@gmail.com")
#         print(f'---------Done Loading Event Details for Event {index}-------------------------')

#         # add the event to the "events" collection in firestore (A NoSQL Database)
#         print(f'---------Adding Event {index} To Events Collection----------------------------')
#         # print(event_info)

#         doc_ref = db.collection("whatstheplace")
#         #
#         events_ref = db.collection("events")

#         venue_query = (
#             doc_ref
#             .where(filter=FieldFilter("id", "==", event_info[1]['id']))
#         )
#         #
#         docs = list(venue_query.stream())
#         # print(docs)
#         event_query = (
#             events_ref
#             .where(filter=FieldFilter("paymentPortal", "==", event_info[0]['paymentPortal']))
#         )
#         #
#         docs_event = list(event_query.stream())

#         '''
#           First condition is to check if a venue already exists in our collection:
#               if the venue doesn't exist then check if the event exists, 
#                   if the event doesn't exist then add it to the events collection
#                   if the venue exists from our API then add it to the whatstheplace collection
#         '''
#         if event_info[1] is not None:
#             venue_ref = db.collection("whatstheplace").add(event_info[1]) # enable us to obtain document id
#             # print(venue_ref[1].id)

#             if not docs_event:
#                 new_row = event_info[0]
#                 new_row['venueId'] = str(venue_ref[1].id) # adding document id to new row

#                 db.collection("events").add(new_row)



#         else:
#             query_results = venue_query.stream() # stream venue query

#             venue_id = [doc.id for doc in query_results] # iterate through document fields for document id

#             if not docs_event:
#                 new_row = event_info[0]
#                 new_row['venueId'] = str(venue_id) # add document id to new row
#                 db.collection("events").add(event_info[0])


#         print(f'---------Done Adding Event {index} To Events Collection-----------------------')


#     if wbtckts_match:
#         print(f'---------Loading Event Details for Event {index}------------------------------')
#         event_info = webtickets_event_extractor(event_link=value, email="kgalemakhwezi0@gmail.com")
        
#         if isinstance(event_info, str):
#             print(f'Error: {event_info}')
#             print(f'---------Skipping Webtickets Event {index}-----------------------')
#             continue
            
#         print(f'---------Done Loading Event Details for Event {index}-------------------------')

#         # add the event to the "events" collection in firestore (A NoSQL Database)
#         print(f'---------Adding Event {index} To Events Collection----------------------------')
        
#         event_data, establishment_details = event_info
        
#         # Handle venue logic
#         venue_id = None
#         if establishment_details is not None:
#             doc_ref = db.collection("whatstheplace")
#             venue_query = (
#                 doc_ref
#                 .where(filter=FieldFilter("id", "==", establishment_details['id']))
#             )
#             docs = list(venue_query.stream())

#             if not docs:
#                 venue_ref = db.collection("whatstheplace").add(establishment_details)
#                 venue_id = venue_ref[1].id
#                 print("Added new venue")
#             else:
#                 venue_id = docs[0].id
#                 print("Using existing venue")
        
#         # Update venueId in event_data if we have a venue
#         if venue_id:
#             event_data['venueId'] = str(venue_id)
        
#         # Check if event already exists
#         events_ref = db.collection("events")
#         event_query = events_ref.where(filter=FieldFilter("paymentPortal", "==", event_data['paymentPortal']))
#         existing_events = list(event_query.stream())
        
#         if not existing_events:
#             db.collection("events").add(event_data)
#             print(f'---------Done Adding Event {index} To Events Collection-----------------------')
#         else:
#             print(f'---------Event {index} Already Exists-----------------------')


#     if cmptckt_match:
#         print(f'---------Loading Event Details for Event {index}------------------------------')
#         event_info = computicket_event_extractor(event_link=value, email="kgalemakhwezi0@gmail.com")
        
#         if isinstance(event_info, str):
#             print(f'Error: {event_info}')
#             print(f'---------Skipping Computicket Event {index}-----------------------')
#             continue
            
#         print(f'---------Done Loading Event Details for Event {index}-------------------------')

#         # add the event to the "events" collection in firestore (A NoSQL Database)
#         print(f'---------Adding Event {index} To Events Collection----------------------------')
        
#         event_data, establishment_details = event_info
        
#         # Handle venue logic
#         venue_id = None
#         if establishment_details is not None:
#             doc_ref = db.collection("whatstheplace")
#             venue_query = (
#                 doc_ref
#                 .where(filter=FieldFilter("id", "==", establishment_details['id']))
#             )
#             docs = list(venue_query.stream())

#             if not docs:
#                 venue_ref = db.collection("whatstheplace").add(establishment_details)
#                 venue_id = venue_ref[1].id
#                 print("Added new venue")
#             else:
#                 venue_id = docs[0].id
#                 print("Using existing venue")
        
#         # Update venueId in event_data if we have a venue
#         if venue_id:
#             event_data['venueId'] = str(venue_id)
        
#         # Check if event already exists
#         events_ref = db.collection("events")
#         event_query = events_ref.where(filter=FieldFilter("paymentPortal", "==", event_data['paymentPortal']))
#         existing_events = list(event_query.stream())
        
#         if not existing_events:
#             db.collection("events").add(event_data)
#             print(f'---------Done Adding Event {index} To Events Collection-----------------------')
#         else:
#             print(f'---------Event {index} Already Exists-----------------------')




