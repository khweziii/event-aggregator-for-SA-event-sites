"""
Webtickets scraper implementation.
"""

import re
import requests
from datetime import datetime
from typing import Optional, Dict, List
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from .base_scraper import BaseScraper, EventDetails


class WebticketsScraper(BaseScraper):
    """Webtickets-specific scraper implementation."""
    
    def __init__(self):
        super().__init__()
    
    def can_handle(self, url: str) -> bool:
        """Check if this scraper can handle the given URL."""
        return 'webtickets.co.za' in url.lower()
    
    def extract_event_details(self, url: str) -> Optional[EventDetails]:
        """Extract event details from a Webtickets URL."""
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
                source='webtickets',
                raw_data={
                    'title': title,
                    'venue': venue,
                    'location': location
                }
            )
        except Exception as e:
            print(f"Error extracting Webtickets event details: {e}")
            return None
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract the event title."""
        title_elem = soup.find('h1', id='PageHeaderPanel_pageHeader')
        if not title_elem:
            title_elem = soup.find('title')
            if title_elem and title_elem.get('title'):
                return title_elem.get('title')
        return title_elem.get_text(strip=True) if title_elem else "No title found"
    
    def _extract_description(self, soup: BeautifulSoup) -> str:
        """Extract the event description."""
        # Try multiple approaches to find the description
        desc_elem = soup.find('div', class_='event-description')
        if desc_elem:
            return desc_elem.get_text(strip=True)
        
        # Look for any div with text that seems like a description
        # Try to find content that's not just navigation or ticket info
        all_divs = soup.find_all('div')
        for div in all_divs:
            text = div.get_text(strip=True)
            # Look for substantial text that might be a description
            if (len(text) > 100 and 
                'ticket' not in text.lower() and 
                'price' not in text.lower() and
                'venue' not in text.lower() and
                'date' not in text.lower() and
                not text.startswith('R') and
                'webtickets' not in text.lower()):
                # Clean up the description
                text = self._clean_description(text)
                return text
        
        # Fallback: look for paragraphs with substantial content
        paragraphs = soup.find_all('p')
        for p in paragraphs:
            text = p.get_text(strip=True)
            if len(text) > 100:
                text = self._clean_description(text)
                return text
                
        return ""
    
    def _clean_description(self, text: str) -> str:
        """Clean up the description text."""
        if not text:
            return text
            
        # Remove "About" prefix if present (case insensitive)
        if text.lower().startswith('about'):
            text = text[5:]  # Remove "About"
            # Remove any leading whitespace after removing "About"
            text = text.strip()
        
        # Remove other common prefixes
        prefixes_to_remove = ['about', 'description:', 'details:']
        for prefix in prefixes_to_remove:
            if text.lower().startswith(prefix):
                text = text[len(prefix):].strip()
        
        return text
    
    def _extract_venue_and_location(self, soup: BeautifulSoup) -> tuple[str, str]:
        """Extract venue and location information."""
        # Look for the row containing "Venue" text
        rows = soup.find_all('div', class_='row')
        for row in rows:
            if row.get_text() and 'Venue' in row.get_text():
                # Find the col-lg-8 within this row
                venue_div = row.find('div', class_='col-lg-8')
                if venue_div:
                    venue_text = venue_div.get_text(strip=True)
                    # Remove "Location on Google Maps" if present
                    venue_text = venue_text.replace('Location on Google Maps', '').strip()
                    # Split venue and location if possible
                    if ',' in venue_text:
                        parts = venue_text.split(',', 1)
                        venue = parts[0].strip()
                        location = parts[1].strip()
                        return venue, location
                    return venue_text, venue_text
        
        return "Venue not specified", "Location not specified"
    
    def _extract_dates(self, soup: BeautifulSoup) -> tuple[Optional[datetime], Optional[datetime]]:
        """Extract start and end dates."""
        # Look specifically in ticket panels first
        ticket_panels = soup.find_all('div', class_='ticket-panel')
        for panel in ticket_panels:
            # Look for ticket panel title within this panel
            title_elem = panel.find('div', class_='ticket-panel-title')
            if title_elem:
                date_str = title_elem.get_text(strip=True)
                
                # Extract date part (e.g., "06 Dec 2025 12:00" from "Golden Circle - Standing 06 Dec 2025 12:00R550")
                date_match = re.search(r'(\d{1,2}\s+\w{3}\s+\d{4}\s+\d{1,2}:\d{2})', date_str)
                if date_match:
                    date_str = date_match.group()
                    try:
                        start_date = datetime.strptime(date_str, '%d %b %Y %H:%M')
                        return start_date, None  # Single event, no end date
                    except ValueError:
                        continue
        
        # Fallback: look for any element containing date patterns
        all_text = soup.get_text()
        # Look for pattern like "DD Mon YYYY HH:MM"
        date_matches = re.findall(r'\d{1,2}\s+\w{3}\s+\d{4}\s+\d{1,2}:\d{2}', all_text)
        if date_matches:
            try:
                start_date = datetime.strptime(date_matches[0], '%d %b %Y %H:%M')
                return start_date, None
            except ValueError:
                pass
        
        return None, None
    
    def _extract_image_url(self, soup: BeautifulSoup, base_url: str) -> Optional[str]:
        """Extract the event image URL."""
        # Try the original approach first
        img_elem = soup.find('img', class_='event-image')
        if img_elem and 'src' in img_elem.attrs:
            img_src = img_elem['src']
            if img_src.startswith(('http://', 'https://')):
                return img_src
            return urljoin(base_url, img_src)
        
        # Look for image with alt text containing "Event Logo" or "sharing"
        img_elem = soup.find('img', alt=lambda x: x and ('event logo' in x.lower() or 'sharing' in x.lower()))
        if img_elem and 'src' in img_elem.attrs:
            img_src = img_elem['src']
            if img_src.startswith(('http://', 'https://')):
                return img_src
            return urljoin(base_url, img_src)
        
        # Look for images from content.webtickets.co.za domain
        img_elem = soup.find('img', src=lambda x: x and 'content.webtickets.co.za' in x)
        if img_elem:
            img_src = img_elem['src']
            if img_src.startswith(('http://', 'https://')):
                return img_src
            return urljoin(base_url, img_src)
        
        # Fallback: look for any meaningful image (skip logos and icons)
        all_imgs = soup.find_all('img')
        for img in all_imgs:
            src = img.get('src', '')
            alt = img.get('alt', '')
            # Skip logos, icons, and small images
            if (src and 
                'logo' not in src.lower() and 
                'icon' not in src.lower() and
                'webticketsLogo' not in src and
                'pnplogo' not in src and
                ('content.webtickets.co.za' in src or 'event' in alt.lower())):
                if src.startswith(('http://', 'https://')):
                    return src
                return urljoin(base_url, src)
        
        return None
    
    def _extract_prices(self, soup: BeautifulSoup) -> list[Dict[str, str]]:
        """Extract pricing information."""
        prices = []
        
        # Look at all ticket panels to find individual prices
        ticket_panels = soup.find_all('div', class_='ticket-panel')
        all_prices = []
        
        for panel in ticket_panels:
            text = panel.get_text()
            # Look for individual prices (R followed by digits)
            price_matches = re.findall(r'R(\d+)', text)
            for price in price_matches:
                price_value = int(price)
                # Only include prices greater than 0
                if price_value > 0:
                    all_prices.append(price_value)
        
        if all_prices:
            # Get the lowest price greater than 0
            min_price = min(all_prices)
            prices.append({
                'type': 'General',
                'price': f'R{min_price}'
            })
        
        # Also check product-card-price elements as fallback
        price_elems = soup.find_all('div', class_='product-card-price')
        for elem in price_elems:
            text = elem.get_text(strip=True)
            price_match = re.search(r'R(\d+)', text)
            if price_match:
                price_value = int(price_match.group(1))
                if price_value > 0:
                    prices.append({
                        'type': 'General',
                        'price': f'R{price_value}'
                    })
        
        return prices
