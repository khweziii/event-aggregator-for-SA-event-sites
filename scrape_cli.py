#!/usr/bin/env python3
"""
Command-line interface for the event scraper.
Usage: python scrape_cli.py <url>
"""

import sys
import json
from src.components.base_scrapers.base_scraper import BaseScraper

def main():
    if len(sys.argv) != 2:
        print("Usage: python scrape_cli.py <event-url>")
        print("Example: python scrape_cli.py https://www.webtickets.co.za/v2/event.aspx?itemid=1573126494")
        sys.exit(1)
    
    url = sys.argv[1]
    
    try:
        print(f"Scraping event from: {url}")
        scraper = BaseScraper.get_scraper_for_url(url)
        event = scraper.extract_event_details(url)
        
        if event:
            print("\n=== Event Details ===")
            print(f"Title: {event.title}")
            print(f"Venue: {event.venue}")
            print(f"Location: {event.location}")
            if event.start_date:
                print(f"Start Date: {event.start_date}")
            if event.end_date:
                print(f"End Date: {event.end_date}")
            if event.description:
                print(f"Description: {event.description}")
            if event.prices:
                print("\nPrices:")
                for price in event.prices:
                    print(f"  - {price['type']}: {price['price']}")
            if event.image_url:
                print(f"Image URL: {event.image_url}")
            
            print("\n=== Full JSON Output ===")
            print(json.dumps(event.model_dump(), indent=2, default=str))
        else:
            print("Failed to extract event details")
            sys.exit(1)
            
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
