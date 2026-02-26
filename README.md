# Web Scraper for South African Event Websites

A comprehensive Python application that automatically scrapes event details from South Africa's major ticketing platforms (Quicket, Howler, Webtickets, and Computicket) and manages them through Firebase with a Flask web interface.

---

## 📋 Table of Contents

- [Project Overview](#project-overview)
- [Key Features](#key-features)
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Environment Setup](#environment-setup)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [How It Works](#how-it-works)
- [Data Architecture](#data-architecture)
- [Technical Details](#technical-details)
- [Error Handling](#error-handling)
- [Contributing](#contributing)
- [FAQ](#faq)
- [Support](#support)

---

## Project Overview

The **Web Scraper for South African Event Websites** is a production-ready event data aggregation system designed for the "What's the Plan" (WTP) application. It automates the collection of event information from multiple ticketing platforms, validates venue data through Google Places API, and stores everything in Firebase for seamless integration with web and mobile applications.

### Use Case
Instead of manually entering event data, WTP uses this scraper to automatically populate and keep its event database current. Users simply add event URLs through the web interface, and the system handles the rest—extracting details, validating venues, enriching data, and storing it in Firebase.

### Problem Solved
- ❌ **Manual data entry** → ✅ Automated extraction
- ❌ **Inconsistent data formatting** → ✅ Structured Pydantic models
- ❌ **Duplicate venues** → ✅ Google Places API validation
- ❌ **Lost logs** → ✅ Firebase Storage + Google Drive backup
- ❌ **Single URL processing** → ✅ Batch processing with web UI

---

## Key Features

### 🎯 Multi-Platform Support
| Platform | Method | Status |
|----------|--------|--------|
| **Quicket** | Official API | ✅ Reliable & Fast |
| **Howler** | Web Scraping | ✅ Price Extraction |
| **Webtickets** | Web Scraping | ✅ Comprehensive |
| **Computicket** | Web Scraping | ✅ Multi-format Dates |

### 📊 Extracted Data
Each event is enriched with:
- **Event Details**: Title, description, image URL
- **Venue Information**: Name, address, coordinates, Google Places ID
- **Dates & Times**: Start/end with timezone auto-conversion to SAST
- **Pricing**: Minimum available (non-sold-out) price
- **Manager**: Account/organizer information

### 🔗 Backend Integration
- **Firebase Firestore** - Primary event & venue storage
- **Firebase Storage** - Log file archival
- **Google Drive** - Backup log storage
- **Google Places API** - Venue validation & enrichment
- **Google Sheets** - Optional URL source management

### 🌐 Web Interface
- User-friendly Flask web app (`app.py`)
- Real-time progress tracking via Server-Sent Events (SSE)
- Session-based batch processing
- Add, remove, and manage multiple event URLs
- Download processing logs

---

## Quick Start

### 1. Clone & Setup Virtual Environment

```bash
# Clone the repository
git clone <repository-url>
cd webscraper-project

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your API keys (see Environment Setup section)
nano .env
```

### 4. Set Up Firebase

1. Create project at [firebase.google.com](https://firebase.google.com)
2. Generate service account key from Firebase Console
3. Save as `wtp.json` in project root
4. Enable: Firestore, Cloud Storage, Admin SDK

### 5. Run It!

```bash
# Web Interface
python app.py
# Visit http://localhost:8000

# Or CLI
python scrape_cli.py "https://www.quicket.co.za/events/360940-spokocafe/"

# Or Batch Processing
python main.py
```

---

## Installation

### System Requirements

- **Python**: 3.8+
- **OS**: macOS, Linux, or Windows
- **RAM**: 256MB+ (typically uses ~50MB)
- **Internet**: Required for API access

### Step-by-Step Installation

```bash
# 1. Clone repository
git clone <repository-url>
cd webscraper-project

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # or: venv\Scripts\activate on Windows

# 3. Install all dependencies
pip install -r requirements.txt

# 4. Verify installation
python -c "from event_scraper.base_scraper import BaseScraper; print('✅ Installation successful')"
```

### Verify Each Scraper

```bash
# Test a sample URL from each platform
python scrape_cli.py "https://www.quicket.co.za/events/360940-spokocafe/"      # Quicket
python scrape_cli.py "https://www.howler.co.za/events/joburg-freshers-c8f6"    # Howler
python scrape_cli.py "https://www.webtickets.co.za/v2/event.aspx?itemid=1573126494"  # Webtickets
python scrape_cli.py "https://computicket-boxoffice.com/e/makhadzi-one-wiman-show-hhZzdO"  # Computicket
```

---

## Environment Setup

### 1. Create `.env` File

```bash
cp .env.example .env
```

### 2. Obtain Required API Keys

#### Quicket API Key
1. Visit [Quicket Partner Portal](https://www.quicket.co.za/)
2. Contact support or register as a partner
3. Get your API key

#### Google Places API
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create new project
3. Enable "Places API"
4. Create API key (restrict to Places API)

#### Google Sheets API (Optional)
1. [Google Cloud Console](https://console.cloud.google.com/)
2. Enable "Google Sheets API"
3. Create service account or OAuth credentials
4. Get your API key/credentials

#### Google Drive (Optional)
1. Same Google Cloud project
2. Enable "Google Drive API"
3. Get folder ID from Drive UI (right-click folder → Get link)

#### Firebase Service Account
1. [Firebase Console](https://console.firebase.google.com/)
2. Project Settings → Service Accounts
3. Generate new key
4. Save as `wtp.json` in project root

### 3. Complete `.env` File

```bash
# Quicket API
QUICKET_API_KEY=your_quicket_api_key_here

# Google Places (venue validation)
PLACES_API=your_google_places_api_key_here

# Google Sheets (optional for URL sources)
SPREADSHEET_ID_EVENTS=your_spreadsheet_id_here
SHEET_NAME=Events
SHEETS_API=your_google_sheets_api_key_here

# Google Drive (optional for log backup)
DRIVE_FOLDER_ID=your_drive_folder_id_here

# Flask (for web interface)
FLASK_SECRET_KEY=your_random_secret_key_here
FLASK_ENV=development  # or production
```

### 4. Firebase Setup

```bash
# Create Firestore collections
# The app will auto-create if they don't exist:
# - 'events' - Event documents
# - 'whatstheplace' - Venue documents

# Verify connection
python -c "from src.components.base_functions.initialize_firebase import initialize_firebase; db = initialize_firebase(); print('✅ Firebase connected')"
```

---

## Usage

### 📱 Web Interface

Perfect for management and interactive batch processing:

```bash
python app.py
```

Then visit **http://localhost:8000**

**Features:**
- Add event URLs one at a time
- Remove URLs before processing
- View real-time scraping progress
- Download logs after completion
- Session management

**Workflow:**
1. Add multiple event URLs
2. Click "Start Processing"
3. Monitor progress in real-time
4. Results stored in Firebase automatically

### 💻 Command Line - Single Event

Quick scraping of individual events:

```bash
python scrape_cli.py "https://www.quicket.co.za/events/360940-spokocafe/"
```

**Output:**
```json
{
  "title": "Spoko Cafe Concert",
  "venue": "Spoko Cafe",
  "location": "Cape Town, South Africa",
  "start_date": "2026-03-15T19:00:00+02:00",
  "price": 150,
  "image_url": "https://...",
  "source": "quicket"
}
```

### 📊 Batch Processing with Google Sheets

Automated processing from spreadsheet sources:

```bash
python main.py
```

**What it does:**
1. Reads URLs from Google Sheets
2. Scrapes all events
3. Validates venues with Google Places
4. Stores in Firebase
5. Uploads logs to Firebase Storage & Google Drive

### 🐍 Python API

Direct integration in your applications:

```python
from event_scraper.base_scraper import BaseScraper
from src.components.base_functions.initialize_firebase import initialize_firebase
import json

# Initialize Firebase
db = initialize_firebase()

# Scrape event
url = "https://www.quicket.co.za/events/360940-spokocafe/"
scraper = BaseScraper.get_scraper_for_url(url)
event = scraper.extract_event_details(url)

if event:
    # Use the data
    print(f"Event: {event.title}")
    print(f"Venue: {event.venue}")
    print(f"Date: {event.start_date}")
    
    # Or store to Firebase
    db.collection('events').document(event.title).set(event.model_dump(mode='json'))
```

### 🔍 Example Scripts

Learn from provided examples:

```bash
python example.py  # Shows various usage patterns
python legacy/local_main.py  # Original implementation
```

---

## Project Structure

```
webscraper-project/
│
├── 📁 event_scraper/               # Core scraper implementations
│   ├── __init__.py
│   ├── base_scraper.py            # Base class + factory method
│   ├── models.py                  # Pydantic EventDetails model
│   ├── quicket_scraper.py         # Quicket API implementation
│   ├── howler_scraper.py          # Howler web scraper
│   ├── webtickets_scraper.py      # Webtickets web scraper
│   ├── computicket_scraper.py     # Computicket web scraper
│   └── __pycache__/
│
├── 📁 src/                         # Application components
│   ├── __init__.py
│   ├── exception.py               # Custom exceptions
│   ├── logger.py                  # Logging configuration
│   │
│   ├── components/
│   │   ├── base_functions/        # Utility functions
│   │   │   ├── __init__.py
│   │   │   ├── identify_platform.py    # Regex-based platform detection
│   │   │   ├── initialize_firebase.py  # Firebase setup
│   │   │   ├── process_event_urls.py   # Main processing pipeline
│   │   │   ├── get_event_urls.py       # URL source management
│   │   │   ├── get_events_from_sheets.py  # Google Sheets reader
│   │   │   ├── get_drive_service.py    # Google Drive integration
│   │   │   ├── google_sheets.py        # Sheets API client
│   │   │   └── __pycache__/
│   │   │
│   │   └── base_scrapers/         # Legacy function wrappers
│   │       ├── __init__.py
│   │       ├── computicket_function.py
│   │       ├── date_extractor.py
│   │       ├── howler_function.py
│   │       ├── places_function.py  # Google Places integration
│   │       ├── quicket_function.py
│   │       ├── ticketpro_function.py
│   │       ├── webtickets_function.py
│   │       └── __pycache__/
│   │
│   └── pipeline/                  # Processing orchestration
│       ├── __init__.py
│       ├── event_pipeline.py      # Main event processing logic
│       └── __pycache__/
│
├── 📁 legacy/                      # Original implementation (v1)
│   ├── __init__.py
│   ├── local_main.py
│   ├── quicket_function.py
│   ├── howler_function.py
│   └── __pycache__/
│
├── 📁 templates/                   # Flask HTML templates
│   └── index.html
│
├── 📁 static/                      # Web assets
│   └── css/
│       └── style.css
│
├── 📁 logs/                        # Development logs
│
├── 📁 logs_production/             # Production logs (timestamped)
│   └── [timestamp].txt
│
├── 📄 app.py                       # Flask web application
├── 📄 main.py                      # Batch processing CLI
├── 📄 scrape_cli.py               # Single event CLI
├── 📄 example.py                   # Usage examples
├── 📄 requirements.txt             # Python dependencies
├── 📄 .env.example                # Environment template
├── 📄 .env                         # Environment variables (don't commit)
├── 📄 wtp.json                     # Firebase credentials (don't commit)
├── 📄 wtp_client.json             # Client credentials (optional)
├── 📄 README.md                    # This file
└── 📄 .gitignore
```

---

## How It Works

### 1. Platform Identification

Event URLs are automatically classified using regex patterns:

```
Input: https://www.quicket.co.za/events/360940/...
       ↓
Regex match: quicket.co.za
       ↓
Output: QuicketScraper (API-based)
```

### 2. Data Extraction

Each platform scraper extracts details using the optimal method:

| Platform | Method | Speed | Reliability |
|----------|--------|-------|-------------|
| Quicket | REST API | 2-3s | ⭐⭐⭐⭐⭐ |
| Howler | BeautifulSoup | 5-8s | ⭐⭐⭐⭐ |
| Webtickets | BeautifulSoup | 5-8s | ⭐⭐⭐⭐ |
| Computicket | BeautifulSoup | 5-10s | ⭐⭐⭐⭐ |

### 3. Venue Enrichment

Extracted venue names are validated through Google Places API:

```python
Input venue: "Spoko Cafe, Cape Town"
       ↓
Google Places Search
       ↓
Returns: {
  "place_id": "ChIJ...",
  "formatted_address": "123 Main St, Cape Town, 8000",
  "location": {"lat": -33.95, "lng": 18.64}
}
```

### 4. Data Validation

Pydantic models ensure data integrity:

```python
EventDetails(
    title: str           # Required
    venue: str          # Required
    start_date: datetime # Auto-validated
    prices: List[Price] # Structured
    location: str       # Optional but validated
)
```

### 5. Firebase Storage

Normalized data stored with automatic deduplication:

```
Firestore:
├── events/[event_id]
│   ├── title: "Concert 2026"
│   ├── venueId: "ref_to_venue"
│   ├── startDate: timestamp
│   └── ...
│
└── whatstheplace/[venue_id]
    ├── name: "Venue Name"
    ├── placeId: "google_places_id"
    └── ...
```

### 6. Logging & Archival

Comprehensive logging with automatic backup:

```
[2026-02-26 21:29:11] Processing: quicket.co.za/events/360940/
[2026-02-26 21:29:15] ✅ Extracted: Spoko Cafe Concert
[2026-02-26 21:29:18] ✅ Venue validated: Spoko Cafe
[2026-02-26 21:29:18] ✅ Stored in Firebase
       ↓
Uploaded to Firebase Storage & Google Drive
```

---

## Data Architecture

### EventDetails Model

```python
class EventDetails(BaseModel):
    title: str                          # Event name
    description: Optional[str]          # Full description
    venue: str                          # Venue name
    location: str                       # Address/location
    start_date: Optional[datetime]      # Start timestamp
    end_date: Optional[datetime]        # End timestamp
    prices: List[Dict[str, str]]        # [{"price": "150", "currency": "ZAR"}]
    image_url: Optional[HttpUrl]        # Event image
    event_url: HttpUrl                  # Source URL
    source: str                         # 'quicket', 'howler', etc.
    raw_data: Dict[str, Any]           # Original HTML/API response (debug)
```

### Firebase Structure

**Collection: `events`**
```
Document: "event_uuid"
├── title: "Spoko Cafe Concert"
├── description: "Live music event..."
├── venueId: "venue_uuid"            # Reference to whatstheplace collection
├── startDate: Timestamp(2026-03-15 19:00:00)
├── endDate: Timestamp(2026-03-15 23:00:00)
├── minPrice: 150
├── image: "https://..."
├── source: "quicket"
├── eventUrl: "https://www.quicket.co.za/events/360940/"
└── createdAt: Timestamp
```

**Collection: `whatstheplace`**
```
Document: "venue_uuid"
├── name: "Spoko Cafe"
├── placeId: "ChIJ..."                # Google Places ID
├── formattedAddress: "123 Main St, Cape Town, 8000"
├── location: GeoPoint(lat: -33.95, lng: 18.64)
├── phones: ["+27 21 123 4567"]
├── website: "https://..."
└── createdAt: Timestamp
```

---

## Technical Details

### Scraper Architecture

**BaseScraper** (Abstract Base Class)
```python
class BaseScraper(ABC):
    @staticmethod
    def get_scraper_for_url(url: str) -> Optional[BaseScraper]:
        """Factory method - returns appropriate scraper"""
    
    @abstractmethod
    def extract_event_details(self, url: str) -> Optional[EventDetails]:
        """Platform-specific implementation"""
```

**Platform Implementations**
```python
class QuicketScraper(BaseScraper):
    # Uses: requests + official Quicket API
    # Auth: API key from environment
    
class HowlerScraper(BaseScraper):
    # Uses: BeautifulSoup + requests
    # Extracts: Price from purchase modal
    
class WebticketsScraper(BaseScraper):
    # Uses: BeautifulSoup + regex patterns
    # Handles: Multiple date formats
    
class ComputicketScraper(BaseScraper):
    # Uses: BeautifulSoup + dateutil parser
    # Handles: All Computicket variations
```

### Request Headers

All requests include realistic user-agent to avoid blocking:

```python
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
    'Cache-Control': 'no-cache'
}
```

### Timeout Strategy

```python
# Individual request timeout
timeout = 10  # seconds

# Retry logic
max_retries = 3
retry_delay = 2  # seconds

# Session-wide timeout
total_timeout = 300  # 5 minutes for batch processing
```

### Memory Management

```
Typical memory usage:
- Idle: ~20MB
- Processing 1 event: ~50MB
- Batch of 10 events: ~80MB

Optimizations:
- Stream responses (no full page load in memory)
- Delete session objects after each event
- Garbage collection between batches
```

---

## Error Handling

### Network Errors

```python
try:
    response = requests.get(url, timeout=10)
    response.raise_for_status()
except requests.ReadTimeout:
    logger.error(f"Timeout: {url}")
    return None
except requests.ConnectionError:
    logger.error(f"Connection failed: {url}")
    return None
```

### Parsing Errors

```python
try:
    price = float(price_text.strip())
except (ValueError, AttributeError):
    logger.warning(f"Could not parse price: {price_text}")
    price = None  # Graceful fallback
```

### Firebase Errors

```python
try:
    db.collection('events').document(doc_id).set(data)
except google.cloud.exceptions.AlreadyExists:
    logger.warning(f"Event already exists: {doc_id}")
except PermissionError:
    logger.error("Firebase permission denied - check credentials")
```

### Validation Errors

```python
try:
    event = EventDetails(**extracted_data)
except ValidationError as e:
    logger.error(f"Invalid data: {e}")
    raise  # Propagate to caller
```

---

## Contributing

### Adding Support for a New Platform

1. **Create Scraper Class**

```python
# event_scraper/newplatform_scraper.py
from event_scraper.base_scraper import BaseScraper
from event_scraper.models import EventDetails

class NewplatformScraper(BaseScraper):
    def extract_event_details(self, url: str) -> Optional[EventDetails]:
        """Extract event details from newplatform"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            # Parse and extract
            soup = BeautifulSoup(response.content, 'html.parser')
            title = soup.find('h1', class_='event-title').text.strip()
            
            # Return structured data
            return EventDetails(
                title=title,
                venue="",
                location="",
                event_url=url,
                source="newplatform"
            )
        except Exception as e:
            self.logger.error(f"Failed to scrape: {e}")
            return None
```

2. **Update Platform Detection**

```python
# src/components/base_functions/identify_platform.py
def identify_platform(url: str) -> Optional[str]:
    if 'newplatform.co.za' in url:
        return 'newplatform'
    # ... other platforms
```

3. **Register in Factory**

```python
# event_scraper/base_scraper.py
@staticmethod
def get_scraper_for_url(url: str) -> Optional[BaseScraper]:
    platform = identify_platform(url)
    scrapers = {
        'quicket': QuicketScraper,
        'howler': HowlerScraper,
        'newplatform': NewplatformScraper,  # Add here
        # ...
    }
    return scrapers.get(platform)()
```

4. **Add Tests**

```bash
python scrape_cli.py "https://www.newplatform.co.za/events/sample-event/"
```

5. **Update README**

Add entry to Features section and Platform-Specific Notes.

---

## FAQ

### **Q: Why use API for Quicket but web scraping for others?**
A: Quicket provides an official, stable API. Most other platforms don't have public APIs, so web scraping is the only option. Quicket's API is also faster (2-3s vs 5-10s) and more reliable.

### **Q: What if a website changes its HTML structure?**
A: The system will log parsing errors. You'll need to update the CSS selectors/regex patterns in the affected scraper class. CSS changes are quick fixes; major restructures may require more work.

### **Q: Can I use this without Firebase?**
A: Yes! The scrapers return `EventDetails` objects. You can modify `process_event_urls()` to use your own database backend instead of Firebase.

### **Q: How often should I run the scraper?**
A: Depends on your needs:
- **New event discovery**: Hourly
- **User-driven**: On-demand when URLs are added
- **Event updates**: Daily for active events

### **Q: What happens if a venue already exists in Firebase?**
A: The system checks Google Places ID to detect duplicates and reuses the existing venue document. This prevents data duplication.

### **Q: How are prices handled when multiple tiers exist?**
A: The scraper extracts the **minimum non-sold-out price** to show the cheapest option. Full price list can be added if needed.

### **Q: Can I schedule automated scraping?**
A: Use a cron job or Airflow:
```bash
# Add to crontab for hourly scraping
0 * * * * cd /path/to/webscraper-project && source venv/bin/activate && python main.py
```

### **Q: What if scraping fails for a URL?**
A: Check logs in `logs_production/[timestamp].txt`:
- Network errors: Check internet & URL
- Parsing errors: Website structure may have changed
- Invalid data: Website may not have event details

### **Q: How much does running this cost?**
A: Mostly free tier:
- **Firebase**: Free tier includes 50K reads/day
- **Google Places**: $0.01-7 per request (request it for testing)
- **Google Sheets/Drive**: Free with Google account

### **Q: Is my data secure?**
A: Yes:
- ✅ Firebase rules restrict access
- ✅ Service account keys in `.env` (not committed to Git)
- ✅ HTTPS for all API calls
- ✅ No sensitive data in logs

### **Q: Can I process events in parallel?**
A: Current implementation is sequential. To parallelize:
```python
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=5) as executor:
    futures = [executor.submit(process_url, url) for url in urls]
    results = [f.result() for f in futures]
```

---

## Support

### Common Issues & Solutions

**Issue: `ImportError: No module named 'event_scraper'`**
- Solution: Ensure you're in project root and virtual environment is activated
- ```bash
  cd webscraper-project
  source venv/bin/activate
  ```

**Issue: `Firebase credentials not found`**
- Solution: Create `wtp.json` from service account key
- Check `GOOGLE_APPLICATION_CREDENTIALS` environment variable

**Issue: `Quicket API 401 Unauthorized`**
- Solution: Verify `QUICKET_API_KEY` in `.env`
- Test: `python -c "print(os.getenv('QUICKET_API_KEY'))"`

**Issue: `TimeoutError` when scraping**
- Solution: Website may be down or slow
- Try manual request: `curl https://www.[website].com`

**Issue: Prices showing as `None`**
- Solution: Website structure may have changed
- Check raw HTML in logs → update CSS selector

### Getting Help

1. **Check logs**: `logs_production/` directory
2. **Review code**: Comments in `event_scraper/` classes
3. **Read examples**: `example.py` for API usage
4. **Test manually**: `python scrape_cli.py <url>`

---

## Performance & Limitations

### Performance Metrics

| Operation | Time | Notes |
|-----------|------|-------|
| Single Quicket event | 2-3s | API call only |
| Single web scraped event | 5-10s | HTTP + parsing |
| Batch of 10 events | 50-100s | Sequential processing |
| Firebase write | 500ms | Depends on network |
| Google Places lookup | 300ms | API call |

### Limitations

1. **Rate limiting**: Websites may block rapid requests (add delays between requests)
2. **Structure changes**: Website HTML changes require code updates
3. **JavaScript rendering**: Sites requiring JS execution need Selenium/Playwright
4. **Login requirements**: Can't scrape pages requiring authentication
5. **Geographic IP blocking**: Some sites restrict based on IP location

---

## Logging & Monitoring

### Log Format

```
[DATE TIME] LINE_NO MODULE - LEVEL - MESSAGE
[2026-02-26 21:29:11,046] 51 root - INFO - --- Event 1/1 ---
[2026-02-26 21:29:15,688] 167 root - INFO - Successfully extracted quicket event
```

### Log Locations

- **Development**: `logs/`
- **Production**: `logs_production/[timestamp].txt`
- **Uploaded to**: Firebase Storage + Google Drive backup

### Monitoring Best Practices

```python
# Track processing metrics
total_events = 0
successful = 0
failed = 0

for url in event_urls:
    event = scrape_and_store(url)
    total_events += 1
    if event:
        successful += 1
    else:
        failed += 1

print(f"Success rate: {successful}/{total_events} ({100*successful/total_events:.1f}%)")
```

---

## Roadmap

- [ ] Add Selenium support for JavaScript-heavy sites
- [ ] Implement webhook notifications for new events
- [ ] Add event duplicate detection using similarity scoring
- [ ] Build admin dashboard for monitoring & management
- [ ] Add ticket availability tracking
- [ ] Support for event categories & tags
- [ ] Multi-language support (Afrikaans, Zulu, etc.)

---

## License

This project is for educational and commercial use within the WTP (What's the Plan) ecosystem. Please respect the terms of service of the websites being scraped.

### Third-Party Libraries

- BeautifulSoup4 (MIT License)
- Requests (Apache 2.0)
- Firebase Admin SDK (Apache 2.0)
- Flask (BSD)
- Pydantic (MIT)

---

## Version History

**v2.0** (February 2026)
- ✨ Unified scraper architecture
- ✨ Flask web interface with real-time progress
- ✨ Google Places venue enrichment
- ✨ Multi-platform support (4 sites)
- ✨ Firebase integration
- ✨ Automated logging & backup

**v1.0** (Legacy)
- Original implementation with individual scraper functions
- Preserved in `legacy/` directory

---

**Last Updated**: February 26, 2026  
**Maintained by**: WTP Development Team
