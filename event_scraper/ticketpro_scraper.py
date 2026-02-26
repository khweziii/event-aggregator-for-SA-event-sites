"""
Ticketpro scraper implementation.
"""

import re
import requests
from datetime import datetime
from typing import Optional, Dict, List, Tuple
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from .base_scraper import BaseScraper, EventDetails


class TicketproScraper(BaseScraper):
    """Ticketpro-specific scraper implementation."""
    
    def __init__(self):
        super().__init__()
    
    def can_handle(self, url: str) -> bool:
        """Check if this scraper can handle the given URL."""
        return 'ticketpro.co.za' in url.lower() or 'ticketproshop.co.za' in url.lower()
    
    def extract_event_details(self, url: str) -> Optional[EventDetails]:
        """Extract event details from a Ticketpro URL."""
        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract all event information
            title = self._extract_title(soup)
            description = self._extract_description(soup)
            venue, location = self._extract_venue_and_location(soup)
            start_date, end_date = self._extract_dates(soup)
            image_url = self._extract_image_url(soup, url)
            prices = self._extract_prices(soup)
            
            # Create and return the event details
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
                source='ticketpro',
                raw_data={
                    'title': title,
                    'venue': venue,
                    'location': location
                }
            )
        except Exception as e:
            print(f"Error extracting Ticketpro event details: {e}")
            return None
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract the event title."""
        # Look for h1 first
        title_elem = soup.find('h1')
        if title_elem:
            title = title_elem.get_text(strip=True)
            # Clean up title if it contains "Tickets for"
            if title.startswith('Tickets for '):
                title = title.replace('Tickets for ', '').replace(' | Ticketpro', '')
            return title
        
        # Fallback to title tag
        title_elem = soup.find('title')
        if title_elem:
            title = title_elem.get_text()
            if title.startswith('Tickets for '):
                title = title.replace('Tickets for ', '').replace(' | Ticketpro', '')
            return title
        
        return "No title found"
    
    def _extract_description(self, soup: BeautifulSoup) -> str:
        """Extract the event description."""
        # First try meta description - often the best for Ticketpro
        meta_desc = soup.find('meta', {'name': 'description'})
        if meta_desc:
            desc = meta_desc.get('content', '')
            # Clean up the description
            desc = desc.replace('Buy tickets for', '').replace('from Ticketpro', '')
            if len(desc) > 100:
                return self._clean_description(desc)
        
        # Look for description in various elements
        description_patterns = [
            soup.find('div', class_='description'),
            soup.find('p', class_='description'),
            soup.find('div', {'data-testid': 'event-description'})
        ]
        
        for pattern in description_patterns:
            if pattern:
                desc = pattern.get_text(strip=True)
                if desc and len(desc) > 50:  # Ensure it's a substantial description
                    return self._clean_description(desc)
        
        # Look for paragraphs that might contain description
        paragraphs = soup.find_all('p')
        for p in paragraphs:
            text = p.get_text(strip=True)
            if (len(text) > 100 and 
                'ticket' not in text.lower() and 
                'price' not in text.lower() and
                'venue' not in text.lower() and
                'date' not in text.lower() and
                not text.startswith('R') and
                'ticketpro' not in text.lower()):
                return self._clean_description(text)
        
        return ""
    
    def _clean_description(self, text: str) -> str:
        """Clean up the description text."""
        if not text:
            return text
            
        # Remove common prefixes
        prefixes_to_remove = ['about', 'description:', 'details:']
        for prefix in prefixes_to_remove:
            if text.lower().startswith(prefix):
                text = text[len(prefix):].strip()
        
        return text
    
    def _extract_venue_and_location(self, soup: BeautifulSoup) -> tuple[str, str]:
        """Extract venue and location information."""
        page_text = soup.get_text()
        
        # Look for location patterns in the page text
        location_patterns = [
            r'Location\s*([^\n]+?)(?:\d{4}|$)',
            r'Venue\s*([^\n]+?)(?:\d{4}|$)',
            r'at\s+([^\n]+?)(?:\d{4}|Tickets)',
            r'Location\s*([^\n]+?)(?:Tickets|from|$)'
        ]
        
        for pattern in location_patterns:
            match = re.search(pattern, page_text, re.IGNORECASE)
            if match:
                location_text = match.group(1).strip()
                # Clean up the location text
                location_text = re.sub(r'\s+', ' ', location_text)
                location_text = location_text.replace('(opens in a new tab)', '').strip()
                
                # Split venue and location if possible
                if ',' in location_text:
                    parts = location_text.split(',', 1)
                    venue = parts[0].strip()
                    location = parts[1].strip()
                    return venue, location
                
                return location_text, location_text
        
        return "Venue not specified", "Location not specified"
    
    def _extract_dates(self, soup: BeautifulSoup) -> tuple[Optional[datetime], Optional[datetime]]:
        """Extract start and end dates."""
        page_text = soup.get_text()
        
        # Look for date patterns like "Dec 06" or "12/06/2025"
        date_patterns = [
            r'(\w{3}\s+\d{1,2})',  # "Dec 06"
            r'(\d{1,2}/\d{1,2}/\d{4})',  # "12/06/2025"
        ]
        
        # Look for time patterns like "1:00 PM - 11:59 PM"
        time_range_pattern = r'(\d{1,2}:\d{2}\s*(?:AM|PM))\s*[-–]\s*(\d{1,2}:\d{2}\s*(?:AM|PM))'
        time_range_match = re.search(time_range_pattern, page_text)
        
        # Find the date
        event_date = None
        for pattern in date_patterns:
            match = re.search(pattern, page_text)
            if match:
                date_str = match.group(1)
                try:
                    if '/' in date_str:  # "12/06/2025" format
                        event_date = datetime.strptime(date_str, '%m/%d/%Y')
                    else:  # "Dec 06" format - assume current year
                        current_year = datetime.now().year
                        event_date = datetime.strptime(f"{date_str} {current_year}", '%b %d %Y')
                    break
                except ValueError:
                    continue
        
        if not event_date:
            return None, None
        
        # Parse the time range
        if time_range_match:
            try:
                start_time_str = time_range_match.group(1)
                end_time_str = time_range_match.group(2)
                
                # Parse times
                start_time = datetime.strptime(start_time_str, '%I:%M %p')
                end_time = datetime.strptime(end_time_str, '%I:%M %p')
                
                # Combine date and time
                start_date = datetime(
                    event_date.year, event_date.month, event_date.day,
                    start_time.hour, start_time.minute
                )
                
                # Handle end date - if end time is earlier than start time, it's next day
                if end_time.hour < start_time.hour:
                    event_date = datetime(
                        event_date.year, event_date.month, event_date.day + 1
                    )
                
                end_date = datetime(
                    event_date.year, event_date.month, event_date.day,
                    end_time.hour, end_time.minute
                )
                
                return start_date, end_date
                
            except ValueError:
                pass
        
        # Fallback: single time with 4-hour default duration
        single_time_pattern = r'(\d{1,2}:\d{2}\s*(?:AM|PM))'
        time_match = re.search(single_time_pattern, page_text)
        if time_match:
            try:
                time_str = time_match.group(1)
                time_obj = datetime.strptime(time_str, '%I:%M %p')
                
                start_date = datetime(
                    event_date.year, event_date.month, event_date.day,
                    time_obj.hour, time_obj.minute
                )
                
                # Add 4 hours for end time if no end time found
                from datetime import timedelta
                end_date = start_date + timedelta(hours=4)
                
                return start_date, end_date
                
            except ValueError:
                pass
        
        # Last resort: date only with default times
        start_date = datetime(
            event_date.year, event_date.month, event_date.day,
            17, 0  # Default 5:00 PM
        )
        end_date = start_date + timedelta(hours=4)  # Default 9:00 PM
        
        return start_date, end_date
    
    def _extract_image_url(self, soup: BeautifulSoup, base_url: str) -> Optional[str]:
        """Extract the event image URL."""
        # Look for various image patterns
        image_selectors = [
            soup.find('meta', {'property': 'og:image'}),
            soup.find('img', {'alt': lambda x: x and 'event' in x.lower()}),
            soup.find('img', class_='event-image'),
            soup.find('img', {'data-testid': 'event-image'})
        ]
        
        for selector in image_selectors:
            if selector:
                if selector.name == 'meta':
                    img_src = selector.get('content')
                else:
                    img_src = selector.get('src')
                
                if img_src:
                    if img_src.startswith(('http://', 'https://')):
                        return img_src
                    return urljoin(base_url, img_src)
        
        # Fallback: look for any meaningful image
        all_imgs = soup.find_all('img')
        for img in all_imgs:
            src = img.get('src', '')
            alt = img.get('alt', '')
            if (src and 
                'logo' not in src.lower() and 
                'icon' not in src.lower() and
                'ticketpro' not in src.lower() and
                ('event' in alt.lower() or len(src) > 50)):
                if src.startswith(('http://', 'https://')):
                    return src
                return urljoin(base_url, src)
        
        return None
    
    def _extract_prices(self, soup: BeautifulSoup) -> list[Dict[str, str]]:
        """Extract pricing information."""
        prices = []
        page_text = soup.get_text()
        
        # Look for "Tickets start at" or "from" patterns first - these are usually the starting prices
        start_price_patterns = [
            r'Tickets? start at\s+(?:ZAR\s+)?R?(\d+(?:\.\d{2})?)',
            r'from\s+(?:ZAR\s+)?R?(\d+(?:\.\d{2})?)',
            r'Starting from\s+(?:ZAR\s+)?R?(\d+(?:\.\d{2})?)'
        ]
        
        for pattern in start_price_patterns:
            matches = re.findall(pattern, page_text, re.IGNORECASE)
            for match in matches:
                try:
                    price_value = float(match)
                    if price_value > 0:
                        prices.append({
                            'type': 'General',
                            'price': f'R{price_value:.0f}' if price_value.is_integer() else f'R{price_value}'
                        })
                        return prices  # Return the first valid starting price found
                except ValueError:
                    continue
        
        # If no starting price found, look for all realistic ticket prices
        all_price_patterns = [
            r'ZAR\s+(\d+(?:\.\d{2})?)',
            r'R(\d+(?:\.\d{2})?)'
        ]
        
        all_prices = []
        for pattern in all_price_patterns:
            matches = re.findall(pattern, page_text)
            for match in matches:
                try:
                    price_value = float(match)
                    # Filter for realistic ticket prices (between R50 and R5000)
                    if 50 <= price_value <= 5000:
                        all_prices.append(price_value)
                except ValueError:
                    continue
        
        if all_prices:
            # Get the lowest realistic price
            min_price = min(all_prices)
            prices.append({
                'type': 'General',
                'price': f'R{min_price:.0f}' if min_price.is_integer() else f'R{min_price}'
            })
        
        return prices
