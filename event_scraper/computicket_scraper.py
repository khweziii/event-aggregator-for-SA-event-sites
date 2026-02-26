from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urljoin
from typing import Optional, Dict, Any, Tuple
from .base_scraper import BaseScraper
from .models import EventDetails

class ComputicketScraper(BaseScraper):
    """Scraper for computicket.co.za event pages."""
    
    def extract_event_details(self, url: str) -> Optional[EventDetails]:
        """Extract event details from a Computicket event page."""
        html_content = self.get_page_content(url)
        if not html_content:
            return None
            
        soup = BeautifulSoup(html_content, 'lxml')
        
        # Extract basic event information
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
            source='computicket',
            raw_data={
                'title': title,
                'venue': venue,
                'location': location
            }
        )
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract the event title."""
        title_elem = soup.find('h1', class_='mt-4')
        return title_elem.get_text(strip=True) if title_elem else "No title found"
    
    def _extract_description(self, soup: BeautifulSoup) -> str:
        """Extract the event description."""
        # Look for the first paragraph that describes the event
        paragraphs = soup.find_all('p')
        for p in paragraphs:
            text = p.get_text(strip=True)
            if text and len(text) > 20 and 'Event' not in text and 'Date:' not in text and 'Time:' not in text:
                return text
        return ""
    
    def _extract_venue_and_location(self, soup: BeautifulSoup) -> Tuple[str, str]:
        """Extract venue and location information."""
        # Look for location in paragraphs
        paragraphs = soup.find_all('p')
        for p in paragraphs:
            text = p.get_text(strip=True)
            if ',' in text and any(word in text.lower() for word in ['south africa', 'limpopo', 'cape town', 'johannesburg']):
                # Split by comma to separate venue and location
                parts = text.split(',', 1)
                if len(parts) == 2:
                    return parts[0].strip(), parts[1].strip()
                return text, text
        
        return "Venue not specified", "Location not specified"
    
    def _extract_dates(self, soup: BeautifulSoup) -> Tuple[Optional[datetime], Optional[datetime]]:
        """Extract start and end dates."""
        import re
        
        # Look for datetime patterns in the entire page text
        page_text = soup.get_text()
        
        # Pattern for "Sat 29 Nov 2025, 12:00 PM - Sun 30 Nov 2025, 06:00 AM" format
        range_pattern = r'(\w{3}\s+\d{1,2}\s+\w{3}\s+\d{4},\s+\d{1,2}:\d{2}\s*(?:AM|PM)?)\s*-\s*(\w{3}\s+\d{1,2}\s+\w{3}\s+\d{4},\s+\d{1,2}:\d{2}\s*(?:AM|PM)?)'
        range_match = re.search(range_pattern, page_text)
        
        if range_match:
            try:
                start_str = range_match.group(1)
                end_str = range_match.group(2)
                
                # Clean up the datetime strings and parse them
                start_date = self._parse_computicket_datetime(start_str)
                end_date = self._parse_computicket_datetime(end_str)
                
                if start_date and end_date:
                    return start_date, end_date
            except Exception as e:
                print(f"Error parsing datetime range: {e}")
                pass
        
        # Fallback: look for individual datetime patterns
        datetime_pattern = r'\w{3}\s+\d{1,2}\s+\w{3}\s+\d{4},\s+\d{1,2}:\d{2}\s*(?:AM|PM)?'
        datetime_matches = re.findall(datetime_pattern, page_text)
        
        if datetime_matches:
            try:
                # Use the first datetime as start date
                start_date = self._parse_computicket_datetime(datetime_matches[0])
                return start_date, None
            except Exception as e:
                print(f"Error parsing single datetime: {e}")
                pass
        
        # Fallback: look for date patterns without time
        date_pattern = r'\w{3}\s+\d{1,2}\s+\w{3}\s+\d{4}'
        date_matches = re.findall(date_pattern, page_text)
        
        if date_matches:
            try:
                start_date = datetime.strptime(date_matches[0], '%a %d %b %Y')
                return start_date, None
            except ValueError:
                pass
        
        # Original fallback logic
        paragraphs = soup.find_all('p')
        for p in paragraphs:
            text = p.get_text(strip=True)
            if 'Date:' in text:
                date_part = text.replace('Date:', '').strip()
                try:
                    start_date = datetime.strptime(date_part.replace('st', '').replace('nd', '').replace('rd', '').replace('th', ''), '%B %d, %Y')
                    return start_date, None
                except ValueError:
                    pass
        
        return None, None
    
    def _parse_computicket_datetime(self, datetime_str: str) -> Optional[datetime]:
        """Parse computicket datetime string, handling various formats."""
        import re
        
        # Clean the datetime string
        datetime_str = datetime_str.strip()
        
        # Handle invalid formats like "18:00 PM" by removing PM for 24-hour times
        if re.search(r'\d{1,2}:\d{2}\s+PM', datetime_str):
            # Check if it's 24-hour format (hour >= 13)
            time_match = re.search(r'(\d{1,2}):(\d{2})\s+PM', datetime_str)
            if time_match:
                hour = int(time_match.group(1))
                if hour >= 13:  # 24-hour format, remove PM
                    datetime_str = datetime_str.replace(' PM', '')
        
        # Try different datetime formats
        formats_to_try = [
            '%a %d %b %Y, %I:%M %p',  # "Sat 29 Nov 2025, 12:00 PM"
            '%a %d %b %Y, %H:%M',     # "Sat 29 Nov 2025, 18:00" (24-hour)
            '%a %d %b %Y, %I:%M',     # "Sat 29 Nov 2025, 12:00" (no AM/PM)
        ]
        
        for fmt in formats_to_try:
            try:
                return datetime.strptime(datetime_str, fmt)
            except ValueError:
                continue
        
        return None
    
    def _extract_image_url(self, soup: BeautifulSoup, base_url: str) -> Optional[str]:
        """Extract the event image URL."""
        # Look for any image with a URL that looks like an event image
        for img in soup.find_all('img'):
            if img.get('src'):
                img_src = img['src']
                # Skip small icons and logos
                if any(x in img_src for x in ['android-chrome', 'favicon', 'icon']):
                    continue
                if img_src.startswith(('http://', 'https://')):
                    return img_src
        return None
    
    def _extract_prices(self, soup: BeautifulSoup) -> list[Dict[str, str]]:
        """Extract pricing information."""
        prices = []
        
        # Look for price text in divs and spans
        for elem in soup.find_all(['div', 'span']):
            text = elem.get_text(strip=True)
            if 'R' in text and 'start at' in text.lower():
                import re
                # Extract price like "R 200.00"
                price_match = re.search(r'R\s*\d+(?:\.\d{2})?', text)
                if price_match:
                    prices.append({
                        'type': 'Starting from',
                        'price': price_match.group()
                    })
        
        return prices
