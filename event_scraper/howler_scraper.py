import requests
from bs4 import BeautifulSoup
from datetime import datetime
from typing import Optional, Dict, Any, List
from urllib.parse import urljoin

from .base_scraper import BaseScraper
from .models import EventDetails

class HowlerScraper(BaseScraper):
    """Scraper for howler.co.za event pages."""
    
    def extract_event_details(self, url: str) -> Optional[EventDetails]:
        """Extract event details from a Howler event page."""
        html_content = self.get_page_content(url)
        if not html_content:
            return None
            
        soup = BeautifulSoup(html_content, 'html.parser')
        
        try:
            # Extract basic event information
            title = self._extract_title(soup)
            description = self._extract_description(soup)
            venue, location = self._extract_venue_and_location(soup)
            start_date, end_date = self._extract_dates(soup)
            image_url = self._extract_image_url(soup)
            prices = self._extract_prices(soup, url)
            
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
                source='howler',
                raw_data={'url': url}
            )
            
        except Exception as e:
            print(f"Error processing Howler event data: {e}")
            return None
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract the event title."""
        try:
            event_page = soup.find("div", class_="page-wrapper")
            if not event_page:
                return "Unknown Event"
            
            event_hero = event_page.find("div", class_="event-hero")
            if not event_hero:
                return "Unknown Event"
            
            hero_one = event_hero.find("div", class_="inset-x--large-on-medium")
            if not hero_one:
                return "Unknown Event"
            
            hero_two = hero_one.find("div", class_="event-hero__content")
            if not hero_two:
                return "Unknown Event"
            
            hero_event_name = hero_two.find("h1", class_="t-display")
            if hero_event_name:
                return hero_event_name.get_text(strip=True)
            
        except Exception as e:
            print(f"Error extracting title: {e}")
        
        return "Unknown Event"
    
    def _extract_description(self, soup: BeautifulSoup) -> str:
        """Extract the event description."""
        try:
            event_page = soup.find("div", class_="page-wrapper")
            if not event_page:
                return ""
            
            event_carousel = event_page.find("div", class_="event-carousel")
            if not event_carousel:
                return ""
            
            carousel_one = event_carousel.find("div", class_="event-section__content")
            if not carousel_one:
                return ""
            
            carousel_event_description = carousel_one.find_all("p")
            if carousel_event_description:
                descriptions = [par.get_text(strip=True) for par in carousel_event_description]
                return "\n".join(descriptions)
            
        except Exception as e:
            print(f"Error extracting description: {e}")
        
        return ""
    
    def _extract_venue_and_location(self, soup: BeautifulSoup) -> tuple[str, str]:
        """Extract venue and location information."""
        try:
            event_page = soup.find("div", class_="page-wrapper")
            if not event_page:
                return "Unknown Venue", "Unknown Location"
            
            event_bar = event_page.find("div", class_="event-bar")
            if not event_bar:
                return "Unknown Venue", "Unknown Location"
            
            bar_one = event_bar.find("div", class_="event-bar__info")
            if not bar_one:
                return "Unknown Venue", "Unknown Location"
            
            bar_three = bar_one.find("div", class_="event-detail event-detail__venue flex flex--align-items--center")
            if not bar_three:
                return "Unknown Venue", "Unknown Location"
            
            bar_venue_name = bar_three.find("h3")
            bar_venue_address = bar_three.find("a")
            
            venue = bar_venue_name.get_text(strip=True) if bar_venue_name else "Unknown Venue"
            location = bar_venue_address.get_text(strip=True) if bar_venue_address else "Unknown Location"
            
            return venue, location
            
        except Exception as e:
            print(f"Error extracting venue and location: {e}")
        
        return "Unknown Venue", "Unknown Location"
    
    def _extract_dates(self, soup: BeautifulSoup) -> tuple[Optional[datetime], Optional[datetime]]:
        """Extract start and end dates."""
        try:
            # Import date extractor function from legacy directory
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
            from legacy.date_extractor import extract_date_components
            
            event_page = soup.find("div", class_="page-wrapper")
            if not event_page:
                return None, None
            
            event_bar = event_page.find("div", class_="event-bar")
            if not event_bar:
                return None, None
            
            bar_one = event_bar.find("div", class_="event-bar__info")
            if not bar_one:
                return None, None
            
            bar_two = bar_one.find("div", class_="event-detail event-detail__date flex flex--align-items--center")
            if not bar_two:
                return None, None
            
            bar_event_dates = bar_two.find("a")
            bar_event_dates_alt = bar_two.find("h3")
            
            if bar_event_dates and bar_event_dates_alt:
                date_string = bar_event_dates.get_text(strip=True)
                alt_date = bar_event_dates_alt.get_text(strip=True)
                
                start, end = extract_date_components(date_string, alt_date)
                
                if start and end:
                    start_date = datetime(start['year'], start['month'], start['day'], 
                                        start['hour'], start['minute'])
                    end_date = datetime(end['year'], end['month'], end['day'], 
                                      end['hour'], end['minute'])
                    return start_date, end_date
            
        except Exception as e:
            print(f"Error extracting dates: {e}")
        
        return None, None
    
    def _extract_image_url(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract the event image URL."""
        try:
            event_page = soup.find("div", class_="page-wrapper")
            if not event_page:
                return None
            
            event_hero = event_page.find("div", class_="event-hero")
            if not event_hero:
                return None
            
            hero_one = event_hero.find("div", class_="inset-x--large-on-medium")
            if not hero_one:
                return None
            
            hero_two = hero_one.find("div", class_="event-hero__content")
            if not hero_two:
                return None
            
            hero_event_image = hero_two.find("img")
            if hero_event_image and hero_event_image.get("src"):
                return hero_event_image["src"]
            
        except Exception as e:
            print(f"Error extracting image URL: {e}")
        
        return None
    
    def _extract_prices(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, str]]:
        """Extract ticket prices."""
        prices = []
        
        try:
            event_page = soup.find("div", class_="page-wrapper")
            if not event_page:
                return prices
            
            event_bar = event_page.find("div", class_="event-bar")
            if not event_bar:
                return prices
            
            bar_four = event_bar.find("div", class_="event-bar__action")
            if not bar_four:
                return prices
            
            bar_link_to_purchase = bar_four.find("a")
            if not bar_link_to_purchase or not bar_link_to_purchase.get("href"):
                return prices
            
            # Get ticket page URL
            ticket_url = f"https://ag.howler.co.za{bar_link_to_purchase['href']}"
            
            # Fetch ticket page
            ticket_response = requests.get(ticket_url, headers=self.headers, timeout=10)
            if ticket_response.status_code != 200:
                return prices
            
            ticket_soup = BeautifulSoup(ticket_response.content, "html.parser")
            ticket_page = ticket_soup.find("div", class_="purchase-process-wrapper")
            
            if not ticket_page:
                return prices
            
            ticket_one = ticket_page.find("div", class_="ticket-selection-layout__main")
            if not ticket_one:
                return prices
            
            ticket_forms = ticket_one.find_all("form", id="ticket_order_form")
            ticket_form = None
            
            for form in ticket_forms:
                if form.get("action") == "/ticket_order/tickets":
                    ticket_form = form
                    break
            
            if not ticket_form:
                return prices
            
            # Try different ticket selection layouts
            ticket_prices = self._extract_ticket_prices_from_form(ticket_form)
            
            if ticket_prices:
                for price in ticket_prices:
                    prices.append({
                        'type': 'General',
                        'price': str(price)
                    })
            
        except Exception as e:
            print(f"Error extracting prices: {e}")
        
        return prices
    
    def _extract_ticket_prices_from_form(self, ticket_form) -> List[int]:
        """Extract prices from ticket form."""
        ticket_prices = []
        
        try:
            # Try accordion content layout
            ticket_types = ticket_form.find("div", class_="accordion-content ticket-selection__accordion-content")
            
            if ticket_types:
                for ticket in ticket_types.find_all(recursive=False):
                    try:
                        ticket_status = ticket.find("div", class_="ticket-info__booking-status")
                        if ticket_status:
                            continue  # Skip sold out tickets
                        
                        price_elem = ticket.find("div", class_="ticket__price")
                        if price_elem:
                            price_text = price_elem.get_text(strip=True)
                            price_num = ''.join(char for char in price_text if char.isdigit() or char == ".")
                            if price_num:
                                ticket_prices.append(int(float(price_num)))
                    
                    except Exception:
                        continue
            else:
                # Try loose ticket layout
                ticket_types = ticket_form.find_all("div", class_="ticket-selection ticket-selection--loose-ticket")
                
                for ticket in ticket_types:
                    try:
                        ticket_status = ticket.find("div", class_="ticket-info__booking-status")
                        if ticket_status:
                            continue  # Skip sold out tickets
                        
                        price_elem = ticket.find("div", class_="ticket__price")
                        if price_elem:
                            price_text = price_elem.get_text(strip=True)
                            price_num = ''.join(char for char in price_text if char.isdigit() or char == ".")
                            if price_num:
                                ticket_prices.append(int(float(price_num)))
                    
                    except Exception:
                        continue
        
        except Exception as e:
            print(f"Error extracting ticket prices from form: {e}")
        
        return ticket_prices
