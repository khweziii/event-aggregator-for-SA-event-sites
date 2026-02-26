import os
import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv

from .base_scraper import BaseScraper
from .models import EventDetails

class QuicketScraper(BaseScraper):
    """Scraper for quicket.co.za event pages."""
    
    def extract_event_details(self, url: str) -> Optional[EventDetails]:
        """Extract event details from a Quicket event page."""
        load_dotenv()
        
        # Extract event ID from URL
        pattern = r"/events/(\d{6})"
        match = re.search(pattern, url)
        
        if not match:
            print(f'Could not retrieve event id from event link: {url}')
            return None
            
        event_id = match.group(1)
        
        # Get API key from environment
        api_key = os.environ.get("QUICKET_API_KEY")
        if not api_key:
            print("QUICKET_API_KEY not found in environment variables")
            return None
        
        # Define parameters for the API request
        params = {'api_key': api_key}
        
        # Define Quicket API URL
        quicket_url = f"https://api.quicket.co.za/api/Events/{event_id}"
        
        try:
            # Make API request
            response = requests.get(url=quicket_url, params=params, timeout=10)
            response.raise_for_status()
            response_json = response.json()
            
            # Extract event details
            title = response_json.get("name", "Unknown")
            description = self._clean_description(response_json.get("description", ""))
            
            # Extract venue and location information
            venue, location = self._extract_venue_and_location(response_json)
            
            # Extract dates
            start_date, end_date = self._extract_dates(response_json)
            
            # Extract image URL
            image_url = self._extract_image_url(response_json)
            
            # Extract prices
            prices = self._extract_prices(response_json)
            
            return EventDetails(
                title=title,
                description=description,
                venue=venue,
                location=location,
                start_date=start_date,
                end_date=end_date,
                prices=prices,
                image_url=image_url,
                event_url=url,
                source='quicket',
                raw_data=response_json
            )
            
        except requests.RequestException as e:
            print(f"Error fetching Quicket API data: {e}")
            return None
        except Exception as e:
            print(f"Error processing Quicket event data: {e}")
            return None
    
    def _clean_description(self, description: str) -> str:
        """Clean HTML description to plain text."""
        if not description:
            return ""
        
        soup = BeautifulSoup(description, "html.parser")
        cleaned_description = soup.get_text(separator="\n")
        cleaned_text = cleaned_description.replace("\xa0", " ").strip()
        return cleaned_text
    
    def _extract_venue_and_location(self, response_json: Dict[str, Any]) -> tuple[str, str]:
        """Extract venue and location information from API response."""
        venue_data = response_json.get('venue', {})
        locality_data = response_json.get('locality', {})
        
        venue_name = venue_data.get('name', 'Unknown Venue')
        
        # Build location string
        address_parts = []
        if venue_data.get('addressLine1'):
            address_parts.append(venue_data['addressLine1'])
        if venue_data.get('addressLine2'):
            address_parts.append(venue_data['addressLine2'])
        if locality_data.get('levelThree'):  # Town
            address_parts.append(locality_data['levelThree'])
        if locality_data.get('levelTwo'):   # Province
            address_parts.append(locality_data['levelTwo'])
        if locality_data.get('levelOne'):   # Country
            address_parts.append(locality_data['levelOne'])
        
        location = ", ".join(address_parts) if address_parts else "Unknown Location"
        
        return venue_name, location
    
    def _extract_dates(self, response_json: Dict[str, Any]) -> tuple[Optional[datetime], Optional[datetime]]:
        """Extract start and end dates from API response."""
        try:
            start_date_str = response_json.get("startDate")
            end_date_str = response_json.get("endDate")
            
            start_date = None
            end_date = None
            
            if start_date_str:
                start_date = datetime.strptime(start_date_str, "%Y-%m-%dT%H:%M:%S")
            
            if end_date_str:
                end_date = datetime.strptime(end_date_str, "%Y-%m-%dT%H:%M:%S")
            
            return start_date, end_date
            
        except (ValueError, TypeError) as e:
            print(f"Error parsing dates: {e}")
            return None, None
    
    def _extract_image_url(self, response_json: Dict[str, Any]) -> Optional[str]:
        """Extract image URL from API response."""
        image_url = response_json.get("imageUrl")
        if image_url and not image_url.startswith('http'):
            image_url = f"https:{image_url}"
        return image_url
    
    def _extract_prices(self, response_json: Dict[str, Any]) -> List[Dict[str, str]]:
        """Extract price information from API response."""
        prices = []
        tickets = response_json.get("tickets", [])
        
        # Filter out sold out tickets and get available prices
        available_tickets = [ticket for ticket in tickets if not ticket.get('soldOut', True)]
        
        for ticket in available_tickets:
            price = ticket.get('price')
            ticket_type = ticket.get('name', 'General')
            
            if price is not None:
                prices.append({
                    'type': ticket_type,
                    'price': str(price)
                })
        
        return prices
