import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from typing import Optional
from .models import EventDetails

class BaseScraper:
    """Base class for all scrapers."""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
        }
    
    def get_page_content(self, url: str) -> Optional[str]:
        """Fetch the HTML content of a webpage."""
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None
    
    def extract_event_details(self, url: str) -> Optional[EventDetails]:
        """
        Extract event details from the given URL.
        This method should be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement this method")
    
    @staticmethod
    def get_scraper_for_url(url: str) -> 'BaseScraper':
        """Factory method to get the appropriate scraper for the given URL."""
        from .webtickets_scraper import WebticketsScraper
        from .computicket_scraper import ComputicketScraper
        from .quicket_scraper import QuicketScraper
        from .howler_scraper import HowlerScraper
        from .ticketpro_scraper import TicketproScraper
        
        domain = urlparse(url).netloc.lower()
        
        if 'webtickets.co.za' in domain:
            return WebticketsScraper()
        elif 'computicket.com' in domain or 'computicket-boxoffice.com' in domain:
            return ComputicketScraper()
        elif 'quicket.co.za' in domain:
            return QuicketScraper()
        elif 'howler.co.za' in domain:
            return HowlerScraper()
        elif 'ticketpro.co.za' in domain or 'ticketproshop.co.za' in domain:
            return TicketproScraper()
        else:
            raise ValueError(f"No scraper available for URL: {url}")
