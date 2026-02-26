"""
Ticketpro event extractor function.
"""

import os
from dotenv import load_dotenv
from datetime import datetime, timezone, timedelta
# from src.components.base_scrapers.base_scraper import BaseScraper
from src.components.base_scrapers.places_function import get_place_id
from src.logger import logging

def ticketpro_event_extractor(event_link: str, email: str):
    """
    Extract event information from a Ticketpro URL and return structured event data.
    
    Args:
        event_link (str): The Ticketpro event URL
        email (str): Email for the manager account
        
    Returns:
        tuple: (event_info, establishment_details) or error message string
    """
    logging.info("Starting webtickets extractor function")

    try:
        load_dotenv()
        from event_scraper.base_scraper import BaseScraper
        
        # Get the appropriate scraper and extract event details
        scraper = BaseScraper.get_scraper_for_url(event_link)
        event_details = scraper.extract_event_details(event_link)
        
        if not event_details:
            return f'Could not extract event details from: {event_link}'
        
        # Extract venue name for Places API
        # Combine venue and location for more accurate Google Places results
        venue_name = event_details.venue
        location = event_details.location
        
        # For Ticketpro, combine venue and location to give Google Places more context
        if venue_name and location:
            combined_venue = f"{venue_name}, {location}"
        else:
            combined_venue = venue_name or location
        
        # Get place information using Google Places API
        places_api_key = os.environ.get("PLACES_API")
        establishment_details = None
        
        if combined_venue and places_api_key:
            place_info = get_place_id(combined_venue, api_key=places_api_key)
            
            if place_info is not None:
                establishment_details = {
                    "id": place_info["candidates"][0]['place_id'],
                    "formattedAddress": place_info["candidates"][0]['formatted_address'],
                    "location": place_info["candidates"][0]['geometry']['location'],
                    "displayName": place_info["candidates"][0]['name'],
                    "managerAccount": 'testAddEventEndpoint'
                }
        
        # Extract pricing information
        price = 0
        if event_details.prices:
            try:
                numeric_prices = []
                for price_info in event_details.prices:
                    price_str = price_info.get('price', '0')
                    price_num = ''.join(char for char in price_str if char.isdigit() or char == '.')
                    if price_num:
                        numeric_prices.append(float(price_num))
                
                price = min(numeric_prices) if numeric_prices else 0
            except:
                price = 0
        
        # Create event object following the exact same structure as other platforms
        # Add timezone information for consistency
        start_date_with_tz = None
        end_date_with_tz = None
        
        if event_details.start_date:
            start_date_with_tz = datetime(
                event_details.start_date.year,
                event_details.start_date.month,
                event_details.start_date.day,
                event_details.start_date.hour,
                event_details.start_date.minute,
                tzinfo=timezone(timedelta(hours=2))
            )
        
        if event_details.end_date:
            end_date_with_tz = datetime(
                event_details.end_date.year,
                event_details.end_date.month,
                event_details.end_date.day,
                event_details.end_date.hour,
                event_details.end_date.minute,
                tzinfo=timezone(timedelta(hours=2))
            )
        
        event_info = {
            'ageRestriction': '18 and older',
            'artistNames': [],
            'artists': [],
            'description': event_details.description or '',
            'endDate': end_date_with_tz,
            'genres': [],
            'managerAccount': email,
            'name': event_details.title,
            'paymentPortal': str(event_details.event_url),
            'price': price,
            'startDate': start_date_with_tz,
            'venue': "",  # will be filled with venueId if venue exists
            'venueId': "",
            'whatstheplace': "",
            'eventImageUrl': str(event_details.image_url) if event_details.image_url else ''
        }
        
        return event_info, establishment_details
        
    except Exception as e:
        return f'Error extracting Ticketpro event: {str(e)}'



# ticketpro_event_extractor(event_link="https://shop.ticketpro.co.za/event/utrecht-maskandi-festival-bowj3g", email="Endpoint")