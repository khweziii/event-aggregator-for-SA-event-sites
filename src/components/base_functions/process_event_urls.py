from src.logger import logging 
from google.cloud.firestore import FieldFilter
from src.components.base_functions.identify_platform import identify_platform



def process_event_url(url, db, email="testEndpoint"):
    """Process a single event URL and upload to Firebase using legacy function patterns."""
    logging.info("Processing event URL is initialized")
    try:
        print(f"Processing: {url}")
        logging.info(f"Processing: {url}")
        # Identify platform and use appropriate legacy function
        platform = identify_platform(url)
        
        if platform == 'quicket':
            from src.components.base_scrapers.quicket_function import quicket_event_extractor
            event_result = quicket_event_extractor(url, email)
        elif platform == 'howler':
            from src.components.base_scrapers.howler_function import howler_event_extractor
            event_result = howler_event_extractor(url, email)
        elif platform == 'webtickets':
            from src.components.base_scrapers.webtickets_function import webtickets_event_extractor
            event_result = webtickets_event_extractor(url, email)
        elif platform == 'computicket':
            from src.components.base_scrapers.computicket_function import computicket_event_extractor
            event_result = computicket_event_extractor(url, email)
        elif platform == 'ticketpro':
            from src.components.base_scrapers.ticketpro_function import ticketpro_event_extractor
            event_result = ticketpro_event_extractor(url, email)
        else:
            print(f"Unknown platform: {platform}")
            logging.info(f"Uknown platform: {platform}")
            return False
        
        # Check if event extraction was successful
        if isinstance(event_result, str):
            print(f"Error: {event_result}")
            logging.info(f"Error: {event_result}")
            return False
        
        event_info, establishment_details = event_result
        
        # Get references to collections
        events_ref = db.collection("events")
        venues_ref = db.collection("whatstheplace")
        
        # Check if event already exists
        event_query = events_ref.where(filter=FieldFilter("paymentPortal", "==", event_info['paymentPortal']))
        existing_events = list(event_query.stream())
        
        # Check if venue already exists and handle venue logic like legacy
        venue_id = None
        if establishment_details is not None:
            venue_query = venues_ref.where(filter=FieldFilter("id", "==", establishment_details['id']))
            existing_venues = list(venue_query.stream())
            
            if not existing_venues:
                # Add new venue
                venue_ref = venues_ref.add(establishment_details)
                venue_id = venue_ref[1].id
                print(f"Added new venue: {establishment_details['displayName']}")
                logging.info(f"Added new venue: {establishment_details['displayName']}")
            else:
                venue_id = existing_venues[0].id
                print(f"Using existing venue: {establishment_details['displayName']}")
                logging.info(f"Using existing venue: {establishment_details['displayName']}")
        
        # Add event if it doesn't exist (following legacy logic)
        if not existing_events:
            # Update venueId in event_info if we have a venue
            if venue_id:
                event_info['venueId'] = str(venue_id)
            
            events_ref.add(event_info)
            print(f"Added new event: {event_info['name']}")
            logging.info(f"Added new event: {event_info['name']}")
            return True
        else:
            print(f"Event already exists: {event_info['name']}")
            logging.info(f"Event already exists: {event_info['name']}")
            return True
            
    except Exception as e:
        print(f"Error processing {url}: {e}")
        logging.info(f"Error processing {url}: {e}")
        return False