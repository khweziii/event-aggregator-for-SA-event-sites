from src.logger import logging 
import re

def identify_platform(url):
    """Identify the ticketing platform from URL."""
    logging.info("Identifying the ticketing platfrom from URL.")
    patterns = {
        'quicket': r'quicket',
        'howler': r'howler',
        'webtickets': r'webtickets',
        'computicket': r'computicket',
        'ticketpro': r'ticketpro'
    }
    
    for platform, pattern in patterns.items():
        if re.search(pattern, url, re.IGNORECASE):
            logging.info(f"Platform identified {platform}")
            return platform
    
    logging.info(f"Platform is unknown")
    return 'unknown'