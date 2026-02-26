from src.components.base_scrapers.base_scraper import BaseScraper
import json

def main():
    # Example URLs - replace with actual event URLs
    webtickets_url = "https://www.webtickets.co.za/v2/event.aspx?itemid=1573126494"
    computicket_url = "https://computicket-boxoffice.com/e/makhadzi-one-wiman-show-hhZzdO"
    
    # Test with Webtickets
    try:
        print("Scraping Webtickets event...")
        webtickets_scraper = BaseScraper.get_scraper_for_url(webtickets_url)
        webtickets_event = webtickets_scraper.extract_event_details(webtickets_url)
        
        if webtickets_event:
            print("\nWebtickets Event Details:")
            print(json.dumps(webtickets_event.model_dump(), indent=2, default=str))
        else:
            print("Failed to scrape Webtickets event")
    except Exception as e:
        print(f"Error scraping Webtickets: {e}")
    
    # Test with Computicket
    try:
        print("\nScraping Computicket event...")
        computicket_scraper = BaseScraper.get_scraper_for_url(computicket_url)
        computicket_event = computicket_scraper.extract_event_details(computicket_url)
        
        if computicket_event:
            print("\nComputicket Event Details:")
            print(json.dumps(computicket_event.model_dump(), indent=2, default=str))
        else:
            print("Failed to scrape Computicket event")
    except Exception as e:
        print(f"Error scraping Computicket: {e}")

if __name__ == "__main__":
    main()
